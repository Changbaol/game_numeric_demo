# -*- coding: utf-8 -*-
"""
simulator.py —— Monte Carlo 战斗模拟器

核心思想：把同一场战斗重复模拟 N 次，用"胜率、平均回合数"这类统计量
来判断数值是否平衡。这是游戏数值工作里最常用的验证手段：
    胜率接近 50% → 势均力敌；胜率 80%+ → 玩家碾压；胜率 20%- → 难度过高。
"""

from combat import battle, unit_stats


def win_rate(player_level: int, enemy_level: int, rng,
             n: int = 2000, enemy_hp_scale: float = 1.0):
    """模拟 N 场玩家 vs 敌方战斗，返回 (胜率, 平均回合数)。"""
    player = unit_stats(player_level)
    enemy = unit_stats(enemy_level, hp_scale=enemy_hp_scale)

    wins = 0
    total_rounds = 0
    for _ in range(n):
        winner, rounds = battle(player, enemy, rng)
        total_rounds += rounds
        if winner == "player":
            wins += 1
        # draw（理论较少）按失败处理，保证胜率统计保守
    return wins / n, total_rounds / n
