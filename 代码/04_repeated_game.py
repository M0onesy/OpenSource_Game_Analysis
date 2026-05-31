"""
========================================================================
模块 4：无限期重复博弈与定价协调  →  生成 图6（fig6_repeated_game.png）

数据截止日：2026 年 5 月 28 日
背景：API 定价是大模型公司之间最直接、可观测的重复博弈。本模块用
      冷酷触发（Grim Trigger）策略刻画"默契定价协调"的可持续条件，并引入
      两个现实压力因子——开源颠覆者的租金侵蚀强度 I 与 IPO 短视效应 λ——
      构造"有效贴现因子" δ_eff = δ_base·(1−I)·(1−λ)，解释为何前沿厂商
      难以长期维持高价协调。右图用 2023–2026 年真实 API 输入价格刻画
      "阶段一价格战崩溃 + 阶段二前沿企稳回升"的价格分层格局。

实现内容：
  1. 由差异化伯特兰定价博弈推导四个单期支付 (C, D, P, S)
  2. 冷酷触发临界贴现因子 δ* = (D−C)/(D−P) 的推导与数值
  3. 双因子有效贴现因子瀑布图，给出临界颠覆强度 I*
  4. 前沿旗舰输入价格时间线（对数轴），刻画崩溃—回升的分层结构
========================================================================
"""

import json
import os

import numpy as np
from _cjk_support import configure_matplotlib_backend_for_batch

configure_matplotlib_backend_for_batch()

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from _style import (C_PRIMARY, C_PRIMARY_2, C_ACCENT, C_GOLD, C_GREEN, C_GREY,
                    C_OPEN, C_CLOSED, PLAYER_COLORS, save_fig, style_axes)


# ----------------------------------------------------------------------
# 1. 单期支付的微观基础：差异化伯特兰定价博弈
# ----------------------------------------------------------------------
# 【本版升级】四个单期支付不再外生设定，而是由两家闭源前沿厂商
# （OpenAI、Anthropic）的差异化伯特兰定价博弈推导得到。
#   需求：q_i = a − p_i + g·p_j（g∈(0,1) 为替代度），边际成本 mc≈0
#         （前沿模型的推理边际成本相对 API 价格极小，做标准简化）。
#   合作=双方设联合利润最大价 p^m；背叛=对手维持 p^m 时的最优反应价；
#   惩罚=一次性伯特兰纳什价 p*；被背叛=守约维持 p^m 而对手降价。
BERTRAND_A = 12.0    # 需求截距（市场规模）
BERTRAND_G = 0.50    # 产品替代度（中等差异化）
BERTRAND_MC = 0.0    # 边际成本（推理成本相对 API 价极小）


def bertrand_stage_payoffs(a=BERTRAND_A, g=BERTRAND_G, mc=BERTRAND_MC):
    """由差异化伯特兰模型计算 (合作 C, 背叛 D, 惩罚 P, 被背叛 S) 四个单期支付。"""
    def profit(pi, pj):
        return (pi - mc) * (a - pi + g * pj)
    p_m = a / (2 * (1 - g))                 # 联合利润最大（合谋）价
    p_star = a / (2 - g)                    # 一次性伯特兰纳什价
    p_d = (a + g * p_m) / 2                 # 对手维持 p^m 时的最优反应（背叛）价
    C = profit(p_m, p_m)                    # 合作
    D = profit(p_d, p_m)                    # 背叛者当期
    P = profit(p_star, p_star)              # 价格战（惩罚）
    S = profit(p_m, p_d)                    # 被背叛方当期
    return C, D, P, S, dict(p_m=p_m, p_star=p_star, p_d=p_d)


PAYOFF_COOP, PAYOFF_DEFECT, PAYOFF_PUNISH, PAYOFF_SUCKER, BERTRAND_PRICES = \
    bertrand_stage_payoffs()


