#!/usr/bin/env python3
"""Lambda Calculus 解譯器：逐步顯示 β-reduction 過程。

用法：
  python lambda_calc.py                      # 進入 REPL（已載入 Prelude）
  python lambda_calc.py --example fact       # 執行內建範例：basic / fact / fib
  python lambda_calc.py prog.lc              # 執行檔案
  python lambda_calc.py -e "PLUS 2 3"        # 直接求值一個運算式
選項：--applicative（應用序）  --max N（步數上限）  --no-fold（完整展開，不用名稱/數字縮寫）

語法：\\x y. body 或 λx. body；應用左結合；數字 3 = Church numeral；
      NAME = 運算式 為定義；-- 或 # 開頭為註解。被化簡的 redex 以 ⟦ ⟧ 標示。
"""
import argparse, re, sys

sys.setrecursionlimit(20000)

# ---------------------------------------------------------------- 語法樹
class Var:
    __slots__ = ("n",)
    def __init__(self, n): self.n = n
class Lam:
    __slots__ = ("p", "b")
    def __init__(self, p, b): self.p, self.b = p, b
class App:
    __slots__ = ("f", "a")
    def __init__(self, f, a): self.f, self.a = f, a

def church(n):
    b = Var("x")
    for _ in range(n):
        b = App(Var("f"), b)
    return Lam("f", Lam("x", b))

# ---------------------------------------------------------------- 解析
TOKEN = re.compile(r"λ|\\|[A-Za-z_][\w']*|\d+|[().=]|\S")

def parse(tk, defs):
    pos = 0
    bound = []
    is_id = lambda x: x is not None and re.match(r"[A-Za-z_]", x)
    is_lam = lambda x: x in ("λ", "\\")
    starts = lambda x: x is not None and (is_id(x) or x[0].isdigit() or x == "(" or is_lam(x))
    peek = lambda: tk[pos] if pos < len(tk) else None

    def atom():
        nonlocal pos
        x = tk[pos]; pos += 1
        if x == "(":
            e = expr()
            if peek() != ")": raise SyntaxError('缺少 ")"')
            pos += 1
            return e
        if x[0].isdigit(): return church(int(x))
        if x in bound: return Var(x)
        return defs.get(x) or Var(x)       # 已定義的名稱直接展開（共享同一棵子樹）

    def expr():
        nonlocal pos
        if is_lam(peek()):
            pos += 1
            ps = []
            while is_id(peek()):
                ps.append(tk[pos]); pos += 1
            if not ps or peek() != ".": raise SyntaxError('λ 後需要參數並以 "." 結尾')
            pos += 1
            bound.extend(ps)
            body = expr()
            del bound[len(bound) - len(ps):]
            for p in reversed(ps): body = Lam(p, body)
            return body
        r = None
        while starts(peek()):
            lam = is_lam(peek())
            a = expr() if lam else atom()
            r = a if r is None else App(r, a)
            if lam: break
        if r is None: raise SyntaxError("缺少運算式")
        return r

    e = expr()
    if pos < len(tk): raise SyntaxError(f'無法解析："{tk[pos]}"')
    return e

# ---------------------------------------------------------------- 化簡
def fv(t):
    if isinstance(t, Var): return {t.n}
    if isinstance(t, App): return fv(t.f) | fv(t.a)
    return fv(t.b) - {t.p}

def occurs(x, t):
    if isinstance(t, Var): return t.n == x
    if isinstance(t, App): return occurs(x, t.f) or occurs(x, t.a)
    return t.p != x and occurs(x, t.b)

def subst(t, x, s, fs):
    """t[x := s]，capture-avoiding；fs = FV(s)。"""
    if isinstance(t, Var): return s if t.n == x else t
    if isinstance(t, App):
        f, a = subst(t.f, x, s, fs), subst(t.a, x, s, fs)
        return t if f is t.f and a is t.a else App(f, a)
    if t.p == x or not occurs(x, t.b): return t
    if t.p in fs:                           # 需要 α-renaming 以避免變數被捕獲
        avoid = fs | fv(t.b) | {x}
        q = t.p
        while q in avoid: q += "'"
        return Lam(q, subst(subst(t.b, t.p, Var(q), {q}), x, s, fs))
    return Lam(t.p, subst(t.b, x, s, fs))

