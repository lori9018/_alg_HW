import time
# ======================================================
# 版本二:動態規劃
# ======================================================

def comb_dp_2d(n, k):
    """二維 DP(Bottom-up,即巴斯卡三角形)。
    dp[i][j] 代表 C(i, j)。
    時間複雜度 O(n*k),空間複雜度 O(n*k)。
    """
    if k < 0 or k > n:
        return 0
    dp = [[0] * (k + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        for j in range(min(i, k) + 1):
            if j == 0 or j == i:
                dp[i][j] = 1
            else:
                dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j]
    return dp[n][k]


def comb_dp_1d(n, k):
    """一維 DP(空間優化)。
    只保留「上一列」,更新時 j 由大到小,避免覆蓋還需要用到的值。
    時間複雜度 O(n*k),空間複雜度 O(k)。
    """
    if k < 0 or k > n:
        return 0
    dp = [0] * (k + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for j in range(min(i, k), 0, -1):
            dp[j] += dp[j - 1]
    return dp[k]


# ======================================================
# 測試
# ======================================================

def timeit(func, n, k):
    start = time.perf_counter()
    value = func(n, k)
    return value, time.perf_counter() - start


if __name__ == "__main__":
    # 正確性測試
    tests = [(5, 2), (10, 3), (20, 10), (6, 0), (6, 6), (4, 5)]
    print("=== 正確性測試 ===")
    for n, k in tests:
        r = [comb_dp_2d(n, k), comb_dp_1d(n, k)]
        status = "OK" if len(set(r)) == 1 else "ERROR"
        print(f"C({n},{k}) = {r[0]}  [{status}]")

    # 效能比較
    n, k = 25, 12
    print(f"\n=== 耗時 C({n},{k}) ===")
    for name, f in [("DP 二維陣列 ", comb_dp_2d),
                    ("DP 一維陣列 ", comb_dp_1d)]:
        v, t = timeit(f, n, k)
        print(f"{name}: {v}  耗時 {t:.6f} 秒")

    # 大數(遞迴版會跑不完,所以不測)
    n, k = 1000, 500
    print(f"\nC({n},{k}) 的位數:{len(str(comb_dp_1d(n, k)))}")