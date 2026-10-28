"""方法 4：梯度下降法（彈性網路 Elastic Net）
TSP 是離散問題，無法直接微分，所以先連續化：
在平面上放一個由 M 個節點組成的「彈性環」y_j，對能量函數做梯度下降：
    E = -α K Σ_i ln Σ_j exp(-|x_i - y_j|² / 2K²)  +  (β/2) Σ_j |y_{j+1} - y_j|²
 - 第一項：把環往城市拉（梯度 = 城市對節點的吸引力）
 - 第二項：讓環保持平滑、縮短（梯度 = 拉普拉斯項）
K 逐步縮小，環會逐漸貼合所有城市；最後依每個城市最近的節點順序解碼成路徑。
"""
import time
import numpy as np
from tsp_data import CITIES, N_CITIES, ALGO_SEED, report

ALPHA, BETA = 0.2, 2.0
K_START, K_END, K_DECAY, DECAY_EVERY = 0.2, 0.01, 0.99, 25
LR = 1.0


def elastic_net():
    rng = np.random.default_rng(ALGO_SEED)
    X = np.array(CITIES, dtype=float)
    lo, hi = X.min(0), X.max(0)
    X = (X - lo) / (hi - lo).max()                      # 正規化到 [0,1]

    M = 3 * N_CITIES                                    # 環上節點數
    theta = np.linspace(0, 2 * np.pi, M, endpoint=False)
    center = X.mean(0)
    Y = center + 0.1 * np.c_[np.cos(theta), np.sin(theta)]
    Y += rng.normal(0, 1e-3, Y.shape)

    K, it = K_START, 0
    while K > K_END:
        d2 = ((X[:, None, :] - Y[None, :, :]) ** 2).sum(-1)       # (N, M)
        w = np.exp(-(d2 - d2.min(1, keepdims=True)) / (2 * K * K))
        w /= w.sum(1, keepdims=True)                              # softmax 權重
        pull = (w[:, :, None] * (X[:, None, :] - Y[None, :, :])).sum(0)
        smooth = np.roll(Y, -1, 0) - 2 * Y + np.roll(Y, 1, 0)
        Y += LR * (ALPHA * pull + BETA * K * smooth)              # 梯度下降一步
        it += 1
        if it % DECAY_EVERY == 0:
            K *= K_DECAY

    # 解碼：每個城市找最近節點，依節點位置排序
    d2 = ((X[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
    pos = d2.argmin(1)
    return sorted(range(N_CITIES), key=lambda i: (pos[i], d2[i, pos[i]]))


if __name__ == "__main__":
    t0 = time.perf_counter()
    report("4. 梯度下降法 (彈性網路)", elastic_net(), t0)
