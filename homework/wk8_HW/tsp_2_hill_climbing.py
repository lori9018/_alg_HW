"""方法 2：爬山演算法 (Hill Climbing)
隨機產生初始路徑 -> 隨機交換兩個城市 -> 只接受「更短」的結果。
因為只會往上爬，容易卡在區域最佳解，所以加上多次隨機重啟取最佳。
"""
import random
import time
from tsp_data import N_CITIES, ALGO_SEED, tour_length, report

RESTARTS = 10
MAX_ITER = 20000


def hill_climbing(rng):
    tour = list(range(N_CITIES))
    rng.shuffle(tour)
    best_len = tour_length(tour)
    for _ in range(MAX_ITER):
        i, j = rng.sample(range(N_CITIES), 2)
        tour[i], tour[j] = tour[j], tour[i]          # 鄰近解：交換兩城市
        new_len = tour_length(tour)
        if new_len < best_len:                       # 只接受更好的
            best_len = new_len
        else:
            tour[i], tour[j] = tour[j], tour[i]      # 還原
    return tour, best_len


if __name__ == "__main__":
    t0 = time.perf_counter()
    rng = random.Random(ALGO_SEED)
    best, best_len = None, float("inf")
    for _ in range(RESTARTS):
        t, l = hill_climbing(rng)
        if l < best_len:
            best, best_len = t[:], l
    report("2. 爬山演算法", best, t0)
