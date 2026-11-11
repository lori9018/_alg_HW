# wk7_HW — 組合數 C(n, k)：非動態規劃 vs 動態規劃

用同一個問題——**組合數 C(n, k)**（從 n 個不同元素中取出 k 個的方法數）——實作並比較「不用 DP」與「用 DP」的各種解法，實測它們的耗時差異。

核心遞迴關係是**巴斯卡恆等式**：

```
C(n, k) = C(n-1, k-1) + C(n-1, k)
C(n, 0) = C(n, n) = 1
```

---

## 一、檔案架構

```
wk7_HW/
├── README.md              # 本說明文件
├── Combination.nonDPpy    # 版本一：非 DP（純遞迴 + 公式迭代）
├── Combination_DP.py      # 版本二：DP（二維表 + 一維空間優化）
└── combination_explained.md   # 詳細原理講解（複雜度推導、巴斯卡三角形、記憶化延伸）
```

| 檔案 | 內容 |
|------|------|
| `Combination.nonDPpy` | `comb_recursive`（純遞迴，O(2ⁿ)）、`comb_formula`（公式迭代，O(k)）；附正確性測試與耗時比較 |
| `Combination_DP.py` | `comb_dp_2d`（二維 DP 表）、`comb_dp_1d`（一維空間優化）；附測試、耗時比較與大數示範 |
| `combination_explained.md` | 數學推導與四種方法的完整優缺點分析，適合作為書面報告主體 |

> 註：`Combination.nonDPpy` 的副檔名刻意不叫 `.py`（避免與 `Combination_DP.py` 混淆），但內容是純 Python，直接 `python Combination.nonDPpy` 即可執行。

---

## 二、使用方式

```powershell
python Combination.nonDPpy    # 非 DP 版：正確性測試 + C(25,12) 耗時比較
python Combination_DP.py     # DP 版：正確性測試 + C(25,12) 耗時 + C(1000,500) 大數
```

> Windows 若提示找不到 `python`，可改用 `py`。

---

## 三、四種解法

### 1. 純遞迴 `comb_recursive`（非 DP）

直接把巴斯卡恆等式寫成遞迴。問題在於**重複計算**：以 C(5,2) 為例，遞迴樹中 `C(3,1)`、`C(2,1)` 都被算了好幾次，n 越大越嚴重。

- 時間：O(C(n,k))，最壞 O(2ⁿ)（遞迴樹的葉節點全部回傳 1，葉數恰為 C(n,k)）
- 空間：O(n)（遞迴深度）

### 2. 公式迭代 `comb_formula`（非 DP）

$$C(n,k)=\prod_{i=1}^{k}\frac{n-k+i}{i}$$

約分後只算分子的 k 項，並利用對稱性 `k = min(k, n−k)` 減半。**先乘再除**保證每一步中間結果都是整數（第 i 步後 result 恰為 C(n−k+i, i)），所以可安全用 `//`。

- 時間：O(k)；空間：O(1)

### 3. 二維 DP `comb_dp_2d`（Bottom-up）

`dp[i][j] = C(i, j)`，由小到大逐列填表，就是**巴斯卡三角形**：

```
i\j  0   1   2   3
0    1
1    1   1
2    1   2   1
3    1   3   3   1
```

- 時間：O(n·k)；空間：O(n·k)。整張表建好後可 O(1) 查詢任何 C(i, j)。

### 4. 一維 DP `comb_dp_1d`（空間優化）

算第 i 列只會用到第 i−1 列，所以只留一條長度 k+1 的陣列，且 **j 由大到小**更新：

```python
for i in range(1, n + 1):
    for j in range(min(i, k), 0, -1):
        dp[j] += dp[j - 1]
```

由大到小的原因：`dp[j] += dp[j-1]` 需要讀「上一列」的 `dp[j-1]`；若由小到大，`dp[j-1]` 已被本列覆蓋會算錯（與 0/1 背包的一維優化同一技巧）。

- 時間：O(n·k)；空間：O(k)

---

## 四、複雜度與實測

| 方法 | 類別 | 時間 | 空間 | 實測 C(25,12) |
|------|------|------|------|---------------|
| `comb_recursive` | 非 DP | O(C(n,k)) ≤ O(2ⁿ) | O(n) | 約 0.77 秒（約 1,040 萬次函式呼叫） |
| `comb_formula` | 非 DP | O(k) | O(1) | 約 0.000008 秒（12 次乘除） |
| `comb_dp_2d` | DP | O(n·k) | O(n·k) | 約 0.00003 秒（300 次加法） |
| `comb_dp_1d` | DP | O(n·k) | O(k) | 約 0.00001 秒 |

補充實測：`C(1000, 500)` 用 `comb_dp_1d` 算出來是 **300 位數**的大整數——純遞迴版在這種規模根本跑不完。

### 為什麼 DP 比純遞迴快？

- 純遞迴：同一個 `C(i, j)` 被算很多次，總呼叫數 ≈ 2·C(n,k) − 1。
- DP：每個 `C(i, j)` **只算一次**，之後直接查表。這正是 DP 的兩個前提——**最佳子結構**（巴斯卡恆等式）與**重疊子問題**（遞迴樹中重複的節點）。

---

## 五、什麼時候用哪一種？

- **只求一次 C(n, k)** → 公式迭代（最快、最省記憶體）。
- **要查很多不同的 C(i, j)**（多筆測資、機率計算） → 二維 DP 建表後每次 O(1) 查表。
- **記憶體吃緊但仍要 DP** → 一維 DP。
- **教學/理解遞迴關係** → 純遞迴，或加上 `functools.lru_cache` 變成 Top-down 記憶化 DP（詳見 `combination_explained.md` 第 5 節）。

---

## 六、閱讀順序建議

1. 先看 `combination_explained.md` 建立完整觀念（問題定義 → 重複計算 → DP 建表 → 空間優化）。
2. 執行 `Combination.nonDPpy`，親眼看到純遞迴在 C(25,12) 就要 0.7 秒。
3. 執行 `Combination_DP.py`，比較 DP 兩種寫法，以及 C(1000,500) 的大數結果。
