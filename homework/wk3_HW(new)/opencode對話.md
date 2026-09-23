# Python SAT求解器 列舉 不用itertools

**Session ID:** ses_f33bf4657ffedTTLq6WuHzB5ez
**Created:** 2026/9/23 上午11:13:09
**Updated:** 2026/9/23 上午11:13:11

---

## User

請寫一個 python 程式可以求解 SAT 問題（布林滿足），不要用 itertools , 自己寫程式列舉，然後用內建的 python運算式語法，不要修改，並寫在wk3_HW(new)下

---

## Assistant

_Thinking:_

The user wants a Python program to solve SAT problems (Boolean satisfiability). Requirements:
1. Don't use itertools - write own enumeration (backtracking/DFS)
2. Use Python's built-in expression syntax (eval) to evaluate the Boolean formula
3. Write it in `wk3_HW(new)` directory

Let me look at the current working directory to understand the context.

Working directory: C:\algorithm_HW\_alg_HW\homework\wk3_HW(new)

Let me check what's there first.

**Tool: shell**

**Input:**
```json
{
  "command": "Get-ChildItem -Force | Select-Object Name, Length"
}
```

(no output)
Command exited with code 0.

---

## Assistant

_Thinking:_

The directory is empty. Let me create a Python SAT solver program.

Requirements:
1. Solve SAT (Boolean satisfiability)
2. Don't use itertools - write own enumeration (backtracking / DFS with pruning)
3. Use Python's built-in expression syntax (eval) to evaluate the Boolean formula - don't modify the formula
4. Write in wk3_HW(new) directory

Let me design:

- Input: a Boolean expression string (using Python syntax: `and`, `or`, `not`, parentheses, variables)
- Extract variables from the expression
- Enumerate all assignments using a custom backtracking search (no itertools.product)
- For each assignment, substitute variable values and eval the expression
- If satisfiable, return the assignment / model; also print all satisfying assignments if desired

Let me write a clean program:

```python
"""
SAT 求解器
- 不用 itertools，自行以 backtracking 列舉所有變數指派
- 使用 Python 內建 `eval` 直接求值布林運算式（不修改運算式）
"""

import re
import sys


def extract_variables(expr):
    """從運算式中抽出所有變數名稱（英文字母開頭、可含數字與底線）"""
    return sorted(set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr)))


def evaluate(expr, assignment):
    """用 Python 內建的運算式語法求值（不修改原運算式）"""
    return bool(eval(expr, {"__builtins__": {}}, assignment))


def search(expr, variables, assignment, index, results, limit):
    """自行實作的列舉（backtracking DFS），不使用 itertools"""
    if len(results) >= limit:
        return
    if index == len(variables):
        if evaluate(expr, assignment):
            results.append(dict(assignment))
        return

    var = variables[index]

    assignment[var] = True
    search(expr, variables, assignment, index + 1, results, limit)

    assignment[var] = False
    search(expr, variables, assignment, index + 1, results, limit)

    del assignment[var]


def solve(expr, limit=10):
    variables = extract_variables(expr)
    results = []
    assignment = {}
    search(expr, variables, assignment, 0, results, limit)
    return variables, results


def main():
    if len(sys.argv) > 1:
        expr = sys.argv[1]
    else:
        expr = "(p or q) and not (p and q)"  # 範例：XOR

    # 合法性檢查（只有簡單的變數與布林運算符）
    if "=" in expr or "__" in expr:
        print("拒絕含有 '=' 或 '__' 的輸入。")
        return

    variables, results = solve(expr, limit=...)
    ...
```

Wait, need to be careful with eval and security. Use `{"__builtins__": {}}` as globals and assignment dict as locals. Variables in expression must match assignment keys. Python identifiers work.

Note: extract_variables via regex will capture things like `and`, `or`, `not`, `True`, `False`? Well those are keywords - `and`, `or`, `not` are Python keywords so assigning them as variable names in the dict... Actually dict keys can be "and" but eval would parse them as keywords, not names. So we should exclude Python keywords and builtins like True/False. Let me filter with keyword.iskeyword from the keyword module, and also exclude the literals True/False.

Let me refine extract_variables to exclude Python keywords and True/False.

Also should handle that the expression could contain `True`/`False` literals. Excluding them is fine.

Let me also print satisfying assignments nicely, and count. Provide option to show all solutions.

Here's my plan for a complete program:

1. `extract_variables(expr)` - regex + filter keywords/literals
2. `evaluate(expr, assignment)` - eval with restricted globals
3. Custom DFS enumeration with pruning option (e.g., early terminate? Not trivial with eval of whole expr; partial evaluation could allow pruning, but that requires parsing. Keep it simple: full assignment enumeration but implemented ourselves with backtracking. Maybe add ability to stop at first solution.)

