"""Lambda Calculus 解譯器 —— 核心引擎

本模組實作純 Lambda Calculus 的解析與 Normal order（最左最外）β-歸約，
並且能回傳「每一個歸約步驟」的完整過程。

包含：
    1. AST 節點          Var / Abs / App
    2. 詞法分析          tokenize()
    3. 語法分析          parse()
    4. 自由變數          free_vars()
    5. 新鮮變數          fresh()
    6. 捕獲避免代換      substitute()
    7. Normal order 歸約  reduce_step() / reduce_with_trace()
    8. Pretty printer    to_str()
    9. .lam 程式解析      parse_program() / expand_definitions()
   10. 對外高階函式      evaluate() / evaluate_file()

語法：
    \\x. body     抽象（也接受 λx. body）
    \\x y. body   多參數，等同 \\x.\\y. body
    f a b         函數應用（左結合），等同 ((f a) b)
    (e)           括號
    3             數字語糖，展開成 Church 數 \\f.\\x. f (f (f x))

    .lam 檔中可以用 `name = expr` 先定義縮寫，最後寫要計算的運算式。
    `#` 之後為註解。
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass

# 讓很深的遞迴（Church 數會產生深層項）不至於爆掉
if sys.getrecursionlimit() < 200_000:
    sys.setrecursionlimit(200_000)

# 預設最多歸約步數，避免使用者不小心寫出不停機的項
DEFAULT_MAX_STEPS = 100_000

_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_']*$")


# ============================================================
# 1. AST 節點
# ============================================================
class Expr:
    """所有 AST 節點的基底類別。"""

    __slots__ = ()


@dataclass(frozen=True)
class Var(Expr):
    """變數，例如 x。"""

    name: str


@dataclass(frozen=True)
class Abs(Expr):
    """抽象（函數），例如 \\x. body。"""

    param: str
    body: Expr


@dataclass(frozen=True)
class App(Expr):
    """應用，例如 func arg。"""

    func: Expr
    arg: Expr


# ============================================================
# 2. 詞法分析
# ============================================================
def tokenize(text: str):
    """把字串切成 token 串。回傳 list[(kind, value)]，結尾附 EOF。"""
    tokens = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif c in "\\λ":
            tokens.append(("LAMBDA", c))
            i += 1
        elif c == ".":
            tokens.append(("DOT", "."))
            i += 1
        elif c == "(":
            tokens.append(("LPAREN", "("))
            i += 1
        elif c == ")":
            tokens.append(("RPAREN", ")"))
            i += 1
        elif c.isdigit():
            j = i
            while j < n and text[j].isdigit():
                j += 1
            tokens.append(("NUMBER", text[i:j]))
            i = j
        elif c.isalpha() or c == "_":
            j = i
            while j < n and (text[j].isalnum() or text[j] in "_'"):
                j += 1
            tokens.append(("IDENT", text[i:j]))
            i = j
        else:
            raise SyntaxError(f"無法辨識的字元: {c!r}")
    tokens.append(("EOF", ""))
    return tokens


# ============================================================
# 3. 語法分析（遞迴下降）
# ============================================================
class Parser:
    """把 token 串解析成 AST。

    文法（EBNF）：
        expr        := abstraction
        abstraction := LAMBDA IDENT+ DOT expr | application
        application := atom+
        atom        := IDENT | LPAREN expr RPAREN
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, kind):
        tok = self.advance()
        if tok[0] != kind:
            raise SyntaxError(f"預期 {kind}，卻看到 {tok[0]} ({tok[1]!r})")
        return tok

    def parse(self) -> Expr:
        expr = self.parse_expr()
        if self.peek()[0] != "EOF":
            tok = self.peek()
            raise SyntaxError(f"運算式結尾有多餘的 token: {tok[1]!r}")
        return expr

    def parse_expr(self) -> Expr:
        if self.peek()[0] == "LAMBDA":
            return self.parse_abstraction()
        return self.parse_application()

    def parse_abstraction(self) -> Expr:
        self.expect("LAMBDA")
        params = []
        while self.peek()[0] == "IDENT":
            params.append(self.advance()[1])
        if not params:
            raise SyntaxError("lambda 後面缺少參數名稱")
        self.expect("DOT")
        body = self.parse_expr()
        # 多參數 -> 柯里化：\x y. body == \x.\y. body
        for name in reversed(params):
            body = Abs(name, body)
        return body

    def parse_application(self) -> Expr:
        expr = self.parse_atom()
        while self.peek()[0] in ("IDENT", "LPAREN", "NUMBER"):
            expr = App(expr, self.parse_atom())
        return expr

    def parse_atom(self) -> Expr:
        tok = self.peek()
        if tok[0] == "IDENT":
            self.advance()
            return Var(tok[1])
        if tok[0] == "NUMBER":
            self.advance()
            return church_numeral(int(tok[1]))
        if tok[0] == "LPAREN":
            self.advance()
            expr = self.parse_expr()
            self.expect("RPAREN")
            return expr
        raise SyntaxError(f"預期變數、數字或 '('，卻看到 {tok[0]} ({tok[1]!r})")


