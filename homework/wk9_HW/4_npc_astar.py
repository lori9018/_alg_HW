"""
問題 4：NPC 搜尋玩家 (A*)
f(n) = g(n) + h(n)
  g = 從 NPC 走到 n 的實際步數
  h = 到玩家的曼哈頓距離（四方向移動時不會高估，所以 A* 保證最短）
Part 1：單次尋路；Part 2：玩家移動，NPC 每回合重新規劃，直到抓到玩家。
"""
import heapq

MAP = [
    "..........",
    ".####.###.",
    ".#..#...#.",
    ".#.##.#.#.",
    ".#....#...",
    ".####.###.",
    "..........",
]
ROWS, COLS = len(MAP), len(MAP[0])


def h(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal):
    open_heap = [(h(start, goal), 0, start)]    # (f, g, 位置)
    came_from = {start: None}
    g_cost = {start: 0}

    while open_heap:
        _, g, cur = heapq.heappop(open_heap)
        if cur == goal:
            path = []
            while cur is not None:
                path.append(cur)
                cur = came_from[cur]
            return path[::-1]
        if g > g_cost[cur]:                      # 過期的舊紀錄
            continue
        r, c = cur
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and MAP[nr][nc] != "#":
                ng = g + 1
                if ng < g_cost.get((nr, nc), float("inf")):
                    g_cost[(nr, nc)] = ng
                    came_from[(nr, nc)] = cur
                    heapq.heappush(open_heap, (ng + h((nr, nc), goal), ng, (nr, nc)))
    return None


def draw(npc, player, path=()):
    grid = [list(row) for row in MAP]
    for r, c in path:
        grid[r][c] = "*"
    grid[npc[0]][npc[1]] = "N"
    grid[player[0]][player[1]] = "P"
    print("\n".join("".join(row) for row in grid))


if __name__ == "__main__":
    npc, player = (0, 0), (4, 5)

    print("=== Part 1：單次尋路 ===")
    path = astar(npc, player)
    draw(npc, player, path[1:-1])
    print(f"最短路徑 {len(path) - 1} 步\n")

    print("=== Part 2：追逐模擬（玩家沿固定路線逃跑）===")
    escape = [(5, 5), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9)]
    turn = 0
    for nxt in escape:
        turn += 1
        player = nxt                                # 玩家先移動
        npc = astar(npc, player)[1]                 # NPC 重新規劃、走一步
        print(f"-- 回合 {turn} --")
        draw(npc, player)
        if npc == player:
            print("NPC 抓到玩家了！")
            break
    else:
        print("玩家逃掉了～")
