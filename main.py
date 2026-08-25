# -*- coding: utf-8 -*-
"""
main.py —— 一键运行整套数值平衡模拟 Demo

运行方式：
    pip install -r requirements.txt
    python main.py

输出目录：outputs/
  - growth_curves.png          成长曲线图
  - winrate_before_after.png   调优前后胜率对比图
  - gacha_distribution.png     抽卡分布图
  - stats_by_level.csv         等级数值表
  - winrate.csv                胜率明细表
  - gacha_summary.csv          抽卡指标表
  - balance_report.md          调优报告
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from combat import GROWTH, MAX_LEVEL, stat_value  # noqa: E402
from gacha import (BASE_RATE, HARD_PITY, PRICE_PER_PULL,  # noqa: E402
                   SOFT_PITY_START, simulate_first_ssr)
from report import (OUT_DIR, ensure_out, plot_gacha, plot_growth_curves,  # noqa: E402
                    plot_winrate, write_csv, write_report)
from simulator import win_rate  # noqa: E402

# ---------------- 可调参数 ----------------
PLAYER_LEVEL = 50            # 玩家测试等级
ENEMY_LEVELS = list(range(1, 61))   # 敌方关卡等级范围
N_BATTLE = 2000              # 每个关卡等级的模拟场次
ENEMY_HP_SCALE_AFTER = 0.88  # 调优：敌方生命下调 12%
N_GACHA_PLAYERS = 100_000    # 抽卡模拟人数
MONTHLY_FREE_PULLS = 30      # 月免费抽数（用于资源产出测算）
SEED = 2026                  # 随机种子，保证结果可复现


def main():
    ensure_out()
    rng = np.random.default_rng(SEED)

    print("=" * 60)
    print("卡牌养成游戏数值平衡模拟 Demo")
    print("=" * 60)

    # 1) 成长曲线
    print("\n[1/5] 生成成长曲线 ...")
    plot_growth_curves()
    stats_rows = [
        {"等级": lv,
         "生命": round(stat_value("hp", lv), 1),
         "攻击": round(stat_value("atk", lv), 1),
         "防御": round(stat_value("def", lv), 1)}
        for lv in range(1, MAX_LEVEL + 1)
    ]

    # 2) 战斗平衡模拟（调优前）
    print(f"[2/5] 战斗模拟（玩家 {PLAYER_LEVEL} 级 vs 敌方 1-60 级，每档 {N_BATTLE} 场）...")
    before = []
    for elv in ENEMY_LEVELS:
        wr, avg_rounds = win_rate(PLAYER_LEVEL, elv, rng, n=N_BATTLE)
        before.append(wr)
        print(f"  敌方 {elv:>2} 级：胜率 {wr:6.1%}，平均 {avg_rounds:.1f} 回合")

    # 3) 调优后重新模拟
    print(f"[3/5] 调优（敌方生命 -12%）后重新模拟 ...")
    after = []
    for elv in ENEMY_LEVELS:
        wr, _ = win_rate(PLAYER_LEVEL, elv, rng, n=N_BATTLE,
                         enemy_hp_scale=ENEMY_HP_SCALE_AFTER)
        after.append(wr)

    cross_before = next(lv for lv, wr in zip(ENEMY_LEVELS, before) if wr < 0.5)
    cross_after = next(lv for lv, wr in zip(ENEMY_LEVELS, after) if wr < 0.5)
    print(f"\n  调优前 50% 胜率分界：敌方 {cross_before} 级")
    print(f"  调优后 50% 胜率分界：敌方 {cross_after} 级")

    # 4) 抽卡模型
    print(f"[4/5] 抽卡模拟（{N_GACHA_PLAYERS:,} 人）...")
    pulls = simulate_first_ssr(rng, n_players=N_GACHA_PLAYERS)
    print(f"  期望抽数 ≈ {pulls.mean():.2f}，中位数 {np.median(pulls):.0f}，"
          f"90 分位 {np.percentile(pulls, 90):.0f}")

    # 5) 图表、CSV 与报告
    print("[5/5] 生成图表、数值表与调优报告 ...")
    plot_winrate(before, after, ENEMY_LEVELS, cross_before, cross_after)
    plot_gacha(pulls)

    winrate_rows = [
        {"敌方等级": lv, "调优前胜率": round(b, 4), "调优后胜率": round(a, 4)}
        for lv, b, a in zip(ENEMY_LEVELS, before, after)
    ]
    gacha_summary = [
        {"指标": "基础概率", "数值": f"{BASE_RATE:.1%}"},
        {"指标": "软保底起点", "数值": f"第 {SOFT_PITY_START} 抽"},
        {"指标": "硬保底", "数值": f"第 {HARD_PITY} 抽"},
        {"指标": "期望抽数", "数值": f"{pulls.mean():.2f}"},
        {"指标": "中位抽数", "数值": f"{np.median(pulls):.0f}"},
        {"指标": "90分位抽数", "数值": f"{np.percentile(pulls, 90):.0f}"},
        {"指标": "单抽价格(元)", "数值": f"{PRICE_PER_PULL:.0f}"},
        {"指标": "期望花费(元)", "数值": f"{pulls.mean() * PRICE_PER_PULL:.0f}"},
        {"指标": "月免费抽数", "数值": f"{MONTHLY_FREE_PULLS}"},
        {"指标": "月期望SSR", "数值": f"{MONTHLY_FREE_PULLS / pulls.mean():.2f}"},
    ]
    write_csv(stats_rows, winrate_rows, gacha_summary)
    write_report(before, after, ENEMY_LEVELS, cross_before, cross_after,
                 pulls, MONTHLY_FREE_PULLS)

    print(f"\n完成！全部产物已输出到：{os.path.normpath(OUT_DIR)}")
    print("报告见 outputs/balance_report.md")


if __name__ == "__main__":
    main()
