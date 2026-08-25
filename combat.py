# -*- coding: utf-8 -*-
"""
combat.py —— 角色成长曲线 + 战斗公式（数值框架的"地基"）

本文件包含：
1) stat_value()   根据等级计算单项属性（线性 + 二次的成长曲线）
2) unit_stats()   得到某个等级角色的完整属性面板
3) damage()       伤害公式：经典"防御减伤"模型 + 暴击
4) battle()       1v1 回合制战斗，含回合上限判定

你可以像搭积木一样修改这里的公式和系数，
然后重新运行 main.py，观察平衡模拟结果如何变化。
"""

# 1 级基础属性
BASE_STATS = {
    "hp": 120.0,          # 生命
    "atk": 22.0,          # 攻击
    "def": 12.0,          # 防御
    "crit_rate": 0.05,    # 基础暴击率 5%
    "crit_mult": 1.5,     # 暴击伤害 150%
}

# 成长系数：stat(lv) = base + a * lv + b * lv^2
# 二次项 b 控制"后期成长加速度"，b 越大，高等级收益越高
GROWTH = {
    "hp": (16.0, 0.15),
    "atk": (2.8, 0.025),
    "def": (1.4, 0.012),
}

MAX_LEVEL = 80    # 满级
MAX_ROUNDS = 60   # 战斗回合上限


def stat_value(key: str, level: int) -> float:
    """根据等级计算属性值（成长曲线）。"""
    a, b = GROWTH[key]
    return BASE_STATS[key] + a * level + b * level * level


def unit_stats(level: int, hp_scale: float = 1.0) -> dict:
    """返回某个等级角色的完整属性面板。

    hp_scale 用于平衡对比：例如敌方生命成长下调 12% 时传入 0.88。
    """
    stats = {
        "hp": stat_value("hp", level),
        "atk": stat_value("atk", level),
        "def": stat_value("def", level),
        "crit_rate": BASE_STATS["crit_rate"],
        "crit_mult": BASE_STATS["crit_mult"],
    }
    stats["hp"] *= hp_scale
    return stats


def damage(atk: float, defense: float, crit_rate: float,
           crit_mult: float, rng) -> float:
    """伤害公式：基础伤害 = 攻击力 * 100 / (100 + 防御力)。

    防御越高减伤越多，但收益递减（这是很多游戏采用的形式）；
    暴击按概率触发 crit_mult 倍伤害，保底 1 点伤害。
    """
    base_damage = atk * 100.0 / (100.0 + defense)
    if rng.random() < crit_rate:
        base_damage *= crit_mult
    return max(1.0, base_damage)


def battle(player: dict, enemy: dict, rng, max_rounds: int = MAX_ROUNDS):
    """1v1 回合制战斗，玩家先手。

    返回 (winner, rounds)，winner 为 'player' / 'enemy' / 'draw'。
    达到回合上限时按双方剩余血量比例判定胜负（模拟"回合数封顶"规则）。
    """
    p_hp = player["hp"]
    e_hp = enemy["hp"]
    for r in range(1, max_rounds + 1):
        # 玩家回合
        e_hp -= damage(player["atk"], enemy["def"],
                       player["crit_rate"], player["crit_mult"], rng)
        if e_hp <= 0:
            return "player", r
        # 敌方回合
        p_hp -= damage(enemy["atk"], player["def"],
                       enemy["crit_rate"], enemy["crit_mult"], rng)
        if p_hp <= 0:
            return "enemy", r
    # 回合上限判定：血量比例更高的一方获胜
    if p_hp / player["hp"] >= e_hp / enemy["hp"]:
        return "player", max_rounds
    return "enemy", max_rounds