def church_numeral(n: int) -> Expr:
    """把整數 n 轉成 Church 數： n = \\f. \\x. f (f (... (f x)))（f 套用 n 次）。"""
    if n < 0:
        raise SyntaxError("Church 數不能是負數")
    f, x = Var("f"), Var("x")
    body = x
    for _ in range(n):
        body = App(f, body)
    return Abs("f", Abs("x", body))


def parse(text: str) -> Expr:
    """解析單一 lambda 運算式。"""
    if not text.strip():
        raise SyntaxError("空白的運算式")
    return Parser(tokenize(text)).parse()


# ============================================================
# 4. 自由變數 / 5. 新鮮變數
# ============================================================
def free_vars(expr: Expr) -> set:
    """回傳運算式中「自由（未被綁定）」的變數名稱。"""
    result = set()
    stack = [(expr, frozenset())]
    while stack:
        node, bound = stack.pop()
        if isinstance(node, Var):
            if node.name not in bound:
                result.add(node.name)
        elif isinstance(node, Abs):
            stack.append((node.body, bound | {node.param}))
        else:  # App
            stack.append((node.func, bound))
            stack.append((node.arg, bound))
    return result


def all_vars(expr: Expr) -> set:
    """回傳運算式中出現的所有變數名稱（含被綁定的）。"""
    result = set()
    stack = [expr]
    while stack:
        node = stack.pop()
        if isinstance(node, Var):
            result.add(node.name)
        elif isinstance(node, Abs):
            result.add(node.param)
            stack.append(node.body)
        else:  # App
            stack.append(node.func)
            stack.append(node.arg)
    return result


def fresh(name: str, avoid: set) -> str:
    """在 name 後面加 ' 直到不與 avoid 衝突，用於 alpha-換名。"""
    base = name.rstrip("'") or name
    candidate = base + "'"
    while candidate in avoid:
        candidate += "'"
    return candidate


# ============================================================
# 6. 捕獲避免代換（capture-avoiding substitution）
# ============================================================
def substitute(expr: Expr, var: str, value: Expr) -> Expr:
    """把 expr 中自由的 var 代換成 value，且避免變數捕獲。

    這就是 λ 演算的核心運算：expr[var := value]
    """
    if isinstance(expr, Var):
        return value if expr.name == var else expr

    if isinstance(expr, App):
        return App(
            substitute(expr.func, var, value),
            substitute(expr.arg, var, value),
        )

    # Abs
    if expr.param == var:
        # 內層同名參數會遮蔽外層，不需代換
        return expr

    if expr.param in free_vars(value):
        # 會發生捕獲：先把綁定變數換成名稱不衝突的新變數
        avoid = free_vars(value) | all_vars(expr.body) | {var}
        new_param = fresh(expr.param, avoid)
        renamed_body = substitute(expr.body, expr.param, Var(new_param))
        return Abs(new_param, substitute(renamed_body, var, value))

    return Abs(expr.param, substitute(expr.body, var, value))


# ============================================================
# 7. Normal order β-歸約
# ============================================================
def reduce_step(expr: Expr):
    """對 expr 做「一次」normal order（最左最外）β-歸約。

    回傳 (redex, result)：
        redex  = 這次被歸約的子項 (\\x. body) arg
        result = 歸約後的完整運算式
    若已經沒有 redex（已是 normal form）則回傳 None。
    """
    if isinstance(expr, App):
        if isinstance(expr.func, Abs):
            # 找到 redex：(\\x. body) arg  ->  body[x := arg]
            redex = expr
            result = substitute(expr.func.body, expr.func.param, expr.arg)
            return redex, result

        found = reduce_step(expr.func)
        if found is not None:
            redex, new_func = found
            return redex, App(new_func, expr.arg)

        found = reduce_step(expr.arg)
        if found is not None:
            redex, new_arg = found
            return redex, App(expr.func, new_arg)

        return None

    if isinstance(expr, Abs):
        found = reduce_step(expr.body)
        if found is not None:
            redex, new_body = found
            return redex, Abs(expr.param, new_body)
        return None

    return None  # Var，沒有 redex


