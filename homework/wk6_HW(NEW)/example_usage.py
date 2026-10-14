"""用 lambda_calc.py 計算 FACTORIAL 與 FIBONACCI，並和 Python 內建結果對照。
執行：python example_usage.py
"""
import argparse, math
from lambda_calc import PRELUDE, run_line, run_program, parse, evaluate, is_num, TOKEN

opt = argparse.Namespace(applicative=False, max=200000, fold=True)

# 1) 載入 Prelude，再定義 FACT / FIB（都是純 λ 項，遞迴靠 Y combinator）
defs = {}
run_program(PRELUDE, defs, opt)
run_line(r"FACT = Y (\f n. IF (ISZERO n) 1 (MULT n (f (PRED n))))", defs, opt)
run_line(r"FIB  = Y (\f n. IF (LEQ n 1) n (PLUS (f (PRED n)) (f (SUB n 2))))", defs, opt)

# 2) 完整顯示一個小例子的化簡過程
print("===== FACT 2 的完整計算過程 =====")
run_line("FACT 2", defs, opt)

# 3) 批次計算：只看結果與步數，並與 Python 對照
def lam(expr):
    steps, nf, ok = evaluate(parse(TOKEN.findall(expr), defs), False, opt.max)
    assert ok, "超過步數上限"
    return is_num(nf), len(steps)

print("\n===== FACTORIAL =====")
for n in range(5):
    v, s = lam(f"FACT {n}")
    print(f"FACT {n} = {v:<4} ({s} 步)  Python: {math.factorial(n)}")

def fib(n): return n if n < 2 else fib(n - 1) + fib(n - 2)
print("\n===== FIBONACCI =====")
for n in range(6):
    v, s = lam(f"FIB {n}")
    print(f"FIB {n} = {v:<4} ({s} 步)  Python: {fib(n)}")
