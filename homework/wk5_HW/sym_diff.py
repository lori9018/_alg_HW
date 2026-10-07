"""
遞迴符號微分 sym_diff(expr, var='x')

運算式表示法（巢狀 tuple，即抽象語法樹 AST）：
    數字      : 3, 2.5
    變數      : 'x', 'y'
    二元運算  : ('+', a, b)  ('-', a, b)  ('*', a, b)  ('/', a, b)  ('^', a, b)
    一元函數  : ('neg', a)  ('sin', a)  ('cos', a)  ('tan', a)  ('exp', a)  ('ln', a)
"""


def is_num(e):
    return isinstance(e, (int, float))


def contains(e, var):
    """expr 中是否含有變數 var（同樣用遞迴）"""
    if is_num(e):
        return False
    if isinstance(e, str):
        return e == var
    return any(contains(sub, var) for sub in e[1:])


def sym_diff(expr, var='x'):
    """回傳 expr 對 var 的導函數（已化簡）。"""
    return simplify(_diff(expr, var))


def _diff(e, v):
    # ---- base case ----
    if is_num(e):
        return 0
    if isinstance(e, str):
        return 1 if e == v else 0

    # ---- recursive case ----
    op, a, *rest = e

    if op == '+':
        return ('+', _diff(a, v), _diff(rest[0], v))
    if op == '-':
        return ('-', _diff(a, v), _diff(rest[0], v))
    if op == 'neg':
        return ('neg', _diff(a, v))

    if op == '*':                                   # 乘法法則
        b = rest[0]
        return ('+', ('*', _diff(a, v), b), ('*', a, _diff(b, v)))

    if op == '/':                                   # 除法法則
        b = rest[0]
        num = ('-', ('*', _diff(a, v), b), ('*', a, _diff(b, v)))
        return ('/', num, ('^', b, 2))

    if op == '^':
        b = rest[0]
        if not contains(b, v):                      # 冪次法則 + 連鎖律
            return ('*', ('*', b, ('^', a, ('-', b, 1))), _diff(a, v))
        # 一般情形 a^b = e^(b ln a)
        inner = ('+', ('*', _diff(b, v), ('ln', a)),
                      ('/', ('*', b, _diff(a, v)), a))
        return ('*', e, inner)

    # 連鎖律： (f(u))' = f'(u) * u'
    du = _diff(a, v)
    if op == 'sin':
        return ('*', ('cos', a), du)
    if op == 'cos':
        return ('*', ('neg', ('sin', a)), du)
    if op == 'tan':
        return ('*', ('/', 1, ('^', ('cos', a), 2)), du)
    if op == 'exp':
        return ('*', e, du)
    if op == 'ln':
        return ('/', du, a)

    raise ValueError(f"不支援的運算: {op}")


def simplify(e):
    """由下而上遞迴化簡：常數運算、0/1 恆等式。"""
    if is_num(e) or isinstance(e, str):
        return e

    op = e[0]
    args = [simplify(s) for s in e[1:]]

    if op == 'neg':
        a = args[0]
        if is_num(a):
            return -a
        if isinstance(a, tuple) and a[0] == 'neg':
            return a[1]
        return ('neg', a)

    if len(args) == 1:
        return (op, args[0])

    a, b = args
    both = is_num(a) and is_num(b)

    if op == '+':
        if both: return a + b
        if a == 0: return b
        if b == 0: return a
    elif op == '-':
        if both: return a - b
        if b == 0: return a
        if a == 0: return simplify(('neg', b))
        if a == b: return 0
    elif op == '*':
        if both: return a * b
        if a == 0 or b == 0: return 0
        if a == 1: return b
        if b == 1: return a
    elif op == '/':
        if both and b != 0:
            q = a / b
            return int(q) if q == int(q) else q
        if a == 0: return 0
        if b == 1: return a
    elif op == '^':
        if b == 0: return 1
        if b == 1: return a
        if both: return a ** b
    return (op, a, b)


def to_str(e):
    """把 AST 轉回人類可讀的字串。"""
    if is_num(e):
        return str(e)
    if isinstance(e, str):
        return e
    op = e[0]
    if op == 'neg':
        return f"-{to_str(e[1])}" if is_num(e[1]) or isinstance(e[1], str) \
            else f"-({to_str(e[1])})"
    if len(e) == 2:
        return f"{op}({to_str(e[1])})"
    a, b = to_str(e[1]), to_str(e[2])
    return f"({a} {op} {b})"


if __name__ == "__main__":
    tests = [
        ('^', 'x', 3),                                   # x^3
        ('*', 'x', ('sin', 'x')),                        # x sin x
        ('sin', ('^', 'x', 2)),                          # sin(x^2)
        ('/', 'x', ('+', 'x', 1)),                       # x/(x+1)
        ('ln', ('+', ('^', 'x', 2), 1)),                 # ln(x^2+1)
        ('exp', ('*', 3, 'x')),                          # e^(3x)
        ('^', 'x', 'x'),                                 # x^x
        ('+', ('*', 3, ('^', 'x', 2)), ('*', 5, 'x')),   # 3x^2 + 5x
    ]
    for t in tests:
        print(f"d/dx {to_str(t):<28} = {to_str(sym_diff(t))}")