Actually to keep it "SAT" (satisfiability), we can stop at first model found by default, but also allow listing all. Let me implement both: default finds first solution (UNSAT/SAT), with `--all` or input mode to list all satisfying assignments.

Let me also add a simple partial-assignment pruning using Python eval? We could substitute only assigned variables and leave unassigned ones as... no, eval would fail. We could replace unassigned vars with a placeholder? That modifies expression. Keep it clean: full enumeration with backtracking.

To make the enumeration more interesting (not just 2^n product), I can implement DFS with memo... no, simple backtracking is fine and matches the request "自己寫程式列舉" (write your own enumeration code).

Let me write the file. Directory: C:\algorithm_HW\_alg_HW\homework\wk3_HW(new). File name: SAT_solver.py or sat_solver.py. The user wrote in Chinese; program comments can be in Chinese + English. Let me write with both Chinese and English comments.

Let me write a nice, well-structured program.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAT 求解器（布林可滿足性問題）
==============================

特性
----
1. 不使用 itertools：自行以 backtracking（深度優先搜尋）列舉所有變數指派。
2. 使用 Python 內建的運算式語法（eval）直接求值，不修改使用者的運算式。

使用方法
--------
    python sat_solver.py                        # 使用內建範例 (p∨q)∧¬(p∧q)
    python sat_solver.py "(a or b) and not c"   # 從命令列指定運算式
    python sat_solver.py --all "(a or b)"       # 列出所有滿足解
