# wk5_HW — 遞迴練習：河內塔、符號微分、無迴圈泡沫排序

本次作業共三個主題，全部用**遞迴**完成（其中一題刻意「完全不用迴圈」）：

| 主題 | 檔案 | 重點 |
|------|------|------|
| 河內塔 Tower of Hanoi | `hanoi.py`、`hanoi_iterative.py` | 遞迴解法 + 兩種不遞迴的解法，移動數 `2^n − 1` |
| 遞迴符號微分 | `sym_diff.py` | 對巢狀 tuple 表示的算式做 `d/dx`，含化簡 |
| 函數式泡沫排序 | `bubblesort/` | 自製 `map/filter/reduce`，全檔不用 for / while |

---

## 一、檔案架構

```
wk5_HW/
├── README.md
├── hanoi.py                 # 河內塔：遞迴版（可畫圖顯示每步狀態）
├── hanoi_iterative.py       # 河內塔：非遞迴版（規則法 + 堆疊模擬法）
├── sym_diff.py              # 遞迴符號微分
└── bubblesort/
    ├── bubble_sort_fp.py    # 自製高階函數 + 無迴圈泡沫排序（含自我測試）
    └── main.py              # 使用範例
```

> `__pycache__/` 是 Python 自動產生的快取，可刪。

---

## 二、河內塔

### 問題與規則

把 n 個圓盤從 A 柱搬到 C 柱：一次動一個、只能動最上面的、大盤不能疊在小盤上。**最少移動次數 = 2^n − 1**。

### 遞迴解法（`hanoi.py`）

把「n 個盤子 source→target」拆成三步：

1. 上面 n−1 個盤子 `source → auxiliary`（target 借用作輔助）
2. 最大盤 `source → target`
3. 那 n−1 個盤子 `auxiliary → target`（source 借用作輔助）

```powershell
python hanoi.py          # 預設 3 盤，印出每一步
python hanoi.py 4        # 4 盤
python hanoi.py 3 -b     # 額外畫出每步的三柱圖形狀態
python hanoi.py 10 -q    # 只印總移動次數（1023）
```

範例輸出（`python hanoi.py`）：

```
圓盤數量: 3
最少移動次數: 7
實際移動次數: 7

步驟   1: 將圓盤 1 從 A 移到 C
步驟   2: 將圓盤 2 從 A 移到 B
...
完成！總共移動 7 次。
```

### 非遞迴解法（`hanoi_iterative.py`）

提供兩種「不用遞迴」的解法，結果與遞迴版完全相同：

| 方法 | 函式 | 原理 |
|------|------|------|
| 經典迭代規則法 | `hanoi_by_rule` | 奇數步永遠移動最小盤（圓盤 1 依固定循環順序跳）；偶數步做另外兩柱之間「唯一合法」的移動 |
| 堆疊模擬法 | `hanoi_by_stack` | 用顯式 stack 存 `(n, 來源, 輔助, 目標, 狀態)`，模擬遞迴的呼叫／返回過程 |

```powershell
python hanoi_iterative.py                # 預設規則法，3 盤
python hanoi_iterative.py 4 -a stack     # 堆疊模擬法
python hanoi_iterative.py 3 -b          # 每步畫圖
python hanoi_iterative.py 3 --compare    # 比較兩種迭代解法是否一致
```

`--compare` 輸出：

```
規則法移動次數: 7
堆疊法移動次數: 7
兩者結果一致: True
```

> `hanoi_iterative.py` 會 `from hanoi import draw_pegs` 重用畫圖函式，請在同一資料夾內執行。

---

## 三、遞迴符號微分（`sym_diff.py`）

算式以**巢狀 tuple（AST）**表示：

```
數字     : 3, 2.5
變數     : 'x', 'y'
二元運算 : ('+', a, b)  ('-', a, b)  ('*', a, b)  ('/', a, b)  ('^', a, b)
一元函數 : ('neg', a)  ('sin', a)  ('cos', a)  ('tan', a)  ('exp', a)  ('ln', a)
```

`sym_diff(expr, var='x')` 依序做兩件事：

