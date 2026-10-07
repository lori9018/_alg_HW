"""河內塔 (Tower of Hanoi)

規則：
1. 一次只能移動一個圓盤。
2. 每次只能移動最上面的圓盤。
3. 大圓盤不能放在小圓盤上面。

使用遞迴解法，將 n 個圓盤從來源柱 (A) 經由輔助柱 (B) 移動到目標柱 (C)。
最少移動次數為 2^n - 1。
"""

import argparse
import sys

# 讓 Windows 主控台也能正確顯示中文
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def hanoi(n, source="A", auxiliary="B", target="C", moves=None):
    """遞迴解河內塔。

    參數：
        n         : 圓盤數量
        source    : 來源柱
        auxiliary : 輔助柱
        target    : 目標柱
        moves     : 用來累積移動步驟的 list（可選）

    回傳：
        移動步驟的 list，每個元素為 (圓盤編號, 從, 到)。
    """
    if moves is None:
        moves = []

    if n == 1:
        # 基本情況：只有一個圓盤，直接搬到目標柱
        moves.append((1, source, target))
        return moves

    # 1. 把上面 n-1 個圓盤從 source 移到 auxiliary（目標柱當輔助）
    hanoi(n - 1, source, target, auxiliary, moves)
    # 2. 把最大的第 n 個圓盤從 source 移到 target
    moves.append((n, source, target))
    # 3. 把 n-1 個圓盤從 auxiliary 移到 target（來源柱當輔助）
    hanoi(n - 1, auxiliary, source, target, moves)

    return moves


def draw_pegs(pegs, n, width=None):
    """把三根柱子的目前狀態畫成文字圖。"""
    if width is None:
        width = n  # 最大圓盤寬度

    lines = []
    for level in range(n - 1, -1, -1):
        row = []
        for peg in ("A", "B", "C"):
            disks = pegs[peg]
            if level < len(disks):
                size = disks[level]
                row.append(("=" * size).center(width * 2 + 1))
            else:
                row.append(" " * (width * 2 + 1))
        lines.append("|".join(row))
    lines.append("---".join("-" * (width * 2 + 1) for _ in range(3)))
    lines.append("   ".join(peg.center(width * 2 + 1) for peg in ("A", "B", "C")))
    return "\n".join(lines)


def solve_and_print(n, show_steps=True, show_board=False):
    """解題並印出結果。"""
    moves = hanoi(n)

    print(f"圓盤數量: {n}")
    print(f"最少移動次數: {2 ** n - 1}")
    print(f"實際移動次數: {len(moves)}")
    print()

    if show_board:
        pegs = {"A": list(range(n, 0, -1)), "B": [], "C": []}
        print("初始狀態：")
        print(draw_pegs(pegs, n))
        print()

    for i, (disk, src, dst) in enumerate(moves, start=1):
        print(f"步驟 {i:>3}: 將圓盤 {disk} 從 {src} 移到 {dst}")

        if show_board:
            pegs[src].pop()
            pegs[dst].append(disk)
            print(draw_pegs(pegs, n))
            print()

    print(f"\n完成！總共移動 {len(moves)} 次。")


def main():
    parser = argparse.ArgumentParser(description="河內塔 (Tower of Hanoi) 遞迴解法")
    parser.add_argument("n", nargs="?", type=int, default=3, help="圓盤數量 (預設 3)")
    parser.add_argument("-q", "--quiet", action="store_true", help="只顯示移動總次數")
    parser.add_argument("-b", "--board", action="store_true", help="顯示每步的圖形狀態")
    args = parser.parse_args()

    if args.n < 1:
        parser.error("圓盤數量必須大於等於 1")

    if args.quiet:
        moves = hanoi(args.n)
        print(f"n={args.n} 的移動次數: {len(moves)}")
    else:
        solve_and_print(args.n, show_board=args.board)


if __name__ == "__main__":
    main()
