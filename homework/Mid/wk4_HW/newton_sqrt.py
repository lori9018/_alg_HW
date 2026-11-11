"""
迭代法範例：用牛頓法（Newton's Method）計算平方根

問題：求 sqrt(a)，也就是找 x 使得 x * x = a

迭代公式：x_next = (x + a / x) / 2
意思：每次用「目前的猜測 x」和「a / x」的平均值，當作更好的猜測。
"""


def newton_sqrt(a, tolerance=1e-10, max_iter=100):
    """用迭代法求 a 的平方根，並印出每一步的過程。"""
    if a < 0:
        raise ValueError("不能對負數開平方根")
    if a == 0:
        return 0.0

    x = a / 2 if a > 1 else 1.0  # 1. 初始猜測值（隨便猜一個正數）

    print(f"求 sqrt({a})")
    print(f"{'次數':>4} | {'目前的猜測 x':>18} | {'誤差 |x*x - a|':>16}")
    print("-" * 48)

    for i in range(1, max_iter + 1):
        x_next = (x + a / x) / 2   # 2. 套用迭代公式，得到更好的猜測
        error = abs(x_next * x_next - a)
        print(f"{i:>4} | {x_next:>18.12f} | {error:>16.3e}")

        if abs(x_next - x) < tolerance:  # 3. 兩次結果差距很小 → 收斂，停止
            return x_next
        x = x_next                       # 4. 用新的猜測繼續下一輪

    print("警告：超過最大迭代次數，尚未收斂")
    return x


if __name__ == "__main__":
    result = newton_sqrt(2)
    print("-" * 48)
    print(f"迭代結果：{result:.12f}")
    print(f"內建 math.sqrt：{2 ** 0.5:.12f}")
