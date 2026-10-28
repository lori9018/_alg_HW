"""方法 1：改良法（2-opt 路徑改良）
先用任意方式建立一條可行路徑，再反覆「拆掉兩條邊、反轉中間路段重新接上」，
只要總長變短就接受，直到任何 2-opt 交換都無法再改善為止。
"""
import time
from tsp_data import N_CITIES, DIST, report


def initial_tour():
    return list(range(N_CITIES))        # 最簡單的初始解：依編號順序


def two_opt(tour):
    n = len(tour)
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                a, b = tour[i], tour[i + 1]
                c, d = tour[j], tour[(j + 1) % n]
                # 原本的邊 (a,b)+(c,d) 與換成 (a,c)+(b,d) 比較
                delta = DIST[a][c] + DIST[b][d] - DIST[a][b] - DIST[c][d]
                if delta < -1e-12:
                    tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                    improved = True
    return tour


if __name__ == "__main__":
    t0 = time.perf_counter()
    result = two_opt(initial_tour())
    report("1. 改良法 (2-opt)", result, t0)
