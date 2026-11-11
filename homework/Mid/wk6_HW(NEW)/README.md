# wk6_HW(NEW) — Lambda Calculus 解譯器（單檔版）

一個用 Python 實作的 **純 λ-演算（Lambda Calculus）解譯器**，逐步顯示**完整的 β-reduction 過程**（一行一步，並以 ⟦ ⟧ 標示正在被化簡的 redex）。

這是 `../wk6_HW/` 的**重寫版**：整個解譯器濃縮成單一檔案 `lambda_calc.py`，新增 **applicative order（應用序）**、**名稱／Church 數字縮寫折疊顯示**等功能；內建 Church 編碼的 Prelude（`TRUE`、`SUCC`、`PLUS`、`MULT`、`Y` combinator…），並附上用 λ-演算寫的 **階乘 factorial** 與 **費氏數列 fibonacci**。

---

## 一、檔案架構

```
wk6_HW(NEW)/
├── README.md         # 本說明文件
├── lambda_calc.py    # 解譯器本體：tokenizer / parser / capture-avoiding 代換 / β-歸約 / 印表
├── example_usage.py  # 用 Python 呼叫解譯器，計算 FACT/FIB 並與 Python 內建結果對照
├── factorial.lc      # λ 程式：FACT（用 Y combinator 定義遞迴），算 0! ~ 3!
└── fibonacci.lc      # λ 程式：FIB（遞迴），算 fib(0) ~ fib(3)
```

| 檔案 | 內容 |
|------|------|
| `lambda_calc.py` | `parse` 遞迴下降剖析、`subst` capture-avoiding substitution（含 α-renaming）、`step` 單步 β-歸約（normal / applicative order）、`show` 印表（把符合定義的子樹折疊成名稱、把 Church numeral 顯示成數字）、`PRELUDE`（Church 編碼庫）、REPL 與 CLI |
| `example_usage.py` | 以 `run_program` / `evaluate` 等 API 批次計算 FACT 0~4、FIB 0~5，列出 β-歸約步數並與 `math.factorial`、Python 遞迴 fib 比對 |
| `factorial.lc` / `fibonacci.lc` | 給 CLI 直接執行的 `.lc` 腳本 |

---

## 二、λ-演算語法

| 語法 | 意義 |
|------|------|
| `x` | 變數 |
| `\x. body` 或 `λx. body` | 抽象（函數）；`\x y. body` 等同 `\x.\y. body` |
| `f a b` | 應用，**左結合**，等同 `((f a) b)` |
| `(e)` | 括號 |
| `3` | 數字語糖，展開成 Church numeral `λf x. f (f (f x))` |
| `NAME = expr` | 定義（之後的行可以使用此名稱） |
| `--` 或 `#` 開頭 | 註解 |

顯示時，normal form 若剛好是 Church numeral 會折疊成數字；若與某個定義（如 `PLUS`）α-等價則折疊成名稱，方便閱讀。被化簡的 redex 以 `⟦...⟧` 標示。

### 內建 Prelude（自動載入）

`TRUE`、`FALSE`、`AND`、`OR`、`NOT`、`IF`、`PAIR/FST/SND`、`SUCC`、`PLUS`、`MULT`、`POW`、`PRED`、`SUB`、`ISZERO`、`LEQ`、`Y`（Y combinator）。

---

## 三、使用方式

```powershell
# Windows 主控台若出現 UnicodeEncodeError，先加上 -X utf8（或設定 PYTHONIOENCODING=utf-8）
py -X utf8 lambda_calc.py                      # 進入 REPL（已載入 Prelude），:q 離開
py -X utf8 lambda_calc.py --example basic      # 內建範例：SUCC/PLUS/MULT/POW/PRED/AND/IF...
py -X utf8 lambda_calc.py --example fact       # Y combinator 階乘 FACT 3
py -X utf8 lambda_calc.py --example fib        # Y combinator 費氏 FIB 0~3
py -X utf8 lambda_calc.py factorial.lc --max 20000
py -X utf8 lambda_calc.py fibonacci.lc --max 20000
py -X utf8 lambda_calc.py -e "PLUS 2 3"        # 直接求值一行運算式

# 驗證腳本：FACT/FIB 與 Python 內建對照
py -X utf8 example_usage.py
```

