#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAT 求解器（布林可滿足性問題 Boolean Satisfiability Problem）
=============================================================

特性
----
1. 不使用 itertools：自行以 backtracking（深度優先搜尋）列舉所有變數指派。
2. 使用 Python 內建的運算式語法（eval）直接求值，完全不修改使用者輸入的運算式。
3. 搜尋到第一個解即可提前剪枝停止（SAT），也可選擇列出所有解。

演算法
------
    對 n 個變數，遞迴地依序把每個變數指派為 True / False，
    形成一棵深度為 n 的二元決策樹；當所有變數都被指派後，
    用 eval 對原運算式求值一次。DFS 在找到第一個解後立刻回溯剪枝。

使用方法
--------
    python sat_solver.py                            # 內建範例: (p or q) and not (p and q)
    python sat_solver.py "(a or b) and not c"       # 命令列指定運算式（須加引號）
    python sat_solver.py --all "(a or b)"           # 列出所有滿足解
"""

import re
import sys
import keyword

# 讓中文輸出在 Windows 終端機也能正常顯示
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Python 保留字與內建字面值不能當成變數名稱
_RESERVED = set(keyword.kwlist) | {"True", "False", "None"}

# 內建範例：p、q 恰好一個為真（互斥或 XOR）
DEFAULT_EXPR = "(p or q) and not (p and q)"


# ----------------------------------------------------------------------
# 1) 抽出運算式中的所有變數
# ----------------------------------------------------------------------
def extract_variables(expr):
    """從運算式中抽出所有可當作變數的識別字（不含保留字）。"""
    names = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr)
    return sorted(set(name for name in names if name not in _RESERVED))


# ----------------------------------------------------------------------
# 2) 以 Python 內建語法求值（eval），不修改運算式
# ----------------------------------------------------------------------
def evaluate(expr, assignment):
    """把變數指派代入後用 eval 求值。

    globals 的 __builtins__ 設為空字典，避免運算式呼叫任何內建函式。
    """
    return bool(eval(expr, {"__builtins__": {}}, assignment))


# ----------------------------------------------------------------------
# 3) 自行實作的列舉（backtracking DFS），不使用 itertools
# ----------------------------------------------------------------------
def enumerate_assignments(variables, index, assignment, on_assignment):
    """遞迴列舉所有 2^n 種變數指派。

    每指派完一組完整解就會呼叫 on_assignment(dict)；
    若 on_assignment 回傳 True，代表已經找到解，立刻剪枝停止整棵搜尋樹。

    回傳值：True = 已停止搜尋；False = 走完所有分支。
    """
    if index == len(variables):
        # 所有變數都已指派，交給回呼處理（例如求值、記錄解）
        return on_assignment(dict(assignment))

    var = variables[index]
    for value in (True, False):          # 每個變數只有兩個可能值
        assignment[var] = value
        if enumerate_assignments(variables, index + 1, assignment, on_assignment):
            return True                  # 子樹已找到解，回溯剪枝

    del assignment[var]                  # 回溯：移除這個變數
    return False


# ----------------------------------------------------------------------
# 4) SAT 判斷與列出所有解
# ----------------------------------------------------------------------
def find_first_solution(expr, variables):
    """回傳第一個滿足解；若為不可滿足（UNSAT）則回傳 None。"""
    box = [None]

    def check(assignment):
        if evaluate(expr, assignment):
            box[0] = assignment
            return True                  # 找到解 => 回傳 True 停止搜尋

    enumerate_assignments(variables, 0, {}, check)
    return box[0]


def find_all_solutions(expr, variables):
    """列出所有滿足解（回呼恆回傳 False，因此不會提早停止）。"""
    solutions = []

    def check(assignment):
        if evaluate(expr, assignment):
            solutions.append(assignment)
        return False                     # 繼續列舉其餘指派

    enumerate_assignments(variables, 0, {}, check)
    return solutions


# ----------------------------------------------------------------------
# 5) 主程式
# ----------------------------------------------------------------------
def main():
    args = list(sys.argv[1:])
    list_all = "--all" in args
    if list_all:
        args.remove("--all")

    if args:
        expr = " ".join(args)            # 允許 "a and b" 不用引號也能合併
    else:
        expr = DEFAULT_EXPR

    # 基本防護：拒絕明顯不安全的輸入
    if any(t in expr for t in ("=", "__", "import", "lambda", "exec", "eval")):
        print("錯誤：運算式含有不允許的關鍵字，已拒絕。")
        return

    variables = extract_variables(expr)
    if not variables:
        print("錯誤：運算式中找不到任何變數。")
        return

    print("=" * 60)
    print(f"運算式 : {expr}")
    print(f"變數   : {', '.join(variables)}  (共 {len(variables)} 個)")
    print("=" * 60)

    if list_all:
        solutions = find_all_solutions(expr, variables)
        if not solutions:
            print("結果：UNSAT（不可滿足，沒有任何指派能讓運算式為真）")
            return
        print(f"結果：SAT，共有 {len(solutions)} 組滿足解：")
        for i, sol in enumerate(solutions, 1):
            print(f"  解 {i:>2d}: " + format_assignment(sol))
    else:
        solution = find_first_solution(expr, variables)
        if solution is None:
            print("結果：UNSAT（不可滿足，沒有任何指派能讓運算式為真）")
        else:
            print("結果：SAT（可滿足），找到的解：")
            print("  " + format_assignment(solution))
            print(f"驗證 : eval 結果 = {evaluate(expr, solution)}")


def format_assignment(assignment):
    """把指派字典排版成好讀的字串，例如 p=True, q=False。"""
    return ", ".join(f"{k}={v}" for k, v in assignment.items())


if __name__ == "__main__":
    main()