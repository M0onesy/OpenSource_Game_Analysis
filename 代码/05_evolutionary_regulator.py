"""
========================================================================
模块 5：演化博弈与监管者  →  生成 图4（fig4_evolutionary.png）

数据截止日：2026 年 5 月 28 日
背景：把"开源 vs 闭源"视为大规模厂商群体中的策略频率演化。设群体中
      选择"开放权重"策略的比例为 x，其期望支付随 x 上升而下降（开源生态
      拥挤、商品化压低租金）；闭源策略支付随 x 上升而上升（稀缺差异化溢价）。
      引入"监管者"作为环境参数 reg，平移开源策略的相对收益，刻画不同司法辖区
      （欧盟 AI Act、中国《AI+》行动、美国 EO 14179 / 加州 SB53）如何改变
      演化稳定策略（ESS）。

模型：复制动态  dx/dt = x(1−x)[π_O(x) − π_C(x)]
      π_O(x) = α − β·x + reg  （α=2, β=1）
      π_C(x) = γ + δ·x        （γ=1, δ=0.5）
      内部不动点 x* = (α − γ + reg)/(β + δ)，且为唯一演化稳定策略。

四情景 reg 取值与对应 ESS：
      基线   reg = 0.0  → x* = 0.667
      欧盟   reg = −0.5 → x* = 0.333   （合规义务偏重前沿开放模型）
      中国   reg = +0.3 → x* = 0.867   （政策与生态扶持开源）
      美国   reg = −0.1 → x* = 0.600   （去管制为主、对开闭近中性、边际偏存量）
========================================================================
"""

import json
import os

import numpy as np
from _cjk_support import configure_matplotlib_backend_for_batch

configure_matplotlib_backend_for_batch()

import matplotlib.pyplot as plt
from scipy.integrate import odeint

from _style import (C_PRIMARY, C_PRIMARY_2, C_ACCENT, C_GOLD, C_GREEN, C_GREY,
                    C_OPEN, C_CLOSED, save_fig, style_axes)


# ----------------------------------------------------------------------
# 1. 模型参数与解析解
# ----------------------------------------------------------------------
ALPHA, BETA, GAMMA, DELTA = 2.0, 1.0, 1.0, 0.5

SCENARIOS = [
    # 名称, reg, 颜色
    ("基线（无监管）", 0.0, C_PRIMARY),
    ("欧盟 AI Act",    -0.5, C_ACCENT),
    ("中国《AI+》行动", 0.3, C_GREEN),
    ("美国 EO/加州 SB53", -0.1, C_GOLD),
]


def pi_open(x, reg):
    return ALPHA - BETA * x + reg


def pi_closed(x):
    return GAMMA + DELTA * x


def ess(reg):
    """内部演化稳定策略 x* = (α − γ + reg)/(β + δ)，并截断到 [0,1]。"""
    xstar = (ALPHA - GAMMA + reg) / (BETA + DELTA)
    return min(1.0, max(0.0, xstar))


def replicator(x, t, reg):
    x = np.clip(x, 0.0, 1.0)
    return x * (1 - x) * (pi_open(x, reg) - pi_closed(x))