| 選項 | 說明 |
|------|------|
| `--example {basic,fact,fib}` | 執行內建範例 |
| `-e, --expr EXPR` | 直接求值一個運算式 |
| `file.lc` | 執行檔案（Prelude 會先自動載入） |
| `--applicative` | 改用**應用序**歸約（預設為 **normal order**：最左最外） |
| `--max N` | β-歸約步數上限（預設 3000，防止不停機的項） |
| `--no-fold` | 完整展開顯示，不用名稱／數字縮寫 |

> 兩種歸約策略的差異可自己試：`py -X utf8 lambda_calc.py -e "(\x. x) ((\y. y) z)"` —— normal order 一步就結束；applicative order 會先把引數 `((\y. y) z)` 化簡完再代入。

---

## 四、範例輸出

`py -X utf8 lambda_calc.py -e "PLUS 2 3"`：

```
▶ PLUS 2 3
  start  : ⟦PLUS 2⟧ 3
  →β 1   : ⟦(λn f x. 2 f (n f x)) 3⟧
  →β 2   : λf x. ⟦2 f⟧ (3 f x)
  →β 3   : λf x. ⟦(λx. f (f x)) (3 f x)⟧
  →β 4   : λf x. f (f (⟦3 f⟧ x))
  →β 5   : λf x. f (f (⟦(λx. f (f (f x))) x⟧))
  NF     : 5
  ✔ normal form，共 6 步　= Church numeral 5
```

`example_usage.py` 的批次結果（節錄）：

```
===== FACTORIAL =====
FACT 0 = 1    (12 步)  Python: 1
FACT 1 = 1    (36 步)  Python: 1
FACT 2 = 2    (142 步)  Python: 2
FACT 3 = 6    (694 步)  Python: 6
FACT 4 = 24   (4068 步)  Python: 24

===== FIBONACCI =====
FIB 0 = 0    (22 步)  Python: 0
FIB 1 = 1    (25 步)  Python: 1
FIB 2 = 1    (136 步)  Python: 1
FIB 3 = 2    (294 步)  Python: 2
FIB 4 = 3    (699 步)  Python: 3
FIB 5 = 5    (1472 步)  Python: 5
```

可以觀察到：在 λ-演算中算一次階乘，β-歸約步數**指數成長**（0!→4! 從 12 步漲到 4068 步），這是 Church numeral 編碼天生的成本。

---

## 五、遞迴是怎麼來的？—— Y combinator

λ-演算沒有內建遞迴，`factorial.lc` 的寫法是：

```
FACT = Y (\f n. IF (ISZERO n) 1 (MULT n (f (PRED n))))
```

- `Y = \f. (\x. f (x x)) (\x. f (x x))` 滿足 `Y F →* F (Y F)`，會不斷把「自己」餵給函數。
- 被包進去的 `\f n. ...` 中，`f` 就是「FACT 自己」；`IF (ISZERO n) 1 (MULT n (f (PRED n)))` 對應到
  `if n = 0 then 1 else n * FACT(n-1)`。
- 呼叫 `FACT 3` 時，靠 normal order 歸約一步步展開，最後得到 Church numeral `6`。

`fibonacci.lc` 用同一招定義 `FIB n = if n <= 1 then n else FIB(n-1) + FIB(n-2)`。

---

## 六、與舊版 `wk6_HW` 的差異

| | `wk6_HW`（舊） | `wk6_HW(NEW)`（本資料夾） |
|---|---|---|
| 架構 | `lambda_engine.py` + `main.py` + `test_lambda.py` | 單一檔案 `lambda_calc.py` |
| 歸約策略 | normal order | normal order **＋可切換 applicative order** |
| 巨集/定義 | `.lam` 中 `name = expr` | `NAME = expr`（含內建 Prelude 一組） |
| 顯示 | redex 標示、`--quiet` | redex 標示 ＋ **名稱/數字折疊**（`--no-fold` 可關） |
| 範例檔 | `.lam` | `.lc` ＋ `example_usage.py` 對照 Python |

---

## 七、注意事項

- 程式會把 `sys.setrecursionlimit` 提高到 20000，`.lc` 範例請記得加 `--max 20000` 以上，避免中途被步數上限擋下。
- Windows 主控台預設編碼（cp950）印不出 `▶`、`λ`、`⟦⟧` 等符號，請用 `py -X utf8` 或設定環境變數 `PYTHONIOENCODING=utf-8` 執行。
- `__pycache__/` 為 Python 自動產生的快取，可刪。