def critical_delta(C=PAYOFF_COOP, D=PAYOFF_DEFECT, P=PAYOFF_PUNISH):
    """冷酷触发下维持合作所需的临界贴现因子 δ*。
    合作可持续 ⇔ C/(1−δ) ≥ D + δ·P/(1−δ) ⇔ δ ≥ (D−C)/(D−P)。"""
    return (D - C) / (D - P)


# 双因子有效贴现因子
DELTA_BASE = 0.85   # 基准耐心（行业常规贴现因子）
I_DISRUPT  = 0.30   # 开源颠覆者侵蚀的未来租金比例
LAMBDA_IPO = 0.30   # IPO 短视：上市压力抬高当期权重、压低有效贴现


def effective_delta(delta_base=DELTA_BASE, I=I_DISRUPT, lam=LAMBDA_IPO):
    """有效贴现因子 δ_eff = δ_base·(1−I)·(1−λ)。"""
    return delta_base * (1 - I) * (1 - lam)


def critical_disruption(delta_star, delta_base=DELTA_BASE):
    """λ=0 时使 δ_eff 恰好降到 δ* 的临界颠覆强度 I* = 1 − δ*/δ_base。"""
    return 1 - delta_star / delta_base


# ----------------------------------------------------------------------
# 2. 前沿旗舰 API 输入价格时间线（美元 / 百万 tokens，真实数据）
# ----------------------------------------------------------------------
# OpenAI 前沿旗舰线：GPT-4 → GPT-4 Turbo → GPT-4o → GPT-5 → GPT-5.5
OPENAI_LINE = [
    (2023.20, 30.00, "GPT-4 $30"),
    (2023.85, 10.00, "GPT-4 Turbo $10"),
    (2024.40, 5.00,  "GPT-4o $5"),
    (2025.60, 1.25,  "GPT-5 $1.25"),
    (2026.31, 5.00,  "GPT-5.5 $5"),
]
# Anthropic 前沿旗舰线（Opus 档）：Claude 3 Opus → Opus 4 → Opus 4.5 → Opus 4.8
ANTHROPIC_LINE = [
    (2024.20, 15.00, "Claude 3 Opus $15"),
    (2025.38, 15.00, "Opus 4 $15"),
    (2025.90, 5.00,  "Opus 4.5 $5"),
    (2026.40, 5.00,  "Opus 4.8 $5"),
]
# 长尾 / 商品化档（持续下探）
LONGTAIL = [
    (2025.60, 0.05, "GPT-5 nano $0.05", PLAYER_COLORS["OpenAI"]),
    (2026.31, 0.28, "DeepSeek V4 $0.28", PLAYER_COLORS["DeepSeek"]),
]

PRICE_LABEL_POSITIONS = {
    "GPT-4 $30": ((2023.05, 38.0), "left", "bottom"),
    "Claude 3 Opus $15": ((2024.45, 18.8), "right", "bottom"),
    "GPT-4 Turbo $10": ((2023.50, 9.0), "center", "top"),
    "GPT-4o $5": ((2024.73, 3.2), "right", "top"),
    "Opus 4 $15": ((2025.33, 12.6), "right", "top"),
    "GPT-5 $1.25": ((2025.58, 0.82), "center", "top"),
    "Opus 4.5 $5": ((2025.85, 4), "right", "top"),
    "GPT-5.5 $5": ((2026.23, 7.8), "center", "bottom"),
    "Opus 4.8 $5": ((2026.20, 3.2), "left", "top"),
    "GPT-5 nano $0.05": ((2025.95, 0.06), "right", "bottom"),
    "DeepSeek V4 $0.28": ((2025.88, 0.40), "left", "bottom"),
}


