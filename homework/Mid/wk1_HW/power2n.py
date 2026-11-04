#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
power2n：四種求 2^n 的寫法，並比較其執行效率
============================================

方法 1   內建運算子          2 ** n
方法 2a  遞迴（呼叫兩次）    power2n(n-1) + power2n(n-1)   -> 指數時間 O(2^n)
方法 2b  遞迴（呼叫一次）    2 * power2n(n-1)              -> 線性時間 O(n)
方法 3   遞迴 + 查表         先查表，沒算過才遞迴        -> 線性時間 O(n)

方法 2a 與方法 3 的差別只在「有沒有先查表」：方法 2a 每次都重算，
所以呼叫次數是 2^(n+1)-1（n=100 時約 2.5e30 次，實務上不可能跑完）；
方法 3 把算過的結果記下來，於是每個 n 只算一次，呼叫次數降到 2n+1。

執行方法
--------
    python power2n.py        # 預設測試 n = 100
    python power2n.py 20     # 改用 n = 20
"""

import sys
import time
import unicodedata

# 讓中文輸出在 Windows 終端機也能正常顯示
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_N = 100       # 題目要求的測試值
MAX_MEASURED_CALLS = 10_000_000   # 超過這個呼叫次數就不真的跑，改用外推


# =====================================================================
# 方法 1：直接用內建次方運算子
# =====================================================================
def power2n_1(n):
    """方法 1：內建運算子 2 ** n，一次搞定（Python 內部以快速冪實作）。"""
    return 2 ** n


# =====================================================================
# 方法 2a：遞迴 power2n(n-1) + power2n(n-1)
# =====================================================================
def power2n_2a(n):
    """方法 2a：遞迴兩次，時間複雜度 O(2^n)，n 每加 1 時間就翻倍。"""
    if n == 0:                       # 遞迴終止條件
        return 1
    return power2n_2a(n - 1) + power2n_2a(n - 1)


# =====================================================================
# 方法 2b：遞迴 2 * power2n(n-1)
# =====================================================================
def power2n_2b(n):
    """方法 2b：遞迴一次，時間複雜度 O(n)。"""
    if n == 0:                       # 遞迴終止條件
        return 1
    return 2 * power2n_2b(n - 1)


# =====================================================================
# 方法 3：遞迴 + 查表
# =====================================================================
# 記錄「已經算過的 2^n」，避免重複計算
_table = {}


def power2n_3(n):
    """方法 3：先查表，沒算過才遞迴；外層負責清空表格。"""
    _table.clear()
    return _power2n_3(n)


def _power2n_3(n):
    if n in _table:                  # 已經算過 -> 直接查表，O(1)
        return _table[n]
    if n == 0:                       # 遞迴終止條件
        _table[0] = 1
        return 1
    result = _power2n_3(n - 1) + _power2n_3(n - 1)   # 兩次呼叫中第二次會命中表格
    _table[n] = result               # 記錄結果
    return result


# 各方法對應的函式
_METHODS = {
    "方法 1  內建 2**n": power2n_1,
    "方法 2a 遞迴呼叫兩次": power2n_2a,
    "方法 2b 遞迴呼叫一次": power2n_2b,
    "方法 3  遞迴 + 查表": power2n_3,
}


# =====================================================================
# 工具函式：呼叫次數統計 / 計時 / 中文對齊
# =====================================================================
def count_calls(func, n):
    """攔截每一次函式呼叫，統計遞迴的總呼叫次數。

    遞迴函式在內部呼叫的是自己的全域名稱，所以在外面包一層是數不到的，
    只能用 sys.setprofile 攔截。注意：開啟 profiler 會明顯變慢，
    因此這段只用來數次數，不列入時間比較。
    """
    calls = 0

    def tracer(frame, event, arg):
        nonlocal calls
        if event == "call":
            calls += 1

    sys.setprofile(tracer)
    try:
        func(n)
    finally:
        sys.setprofile(None)
    return calls


def best_time(func, n, repeat=5):
    """重複執行取最短時間，避免單次量測失真。"""
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        func(n)
        best = min(best, time.perf_counter() - start)
    return best


def width(text):
    """字串在終端機的顯示寬度（中日韓全形字算 2 格）。"""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in str(text))


def pad(text, size, right=False):
    """依顯示寬度左右對齊。"""
    space = " " * max(0, size - width(text))
    return space + str(text) if right else str(text) + space


def scientific(value):
    """把秒數寫成 1.23e-06 這種形式。"""
    return f"{value:.3e}".replace("e-0", "e-").replace("e+0", "e+")


# =====================================================================
# 測試
# =====================================================================
def test_correct(limit=10):
    """先確認四種方法結果都等於 2 ** n。"""
    print("【正確性檢查】")
    ok = True
    for n in range(limit + 1):
        expect = 2 ** n
        for name, func in _METHODS.items():
            got = func(n)
            if got != expect:
                ok = False
                print(f"  n = {n:2d}  {name} 得到 {got}，應為 {expect}  <-- 錯誤")
    if ok:
        print(f"  四種方法在 n = 0 ~ {limit} 的結果都正確\n")
    return ok


def run_benchmark(n):
    """量測 n = 100（或指定值）時各方法的執行時間與函式呼叫次數。"""
    print(f"【執行效率比較：n = {n}】")
    head = (f"  {pad('方法', 22)}{pad('函式呼叫次數', 18, True)}"
            f"{pad('秒數', 14, True)}   結果")
    print(head)
    print("  " + "-" * (width(head) - 2))

    expect = 2 ** n
    for name, func in _METHODS.items():
        # 方法 2a 的遞迴呼叫次數 T(n) = 2^(n+1) - 1
        if name.startswith("方法 2a") and 2 ** (n + 1) - 1 > MAX_MEASURED_CALLS:
            # 例如 n = 100 時要呼叫約 2.5e30 次，真的跑會等到天荒地老，改以外推呈現
            print(f"  {pad(name, 22)}{pad(scientific(2 ** (n + 1) - 1) + ' 次', 18, True)}"
                  f"{pad('（過慢，見下）', 14, True)}   {expect}")
            continue

        seconds = best_time(func, n)
        calls = count_calls(func, n)
        print(f"  {pad(name, 22)}{pad(f'{calls:,} 次', 18, True)}"
              f"{pad(scientific(seconds) + ' s', 14, True)}   {expect}")
    print()


def run_exponential(n, limit=20, check=10):
    """方法 2a：實測它的指數成長，並外推到目標 n 所需的時間。"""
    print(f"【方法 2a 的指數成長】n = 10 ~ {limit}")
    head = f"  {pad('n', 8)}{pad('函式呼叫次數', 20, True)}{pad('秒數', 14, True)}   成長倍數"
    print(head)
    print("  " + "-" * (width(head) - 2))

    prev = None
    for i in range(10, limit + 1, 2):
        start = time.perf_counter()
        power2n_2a(i)
        seconds = time.perf_counter() - start
        ratio = f"{seconds / prev:.2f} x" if prev else "-"
        print(f"  {pad(i, 8)}{pad(f'{2 ** (i + 1) - 1:,} 次', 20, True)}"
              f"{pad(scientific(seconds) + ' s', 14, True)}   {ratio}")
        prev = seconds

    # 呼叫次數公式的驗證：T(n) = 2 * T(n-1) + 1  =>  T(n) = 2^(n+1) - 1
    measured = count_calls(power2n_2a, check)
    print(f"\n  驗證公式 T(n) = 2*T(n-1) + 1 => 2^(n+1) - 1："
          f"n = {check} 時實測 {measured:,} 次，公式算得 {2 ** (check + 1) - 1:,} 次")

    # 用最後一次實測得到「每次呼叫多少時間」，再外推到目標 n
    per_call = prev / (2 ** (limit + 1) - 1)
    calls = 2 ** (n + 1) - 1
    seconds = per_call * calls
    print(f"\n  外推到 n = {n}：需要 {calls:,} 次函式呼叫")
    if seconds < 365.25 * 24 * 3600:
        print(f"  估算時間約 {seconds:.2e} 秒 → 還跑得完，但比其它方法慢太多")
    else:
        print(f"  估算時間約 {seconds / (365.25 * 24 * 3600):.2e} 年 → 根本不可能跑完")
    print()


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_N

    print(f"sys.getrecursionlimit() = {sys.getrecursionlimit()}"
          f"（方法 2b / 方法 3 需要 n + 1 = {n + 1} 層遞迴）\n")

    test_correct()
    run_benchmark(n)
    run_exponential(n)


if __name__ == "__main__":
    main()
