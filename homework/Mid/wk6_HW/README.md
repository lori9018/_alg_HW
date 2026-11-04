# wk6_HW — Lambda Calculus 解譯器

一個用 Python 實作的 **純 Lambda Calculus (λ-演算) 解譯器**，
使用 **Normal order（最左最外）** β-歸約，並逐步顯示**完整的計算過程**（一行一步）。

內附兩個用 Church 編碼寫成的 Lambda Calculus 程式：**階乘 factorial** 與 **費氏數列 fibonacci**。

---

## 一、檔案架構

```
wk6_HW/
├── README.md            # 本說明文件
├── lambda_engine.py     # 核心引擎：Lexer / Parser / AST / 代換 / Normal order 歸約 / 印表
├── main.py              # 命令列介面 (CLI)：讀 .lam 檔或 -e 運算式，顯示計算過程
├── test_lambda.py       # 單元測試（23 個測試）
└── examples/
    ├── factorial.lam    # Church 編碼階乘，計算 3! = 6
    └── fibonacci.lam    # Church 編碼費氏數列，計算 fib(4) = 3
```

| 檔案 | 負責內容 |
|------|----------|
| `lambda_engine.py` | `tokenize` 詞法分析、`Parser` 語法分析、`Var/Abs/App` AST、`free_vars`、`substitute` 捕獲避免代換、`reduce_step` 單步 normal order 歸約、`to_str` 印表、`.lam` 解析與巨集展開 |
| `main.py` | 命令列參數、讀檔、逐行輸出計算過程與結果 |
| `test_lambda.py` | 解析、代換、歸約、範例結果的單元測試 |

---

## 二、支援的語法

| 語法 | 意義 |
|------|------|
| `x` | 變數 |
| `\x. body`（或 `λx. body`） | 抽象（函數） |
| `\x y. body` | 多參數，等同 `\x.\y. body` |
| `f a b` | 函數應用，左結合，等同 `((f a) b)` |
| `(e)` | 括號（改變結合順序） |
| `3` | 數字語糖，展開成 Church 數 `\f.\x. f (f (f x))` |
| `# ...` | 註解 |

`.lam` 檔中可以用 `name = expr` 先定義縮寫，最後寫一行要計算的運算式。

---

## 三、使用方式

```bash
# 計算內附範例
python main.py examples/factorial.lam
python main.py examples/fibonacci.lam

# 直接計算一行運算式
python main.py -e "(\x. \y. x) a b"

# 只顯示最後結果（不顯示每一步）
python main.py examples/factorial.lam -q

# 每一步額外標示所歸約的 redex
python main.py -e "(\x. x) y" --redex

# 不帶參數會印出使用說明
python main.py
```

選項：

| 選項 | 說明 |
|------|------|
| `-e, --expr EXPR` | 直接給定運算式（不讀檔案） |
| `--max-steps N` | 最多歸約步數（預設 `100000`，避免不停機的項卡住） |
| `-q, --quiet` | 只顯示結果 |
| `--redex` | 每一步額外標示所歸約的 redex |

---

## 四、範例輸出

### 1. 基本歸約：`(\x. x) y`

```
======================================================================
目標：(\x. x) y
======================================================================
計算過程（Normal order，共 1 步）：
     0: (\x. x) y
     1: y
----------------------------------------------------------------------
結果：y
β-歸約步數：1
```

### 2. 常數函數：`(\x. \y. x) a b`（`a` 被回傳，`b` 被丟棄）

```
計算過程（Normal order，共 2 步）：
     0: (\x. \y. x) a b
     1: (\y. a) b
     2: a
結果：a
```

### 3. 階乘 `examples/factorial.lam`（`3! = 6`）

第 0 步是展開所有定義後的巨大項，之後每一步做一次 β-歸約：

```
目標：fact (\f. \x. f (f (f x)))
計算過程（Normal order，共 646 步）：
     0: (\f. (\x. f (x x)) (\x. f (x x))) (\f. \n. ... ) (\f. \x. f (f (f x)))
     1: (\x. (\f. \n. ... ) (x x)) (\x. (\f. \n. ... ) (x x)) (\f. \x. f (f (f x)))
     2: ...（中略）...
   646: \f. \x. f (f (f (f (f (f x)))))
結果：\f. \x. f (f (f (f (f (f x)))))      # 6 = f 套用 6 次
β-歸約步數：646
```

> `\f. \x. f (f (f (f (f (f x)))))` 就是 Church 數 **6**。
>
> 注意：完全展開後，Church 數的歸約會產生很長的項（`fact 3` 最多一步可達數千字元），
> 這是 normal order 的正常現象。輸出量大時建議重導到檔案，例如：
> `python main.py examples/factorial.lam > out.txt`

### 4. 費氏數列 `examples/fibonacci.lam`（`fib(4) = 3`）

```
目標：fib (\f. \x. f (f (f (f x))))
計算過程（Normal order，共 574 步）：
     0: ...
   574: \f. \x. f (f (f x))
結果：\f. \x. f (f (f x))                   # 3 = f 套用 3 次
β-歸約步數：574
```

---

## 五、實作原理

1. **詞法分析**：把字串切成 `\`、`.`、`(`、`)`、識別字、數字等 token。
2. **語法分析**：遞迴下降，文法為
   ```
   expr        := abstraction
   abstraction := LAMBDA IDENT+ DOT expr | application
   application := atom+
   atom        := IDENT | NUMBER | LPAREN expr RPAREN
   ```
   多參數的 `\x y. body` 會被柯里化成 `\x.\y. body`。
3. **AST**：三個節點 `Var / Abs / App`（`dataclass`，不可變）。
4. **捕獲避免代換 (capture-avoiding substitution)**：
   計算 `M[x := N]` 時，若 `N` 的自由變數會被 `M` 中某個 λ 綁定，就先把該綁定變數
   alpha-換名成不衝突的新名稱（例如 `y` → `y'`），避免變數捕獲。
5. **Normal order（最左最外）β-歸約**：
   每一步找出「最左邊、最外面」的 redex `(\x. body) arg`，代換成 `body[x := arg]`，
   記錄下來再繼續，直到沒有 redex（normal form）或達到步數上限。
6. **Y 組合子**：`Y = \f. (\x. f (x x)) (\x. f (x x))`，在 normal order 下可實現遞迴。

### 為什麼範例結果正確？

* `factorial.lam`：`fact 3` 歸約到 `\f.\x. f (f (f (f (f (f x)))))`，即 Church 數 **6**（= 3!）。
* `fibonacci.lam`：`fib 4` 歸約到 `\f.\x. f (f (f x))`，即 Church 數 **3**（= fib(4)）。

---

## 六、測試

```bash
python test_lambda.py
```

23 個測試涵蓋：解析與 pretty print、Church 數、自由變數、捕獲避免代換、
normal order 的「最左最外」順序、Church 加法/乘法、階乘與費氏範例結果、
以及用 Omega `(\x. x x)(\x. x x)` 驗證 `--max-steps` 截斷。

```
Ran 23 tests in 0.4s
OK
```
