# wk3_HW(new) — SAT 求解器（布林可滿足性問題）

用 Python 自製一個 **SAT（Boolean Satisfiability）求解器**：給一個布林運算式（如 `(p or q) and not (p and q)`），判斷是否存在一組變數指派讓整個運算式為真（SAT），並印出其中一組（或全部）解。

依作業要求：

1. **不使用 `itertools`** —— 列舉所有 `2^n` 種變數指派的部分，自行以遞迴 backtracking（DFS）實作。
2. **沿用 Python 內建運算式語法** —— 使用 `and` / `or` / `not` / 括號，直接以 `eval` 對「使用者原封不動的運算式」求值，不另外發明語法。

---

## 一、檔案架構

```
wk3_HW(new)/
├── README.md          # 本說明文件
├── sat_solver.py      # 主程式：SAT 求解器（作業繳交檔）
├── _verify_test.py    # 隨機測試：與 itertools 暴力窮舉對照，驗證正確性（非作業本體）
├── READEME.md         # 開發心得筆記（檔名照舊保留）
└── opencode筆記.md    # 與 AI 協作開發的過程紀錄
```

| 檔案 | 內容 |
|------|------|
| `sat_solver.py` | 抽出變數 → backtracking 列舉指派 → `eval` 求值 → 判定 SAT / UNSAT；支援 `--all` 列出所有解 |
| `_verify_test.py` | 產生 6 個固定 + 200 個隨機運算式，把「第一個解」與「所有解集合」和 itertools 暴力法比對 |
| `READEME.md` | 說明本版是依老師指示重寫的簡化版，並附 Gemini 對話連結輔助理解 |
| `opencode筆記.md` | 當初產生程式的完整對話紀錄 |

---

## 二、演算法原理

### 1. 抽取變數（`extract_variables`）

用正規表示式 `[A-Za-z_][A-Za-z0-9_]*` 抓出運算式中所有識別字，去掉 Python 保留字（`keyword.kwlist`、`True`、`False`、`None`，因為它們會被 `eval` 當成字面值而非變數），排序去重後得到變數清單。

### 2. Backtracking 列舉指派（`enumerate_assignments`）

對 n 個變數建立一棵**深度為 n 的二元決策樹**，遞迴地依序把每個變數指派為 `True` / `False`：

```
                p=True                p=False
          q=True   q=False      q=True   q=False
           ...      ...          ...      ...
```

- 走到葉節點（所有變數都指派完）時呼叫回呼函式 `on_assignment(dict)`。
- 回呼回傳 `True` 代表「已找到解」，整棵搜尋樹立刻**回溯剪枝**停止——這是比 itertools 暴力法聰明的地方：找到第一個 SAT 解就停，不必把 `2^n` 全部跑完。
- UNSAT 時才會完整列舉所有指派。

### 3. 求值（`evaluate`）

```python
bool(eval(expr, {"__builtins__": {}}, assignment))
```

- `assignment`（變數 → True/False 的字典）作為 local namespace 代入。
- `__builtins__` 設為空字典，**讓運算式叫不到任何內建函式**，配合主程式對 `=`、`__`、`import`、`lambda`、`exec`、`eval` 等關鍵字的黑名單過濾，構成基本資安防護（避免例如 `__import__('os').system(...)` 之類的注入）。

### 4. 複雜度

| 項目 | 複雜度 | 說明 |
|------|--------|------|
| 時間 | O(2^n) 最壞情況 | n 為變數個數；找到解可提早剪枝，UNSAT 則須窮舉到底 |
| 空間 | O(n) | 遞迴深度即變數數，assignment 只有一份 |

> 這是教科書上最直觀的「暴力列舉型」SAT 解法；工業級求解器（DPLL、CDCL）靠單元傳播、子句學習等技術大幅剪掉搜尋樹，不在本作業範圍。

---

## 三、使用方式

```powershell
# 內建範例：(p or q) and not (p and q)  （p、q 恰一為真 = XOR）
python sat_solver.py

# 命令列指定運算式（含空格，建議加引號）
python sat_solver.py "(a or b) and not c"

# 不加引號也行，參數會自動合併
python sat_solver.py a and b

# 列出所有滿足解
python sat_solver.py --all "(a or b)"

# 正確性驗證（隨機 200+ 個運算式與 itertools 暴力法對照）
python _verify_test.py
```

> Windows 若提示找不到 `python`，可改用 `py`。

---

## 四、範例輸出

### 1. 預設範例（找第一個解）

```
============================================================
運算式 : (p or q) and not (p and q)
變數   : p, q  (共 2 個)
============================================================
結果：SAT（可滿足），找到的解：
  p=True, q=False
驗證 : eval 結果 = True
```

### 2. `--all` 列出所有解

```
結果：SAT，共有 3 組滿足解：
  解  1: a=True, b=True
  解  2: a=True, b=False
  解  3: a=False, b=True
```

### 3. 驗證腳本

```
OK：206 個隨機運算式全部通過（與 itertools 暴力窮舉一致）。
```

---

## 五、閱讀程式碼的建議順序

1. `extract_variables` —— 輸入怎麼被解析出變數。
2. `evaluate` —— 一組指派怎麼被求值（注意 `__builtins__` 的防護）。
3. `enumerate_assignments` —— 核心的 backtracking／剪枝。
4. `find_first_solution` / `find_all_solutions` —— 兩種「回呼」示範同一套列舉引擎的不同用法。
5. `main` —— 命令列解析與黑名單防護。

---

## 六、注意事項

- 運算式只支援 Python 布林語法：`and`、`or`、`not`、括號、變數（`True` / `False` 會被當字面值而非變數）。
- 惡意輸入（含 `=`、`__`、`import`、`lambda`、`exec`、`eval`）會被直接拒絕；作業情境用不到，但展示了 `eval` 的安全使用方式。
- `__pycache__/` 為 Python 自動產生的快取，可隨時刪除。
