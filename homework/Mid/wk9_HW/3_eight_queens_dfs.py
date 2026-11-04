"""
問題 3：八皇后 (DFS / Backtracking)
一列一列放皇后（深度 = 列數），用三個集合快速檢查衝突：
  欄 col、主對角線 (r-c)、副對角線 (r+c)。
放不下就回溯。共 92 組解。
"""
N = 8


def solve(n=N):
    solutions = []
    cols, diag1, diag2 = set(), set(), set()
    board = []                      # board[r] = 第 r 列皇后所在的欄

    def dfs(r):
        if r == n:
            solutions.append(board[:])
            return
        for c in range(n):
            if c in cols or (r - c) in diag1 or (r + c) in diag2:
                continue
            cols.add(c); diag1.add(r - c); diag2.add(r + c); board.append(c)
            dfs(r + 1)
            board.pop(); cols.remove(c); diag1.remove(r - c); diag2.remove(r + c)

    dfs(0)
    return solutions


def show(sol):
    for c in sol:
        print(" ".join("Q" if i == c else "." for i in range(len(sol))))


if __name__ == "__main__":
    sols = solve()
    print(f"{N} 皇后共有 {len(sols)} 組解\n")
    print("第 1 組解：")
    show(sols[0])
    print("\n欄位表示：", sols[0])
