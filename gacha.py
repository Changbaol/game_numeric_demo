# -*- coding: utf-8 -*-
"""
gacha.py —— 抽卡概率与保底模型

模拟常见手游抽卡：基础概率 0.6%，第 74 抽起概率递增（软保底），
第 90 抽必出（硬保底）。提供：
1) pity_rate()               第 n 抽的即时出货概率
2) survival_prob(k)          前 k 抽都不出货的概率（解析计算）
3) expected_pulls_analytic() 解析期望抽数
4) simulate_first_ssr()      蒙特卡洛模拟"抽到第一个 SSR"的抽数分布
"""

import numpy as np

BASE_RATE = 0.006        # 基础概率 0.6%
SOFT_PITY_START = 74     # 第 74 抽开始概率提升
HARD_PITY = 90           # 第 90 抽必出
PRICE_PER_PULL = 6.0     # 单抽价格（元），用于估算期望花费


def pity_rate(pull_number: int) -> float:
    """第 n 抽的出货概率（n 从 1 开始）。"""
    if pull_number >= HARD_PITY:
        return 1.0
    if pull_number < SOFT_PITY_START:
        return BASE_RATE
    # 软保底区间：概率从 0.6% 线性提升到第 90 抽的 100%
    step = (1.0 - BASE_RATE) / (HARD_PITY - SOFT_PITY_START)
    return BASE_RATE + step * (pull_number - SOFT_PITY_START + 1)


def survival_prob(k: int) -> float:
    """前 k 抽都未出货的概率（k 从 0 开始，解析解）。"""
    p = 1.0
    for n in range(1, k + 1):
        p *= 1.0 - pity_rate(n)
    return p


def expected_pulls_analytic() -> float:
    """期望抽数 E[T] = sum_{k=0}^{HARD_PITY-1} P(T > k)。"""
    return sum(survival_prob(k) for k in range(HARD_PITY))


def simulate_first_ssr(rng, n_players: int = 100_000) -> np.ndarray:
    """蒙特卡洛模拟：每个玩家抽到第一个 SSR 需要的抽数。"""
    results = np.empty(n_players, dtype=int)
    for i in range(n_players):
        pulls = 0
        while True:
            pulls += 1
            if rng.random() < pity_rate(pulls):
                break
        results[i] = pulls
    return results
