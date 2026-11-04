"""
問題 1：老鼠走迷宮 (DFS)
迷宮符號：S=起點(老鼠)  E=終點(起司)  #=牆  .=路
DFS 使用「堆疊 (stack)」實作，一路走到底、走不通就回溯。
注意：DFS 找到的是「一條」可行路徑，不保證最短。
"""

MAZE = [
    "S.#.......",
    ".##.####.#",
    "....#....#",
    ".####.##.#",
    "....#..#..",
    "###.##.#.#",
    "....#..#..",
    ".####.##.#",
    "......#..E",
]

DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 右、下、左、上


def find(maze, ch):
    for r, row in enumerate(maze):
        if ch in row:
            return r, row.index(ch)


def dfs(maze):
    start, goal = find(maze, "S"), find(maze, "E")
    rows, cols = len(maze), len(maze[0])
    stack = [start]
    parent = {start: None}          # 同時當作 visited 與路徑回溯表

    while stack:
        cur = stack.pop()
        if cur == goal:
            path = []
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            return path[::-1]
        r, c = cur
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            nxt = (nr, nc)
            if (0 <= nr < rows and 0 <= nc < cols
                    and maze[nr][nc] != "#" and nxt not in parent):
                parent[nxt] = cur
                stack.append(nxt)
    return None


def show(maze, path):
    grid = [list(row) for row in maze]
    for r, c in path[1:-1]:
        grid[r][c] = "*"
    print("\n".join("".join(row) for row in grid))


if __name__ == "__main__":
    path = dfs(MAZE)
    if path:
        print(f"找到路徑，共 {len(path) - 1} 步：")
        show(MAZE, path)
        print("座標：", path)
    else:
        print("老鼠無路可走 QQ")