def step(t, ao):
    """化簡一步，回傳 (新項, redex)；已是 normal form 則回傳 None。"""
    if isinstance(t, App):
        red = lambda: (subst(t.f.b, t.f.p, t.a, fv(t.a)), t)
        if not ao and isinstance(t.f, Lam): return red()   # normal order：最左最外
        r = step(t.f, ao)
        if r: return App(r[0], t.a), r[1]
        r = step(t.a, ao)
        if r: return App(t.f, r[0]), r[1]
        if ao and isinstance(t.f, Lam): return red()        # applicative order：先化簡引數
        return None
    if isinstance(t, Lam):
        r = step(t.b, ao)
        return (Lam(t.p, r[0]), r[1]) if r else None
    return None

def evaluate(t, ao, limit):
    steps = []
    while True:
        r = step(t, ao)
        if r is None: return steps, t, True
        if len(steps) >= limit: return steps, t, False
        steps.append((t, r[1]))
        t = r[0]

# ---------------------------------------------------------------- 顯示
def aeq(a, b, la, lb):
    if type(a) is not type(b): return False
    if isinstance(a, Var):
        i = len(la) - 1 - la[::-1].index(a.n) if a.n in la else -1
        j = len(lb) - 1 - lb[::-1].index(b.n) if b.n in lb else -1
        return i == j and (i >= 0 or a.n == b.n)
    if isinstance(a, Lam):
        la.append(a.p); lb.append(b.p)
        r = aeq(a.b, b.b, la, lb)
        la.pop(); lb.pop()
        return r
    return aeq(a.f, b.f, la, lb) and aeq(a.a, b.a, la, lb)

def is_num(t):
    if not (isinstance(t, Lam) and isinstance(t.b, Lam)) or t.p == t.b.p: return -1
    f, x, c, n = t.p, t.b.p, t.b.b, 0
    while isinstance(c, App) and isinstance(c.f, Var) and c.f.n == f:
        n += 1; c = c.a
    return n if isinstance(c, Var) and c.n == x else -1

def has(u, h):
    if h is None: return False
    if u is h: return True
    if isinstance(u, App): return has(u.f, h) or has(u.a, h)
    if isinstance(u, Lam): return has(u.b, h)
    return False

def show(t, hl=None, fold=True, defs=()):
    used = [False]
    def sp(u):
        if not fold: return None
        n = is_num(u)
        if n >= 0: return str(n)
        for name, d in defs:
            if aeq(u, d, [], []) and (u is hl or not has(u, hl)): return name
        return None
    def P(u, m):                            # m: 0 頂層/λ 本體, 1 函數位置, 2 引數位置
        s, par = sp(u), False
        mark = u is hl and not used[0]
        if mark: used[0] = True
        if s is None:
            if isinstance(u, Var): s = u.n
            elif isinstance(u, Lam):
                ps, b = [], u
                while isinstance(b, Lam) and (b is u or sp(b) is None):
                    ps.append(b.p); b = b.b
                s, par = "λ" + " ".join(ps) + ". " + P(b, 0), m > 0
            else:
                s, par = P(u.f, 1) + " " + P(u.a, 2), m == 2
        if mark: s = "⟦" + s + "⟧"
        return "(" + s + ")" if par else s
    return P(t, 0)

