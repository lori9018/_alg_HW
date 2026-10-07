"""河內塔 (Tower of Hanoi) - 非迴圈（迭代）版本

規則與遞迴版相同：
1. 一次只能移動一個圓盤。
2. 每次只能移動最上面的圓盤。
3. 大圓盤不能放在小圓盤上面。

這裡提供兩種不使用遞迴的解法：
- hanoi_by_rule()  : 經典迭代規則（最小圓盤循環 + 另一個合法移動）
- hanoi_by_stack() : 用顯式堆疊 (stack) 模擬遞迴的呼叫過程
兩者產生的移動步驟完全相同，最少移動次數皆為 2^n - 1。
"""

import argparse
import os
import sys

# 讓 Windows 主控台也能正確顯示中文
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 重用遞迴版已寫好的畫圖函式
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hanoi import draw_pegs  # noqa: E402


def hanoi_by_rule(n, source="A", auxiliary="B", target="C"):
    """經典迭代規則解河內塔（不使用遞迴）。

    觀察：
      - 奇數步：移動最小的圓盤 (圓盤 1)。
        奇數個圓盤時，最小圓盤依 source -> target -> auxiliary -> source 循環；
        偶數個圓盤時，依 source -> auxiliary -> target -> source 循環。
      - 偶數步：移動「不含最小圓盤的另外兩根柱子」之間唯一合法的移動。

    回傳：移動步驟 list，每個元素為 (圓盤編號, 從, 到)。
    """
    moves = []
    if n <= 0:
        return moves

    # 三根柱子目前的內容，list 尾端是「最上面的圓盤」
    pegs = {source: list(range(n, 0, -1)), auxiliary: [], target: []}

    # 最小圓盤的循環順序
    if n % 2 == 1:
        order = [source, target, auxiliary]   # A -> C -> B -> A
    else:
        order = [source, auxiliary, target]   # A -> B -> C -> A

    total = 2 ** n - 1
    idx = 0
    for step in range(1, total + 1):
        if step % 2 == 1:
            # 移動最小的圓盤
            src = order[idx]
            dst = order[(idx + 1) % 3]
            idx = (idx + 1) % 3

            disk = pegs[src].pop()
            pegs[dst].append(disk)
            moves.append((disk, src, dst))
        else:
            # 移動另外兩根柱子之間唯一合法的圓盤
            # 先找出「沒有最小圓盤」的那兩根柱子
            others = [p for p in (source, auxiliary, target)
                      if not pegs[p] or pegs[p][-1] != 1]

            # 兩根柱子中，至少一根非空；把非空那根的頂端搬到另一根
            p1, p2 = others
            top1 = pegs[p1][-1] if pegs[p1] else None
            top2 = pegs[p2][-1] if pegs[p2] else None

            if top1 is None:            # p1 空 -> 從 p2 搬到 p1
                move_from, move_to = p2, p1
            elif top2 is None:          # p2 空 -> 從 p1 搬到 p2
                move_from, move_to = p1, p2
            elif top1 < top2:           # 兩根都非空 -> 小的搬到大的
                move_from, move_to = p1, p2
            else:
                move_from, move_to = p2, p1

            disk = pegs[move_from].pop()
            pegs[move_to].append(disk)
            moves.append((disk, move_from, move_to))

    return moves


def hanoi_by_stack(n, source="A", auxiliary="B", target="C"):
    """用顯式堆疊模擬遞迴，產生移動步驟（不使用遞迴）。

    每個堆疊框 (frame) 記錄：剩餘圓盤數、來源、輔助、目標、狀態。
      state = 0：還沒處理第一段遞迴
      state = 1：第一段完成，接著要移動最大圓盤，再處理第二段
    """
    moves = []
    if n <= 0:
        return moves

    # (n, source, auxiliary, target, state)
    stack = [(n, source, auxiliary, target, 0)]

    while stack:
        num, src, aux, dst, state = stack.pop()

        if state == 0:
            if num == 1:
                moves.append((1, src, dst))
            else:
                # 先擱置本框，等第一段做完再回來
                stack.append((num, src, aux, dst, 1))
                # 第一段：把 n-1 個從 src 移到 aux（用 dst 當輔助）
                stack.append((num - 1, src, dst, aux, 0))
        else:  # state == 1
            # 移動最大的圓盤
            moves.append((num, src, dst))
            # 第二段：把 n-1 個從 aux 移到 dst（用 src 當輔助）
            stack.append((num - 1, aux, src, dst, 0))

    return moves


def solve_and_print(n, algorithm="rule", show_board=False):
    """解題並印出結果。"""
    if algorithm == "rule":
        moves = hanoi_by_rule(n)
        name = "經典迭代規則法"
    else:
        moves = hanoi_by_stack(n)
        name = "堆疊模擬法"

    print(f"解法: {name}")
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
    parser = argparse.ArgumentParser(description="河內塔 (Tower of Hanoi) 非迴圈（迭代）解法")
    parser.add_argument("n", nargs="?", type=int, default=3, help="圓盤數量 (預設 3)")
    parser.add_argument("-a", "--algorithm", choices=["rule", "stack"], default="rule",
                        help="迭代演算法：rule=經典規則法(預設), stack=堆疊模擬法")
    parser.add_argument("-b", "--board", action="store_true", help="顯示每步的圖形狀態")
    parser.add_argument("-c", "--compare", action="store_true", help="比較兩種迭代解法的結果是否一致")
    parser.add_argument("-q", "--quiet", action="store_true", help="只顯示移動總次數")
    args = parser.parse_args()

    if args.n < 1:
        parser.error("圓盤數量必須大於等於 1")

    if args.compare:
        m1 = hanoi_by_rule(args.n)
        m2 = hanoi_by_stack(args.n)
        print(f"圓盤數量: {args.n}")
        print(f"規則法移動次數: {len(m1)}")
        print(f"堆疊法移動次數: {len(m2)}")
        print(f"兩者結果一致: {m1 == m2}")
    elif args.quiet:
        moves = hanoi_by_rule(args.n) if args.algorithm == "rule" else hanoi_by_stack(args.n)
        print(f"n={args.n} 的移動次數: {len(moves)}")
    else:
        solve_and_print(args.n, algorithm=args.algorithm, show_board=args.board)


if __name__ == "__main__":
    main()
