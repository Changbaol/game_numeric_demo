# -*- coding: utf-8 -*-
"""
report.py —— 图表、CSV 与调优报告生成
"""

import os

import matplotlib
matplotlib.use("Agg")  # 无窗口环境渲染
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from combat import GROWTH, MAX_LEVEL, MAX_ROUNDS, stat_value
from gacha import (BASE_RATE, HARD_PITY, PRICE_PER_PULL,
                   SOFT_PITY_START, expected_pulls_analytic)

# 中文字体设置（Windows 使用微软雅黑，Linux/macOS 会自动回退）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")


def ensure_out():
    os.makedirs(OUT_DIR, exist_ok=True)


def plot_growth_curves():
    """图1：角色成长曲线（等级 1-80）。"""
    levels = np.arange(1, MAX_LEVEL + 1)
    hp = [stat_value("hp", l) for l in levels]
    atk = [stat_value("atk", l) for l in levels]
    defense = [stat_value("def", l) for l in levels]

    fig, ax1 = plt.subplots(figsize=(9, 4.8))
    ax1.plot(levels, hp, color="#d62728", linewidth=2, label="生命 HP")
    ax1.set_xlabel("等级")
    ax1.set_ylabel("生命", color="#d62728")
    ax1.tick_params(axis="y", labelcolor="#d62728")

    ax2 = ax1.twinx()
    ax2.plot(levels, atk, color="#1f77b4", linewidth=2, label="攻击 ATK")
    ax2.plot(levels, defense, color="#2ca02c", linewidth=2, label="防御 DEF")
    ax2.set_ylabel("攻击 / 防御")

    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [l.get_label() for l in lines], loc="upper left")
    ax1.set_title("角色成长曲线（等级 1-80）")
    ax1.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "growth_curves.png"), dpi=150)
    plt.close(fig)


def plot_winrate(before: list, after: list, enemy_levels: list,
                 cross_before: int, cross_after: int):
    """图2：调优前后胜率对比（玩家 50 级 vs 关卡敌人 1-60 级）。"""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(enemy_levels, before, "o-", color="#d62728", linewidth=2,
            markersize=3, label="调优前")
    ax.plot(enemy_levels, after, "s-", color="#1f77b4", linewidth=2,
            markersize=3, label="调优后（敌方生命 -12%）")
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=1, label="50% 胜率线")
    ax.axvline(cross_before, color="#d62728", linestyle=":", alpha=0.7)
    ax.axvline(cross_after, color="#1f77b4", linestyle=":", alpha=0.7)
    ax.annotate(f"调优前 50% 分界: 敌方 {cross_before} 级",
                xy=(cross_before, 0.5), xytext=(cross_before - 12, 0.72),
                color="#d62728", arrowprops=dict(arrowstyle="->", color="#d62728"))
    ax.annotate(f"调优后 50% 分界: 敌方 {cross_after} 级",
                xy=(cross_after, 0.5), xytext=(cross_after - 8, 0.26),
                color="#1f77b4", arrowprops=dict(arrowstyle="->", color="#1f77b4"))
    ax.set_xlabel("敌方关卡等级")
    ax.set_ylabel("玩家胜率")
    ax.set_title("关卡难度曲线：调优前后对比（每档 2000 场模拟）")
    ax.legend(loc="center right")
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "winrate_before_after.png"), dpi=150)
    plt.close(fig)


def plot_gacha(pulls: np.ndarray):
    """图3：首个 SSR 抽数分布（直方图 + 累积概率 + 期望线）。"""
    fig, ax1 = plt.subplots(figsize=(9, 5))
    bins = np.arange(1, HARD_PITY + 2) - 0.5
    ax1.hist(pulls, bins=bins, color="#1f77b4", alpha=0.75,
             label="玩家分布（10 万人）")
    ax1.set_xlabel("抽数（第几个十连抽出 SSR）")
    ax1.set_ylabel("人数", color="#1f77b4")

    mean_pulls = float(pulls.mean())
    ax2 = ax1.twinx()
    cum = np.cumsum(np.bincount(pulls, minlength=HARD_PITY + 1)) / len(pulls)
    ax2.plot(np.arange(1, HARD_PITY + 1), cum[:HARD_PITY],
             color="#d62728", linewidth=2, label="累积出货概率")
    ax2.set_ylabel("累积出货概率")
    ax2.set_ylim(0, 1.05)

    ax1.axvline(mean_pulls, color="#2ca02c", linestyle="--",
                label=f"期望抽数 ≈ {mean_pulls:.1f}")
    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [l.get_label() for l in lines], loc="center right")
    ax1.set_title("抽卡模型：首个 SSR 抽数分布（基础 0.6%，74 抽软保底，90 抽硬保底）")
    ax1.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "gacha_distribution.png"), dpi=150)
    plt.close(fig)