def reduce_with_trace(expr: Expr, max_steps: int = DEFAULT_MAX_STEPS):
    """不斷做 normal order β-歸約，並記錄每一步。

    回傳一個 dict：
        steps     : list[str]   每個步驟的運算式字串（steps[0] 是原始項）
        redexes   : list[str]   每個步驟所歸約的 redex 字串
        result    : Expr        最終結果（normal form 或截斷處）
        count     : int         實際歸約步數
        truncated : bool        是否因為超過 max_steps 而停止
    """
    steps = [to_str(expr)]
    redexes = []
    current = expr
    count = 0
    truncated = False

    while count < max_steps:
        found = reduce_step(current)
        if found is None:
            break
        redex, current = found
        redexes.append(to_str(redex))
        steps.append(to_str(current))
        count += 1
    else:
        # 迴圈跑滿 max_steps 仍未結束
        truncated = reduce_step(current) is not None

    return {
        "steps": steps,
        "redexes": redexes,
        "result": current,
        "count": count,
        "truncated": truncated,
    }


# ============================================================
# 8. Pretty printer
# ============================================================
def to_str(expr: Expr, prec: int = 0) -> str:
    """把 AST 轉成字串，並依優先順序自動省略多餘括號。

    prec: 0 = 可出現任何形式
          1 = 位於函數位置（App 的左邊）
          2 = 位於參數位置（App 的右邊），需要括號保護
    """
    if isinstance(expr, Var):
        return expr.name

    if isinstance(expr, Abs):
        text = "\\" + expr.param + ". " + to_str(expr.body, 0)
        return f"({text})" if prec >= 1 else text

    # App
    text = to_str(expr.func, 1) + " " + to_str(expr.arg, 2)
    return f"({text})" if prec >= 2 else text


# ============================================================
# 9. .lam 程式解析
# ============================================================
def parse_program(text: str):
    """解析 .lam 程式，回傳 (definitions, expressions)。

    definitions : dict[str, Expr]   name = expr 形式的縮寫定義
    expressions : list[Expr]        要計算的目標運算式（可多行）
    """
    defs: dict = {}
    exprs: list = []

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        try:
            if "=" in line:
                name, rhs = line.split("=", 1)
                name = name.strip()
                if not _IDENT_RE.match(name):
                    raise SyntaxError(f"不合法的定義名稱: {name!r}")
                defs[name] = parse(rhs)
            else:
                exprs.append(parse(line))
        except SyntaxError as exc:
            raise SyntaxError(f"第 {lineno} 行: {exc}") from None

    return defs, exprs


def expand_definitions(expr: Expr, defs: dict, bound=frozenset(), stack=()) -> Expr:
    """把運算式中的「已定義名稱」展開成對應的定義（巨集展開）。

    被 lambda 綁定的同名變數不會被展開；循環定義則保留為自由變數。
    """
    if isinstance(expr, Var):
        if expr.name not in bound and expr.name in defs and expr.name not in stack:
            return expand_definitions(defs[expr.name], defs, bound, stack + (expr.name,))
        return expr

    if isinstance(expr, Abs):
        return Abs(expr.param, expand_definitions(expr.body, defs, bound | {expr.param}, stack))

    return App(
        expand_definitions(expr.func, defs, bound, stack),
        expand_definitions(expr.arg, defs, bound, stack),
    )


# ============================================================
# 10. 對外高階函式
# ============================================================
def evaluate(expr: Expr, defs: dict | None = None, max_steps: int = DEFAULT_MAX_STEPS):
    """展開定義後，用 normal order 歸約到 normal form，回傳 trace。"""
    defs = defs or {}
    expanded = expand_definitions(expr, defs)
    trace = reduce_with_trace(expanded, max_steps=max_steps)
    trace["source"] = to_str(expr)
    trace["expanded"] = to_str(expanded)
    return trace


def evaluate_program(text: str, max_steps: int = DEFAULT_MAX_STEPS):
    """解析 .lam 程式並計算其中的每一個目標運算式。"""
    defs, exprs = parse_program(text)
    return [evaluate(expr, defs, max_steps) for expr in exprs]


def evaluate_file(path: str, max_steps: int = DEFAULT_MAX_STEPS):
    """讀取 .lam 檔並計算。"""
    with open(path, "r", encoding="utf-8") as handle:
        return evaluate_program(handle.read(), max_steps=max_steps)