# ----------------------------------------------------------------------
# 3. 绘图
# ----------------------------------------------------------------------
def make_figure():
    from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.6, 6.6))

    # ============ 左图：有效贴现因子瀑布 ============
    d_star = critical_delta()
    d1 = DELTA_BASE
    d2 = DELTA_BASE * (1 - I_DISRUPT)
    d3 = effective_delta()
    I_star = critical_disruption(d_star)

    xs = [0, 1, 2]
    vals = [d1, d2, d3]
    labels = ["基准贴现因子\n$\\delta_{base}$", "颠覆者侵蚀\n$\\times(1-I)$", "IPO 短视\n$\\times(1-\\lambda)$"]
    colors = [C_GREEN if v >= d_star else C_CLOSED for v in vals]

    axL.bar(xs, vals, width=0.54, color=colors, edgecolor="white",
            linewidth=1.5, zorder=3)

    # 阶梯：横向参考线 + 仅在“柱间空隙”画向下箭头与降幅标签（避免与柱顶数值重叠）
    drop_labels = [f"$-I$ ({I_DISRUPT:.0%})", f"$-\\lambda$ ({LAMBDA_IPO:.0%})"]
    for i in range(len(xs) - 1):
        axL.plot([xs[i] + 0.27, xs[i + 1] + 0.27], [vals[i], vals[i]],
                 color=C_GREY, lw=1.1, ls="--", zorder=2)
        gx = (xs[i] + xs[i + 1]) / 2 + 0.27
        axL.annotate("", xy=(gx, vals[i + 1]), xytext=(gx, vals[i]),
                     arrowprops=dict(arrowstyle="-|>", color=C_ACCENT, lw=1.8), zorder=4)
        axL.text(gx + 0.05, (vals[i] + vals[i + 1]) / 2, drop_labels[i],
                 color=C_ACCENT, fontsize=12, fontweight="bold", ha="left", va="center")

    # δ* 临界线
    axL.axhline(d_star, color=C_PRIMARY, lw=2.0, ls="-", zorder=2)
    axL.text(2.62, d_star + 0.008, f"临界贴现因子 $\\delta^*$ = {d_star:.3f}",
             color=C_PRIMARY, fontsize=13, fontweight="bold", ha="right", va="bottom")

    # 区域底色 + 左侧竖排带标签（位于柱体左侧空白区，不被柱遮挡）
    axL.axhspan(d_star, 1.0, color=C_GREEN, alpha=0.06, zorder=0)
    axL.axhspan(0.0, d_star, color=C_CLOSED, alpha=0.06, zorder=0)
    axL.text(-0.78, (d_star + 1.0) / 2, "合作可持续区（默契高价）", color=C_GREEN,
             fontsize=12.5, fontweight="bold", ha="center", va="center", rotation=90)
    axL.text(-0.78, d_star / 2, "合作破裂区（价格战）", color=C_CLOSED,
             fontsize=12.5, fontweight="bold", ha="center", va="center", rotation=90)

    # 柱顶数值（低于阈值的柱将数值置于柱内白字，避免与 δ* 线相碰）
    for x, v in zip(xs, vals):
        if v >= d_star:
            axL.text(x, v + 0.02, f"{v:.3f}", ha="center", va="bottom",
                     fontsize=14, fontweight="bold", color="#222222")
        else:
            axL.text(x, v - 0.03, f"{v:.3f}", ha="center", va="top",
                     fontsize=14, fontweight="bold", color="white")

    axL.set_xticks(xs)
    axL.set_xticklabels(labels, fontsize=12.5)
    axL.set_ylim(0, 1.0)
    axL.set_xlim(-0.98, 2.78)
    axL.set_ylabel("有效贴现因子 $\\delta_{eff}$", fontsize=14.5)
    axL.set_title("(a)　双因子有效贴现因子：合作为何走向破裂", fontsize=15.5, pad=12)
    style_axes(axL, grid_axis="y")

    note = ("差异化伯特兰：合谋价 $p^m$={:.0f}　纳什价 $p^*$={:.0f}　背叛价 $p_d$={:.0f}\n"
            "单期支付 合作 $C$={:.0f}　背叛 $D$={:.0f}　惩罚 $P$={:.0f}\n"
            "$\\delta^*=(D-C)/(D-P)$ = {:.3f}\n"
            "取 $I$={:.2f}、$\\lambda$={:.2f}：$\\delta_{{eff}}$={:.3f} $<\\delta^*$ → 破裂\n"
            "当 $\\lambda$=0：临界颠覆强度 $I^*=1-\\delta^*/\\delta_{{base}}$ = {:.3f}").format(
                BERTRAND_PRICES["p_m"], BERTRAND_PRICES["p_star"], BERTRAND_PRICES["p_d"],
                PAYOFF_COOP, PAYOFF_DEFECT, PAYOFF_PUNISH, d_star,
                I_DISRUPT, LAMBDA_IPO, d3, I_star)
    axL.text(0.985, 0.30, note, transform=axL.transAxes, ha="right", va="top",
             fontsize=10.6, color="#333333",
             bbox=dict(boxstyle="round,pad=0.5", fc="#F7F9FC", ec=C_GREY, lw=0.9))

    # ============ 右图：前沿旗舰输入价格时间线 ============
    axR.axvspan(2022.95, 2025.78, color=C_CLOSED, alpha=0.05, zorder=0)
    axR.axvspan(2025.78, 2026.72, color=C_GREEN, alpha=0.06, zorder=0)
    axR.text(2024.0, 0.032, "阶段一　价格战崩溃 (2023–2025)", color=C_CLOSED,
             fontsize=12, fontweight="bold", ha="center", va="bottom")
    axR.text(2026.2, 0.032, "阶段二　前沿企稳回升 (2026)", color=C_GREEN,
             fontsize=12, fontweight="bold", ha="center", va="bottom")

    # OpenAI 线 —— 每点独立设置标签偏移，规避重叠
    ox = [p[0] for p in OPENAI_LINE]
    oy = [p[1] for p in OPENAI_LINE]
    axR.plot(ox, oy, "-o", color=PLAYER_COLORS["OpenAI"], lw=2.4, ms=8,
             zorder=4, label="OpenAI 前沿旗舰")
    for x, y, t in OPENAI_LINE:
        (tx, ty), ha, va = PRICE_LABEL_POSITIONS[t]
        axR.annotate(t, (x, y), xytext=(tx, ty), ha=ha, va=va,
                     fontsize=11, color=PLAYER_COLORS["OpenAI"], fontweight="bold")

    # Anthropic 线
    ax_ = [p[0] for p in ANTHROPIC_LINE]
    ay_ = [p[1] for p in ANTHROPIC_LINE]
    axR.plot(ax_, ay_, "-s", color=PLAYER_COLORS["Anthropic"], lw=2.4, ms=8,
             zorder=4, label="Anthropic 前沿旗舰（Opus 档）")
    for x, y, t in ANTHROPIC_LINE:
        (tx, ty), ha, va = PRICE_LABEL_POSITIONS[t]
        axR.annotate(t, (x, y), xytext=(tx, ty), ha=ha, va=va,
                     fontsize=11, color=PLAYER_COLORS["Anthropic"], fontweight="bold")

    # 长尾点
    for x, y, t, c in LONGTAIL:
        axR.scatter([x], [y], s=95, color=c, marker="D", zorder=5,
                    edgecolor="white", linewidth=1.2)
        (tx, ty), ha, va = PRICE_LABEL_POSITIONS[t]
        axR.annotate(t, (x, y), xytext=(tx, ty), ha=ha, va=va,
                     fontsize=11, color=c, fontweight="bold")
    axR.text(2024.45, 0.10, "长尾 / 商品化档：持续下探", color=C_GREY,
             fontsize=11.5, ha="center", style="italic")

    axR.set_yscale("log")
    axR.set_ylim(0.03, 62)
    axR.set_xlim(2022.92, 2026.74)
    axR.set_xticks([2023, 2024, 2025, 2026])
    axR.set_xticklabels(["2023", "2024", "2025", "2026"])
    # 自定义对数刻度，避免 mathtext 负号字形缺失，并直接用美元价标注
    axR.yaxis.set_major_locator(FixedLocator([0.05, 0.1, 0.3, 1, 5, 10, 30]))
    axR.yaxis.set_major_formatter(FixedFormatter(["$0.05", "$0.1", "$0.3", "$1", "$5", "$10", "$30"]))
    axR.yaxis.set_minor_locator(NullLocator())
    axR.set_ylabel("API 输入价格（美元 / 百万 tokens，对数轴）", fontsize=14)
    axR.set_xlabel("年份", fontsize=14.5)
    axR.set_title("(b)　前沿旗舰输入价格：崩溃后的分层与回升", fontsize=15.5, pad=12)
    axR.legend(loc="upper right", framealpha=0.95, edgecolor=C_GREY)
    style_axes(axR, grid_axis="y")

    fig.suptitle("无限期重复博弈：默契定价协调的可持续性与现实瓦解",
                 fontsize=18, fontweight="bold", y=1.005)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    return fig, dict(delta_star=d_star, delta_base=DELTA_BASE, I=I_DISRUPT,
                     lam=LAMBDA_IPO, delta_eff=d3, I_star=I_star)


