"""方法 3：模擬退火法 (Simulated Annealing)
鄰近解：隨機 2-opt（反轉一段路徑）。
較差的解也有機率 exp(-Δ/T) 被接受，溫度 T 逐漸下降，可跳出區域最佳解。
"""
import math
import random
import time
from tsp_data import N_CITIES, ALGO_SEED, tour_length, report

T_START = 100.0
T_END = 1e-3
COOLING = 0.995
ITER_PER_T = 100


def simulated_annealing(rng):
    cur = list(range(N_CITIES))
    rng.shuffle(cur)
    cur_len = tour_length(cur)
    best, best_len = cur[:], cur_len
    T = T_START
    while T > T_END:
        for _ in range(ITER_PER_T):
            i, j = sorted(rng.sample(range(N_CITIES), 2))
            new = cur[:i] + cur[i:j + 1][::-1] + cur[j + 1:]
            new_len = tour_length(new)
            delta = new_len - cur_len
            if delta < 0 or rng.random() < math.exp(-delta / T):
                cur, cur_len = new, new_len
                if cur_len < best_len:
                    best, best_len = cur[:], cur_len
        T *= COOLING
    return best


if __name__ == "__main__":
    t0 = time.perf_counter()
    result = simulated_annealing(random.Random(ALGO_SEED))
    report("3. 模擬退火法", result, t0)