def write_csv(stats_rows, winrate_rows, gacha_summary):
    """输出数值表 CSV，便于在 Excel 里继续分析。"""
    ensure_out()
    pd.DataFrame(stats_rows).to_csv(
        os.path.join(OUT_DIR, "stats_by_level.csv"),
        index=False, encoding="utf-8-sig")
    pd.DataFrame(winrate_rows).to_csv(
        os.path.join(OUT_DIR, "winrate.csv"),
        index=False, encoding="utf-8-sig")
    pd.DataFrame(gacha_summary).to_csv(
        os.path.join(OUT_DIR, "gacha_summary.csv"),
        index=False, encoding="utf-8-sig")


def write_report(before, after, enemy_levels, cross_before, cross_after,
                 pulls, monthly_free_pulls):
    """生成 Markdown 调优报告。"""
    ensure_out()
    mean_pulls = float(pulls.mean())
    median_pulls = float(np.median(pulls))
    p90 = float(np.percentile(pulls, 90))
    analytic = expected_pulls_analytic()
    expected_cost = mean_pulls * PRICE_PER_PULL
    ssr_per_month = monthly_free_pulls / mean_pulls

    # 关键对比点：同级（50）、高 1 级（51）、高 2 级（52）的胜率
    idx_50 = list(enemy_levels).index(50)
    idx_51 = list(enemy_levels).index(51)
    idx_52 = list(enemy_levels).index(52)
    wr_before_50, wr_before_51, wr_before_52 = before[idx_50], before[idx_51], before[idx_52]
    wr_after_51, wr_after_52 = after[idx_51], after[idx_52]

    lines = [
        "# 卡牌养成游戏数值平衡调优报告",
        "",
        "## 一、数值框架",
        f"- 成长曲线：stat(lv) = base + a*lv + b*lv²，满级 {MAX_LEVEL} 级",
        f"  - HP：base=120，a=16.0，b=0.15",
        f"  - ATK：base=22，a=2.8，b=0.025",
        f"  - DEF：base=12，a=1.4，b=0.012",
        f"- 伤害公式：damage = atk × 100 / (100 + def)，暴击率 5%、暴伤 150%",
        f"- 战斗规则：1v1 回合制，玩家先手，回合上限 {MAX_ROUNDS}，超时按剩余血量比例判定",
        "",
        "## 二、平衡验证（玩家 50 级 vs 关卡敌人 1-60 级）",
        f"- 模拟规模：每档敌方等级独立模拟 2000 场战斗",
        f"- 调优前：敌方与玩家同级（50 级）时胜率 {wr_before_50:.0%}，"
        f"仅高出 1 级（51 级）即骤降至 **{wr_before_51:.0%}**，难度出现悬崖式断层",
        "- 问题：胜负对 1 级差距过于敏感——玩家战力小幅成长却带来体验剧变，"
        "中期挫败感强，玩家容易流失",
        "",
        "## 三、调优方案",
        "- 敌方生命成长下调 12%（等效 hp_scale = 0.88），其余公式不动",
        "- 目的：整体右移难度曲线、摊平悬崖，保留后期挑战，缓解中期断层",
        "",
        "## 四、调优后验证",
        f"- 50% 胜率分界点由敌方 **{cross_before} 级** 延后至 **{cross_after} 级**",
        f"- 敌方 51 级（玩家+1）胜率由 {wr_before_51:.0%} 回升至 **{wr_after_51:.0%}**，"
        f"52 级由 {wr_before_52:.0%} 回升至 **{wr_after_52:.0%}**",
        "- 结论：悬崖得到明显缓解，难度曲线整体右移且更平滑；"
        "后续可继续细化分段曲线（如 50-55 级单独标定）",
        "",
        "## 五、抽卡模型（SSR 获取）",
        f"- 基础概率 {BASE_RATE:.1%}，第 {SOFT_PITY_START} 抽起线性提升，"
        f"第 {HARD_PITY} 抽必出",
        f"- 解析期望抽数：**{analytic:.2f}** 抽",
        f"- 蒙特卡洛模拟（10 万玩家）：均值 {mean_pulls:.2f} 抽，"
        f"中位数 {median_pulls:.0f} 抽，90 分位 {p90:.0f} 抽",
        f"- 单抽 {PRICE_PER_PULL:.0f} 元 → 期望花费约 **{expected_cost:.0f} 元**/SSR",
        f"- 月免费资源 {monthly_free_pulls} 抽 → 月期望 SSR ≈ **{ssr_per_month:.2f} 个**",
        "- 说明：期望抽数显著低于硬保底，说明软保底有效降低了玩家方差",
        "",
        "## 六、结论",
        "- 本 Demo 覆盖数值策划的核心工作流：框架设计 → 模拟验证 → 发现问题 → "
        "调优 → 再验证 → 输出报告",
        "- 所有参数均可一键修改（combat.py / gacha.py），复现与延伸分析方便",
        "",
        "## 附：数值表",
        "- stats_by_level.csv：等级属性表",
        "- winrate.csv：调优前后胜率明细",
        "- gacha_summary.csv：抽卡关键指标",
    ]
    with open(os.path.join(OUT_DIR, "balance_report.md"),
              "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