# ---------------------------------------------------------------- 程式執行
PRELUDE = r"""-- ===== Prelude：Church 編碼 =====
TRUE  = \t f. t
FALSE = \t f. f
AND = \p q. p q p
OR  = \p q. p p q
NOT = \p. p FALSE TRUE
IF  = \p a b. p a b
PAIR = \x y f. f x y
FST = \p. p TRUE
SND = \p. p FALSE
SUCC = \n f x. f (n f x)
PLUS = \m n f x. m f (n f x)
MULT = \m n f. m (n f)
POW  = \b e. e b
PRED = \n f x. n (\g h. h (g f)) (\u. x) (\u. u)
SUB  = \m n. n PRED m
ISZERO = \n. n (\x. FALSE) TRUE
LEQ = \m n. ISZERO (SUB m n)
Y = \f. (\x. f (x x)) (\x. f (x x))
"""
EXAMPLES = {
    "basic": r"""(\x. x) y
(\x y. x) a b
SUCC 2
PLUS 2 3
MULT 2 3
POW 2 3
PRED 3
AND TRUE FALSE
IF (ISZERO 0) a b
""",
    "fact": r"""-- FACT n = if n = 0 then 1 else n * FACT (n-1)
FACT = Y (\f n. IF (ISZERO n) 1 (MULT n (f (PRED n))))
FACT 3
""",
    "fib": r"""-- FIB n = if n <= 1 then n else FIB (n-1) + FIB (n-2)
FIB = Y (\f n. IF (LEQ n 1) n (PLUS (f (PRED n)) (f (SUB n 2))))
FIB 0
FIB 1
FIB 3
""",
}

def run_line(line, defs, opt, lineno=0):
    line = re.sub(r"(--|#).*$", "", line).strip()
    if not line: return
    tk = TOKEN.findall(line)
    try:
        if len(tk) > 2 and re.match(r"[A-Za-z_]", tk[0]) and tk[1] == "=":
            defs[tk[0]] = parse(tk[2:], defs)
            return
        term = parse(tk, defs)
    except SyntaxError as e:
        print(f"第 {lineno} 行錯誤：{e}")
        return
    dl = [(k, v) for k, v in defs.items() if not isinstance(v, Var)]
    steps, nf, ok = evaluate(term, opt.applicative, opt.max)
    print(f"\n▶ {line}")
    for k, (t, r) in enumerate(steps):
        print(f"  {'start' if k == 0 else f'→β {k}':<7}: {show(t, r, opt.fold, dl)}")
    print(f"  {'NF' if ok else '...':<7}: {show(nf, None, opt.fold, dl)}")
    n = is_num(nf)
    if ok: print(f"  ✔ normal form，共 {len(steps)} 步" + (f"　= Church numeral {n}" if n >= 0 else ""))
    else:  print(f"  ⚠ 已達步數上限 {opt.max}，可能不會終止")

def run_program(text, defs, opt):
    for i, line in enumerate(text.splitlines(), 1):
        run_line(line, defs, opt, i)

def repl(defs, opt):
    print("Lambda Calculus REPL（已載入 Prelude）。輸入運算式或 NAME = ...；:q 離開")
    while True:
        try: line = input("λ> ")
        except EOFError: break
        if line.strip() in (":q", ":quit"): break
        run_line(line, defs, opt)

def main():
    ap = argparse.ArgumentParser(description="Lambda Calculus 解譯器")
    ap.add_argument("file", nargs="?")
    ap.add_argument("-e", "--expr")
    ap.add_argument("--example", choices=EXAMPLES)
    ap.add_argument("--applicative", action="store_true")
    ap.add_argument("--max", type=int, default=3000)
    ap.add_argument("--no-fold", dest="fold", action="store_false")
    opt = ap.parse_args()
    defs = {}
    for i, line in enumerate(PRELUDE.splitlines(), 1): run_line(line, defs, opt, i)
    if opt.example: run_program(EXAMPLES[opt.example], defs, opt)
    elif opt.expr:  run_program(opt.expr, defs, opt)
    elif opt.file:  run_program(open(opt.file, encoding="utf-8").read(), defs, opt)
    else:           repl(defs, opt)

if __name__ == "__main__":
    main()