if __name__ == "__main__":
    d_star = critical_delta()
    I_star = critical_disruption(d_star)
    print("=" * 60)
    print("模块 4：无限期重复博弈（单期支付由差异化伯特兰模型推导）")
    print(f"  伯特兰参数：a={BERTRAND_A} g(替代度)={BERTRAND_G} mc={BERTRAND_MC}")
    print(f"  合谋价 p^m={BERTRAND_PRICES['p_m']:.2f}  纳什价 p*={BERTRAND_PRICES['p_star']:.2f}"
          f"  背叛价 p_d={BERTRAND_PRICES['p_d']:.2f}")
    print(f"  单期支付：C={PAYOFF_COOP:.1f} D={PAYOFF_DEFECT:.1f} "
          f"P={PAYOFF_PUNISH:.1f} S={PAYOFF_SUCKER:.1f}（满足 D>C>P>S）")
    print(f"  临界贴现因子 δ* = (D−C)/(D−P) = {d_star:.4f}")
    print(f"  基准 δ_base = {DELTA_BASE}")
    print(f"  有效 δ_eff = δ_base·(1−{I_DISRUPT})·(1−{LAMBDA_IPO}) = {effective_delta():.4f}")
    print(f"  临界颠覆强度 I* (λ=0) = 1 − δ*/δ_base = {I_star:.4f}")
    print(f"  δ_eff < δ* ? {effective_delta() < d_star} → 合作破裂")
    print("=" * 60)

    fig, res = make_figure()
    save_fig(fig, "fig6_repeated_game.png")

    out = {
        "module": 4,
        "data_cutoff": "2026-05-28",
        "bertrand_primitives": {"a": BERTRAND_A, "g": BERTRAND_G, "mc": BERTRAND_MC},
        "bertrand_prices": {k: round(v, 3) for k, v in BERTRAND_PRICES.items()},
        "single_period_payoffs": {"coop": round(PAYOFF_COOP, 2),
                                   "defect": round(PAYOFF_DEFECT, 2),
                                   "punish": round(PAYOFF_PUNISH, 2),
                                   "sucker": round(PAYOFF_SUCKER, 2)},
        "critical_delta": round(res["delta_star"], 4),
        "delta_base": res["delta_base"],
        "I_disruption": res["I"],
        "lambda_ipo": res["lam"],
        "delta_effective": round(res["delta_eff"], 4),
        "I_star_critical_disruption": round(res["I_star"], 4),
        "cooperation_collapses": bool(res["delta_eff"] < res["delta_star"]),
        "interpretation": "四个单期支付由差异化伯特兰定价博弈推导（满足 D>C>P>S）；颠覆侵蚀与 IPO 短视将有效贴现因子压低至临界值以下，默契高价协调难以维持；前沿档企稳回升而长尾持续下探，呈价格分层。"
    }
    with open("results_module4.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("[已写出] results_module4.json")