"""
```

Now the code:

```python
import re
import sys
import keyword

# Python 保留字與內建布林字面值，不能當成變數
_RESERVED = set(keyword.kwlist) | {"True", "False", "None"}


def extract_variables(expr):
    """從運算式中抽出所有可當作變數的識別字。"""
    names = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr))
    return sorted(name for name in names if name not in _RESERVED)


def evaluate(expr, assignment):
    """以 Python 內建語法求值：eval(expr, globals, locals)。

    只允許變數查詢，不開放任何內建函式（__builtins__ 設為空）。
    """
    return bool(eval(expr, {"__builtins__": {}}, assignment))


def enumerate_assignments(expr, variables, index, assignment, on_assignment):
    """自行實作的列舉（backtracking DFS）。

    依序把每個變數設成 True / False，直到所有變數都被指派，
    再交給 on_assignment 處理完整指派。
    """
    if index == len(variables):
        on_assignment(assignment)
        return

    var = variables[index]

    # 分支一：指派為 True
    assignment[var] = True
    enumerate_assignments(expr, variables, index + 1, assignment, on_assignment)

    # 分支二：指派為 False
    assignment[var] = False
    enumerate_assignments(expr, variables, index + 1, assignment, on_assignment)

    # 回溯：移除這個變數，恢復原狀
    del assignment[var]


def find_first_solution(expr, variables):
    """回傳第一個滿足解（SAT 判斷），找不到回傳 None。"""
    result = [None]
    stop = [False]

    def check(assignment):
        if not stop[0] and evaluate(expr, assignment):
            result[0] = dict(assignment)
            stop[0] = True  # 提早停止

    enumerate_assignments(expr, variables, 0, {}, check)

    if stop[0]:
        return result[0], stop[0]  # found
    return None, False


def find_all_solutions(expr, variables):
    """列出所有滿足解。"""
    solutions = []
    enumerate_assignments(expr, variables, 0, {}, lambda a: solutions.append(dict(a)) if evaluate(expr, a) else None)
    return solutions
```

Hmm, the early stopping: since enumerate_assignments is recursive, setting a stop flag doesn't actually unwind recursion - it will still continue exploring. But the check function returns early, so it doesn't evaluate further. To properly stop, I'd propagate the flag. Let me make enumerate_assignments return whether to cut. Cleaner:

```python
def enumerate_assignments(expr, variables, index, assignment, on_assignment):
    if index == len(variables):
        if evaluate(expr, assignment):
            on_assignment(dict(assignment))
            return True  # 找到解，回傳 True 通知上層剪枝
        return False

    var = variables[index]
    for value in (True, False):
        assignment[var] = value
        if enumerate_assignments(expr, variables, index + 1, assignment, on_assignment):
            return True
    del assignment[var]
    return False
```

Wait, with early termination we want DFS to stop fully when first solution found. The return True propagation does that. But for find_all, we don't want early termination. So pass a flag "stop_at_first". Let me restructure:

```python
def enumerate_assignments(variables, index, assignment, on_assignment, stop_at_first):
    """自行實作的列舉（backtracking DFS）。

    stop_at_first=True 時，找到第一個解就整棵搜尋樹剪枝停止。
    回傳 True 代表已找到解並停止。
    """
    if index == len(variables):
        if on_assignment(dict(assignment)):
            return True
        return False

    var = variables[index]
    for value in (True, False):
        assignment[var] = value
        if enumerate_assignments(variables, index + 1, assignment, on_assignment, stop_at_first):
            return True
    del assignment[var]
    return False
```

Hmm but stop_at_first logic: on_assignment returns bool meaning "stop now". For find_all, on_assignment returns False always. Actually simpler: on_assignment returns True to stop. Then:

```python
def enumerate_assignments(variables, index, assignment, on_assignment):
    if index == len(variables):
        return on_assignment(dict(assignment))  # 回傳 True => 停止整棵搜尋

    var = variables[index]
    for value in (True, False):
        assignment[var] = value
        if enumerate_assignments(variables, index + 1, assignment, on_assignment):
            return True
    del assignment[var]
    return False
```

This is clean. `on_assignment` checks evaluate(expr, a) and stores result, returns True if should stop.

main():

```python
def main():
    args = sys.argv[1:]
    all_solutions = False
    if "--all" in args:
        all_solutions = True
        args.remove("--all")

    if args:
        expr = " ".join(args)  # 允許 "a and b" 不用引號
    else:
        expr = "(p or q) and not (p and q)"

    # 基本防護：拒絕明顯危險的內容
    if any(t in expr for t in ("=", "__", "import", "lambda", "open", "exec", "eval")):
        print("拒絕含有不安全關鍵字的輸入。")
        return

    variables = extract_variables(expr)
    if not variables:
        print("未找到任何變數。")
        return

    print(f"運算式 : {expr}")
    print(f"變數   : {', '.join(variables)}")

    if all_solutions:
        solutions = []
        enumerate_assignments(variables, 0, {}, lambda a: solutions.append(a) or False)
        ...
```

Wait `solutions.append(a) or False` returns False, good.

Actually for all solutions: on_assignment = lambda a: (solutions.append(a) if evaluate(...) else None) or False... let me just write a named function for clarity.

Let me write the full file now. Also add a verification with the SAT result printed as formula = True/False per variable. And maybe show an interpretation like "p=True, q=False".

Also I want the enumerate to use the expr for evaluation inside on_assignment, so pass expr to closures.

Let me also handle keyboard input with prompt if no args? Keep it simple: default example or command line. Maybe also allow `-i` unknown. I'll keep default example + CLI arg.

Let me also write a quick test run.

Edge: eval with locals dict where keys are variable names; Python identifiers fine. `p` min length 1. Works.

Also note: extract_variables uses regex which may include things inside strings like "abc" — user's responsibility to write a pure Boolean expression. Fine for homework.

Now write the file. Directory: C:\algorithm_HW\_alg_HW\homework\wk3_HW(new). Note parentheses in path - quotes needed in PowerShell. I'll use the write tool which handles paths directly.

File name: sat_solver.py

Let me write it.

I'll add a docstring with algorithm description (suitable for homework): enumerate 2^n assignments via backtracking without itertools, evaluate each with eval.

Let me produce the full code carefully, then test it.

Directory is empty. Let me create the SAT solver program as requested — no `itertools`, a self-written backtracking enumeration, and Python's built-in `eval` for evaluation.

**Tool: write**

**Input:**
```json
{
  "path": "C:\\algorithm_HW\\_alg_HW\\homework\\wk3_HW(new)\\sat_solver.py",
  "content": "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\"\"\"\nSAT 求解器（布林可滿足性問題 Boolean Satisfiability Problem）\n=============================================================\n\n特性\n----\n1. 不使用 itertools：自行以 backtracking（深度優先搜尋）列舉所有變數指派。\n2. 使用 Python 內建的運算式語法（eval）直接求值，完全不修改使用者輸入的運算式。\n3. 搜尋到第一個解即可提前剪枝停止（SAT），也可選擇列出所有解。\n\n演算法\n------\n    對 n 個變數，遞迴地依序把每個變數指派為 True / False，\n    形成一棵深度為 n 的二元決策樹；當所有變數都被指派後，\n    用 eval 對原運算式求值一次。DFS 在找到第一個解後立刻回溯剪枝。\n\n使用方法\n--------\n    python sat_solver.py                            # 內建範例: (p or q) and not (p and q)\n    python sat_solver.py \"(a or b) and not c\"       # 命令列指定運算式（須加引號）\n    python sat_solver.py --all \"(a or b)\"           # 列出所有滿足解\n\"\"\"\n\nimport re\nimport sys\nimport keyword\n\n# Python 保留字與內建字面值不能當成變數名稱\n_RESERVED = set(keyword.kwlist) | {\"True\", \"False\", \"None\"}\n\n# 內建範例：p、q 恰好一個為真（互斥或 XOR）\nDEFAULT_EXPR = \"(p or q) and not (p and q)\"\n\n\n# ----------------------------------------------------------------------\n# 1) 抽出運算式中的所有變數\n# ----------------------------------------------------------------------\ndef extract_variables(expr):\n    \"\"\"從運算式中抽出所有可當作變數的識別字（不含保留字）。\"\"\"\n    names = re.findall(r\"[A-Za-z_][A-Za-z0-9_]*\", expr)\n    return sorted(set(name for name in names if name not in _RESERVED))\n\n\n# ----------------------------------------------------------------------\n# 2) 以 Python 內建語法求值（eval），不修改運算式\n# ----------------------------------------------------------------------\ndef evaluate(expr, assignment):\n    \"\"\"把變數指派代入後用 eval 求值。\n\n    globals 的 __builtins__ 設為空字典，避免運算式呼叫任何內建函式。\n    \"\"\"\n    return bool(eval(expr, {\"__builtins__\": {}}, assignment))\n\n\n# ----------------------------------------------------------------------\n# 3) 自行實作的列舉（backtracking DFS），不使用 itertools\n# ----------------------------------------------------------------------\ndef enumerate_assignments(variables, index, assignment, on_assignment):\n    \"\"\"遞迴列舉所有 2^n 種變數指派。\n\n    每指派完一組完整解就會呼叫 on_assignment(dict)；\n    若 on_assignment 回傳 True，代表已經找到解，立刻剪枝停止整棵搜尋樹。\n\n    回傳值：True = 已停止搜尋；False = 走完所有分支。\n    \"\"\"\n    if index == len(variables):\n        # 所有變數都已指派，交給回呼處理（例如求值、記錄解）\n        return on_assignment(dict(assignment))\n\n    var = variables[index]\n    for value in (True, False):          # 每個變數只有兩個可能值\n        assignment[var] = value\n        if enumerate_assignments(variables, index + 1, assignment, on_assignment):\n            return True                  # 子樹已找到解，回溯剪枝\n\n    del assignment[var]                  # 回溯：移除這個變數\n    return False\n\n\n# ----------------------------------------------------------------------\n# 4) SAT 判斷與列出所有解\n# ----------------------------------------------------------------------\ndef find_first_solution(expr, variables):\n    \"\"\"回傳第一個滿足解；若為不可滿足（UNSAT）則回傳 None。\"\"\"\n    box = [None]\n\n    def check(assignment):\n        if evaluate(expr, assignment):\n            box[0] = assignment\n            return True                  # 找到解 => 回傳 True 停止搜尋\n\n    enumerate_assignments(variables, 0, {}, check)\n    return box[0]\n\n\ndef find_all_solutions(expr, variables):\n    \"\"\"列出所有滿足解（回呼恆回傳 False，因此不會提早停止）。\"\"\"\n    solutions = []\n\n    def check(assignment):\n        if evaluate(expr, assignment):\n            solutions.append(assignment)\n        return False                     # 繼續列舉其餘指派\n\n    enumerate_assignments(variables, 0, {}, check)\n    return solutions\n\n\n# ----------------------------------------------------------------------\n# 5) 主程式\n# ----------------------------------------------------------------------\ndef main():\n    args = list(sys.argv[1:])\n    list_all = \"--all\" in args\n    if list_all:\n        args.remove(\"--all\")\n\n    if args:\n        expr = \" \".join(args)            # 允許 \"a and b\" 不用引號也能合併\n    else:\n        expr = DEFAULT_EXPR\n\n    # 基本防護：拒絕明顯不安全的輸入\n    if any(t in expr for t in (\"=\", \"__\", \"import\", \"lambda\", \"exec\", \"eval\")):\n        print(\"錯誤：運算式含有不允許的關鍵字，已拒絕。\")\n        return\n\n    variables = extract_variables(expr)\n    if not variables:\n        print(\"錯誤：運算式中找不到任何變數。\")\n        return\n\n    print(\"=\" * 60)\n    print(f\"運算式 : {expr}\")\n    print(f\"變數   : {', '.join(variables)}  (共 {len(variables)} 個)\")\n    print(\"=\" * 60)\n\n    if list_all:\n        solutions = find_all_solutions(expr, variables)\n        if not solutions:\n            print(\"結果：UNSAT（不可滿足，沒有任何指派能讓運算式為真）\")\n            return\n        print(f\"結果：SAT，共有 {len(solutions)} 組滿足解：\")\n        for i, sol in enumerate(solutions, 1):\n            print(f\"  解 {i:>2d}: \" + format_assignment(sol))\n    else:\n        solution = find_first_solution(expr, variables)\n        if solution is None:\n            print(\"結果：UNSAT（不可滿足，沒有任何指派能讓運算式為真）\")\n        else:\n            print(\"結果：SAT（可滿足），找到的解：\")\n            print(\"  \" + format_assignment(solution))\n            print(f\"驗證 : eval 結果 = {evaluate(expr, solution)}\")\n\n\ndef format_assignment(assignment):\n    \"\"\"把指派字典排版成好讀的字串，例如 p=True, q=False。\"\"\"\n    return \", \".join(f\"{k}={v}\" for k, v in assignment.items())\n\n\nif __name__ == \"__main__\":\n    main()"
}
```

Created file successfully: sat_solver.py

---

## Assistant

_Thinking:_

Now let me test it with several cases:
1. Default example
2. CLI expression (UNSAT)
3. CLI expression (all solutions)
4. A small benchmark vs brute-force itertools to verify correctness? Can't use itertools in the program, but testing correctness with itertools in a test script is fine (the constraint is on the delivered program). Let me verify correctness by comparing with itertools-derived truth table in a throwaway test.

Let me run tests.

Now let me test it with the default example, a UNSAT case, and the `--all` mode:



**Tool: shell**

**Input:**
```json
{
  "command": "python sat_solver.py",
  "workdir": "C:\\algorithm_HW\\_alg_HW\\homework\\wk3_HW(new)"
}
```

============================================================
�B�⦡ : (p or q) and not (p and q)
�ܼ�   : p, q  (�@ 2 ��)
============================================================
���G�GSAT�]�i�����^�A��쪺�ѡG
  p=True, q=False
���� : eval ���G = True

Command exited with code 0.

**Tool: shell**

**Input:**
```json
{
  "command": "python sat_solver.py \"a and not a\"",
  "workdir": "C:\\algorithm_HW\\_alg_HW\\homework\\wk3_HW(new)"
}
```

============================================================
�B�⦡ : a and not a
�ܼ�   : a  (�@ 1 ��)
============================================================
���G�GUNSAT�]���i�����A�S��������������B�⦡���u�^

Command exited with code 0.

**Tool: shell**

**Input:**
```json
{
  "command": "python sat_solver.py --all \"(a or b) and (c or b)\"",
  "workdir": "C:\\algorithm_HW\\_alg_HW\\homework\\wk3_HW(new)"
}
```

============================================================
�B�⦡ : (a or b) and (c or b)
�ܼ�   : a, b, c  (�@ 3 ��)
============================================================
���G�GSAT�A�@�� 5 �պ����ѡG
  ��  1: a=True, b=True, c=True
  ��  2: a=True, b=True, c=False
  ��  3: a=True, b=False, c=True
  ��  4: a=False, b=True, c=True
  ��  5: a=False, b=True, c=False

Command exited with code 0.

---

## Assistant

_Thinking:_

The program works correctly. The Chinese output is garbled in the console due to encoding (the PowerShell shows mojibake — that's just the terminal codepage, the actual file is UTF-8 with `# -*- coding: utf-8 -*-`). The logic is all correct:

1. Default XOR example: SAT, p=True, q=False ✓
2. `a and not a`: UNSAT ✓
3. `(a or b) and (c or b)`: 5 solutions ✓ (correct: a,c combos with b=False → (c=True,a=True) → 1; with b=True → any a,c → 4; total 5) ✓

The mojibake is just the console encoding on Windows. I could add a sys.stdout reconfigure to UTF-8 to make console output clean. That would be a nice touch. Let me add that at the top of main() or module level:

```python
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
```

This ensures Chinese prints correctly on Windows terminals that support UTF-8 (Windows Terminal). Let me add that.

Also, let me verify correctness against itertools brute force in a separate test script (allowed for testing, not part of the deliverable). Let me do a quick random test.

The logic works correctly for all three cases (the garbled console output is just the Windows codepage, not a program issue). Let me add UTF-8 output handling for cleaner Chinese text on Windows, and then verify correctness against a brute-force truth table:

**Tool: edit**

**Input:**
```json
{
  "oldString": "import re\nimport sys\nimport keyword",
  "newString": "import re\nimport sys\nimport keyword\n\n# 讓中文輸出在 Windows 終端機也能正常顯示\nif hasattr(sys.stdout, \"reconfigure\"):\n    sys.stdout.reconfigure(encoding=\"utf-8\")",
  "path": "C:\\algorithm_HW\\_alg_HW\\homework\\wk3_HW(new)\\sat_solver.py"
}
```

Edited sat_solver.py (1 replacement)

---

## Assistant

_Thinking:_

Now let me verify correctness with a random test vs itertools (in a throwaway test, not part of the deliverable).

**Tool: write**

**Input:**
```json
{
  "content": "# -*- coding: utf-8 -*-\n\"\"\"隨機測試：把 sat_solver 的結果與暴力窮舉 (itertools) 的完整真值表比對。\n此檔案僅供驗證用，不是作業繳交的程式。\"\"\"\nimport itertools\nimport random\nimport sat_solver as s\n\nrandom.seed(42)\nexprs = [\n    \"(a and b) or c\",\n    \"(a or b) and not c\",\n    \"(a or not b) and (b or not c)\",\n    \"not (a and b and c) or d\",\n    \"(a or b) and (not a or c) and (not b or not c)\",\n    \"a and b and c and not d and (e or f)\",\n]\nfor _ in range(200):\n    n = random.randint(1, 3)\n    vs = [chr(ord(\"a\") + i) for i in range(n)]\n    ops = [\"and\", \"or\"]\n    e = vs[0]\n    for v in vs[1:]:\n        e = f\"({e} {random.choice(ops)} {v})\"\n    if random.random() < 0.5:\n        e = f\"not {e}\"\n    exprs.append(e)\n\nbad = 0\nfor expr in exprs:\n    vars_ = s.extract_variables(expr)\n    # 暴力窮舉全部 2^n 組指派\n    brute = []\n    for bits in itertools.product([True, False], repeat=len(vars_)):\n        a = dict(zip(vars_, bits))\n        if eval(expr, {\"__builtins__\": {}}, a):\n            brute.append(a)\n    brute_first = brute[0] if brute else None\n    brute_all_set = set(tuple(sorted(a.items())) for a in brute)\n\n    got_first = s.find_first_solution(expr, vars_)\n    got_all = s.find_all_solutions(expr, vars_)\n    got_all_set = set(tuple(sorted(a.items())) for a in got_all)\n\n    same = (got_first is None) == (brute_first is None)\n    if got_first is not None and brute_first is not None:\n        same_set_first = set(got_first.items()) == set(brute_first.items())\n        same = same and same_set_first  # 我們只要它是一個合法解即可\n    if same and got_all_set == brute_all_set and len(got_all) == len(brute):\n        continue\n    bad += 1\n    print(f\"MISMATCH expr={expr}\")\n    print(f\"  brute first={brute_first} all={len(brute)}\")\n    print(f\"  got   first={got_first} all={len(got_all)}\")\n\nif bad:\n    print(f\"總共 {bad} 個運算式不吻合！\")\nelse:\n    print(f\"OK：{len(exprs)} 個隨機運算式全部通過（與 itertools 暴力窮舉一致）。\")",
  "path": "C:\\algorithm_HW\\_alg_HW\\homework\\wk3_HW(new)\\_verify_test.py"
}
```

Created file successfully: _verify_test.py

---

## Assistant

**Tool: shell**

**Input:**
```json
{
  "command": "python _verify_test.py; Get-Content sat_solver.py -TotalCount 5",
  "workdir": "C:\\algorithm_HW\\_alg_HW\\homework\\wk3_HW(new)"
}
```

OK：206 個隨機運算式全部通過（與 itertools 暴力窮舉一致）。
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAT 求解?��?布�??�滿足性�?�?Boolean Satisfiability Problem�?=============================================================


Command exited with code 0.

---

## Assistant

_Thinking:_

All 206 random expressions pass — the solver matches brute-force enumeration using itertools.

The mojibake in `Get-Content` is again just the console codepage (Big5, not UTF-8). The file itself is UTF-8. Let me verify the file content encoding is fine by reading it with the read tool.

Now, cleanup: should I keep `_verify_test.py`? It's a test file I created for verification. The user asked only for the SAT solver program. I could keep it as a bonus or delete it. I'll keep it since it demonstrates correctness, but it's optional. Actually, let me mention it and keep it — it does not use itertools constraint? Wait, _verify_test.py DOES use itertools, but it's not the deliverable — it's a test harness. That's fine and I'll note that.

Let me verify the final file with the read tool to make sure it's clean, and show the final output running with UTF-8 reconfigure.

All 206 random test expressions pass — the solver matches brute-force enumeration exactly. Let me do a final run to confirm the UTF-8 fix and review the final file:

**Tool: shell**

**Input:**
```json
{
  "command": "chcp 65001 | Out-Null; python sat_solver.py --all \"(a or not b) and (b or not c)\"; python sat_solver.py \"p and q or r\"",
  "workdir": "C:\\algorithm_HW\\_alg_HW\\homework\\wk3_HW(new)"
}
```

============================================================
運算式 : (a or not b) and (b or not c)
變數   : a, b, c  (共 3 個)
============================================================
結果：SAT，共有 4 組滿足解：
  解  1: a=True, b=True, c=True
  解  2: a=True, b=True, c=False
  解  3: a=True, b=False, c=False
  解  4: a=False, b=False, c=False
============================================================
運算式 : p and q or r
變數   : p, q, r  (共 3 個)
============================================================
結果：SAT（可滿足），找到的解：
  p=True, q=True, r=True
驗證 : eval 結果 = True

Command exited with code 0.

**Tool: read**

**Input:**
```json
{
  "path": "C:\\algorithm_HW\\_alg_HW\\homework\\wk3_HW(new)\\sat_solver.py"
}
```

Read file C:\algorithm_HW\_alg_HW\homework\wk3_HW(new)\sat_solver.py, lines 1-168
1: #!/usr/bin/env python3
2: # -*- coding: utf-8 -*-
3: """
4: SAT 求解器（布林可滿足性問題 Boolean Satisfiability Problem）
5: =============================================================
6: 
7: 特性
8: ----
9: 1. 不使用 itertools：自行以 backtracking（深度優先搜尋）列舉所有變數指派。
10: 2. 使用 Python 內建的運算式語法（eval）直接求值，完全不修改使用者輸入的運算式。
11: 3. 搜尋到第一個解即可提前剪枝停止（SAT），也可選擇列出所有解。
12: 
13: 演算法
14: ------
15:     對 n 個變數，遞迴地依序把每個變數指派為 True / False，
16:     形成一棵深度為 n 的二元決策樹；當所有變數都被指派後，
17:     用 eval 對原運算式求值一次。DFS 在找到第一個解後立刻回溯剪枝。
18: 
19: 使用方法
20: --------
21:     python sat_solver.py                            # 內建範例: (p or q) and not (p and q)
22:     python sat_solver.py "(a or b) and not c"       # 命令列指定運算式（須加引號）
23:     python sat_solver.py --all "(a or b)"           # 列出所有滿足解
24: """
25: 
26: import re
27: import sys
28: import keyword
29: 
30: # 讓中文輸出在 Windows 終端機也能正常顯示
31: if hasattr(sys.stdout, "reconfigure"):
32:     sys.stdout.reconfigure(encoding="utf-8")
33: 
34: # Python 保留字與內建字面值不能當成變數名稱
35: _RESERVED = set(keyword.kwlist) | {"True", "False", "None"}
36: 
37: # 內建範例：p、q 恰好一個為真（互斥或 XOR）
38: DEFAULT_EXPR = "(p or q) and not (p and q)"
39: 
40: 
41: # ----------------------------------------------------------------------
42: # 1) 抽出運算式中的所有變數
43: # ----------------------------------------------------------------------
44: def extract_variables(expr):
45:     """從運算式中抽出所有可當作變數的識別字（不含保留字）。"""
46:     names = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr)
47:     return sorted(set(name for name in names if name not in _RESERVED))
48: 
49: 
50: # ----------------------------------------------------------------------
51: # 2) 以 Python 內建語法求值（eval），不修改運算式
52: # ----------------------------------------------------------------------
53: def evaluate(expr, assignment):
54:     """把變數指派代入後用 eval 求值。
55: 
56:     globals 的 __builtins__ 設為空字典，避免運算式呼叫任何內建函式。
57:     """
58:     return bool(eval(expr, {"__builtins__": {}}, assignment))
59: 
60: 
61: # ----------------------------------------------------------------------
62: # 3) 自行實作的列舉（backtracking DFS），不使用 itertools
63: # ----------------------------------------------------------------------
64: def enumerate_assignments(variables, index, assignment, on_assignment):
65:     """遞迴列舉所有 2^n 種變數指派。
66: 
67:     每指派完一組完整解就會呼叫 on_assignment(dict)；
68:     若 on_assignment 回傳 True，代表已經找到解，立刻剪枝停止整棵搜尋樹。
69: 
70:     回傳值：True = 已停止搜尋；False = 走完所有分支。
71:     """
72:     if index == len(variables):
73:         # 所有變數都已指派，交給回呼處理（例如求值、記錄解）
74:         return on_assignment(dict(assignment))
75: 
76:     var = variables[index]
77:     for value in (True, False):          # 每個變數只有兩個可能值
78:         assignment[var] = value
79:         if enumerate_assignments(variables, index + 1, assignment, on_assignment):
80:             return True                  # 子樹已找到解，回溯剪枝
81: 
82:     del assignment[var]                  # 回溯：移除這個變數
83:     return False
84: 
85: 
86: # ----------------------------------------------------------------------
87: # 4) SAT 判斷與列出所有解
88: # ----------------------------------------------------------------------
89: def find_first_solution(expr, variables):
90:     """回傳第一個滿足解；若為不可滿足（UNSAT）則回傳 None。"""
91:     box = [None]
92: 
93:     def check(assignment):
94:         if evaluate(expr, assignment):
95:             box[0] = assignment
96:             return True                  # 找到解 => 回傳 True 停止搜尋
97: 
98:     enumerate_assignments(variables, 0, {}, check)
99:     return box[0]
100: 
101: 
102: def find_all_solutions(expr, variables):
103:     """列出所有滿足解（回呼恆回傳 False，因此不會提早停止）。"""
104:     solutions = []
105: 
106:     def check(assignment):
107:         if evaluate(expr, assignment):
108:             solutions.append(assignment)
109:         return False                     # 繼續列舉其餘指派
110: 
111:     enumerate_assignments(variables, 0, {}, check)
112:     return solutions
113: 
114: 
115: # ----------------------------------------------------------------------
116: # 5) 主程式
117: # ----------------------------------------------------------------------
118: def main():
119:     args = list(sys.argv[1:])
120:     list_all = "--all" in args
121:     if list_all:
122:         args.remove("--all")
123: 
124:     if args:
125:         expr = " ".join(args)            # 允許 "a and b" 不用引號也能合併
126:     else:
127:         expr = DEFAULT_EXPR
128: 
129:     # 基本防護：拒絕明顯不安全的輸入
130:     if any(t in expr for t in ("=", "__", "import", "lambda", "exec", "eval")):
131:         print("錯誤：運算式含有不允許的關鍵字，已拒絕。")
132:         return
133: 
134:     variables = extract_variables(expr)
135:     if not variables:
136:         print("錯誤：運算式中找不到任何變數。")
137:         return
138: 
139:     print("=" * 60)
140:     print(f"運算式 : {expr}")
141:     print(f"變數   : {', '.join(variables)}  (共 {len(variables)} 個)")
142:     print("=" * 60)
143: 
144:     if list_all:
145:         solutions = find_all_solutions(expr, variables)
146:         if not solutions:
147:             print("結果：UNSAT（不可滿足，沒有任何指派能讓運算式為真）")
148:             return
149:         print(f"結果：SAT，共有 {len(solutions)} 組滿足解：")
150:         for i, sol in enumerate(solutions, 1):
151:             print(f"  解 {i:>2d}: " + format_assignment(sol))
152:     else:
153:         solution = find_first_solution(expr, variables)
154:         if solution is None:
155:             print("結果：UNSAT（不可滿足，沒有任何指派能讓運算式為真）")
156:         else:
157:             print("結果：SAT（可滿足），找到的解：")
158:             print("  " + format_assignment(solution))
159:             print(f"驗證 : eval 結果 = {evaluate(expr, solution)}")
160: 
161: 
162: def format_assignment(assignment):
163:     """把指派字典排版成好讀的字串，例如 p=True, q=False。"""
164:     return ", ".join(f"{k}={v}" for k, v in assignment.items())
165: 
166: 
167: if __name__ == "__main__":
168:     main()

---

## Assistant

_Thinking:_

Everything works. The `_verify_test.py` is a test file I created — useful to document correctness but uses itertools, which might confuse the user about "no itertools". I'll keep it but clearly mark it as testing-only (already clearly stated in its docstring). Actually, let me keep it and mention it. It could be deleted to avoid confusion. Hmm. The user asked for a program without itertools — the test file uses itertools only for verification purposes, and its docstring states it's not part of the assignment. I'll leave it but mention it explicitly so there's no ambiguity.

Let me give a final summary.

完成，程式已寫在 `wk3_HW(new)\sat_solver.py`。三個需求全部達成：

## 需求對照

| 需求 | 實作 |
|---|---|
| 不使用 itertools | `enumerate_assignments()`（第 64–83 行）用自己的遞迴 backtracking DFS 列舉，不用 `itertools.product` |
| 內建 Python 運算式語法、不修改 | `evaluate()`（第 53–58 行）直接把原字串交給 `eval()`，不做任何改寫 |
| 寫在 wk3_HW(new) 下 | `C:\algorithm_HW\_alg_HW\homework\wk3_HW(new)\sat_solver.py` |

## 用法

```
python sat_solver.py                         # 內建範例 (p or q) and not (p and q) → SAT
python sat_solver.py "a and not a"           # → UNSAT
python sat_solver.py --all "(a or b) and not c"   # 列出「所有」滿足解
```

## 運作方式

1. `extract_variables()` 用 regex 抽出變數（排除 Python 保留字如 `and`/`or`/`True`）。
2. 對 n 個變數做深度為 n 的二元決策樹 DFS：每個節點把變數設 `True`/`False`，葉節點用 `eval` 求值一次。
3. 找到第一個解就回傳 `True` 讓整棵樹回溯剪枝（SAT 判斷）；不加 `--all` 時只找第一個解。
4. `eval` 的 `globals` 把 `__builtins__` 設為空，避免運算式呼叫內建函式。

## 驗證結果

- 實際輸出：`(p or q) and not (p and q)` → `p=True, q=False`；`a and not a` → UNSAT；`(a or b) and (c or b)` → 5 組解，均正確。
- 另外寫了 `_verify_test.py`（**僅供驗證、非作業程式**）：用 itertools 暴力窮舉 206 個隨機運算式的真值表與本程式比對，**全部吻合**。

如果想調整（例如改成讀檔輸入、支援更大型劇烈搜尋），跟我說一聲即可。
