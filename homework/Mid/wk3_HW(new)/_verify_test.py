# -*- coding: utf-8 -*-
"""隨機測試：把 sat_solver 的結果與暴力窮舉 (itertools) 的完整真值表比對。
此檔案僅供驗證用，不是作業繳交的程式。"""
import itertools
import random
import sat_solver as s

random.seed(42)
exprs = [
    "(a and b) or c",
    "(a or b) and not c",
    "(a or not b) and (b or not c)",
    "not (a and b and c) or d",
    "(a or b) and (not a or c) and (not b or not c)",
    "a and b and c and not d and (e or f)",
]
for _ in range(200):
    n = random.randint(1, 3)
    vs = [chr(ord("a") + i) for i in range(n)]
    ops = ["and", "or"]
    e = vs[0]
    for v in vs[1:]:
        e = f"({e} {random.choice(ops)} {v})"
    if random.random() < 0.5:
        e = f"not {e}"
    exprs.append(e)

bad = 0
for expr in exprs:
    vars_ = s.extract_variables(expr)
    # 暴力窮舉全部 2^n 組指派
    brute = []
    for bits in itertools.product([True, False], repeat=len(vars_)):
        a = dict(zip(vars_, bits))
        if eval(expr, {"__builtins__": {}}, a):
            brute.append(a)
    brute_first = brute[0] if brute else None
    brute_all_set = set(tuple(sorted(a.items())) for a in brute)

    got_first = s.find_first_solution(expr, vars_)
    got_all = s.find_all_solutions(expr, vars_)
    got_all_set = set(tuple(sorted(a.items())) for a in got_all)

    same = (got_first is None) == (brute_first is None)
    if got_first is not None and brute_first is not None:
        same_set_first = set(got_first.items()) == set(brute_first.items())
        same = same and same_set_first  # 我們只要它是一個合法解即可
    if same and got_all_set == brute_all_set and len(got_all) == len(brute):
        continue
    bad += 1
    print(f"MISMATCH expr={expr}")
    print(f"  brute first={brute_first} all={len(brute)}")
    print(f"  got   first={got_first} all={len(got_all)}")

if bad:
    print(f"總共 {bad} 個運算式不吻合！")
else:
    print(f"OK：{len(exprs)} 個隨機運算式全部通過（與 itertools 暴力窮舉一致）。")