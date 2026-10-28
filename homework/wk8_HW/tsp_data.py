"""共用測試資料：五個演算法都從這裡讀取同一組城市座標。"""
import math
import random
import time

N_CITIES = 20
DATA_SEED = 42      # 固定種子 -> 每次城市座標都一樣
ALGO_SEED = 2024    # 演算法內部隨機數種子


def _generate():
    rng = random.Random(DATA_SEED)
    return [(round(rng.uniform(0, 100), 2), round(rng.uniform(0, 100), 2))
            for _ in range(N_CITIES)]


CITIES = _generate()


def dist(a, b):
    """城市 a、b 的歐式距離"""
    (x1, y1), (x2, y2) = CITIES[a], CITIES[b]
    return math.hypot(x1 - x2, y1 - y2)


DIST = [[dist(i, j) for j in range(N_CITIES)] for i in range(N_CITIES)]


def tour_length(tour):
    """封閉路徑總長（含回到起點）"""
    return sum(DIST[tour[i]][tour[(i + 1) % len(tour)]] for i in range(len(tour)))


def report(name, tour, start_time):
    elapsed = time.perf_counter() - start_time
    assert sorted(tour) == list(range(N_CITIES)), "路徑必須恰好經過每個城市一次"
    print(f"=== {name} ===")
    print("路徑  :", " -> ".join(map(str, tour)), "->", tour[0])
    print(f"總長度: {tour_length(tour):.3f}")
    print(f"耗時  : {elapsed * 1000:.1f} ms")
