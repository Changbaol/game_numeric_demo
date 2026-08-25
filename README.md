# 卡牌养成游戏数值平衡模拟 Demo

一个可直接运行的数值策划练习项目：覆盖**成长曲线设计 → 战斗平衡模拟 → 发现
问题 → 调优 → 再验证 → 输出报告**的完整工作流，并附带抽卡保底模型。

## 快速开始

```bash
cd game_numeric_demo
pip install -r requirements.txt
python main.py
```

Windows 也可以直接双击 `run_demo.bat`。

## 效果展示

运行一次 `python main.py` 即可得到以下成果物：

![成长曲线](outputs/growth_curves.png)

![调优前后难度曲线对比](outputs/winrate_before_after.png)

![抽卡出货分布](outputs/gacha_distribution.png)

完整分析见 [outputs/balance_report.md](outputs/balance_report.md)。

## 输出产物（outputs/）

| 文件 | 说明 |
| --- | --- |
| growth_curves.png | 角色成长曲线（等级 1-80） |
| winrate_before_after.png | 调优前后关卡胜率对比 |
| gacha_distribution.png | 抽卡出货分布与累积概率 |
| stats_by_level.csv | 等级数值表（可导入 Excel） |
| winrate.csv | 胜率明细 |
| gacha_summary.csv | 抽卡关键指标 |
| balance_report.md | 完整调优报告 |

## 文件结构

| 文件 | 作用 |
| --- | --- |
| combat.py | 成长曲线、战斗公式、1v1 回合制战斗 |
| gacha.py | 抽卡概率、软/硬保底、期望抽数 |
| simulator.py | Monte Carlo 战斗模拟器 |
| report.py | 图表、CSV 与 Markdown 报告 |
| main.py | 一键运行入口 |

## 怎么把它变成"你自己的项目"

1. **改参数**：打开 `combat.py` 修改成长系数，或打开 `gacha.py` 修改概率与
   保底，观察结果变化；
2. **加玩法**：例如给战斗加入"速度属性决定先手""技能冷却""属性克制"，
   在 `battle()` 里扩展即可；
3. **写自己的分析**：把 `balance_report.md` 里的结论改成你自己的理解，
   面试时能讲清楚"为什么这么调、数据怎么支撑"；
4. **保留随机种子**：`main.py` 里 `SEED = 2026` 保证结果可复现，这是
   "仿真结果可靠、可复现"的直接体现。

## 面试讲解建议

- 先讲工作流（设计 → 模拟 → 调优 → 报告），再讲一个具体结论
  （例如：敌方 50 级后胜率骤降，下调 12% 生命后 50% 分界点右移）；
- 抽卡部分重点讲"软保底把期望抽数从硬保底的 90 拉低到约 70"这个结论。
