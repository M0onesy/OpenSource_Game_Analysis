"""
========================================================================
模块 3：贝叶斯博弈与信号传递（Spence 信号模型）  →  生成 图5（fig5_bayesian_signal.png）

数据截止日：2026 年 5 月 28 日
背景：2024.12.26 DeepSeek 在 V3 技术报告（arXiv:2412.19437）中完整披露
      557.6 万美元训练成本（2.788M H800 GPU 小时 × 2 美元/时）以及 MoE、
      MLA、FP8 训练等细节。这是典型 Spence 信号——强类型（真实低成本）可低
      成本发出可验证信号，弱类型（伪造）因全球可复现而伪造成本极高。本模块
      追踪市场后验信念在五个关键事件下的演化，并刻画分离均衡可行域。

实现内容：
  1. DeepSeek "成本类型" 后验信念的贝叶斯更新（基于真实事件链）
  2. Spence 分离均衡条件 c_S < ΔU < c_W 的区域刻画
  3. 三类结果可视化：分离均衡 / 混同（弱类型亦发信号）/ 混同（均不发信号）
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
                    PLAYER_COLORS, save_fig, style_axes)


# ----------------------------------------------------------------------
# 1. 贝叶斯更新
# ----------------------------------------------------------------------
def bayes(prior, l_strong, l_weak):
    num = l_strong * prior
    return num / (num + l_weak * (1 - prior))


def belief_evolution():
    """返回 DeepSeek 强类型（低成本）后验信念的五阶段演化。"""
    events = [
        ("T0", "2024 年初\n先验信念", None, None),
        ("T1", "V2 论文\n(MoE+MLA)", 0.50, 0.15),
        ("T2", "V3 + 技术报告\n($5.576M)", 0.85, 0.10),
        ("T3", "R1 推理模型\n+ R1-Zero", 0.95, 0.05),
        ("T4", "全球复现\n+ App Store 登顶", 0.99, 0.01),
    ]
    posterior = 0.10
    seq = [(events[0][0], events[0][1], posterior)]
    for tag, name, ls, lw in events[1:]:
        posterior = bayes(posterior, ls, lw)
        seq.append((tag, name, posterior))
    return seq


# ----------------------------------------------------------------------
# 2. 绘图
# ----------------------------------------------------------------------
def plot(seq):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 6.8))

    # ===== 左图：贝叶斯信念演化 =====
    xs = np.arange(len(seq))
    ys = [s[2] for s in seq]
    ax1.plot(xs, ys, "-o", color=C_PRIMARY, linewidth=2.6, markersize=11,
             markerfacecolor=C_ACCENT, markeredgecolor="white",
             markeredgewidth=1.6, zorder=5)
    ax1.axhline(0.5, color=C_GREY, linestyle="--", linewidth=1.2, alpha=0.8)
    ax1.text(0.05, 0.52, "信念 = 0.5（无倾向）", fontsize=12, color=C_GREY)

    label_overrides = {
        "T1": dict(xytext=(1.0, 0.18), ha="center", va="top"),
    }
    for i, (tag, name, p) in enumerate(seq):
        va = "bottom" if i < 3 else "top"
        dy = 0.045 if i < 3 else -0.05
        default_xytext = (i, p + dy + (0.06 if i < 3 else -0.06))
        label_cfg = label_overrides.get(tag, {})
        ax1.annotate(
            f"{tag}：{p:.3f}",
            xy=(i, p),
            xytext=label_cfg.get("xytext", default_xytext),
            ha=label_cfg.get("ha", "center"),
            va=label_cfg.get("va", va),
            fontsize=13,
            fontweight="bold",
            color=C_PRIMARY,
        )
        ax1.text(i, -0.16, name, ha="center", va="top", fontsize=11.5, color="#333333")

    ax1.set_xticks(xs)
    ax1.set_xticklabels([s[0] for s in seq], fontsize=13.5)
    ax1.set_ylim(-0.02, 1.10)
    ax1.set_xlim(-0.5, len(seq) - 0.5)
    ax1.set_ylabel("后验信念 P(强类型｜信号)", fontsize=14.5)
    ax1.set_title("DeepSeek「低成本类型」后验信念的贝叶斯演化\n"
                  "先验 0.10 → 后验 1.00（2024Q1→2025.02）：可验证强信号驱动信念跃迁", fontsize=15)
    style_axes(ax1, grid_axis="y")

    # ===== 右图：Spence 分离均衡可行域 =====
    dU = 4.0       # 被市场识别为强类型的额外收益 ΔU（代表性取值）
    lim = 10.0     # 横轴 c_S / ΔU 参照范围
    ytop = 10.8    # 纵轴范围（上方留白用于放置标签，避免与散点重叠）
    # 三区域填充
    ax2.fill_between([0, dU], dU, ytop, color=C_GREEN, alpha=0.22, zorder=1)   # 分离区
    ax2.fill_between([0, lim], 0, dU, color=C_GOLD, alpha=0.20, zorder=1)      # 混同·均发
    ax2.fill_betweenx([0, ytop], dU, lim, color=C_GREY, alpha=0.16, zorder=1)  # 混同·均不发

    ax2.axvline(dU, color=C_ACCENT, linestyle="--", linewidth=1.6, zorder=2)
    ax2.axhline(dU, color=C_ACCENT, linestyle="--", linewidth=1.6, zorder=2)
    ax2.text(dU + 0.15, ytop - 0.35, f"ΔU = {dU:.0f}", color=C_ACCENT,
             fontsize=13.5, fontweight="bold", va="top")

    # 区域文字（置于各区空白处，远离散点与标签）
    ax2.text(1.7, 5.05, "分离均衡区\nc_S < ΔU < c_W\n（仅强类型发信号·可信）",
             ha="center", va="center", fontsize=12, color="#1E5631", fontweight="bold")
    ax2.text(2.7, 1.42, "混同·均发信号\nc_W < ΔU\n（弱类型亦可负担·失效）",
             ha="center", va="center", fontsize=11.5, color="#8A6D0B")
    ax2.text(7.45, 9.4, "混同·均不发信号\nc_S > ΔU\n（强类型亦不愿发）",
             ha="center", va="center", fontsize=11.5, color="#555555")

    # 真实案例散点（c_S, c_W）：用细引线把标签牵引到空白处，避免相互重叠
    cases = [
        ("DeepSeek",       1.5, 7.5, PLAYER_COLORS["DeepSeek"], (2.55, 6.95), "left"),
        ("Llama 3.1-405B", 1.0, 8.5, PLAYER_COLORS["Meta"],     (0.20, 9.95), "left"),
        ("Qwen3",          2.0, 9.0, PLAYER_COLORS["阿里通义"], (2.35, 10.35), "left"),
        ("营销夸大小模型", 0.6, 1.8, C_GOLD,                    (1.25, 2.80), "left"),
        ("无差异化跟随者", 6.0, 6.6, C_GREY,                    (6.40, 5.55), "left"),
    ]
    for name, cs, cw, col, (tx, ty), ha in cases:
        ax2.scatter(cs, cw, s=150, color=col, edgecolor="black",
                    linewidth=1.4, zorder=6)
        ax2.annotate(f"{name}\n({cs}, {cw})", xy=(cs, cw), xytext=(tx, ty),
                     ha=ha, va="center", fontsize=11, color="#222222",
                     fontweight="bold", zorder=7,
                     arrowprops=dict(arrowstyle="-", color="#9AA4AE",
                                     lw=0.8, shrinkA=2, shrinkB=4))

    ax2.set_xlim(0, lim)
    ax2.set_ylim(0, ytop)
    ax2.set_xlabel("强类型信号成本 c_S（真实低成本→易复现）", fontsize=14.5)
    ax2.set_ylabel("弱类型信号成本 c_W（伪造→易被证伪）", fontsize=14.5)
    ax2.set_title("Spence 分离均衡可行域（ΔU＝4）\n"
                  "强类型低 c_S、弱类型高 c_W，使可验证技术报告成为可信信号", fontsize=15)
    style_axes(ax2, grid=False)

    legend = [
        Patch(facecolor=C_GREEN, alpha=0.5, label="分离均衡区"),
        Patch(facecolor=C_GOLD, alpha=0.5, label="混同（均发信号）"),
        Patch(facecolor=C_GREY, alpha=0.5, label="混同（均不发信号）"),
    ]
    ax2.legend(handles=legend, loc="lower right", fontsize=11.5, framealpha=0.95)

    fig.tight_layout()
    return fig


def main():
    seq = belief_evolution()
    print("=" * 64)
    print("模块 3：贝叶斯信号博弈")
    print("=" * 64)
    print("\n[DeepSeek 后验信念演化]")
    for tag, name, p in seq:
        print(f"  {tag}  {name.replace(chr(10), ' ')}: 后验 P(强类型)={p:.4f}")

    print("\n[Spence 分离均衡条件] c_S < ΔU < c_W（取 ΔU=4）")
    for name, cs, cw in [("DeepSeek", 1.5, 7.5), ("Llama 3.1 405B", 1.0, 8.5),
                         ("Qwen3", 2.0, 9.0), ("营销夸大小模型", 0.6, 1.8),
                         ("无差异化跟随者", 6.0, 6.6)]:
        sep = cs < 4.0 < cw
        print(f"  {name}: c_S={cs}, c_W={cw} → {'分离均衡' if sep else '混同（信号失效）'}")

    fig = plot(seq)
    save_fig(fig, "fig5_bayesian_signal.png")
    plt.close(fig)

    results = {
        "module": 3,
        "data_cutoff": "2026-05-28",
        "belief_path": [round(p, 4) for _, _, p in seq],
        "prior": 0.10,
        "final_posterior": round(seq[-1][2], 4),
        "delta_U": 4.0,
        "separating_condition": "c_S < ΔU < c_W",
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_module3.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[结果已写入] {out}")


if __name__ == "__main__":
    main()
