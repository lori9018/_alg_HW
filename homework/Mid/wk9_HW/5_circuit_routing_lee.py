"""
問題 5：IC 電路繞線 (Lee Algorithm / 迷宮繞線法)
這是最簡單、最經典的 maze routing 作法，本質就是 BFS：
  1. 從起點(pin A)一圈一圈向外「波前擴散」，標記距離。
  2. 波前碰到終點(pin B)後，沿著距離遞減的方向回溯，得到最短線路。
  3. 該線路佔用的格子變成障礙，再繞下一條 net（所以線不會交叉短路）。
地圖：#=障礙(Block/Macro)  .=空格  數字/字母=線路
"""
from collections import deque

GRID = [
    "..........",
    "..##......",
    "..##..###.",
    "......#...",
    ".####.#.#.",
    "......#.#.",
    "..........",
]

# (名稱, 起點 pin, 終點 pin)，座標為 (row, col)
NETS = [
    ("A", (0, 0), (0, 9)),
    ("B", (3, 0), (3, 9)),
    ("C", (6, 0), (6, 9)),
]


def lee_route(grid, src, dst):
    rows, cols = len(grid), len(grid[0])
    dist = {src: 0}
    q = deque([src])
    while q:                                    # 第一階段：波前擴散
        r, c = q.popleft()
        if (r, c) == dst:
            break
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and grid[nr][nc] == "." and (nr, nc) not in dist):
                dist[(nr, nc)] = dist[(r, c)] + 1
                q.append((nr, nc))
    if dst not in dist:
        return None
    path, cur = [dst], dst                      # 第二階段：回溯
    while cur != src:
        r, c = cur
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (r + dr, c + dc)
            if dist.get(nb) == dist[cur] - 1:
                cur = nb
                path.append(cur)
                break
    return path[::-1]


def main():
    grid = [list(row) for row in GRID]
    # 先把所有 pin 標上去，避免別條線穿過別人的 pin
    for name, s, t in NETS:
        grid[s[0]][s[1]] = grid[t[0]][t[1]] = name.lower()

    for name, s, t in NETS:
        # 暫時把自己的 pin 當成可走的空格
        grid[s[0]][s[1]] = grid[t[0]][t[1]] = "."
        path = lee_route(grid, s, t)
        if path is None:
            print(f"Net {name}：繞線失敗 (被擋住了)")
            grid[s[0]][s[1]] = grid[t[0]][t[1]] = name.lower()
            continue
        for r, c in path:
            grid[r][c] = name
        print(f"Net {name}：繞線成功，線長 {len(path) - 1}")

    print()
    print("\n".join("".join(row) for row in grid))


if __name__ == "__main__":
    main()