# ----------------------------------------------------------------------
# 2. 绘图
# ----------------------------------------------------------------------
def make_figure():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(13.6, 6.6))

    # ============ 左图：基线复制动态相图 ============
    x = np.linspace(0, 1, 400)
    reg0 = 0.0
    dxdt = x * (1 - x) * (pi_open(x, reg0) - pi_closed(x))
    xstar0 = ess(reg0)

    axL.axhline(0, color="#888888", lw=1.0, zorder=1)
    # 上升段（dx/dt>0，向 x* 演化）绿色填充；下降段红色
    axL.fill_between(x, dxdt, 0, where=(dxdt >= 0), color=C_GREEN, alpha=0.18, zorder=1)
    axL.fill_between(x, dxdt, 0, where=(dxdt < 0), color=C_CLOSED, alpha=0.18, zorder=1)
    axL.plot(x, dxdt, color=C_PRIMARY, lw=2.6, zorder=3)

    # 平衡点：x=0、x=1 不稳定（空心）；x* 稳定 ESS（实心红）
    axL.scatter([0, 1], [0, 0], s=95, facecolors="white", edgecolors=C_GREY,
                linewidths=2.0, zorder=5)
    axL.scatter([xstar0], [0], s=140, color=C_ACCENT, edgecolors="white",
                linewidths=1.5, zorder=6)
    axL.annotate(f"演化稳定策略\n$x^*$ = {xstar0:.3f}", (xstar0, 0),
                 xytext=(xstar0 + 0.02, 0.052), fontsize=13, fontweight="bold",
                 color=C_ACCENT, ha="left",
                 arrowprops=dict(arrowstyle="-|>", color=C_ACCENT, lw=1.6))
    axL.text(0.012, -0.012, "$x$=0\n(不稳定)", fontsize=12, color=C_GREY,
             ha="left", va="top")
    axL.text(0.988, 0.004, "$x$=1\n(不稳定)", fontsize=12, color=C_GREY,
             ha="right", va="bottom")

    # 演化方向箭头（在 y=0 附近）
    for xa in [0.18, 0.45]:
        axL.annotate("", xy=(xa + 0.10, 0.004), xytext=(xa, 0.004),
                     arrowprops=dict(arrowstyle="-|>", color=C_GREEN, lw=2.0))
    for xa in [0.80, 0.95]:
        axL.annotate("", xy=(xa - 0.10, 0.004), xytext=(xa, 0.004),
                     arrowprops=dict(arrowstyle="-|>", color=C_CLOSED, lw=2.0))

    axL.text(0.54, 0.030, "$\\dot{x}>0$：开源比例上升", color=C_GREEN,
             fontsize=12.5, fontweight="bold", ha="center")
    axL.text(0.84, -0.05, "$\\dot{x}<0$：开源比例下降", color=C_CLOSED,
             fontsize=12.5, fontweight="bold", ha="center")

    axL.set_xlim(-0.02, 1.02)
    axL.set_ylim(-0.075, 0.075)
    axL.set_xlabel("开源策略比例 $x$", fontsize=14.5)
    axL.set_ylabel("复制动态 $\\dot{x}=x(1-x)[\\pi_O-\\pi_C]$", fontsize=14)
    axL.set_title("(a)　基线复制动态相图：唯一内部 ESS", fontsize=15.5, pad=12)
    style_axes(axL, grid_axis="x")

    eqn = ("$\\pi_O(x)=\\alpha-\\beta x+reg$\n$\\pi_C(x)=\\gamma+\\delta x$\n"
           "$x^*=\\dfrac{\\alpha-\\gamma+reg}{\\beta+\\delta}$\n"
           f"$(\\alpha,\\beta,\\gamma,\\delta)$=({ALPHA:.0f},{BETA:.0f},{GAMMA:.0f},{DELTA:.1f})")
    axL.text(0.025, 0.97, eqn, transform=axL.transAxes, ha="left", va="top",
             fontsize=12, color="#333333",
             bbox=dict(boxstyle="round,pad=0.5", fc="#F7F9FC", ec=C_GREY, lw=0.9))

    # ============ 右图：四监管情景演化轨迹 ============
    t = np.linspace(0, 18, 500)
    x0 = 0.5
    for name, reg, color in SCENARIOS:
        sol = odeint(replicator, x0, t, args=(reg,)).flatten()
        xstar = ess(reg)
        axR.plot(t, sol, color=color, lw=2.6, zorder=4,
                 label=f"{name}：$x^*$={xstar:.3f}")
        axR.axhline(xstar, color=color, lw=1.0, ls=":", alpha=0.7, zorder=2)
        axR.text(t[-1] + 0.15, xstar, f"{xstar:.3f}", color=color,
                 fontsize=12.5, fontweight="bold", va="center", ha="left")

    axR.scatter([0], [x0], s=70, color="#333333", zorder=6)
    axR.annotate(f"共同初始 $x_0$={x0:.1f}", (0, x0), xytext=(1.4, 0.49),
                 fontsize=12, color="#333333", ha="left", va="center",
                 arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.3))

    axR.set_xlim(0, 19.6)
    axR.set_ylim(0, 1.0)
    axR.set_xlabel("演化时间 $t$", fontsize=14.5)
    axR.set_ylabel("开源策略比例 $x(t)$", fontsize=14.5)
    axR.set_title("(b)　监管平移 ESS：四司法辖区情景对比", fontsize=15.5, pad=12)
    axR.legend(loc="lower right", bbox_to_anchor=(0.995, 0.06),
               framealpha=0.95, edgecolor=C_GREY, fontsize=12)
    style_axes(axR, grid_axis="y")

    fig.suptitle("演化博弈与监管者：复制动态下开源比例的演化稳定策略",
                 fontsize=18, fontweight="bold", y=1.005)
    fig.tight_layout(rect=[0, 0, 1, 0.985])

    ess_table = {name: round(ess(reg), 4) for name, reg, _ in SCENARIOS}
    return fig, ess_table


if __name__ == "__main__":
    print("=" * 60)
    print("模块 5：演化博弈与监管者")
    print(f"  参数 (α,β,γ,δ) = ({ALPHA},{BETA},{GAMMA},{DELTA})")
    print("  各情景演化稳定策略 x*：")
    for name, reg, _ in SCENARIOS:
        print(f"    {name:<18} reg={reg:+.1f}  →  x* = {ess(reg):.4f}")
    print("=" * 60)

    fig, ess_table = make_figure()
    save_fig(fig, "fig4_evolutionary.png")

    out = {
        "module": 5,
        "data_cutoff": "2026-05-28",
        "model": "dx/dt = x(1-x)[pi_O - pi_C]; pi_O=a-bx+reg, pi_C=g+dx",
        "params": {"alpha": ALPHA, "beta": BETA, "gamma": GAMMA, "delta": DELTA},
        "ess_by_scenario": ess_table,
        "interpretation": "监管作为环境参数平移开源相对收益：扶持型政策(reg>0)抬高开源 ESS，合规重负(reg<0)压低开源 ESS；唯一内部不动点即演化稳定策略。"
    }
    with open("results_module5.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("[已写出] results_module5.json")