1. `_diff`：對每種運算子套對應的微分法則（和差、乘法法則、除法法則、冪次＋連鎖律；`x^x` 這種一般指數用 `a^b = e^(b ln a)` 處理）。
2. `simplify`：由下而上化簡常數運算與 0/1 恆等式（如 `x + 0 → x`、`1 * x → x`）。

```powershell
python sym_diff.py
```

範例輸出：

```
d/dx (x ^ 3)                      = (3 * (x ^ 2))
d/dx (x * sin(x))                 = (sin(x) + (x * cos(x)))
d/dx sin((x ^ 2))                 = (cos((x ^ 2)) * (2 * x))
d/dx (x / (x + 1))                = (((x + 1) - x) / ((x + 1) ^ 2))
d/dx ln(((x ^ 2) + 1))            = ((2 * x) / ((x ^ 2) + 1))
d/dx exp((3 * x))                 = (exp((3 * x)) * 3)
d/dx (x ^ x)                      = ((x ^ x) * (ln(x) + (x / x)))
d/dx ((3 * (x ^ 2)) + (5 * x))    = ((3 * (2 * x)) + 5)
```

---

## 四、無迴圈泡沫排序（`bubblesort/`）

### 限制

`bubble_sort_fp.py` **全檔不使用** `for`、`while`、推導式（list comprehension）、以及內建 `map` / `filter` / `reduce` / `sorted`，一切靠遞迴。

### 自製高階函數

| 函式 | 行為 | 對應內建 |
|------|------|----------|
| `my_map(f, xs)` | `[f(x) for x in xs]` | `map` |
| `my_filter(pred, xs)` | 保留 `pred(x)` 為 True 的元素 | `filter` |
| `my_reduce(f, xs, init)` | 左摺疊 `f(f(init, a), b)...` | `functools.reduce` |
| `my_zip(xs, ys)` | 配對成 `[(x1,y1), ...]` | `zip` |

### 用 reduce 做一趟泡沫（`bubble_pass`）

`step(acc, x)` 中，`acc` 的最後一個元素是「正在往右冒的泡 (carry)」：

- `carry > x` → `x` 放前面，carry 繼續往右帶；
- 否則 → carry 放下，`x` 成為新 carry。

一趟結束後最大值必在尾端。外層再由 `bubble_sort` **遞迴**重複做 `bubble_pass`，直到 `is_sorted`（用 `my_zip` + `my_filter` 找逆序相鄰對，找不到就是排好了）為止。

### 執行

```powershell
python bubblesort\main.py        # 使用範例：排序數字、字串、高階函數
python bubble_sort_fp.py         # 在 bubblesort 資料夾內執行：含自我測試
```

`main.py` 輸出：

```
[1, 2, 4, 5, 8]
['apple', 'fig', 'pear']
[2, 4, 6]
[3, 4]
6
```

`bubble_sort_fp.py` 最後會做 10 組隨機資料的測試並印出：

```
隨機測試全部通過: True
```

---

## 五、各程式的複雜度速覽

| 程式 | 時間 | 空間 | 備註 |
|------|------|------|------|
| `hanoi.py` / `hanoi_iterative.py` | O(2^n)（步數本身 2^n−1） | O(n) | 三種解法產生**完全相同**的步驟序列 |
| `sym_diff.py` | O(算式大小) | O(深度) | 每個節點拜訪常數次 |
| `bubble_sort_fp.py` | O(n²)（泡沫排序天性） | O(n)（遞迴切片） | `xs[1:]` 會複製 list，是換取「無迴圈」的代價 |

---

## 六、閱讀順序建議

1. `hanoi.py`：最經典的「divide and conquer 遞迴」。
2. `hanoi_iterative.py`：看同一問題怎麼用迴圈規則／顯式堆疊改寫，體會遞迴與 stack 的等價性。
3. `sym_diff.py`：樹狀結構上的遞迴（AST），每種運算子一個 case。
4. `bubblesort/bubble_sort_fp.py`：以遞迴取代所有迴圈，並練習高階函數思維。
