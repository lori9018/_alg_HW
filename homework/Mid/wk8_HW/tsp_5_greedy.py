"""方法 5：貪婪演算法（最近鄰居法 Nearest Neighbor）
從起點出發，每一步都走向「尚未造訪、距離最近」的城市，最後回到起點。
速度最快，但每一步只看眼前，不保證最佳。
"""
import time
from tsp_data import N_CITIES, DIST, report


def greedy(start=0):
    tour = [start]
    unvisited = set(range(N_CITIES)) - {start}
    while unvisited:
        cur = tour[-1]
        nxt = min(unvisited, key=lambda c: DIST[cur][c])
        tour.append(nxt)
        unvisited.remove(nxt)
    return tour


if __name__ == "__main__":
    t0 = time.perf_counter()
    report("5. 貪婪演算法 (最近鄰居)", greedy(), t0)
