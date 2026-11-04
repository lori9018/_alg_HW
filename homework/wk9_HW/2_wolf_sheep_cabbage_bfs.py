"""
問題 2：狼、羊、甘藍菜過河 (BFS)
狀態 = (農夫, 狼, 羊, 甘藍菜)，0 = 左岸，1 = 右岸。
規則：船一次只能載農夫 + 最多一樣東西；
      農夫不在時，狼不能和羊同岸、羊不能和甘藍菜同岸。
BFS 保證找到「最少渡河次數」的解。
"""
from collections import deque

NAMES = ["農夫", "狼", "羊", "甘藍菜"]


def is_safe(state):
    f, w, s, c = state
    if w == s and f != w:       # 狼吃羊
        return False
    if s == c and f != s:       # 羊吃菜
        return False
    return True


def next_states(state):
    f = state[0]
    # 農夫自己過河 (i=0)，或帶著與他同岸的某樣東西 (i=1..3)
    for i in range(4):
        if i != 0 and state[i] != f:
            continue
        new = list(state)
        new[0] = 1 - f
        if i != 0:
            new[i] = 1 - f
        new = tuple(new)
        if is_safe(new):
            yield new, ("自己過河" if i == 0 else f"帶{NAMES[i]}過河")


def bfs():
    start, goal = (0, 0, 0, 0), (1, 1, 1, 1)
    queue = deque([start])
    parent = {start: (None, None)}

    while queue:
        cur = queue.popleft()
        if cur == goal:
            steps = []
            while parent[cur][0] is not None:
                prev, action = parent[cur]
                steps.append((action, cur))
                cur = prev
            return steps[::-1]
        for nxt, action in next_states(cur):
            if nxt not in parent:
                parent[nxt] = (cur, action)
                queue.append(nxt)


def describe(state):
    left = [NAMES[i] for i in range(4) if state[i] == 0]
    right = [NAMES[i] for i in range(4) if state[i] == 1]
    return f"左岸:{left or '-'}  |  右岸:{right or '-'}"


if __name__ == "__main__":
    print("初始：", describe((0, 0, 0, 0)))
    for i, (action, state) in enumerate(bfs(), 1):
        print(f"第 {i} 步 {action:<8} -> {describe(state)}")
