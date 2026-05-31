"""
========================================================================
模块 0：分析框架总览  →  生成 图1（fig1_overview.png）

数据截止日：2026 年 5 月 28 日
作用：一图概览全文建模框架——五大参与人（按开源/闭源策略分阵营）、
      基础博弈（静态 + 序贯，得到纳什/子博弈完美均衡），以及三项扩展改进
      （演化博弈+监管、贝叶斯信号、无限期重复博弈），并标注各部分对应的
      关键结论与图表编号。全部文字为中文，可由本脚本 1:1 复现。

关键事实（截至 2026-05-28，均有公开来源支撑，详见 数据来源.md）：
  · OpenAI 估值约 8520 亿美元；Anthropic 新一轮融资后约 9650 亿美元，已反超。
  · 旗舰：OpenAI GPT-5.5、Anthropic Claude Opus 4.8、Meta Llama 4、
          DeepSeek V4、阿里通义 Qwen 3.5。
  · DeepSeek-R1（2025-01）曾致英伟达单日市值蒸发约 5890 亿美元。
  · 通义 Qwen 全面开源，累计下载近 10 亿，约占全球开源衍生模型半数。
========================================================================
"""

import os
from _cjk_support import configure_matplotlib_backend_for_batch

configure_matplotlib_backend_for_batch()

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from _style import (C_PRIMARY, C_PRIMARY_2, C_ACCENT, C_GOLD, C_GREEN, C_GREY,
                    C_OPEN, C_CLOSED, C_LIGHT, PLAYER_COLORS, save_fig)


def _box(ax, cx, cy, w, h, title, lines, fc, ec, title_color="white",
         body_color="#222222", title_fs=11.5, body_fs=8.8, rounding=0.025,
         draw_title_rule=True, body_valign="top", body_y_shift=0.0):
    """绘制带标题条的圆角信息框。"""
    x0, y0 = cx - w / 2, cy - h / 2
    box = FancyBboxPatch((x0, y0), w, h,
                         boxstyle=f"round,pad=0.2,rounding_size={rounding*100}",
                         linewidth=1.6, edgecolor=ec, facecolor=fc, zorder=3,
                         mutation_aspect=1)
    ax.add_patch(box)
    # 标题
    has_title = bool(title)
    if has_title:
        ax.text(cx, y0 + h - 1.55, title, ha="center", va="center",
                fontsize=title_fs, fontweight="bold", color=title_color, zorder=4)
    # 标题分隔线
    if has_title and draw_title_rule:
        ax.plot([x0 + 1.2, x0 + w - 1.2], [y0 + h - 3.0, y0 + h - 3.0],
                color=title_color, lw=0.8, alpha=0.55, zorder=4)
    # 正文
    if lines:
        body = "\n".join(lines)
        if body_valign == "center":
            body_y = cy + body_y_shift
            body_va = "center"
        else:
            body_top = y0 + h - (3.9 if has_title else 1.7)
            body_y = body_top + body_y_shift
            body_va = "top"
        ax.text(cx, body_y, body, ha="center", va=body_va,
                fontsize=body_fs, color=body_color, zorder=4, linespacing=1.45)
    return (cx, y0, y0 + h)


def _arrow(ax, x1, y1, x2, y2, color=C_GREY, lw=1.8, style="-|>"):
    ar = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                         mutation_scale=15, color=color, lw=lw, zorder=2)
    ax.add_patch(ar)


def make_figure():
    fig, ax = plt.subplots(figsize=(14.2, 9.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # ---------------- 标题 ----------------
    ax.text(50, 97.3, "大模型公司开源 vs 闭源战略博弈：分析框架总览",
            ha="center", va="center", fontsize=20.5, fontweight="bold", color=C_PRIMARY)
    ax.text(50, 93.2, "五大参与人　→　基础博弈（静态 + 序贯）　→　三项扩展改进",
            ha="center", va="center", fontsize=13.5, color=C_GREY)

    # ---------------- 第一层：五大参与人 ----------------
    ax.text(50, 90.3, "第一层　参与人与策略阵营", ha="center", va="center",
            fontsize=14.5, fontweight="bold", color="#333333")

    players = [
        ("OpenAI",   "闭源", ["旗舰：GPT-5.5", "估值约 $852B"]),
        ("Anthropic","闭源", ["旗舰：Claude Opus 4.8", "估值约 $965B（↑反超）"]),
        ("Meta",     "开放权重", ["旗舰：Llama 4", "开放权重领跑者"]),
        ("DeepSeek", "开源·颠覆者", ["旗舰：DeepSeek V4", "R1 曾致英伟达 -$589B"]),
        ("阿里通义", "开源·平台", ["旗舰：Qwen 3.5", "累计下载近 10 亿"]),
    ]
    n = len(players)
    margin = 2.5
    gap = 2.2
    cardw = (100 - 2 * margin - (n - 1) * gap) / n
    cardh = 14.0
    cy = 77.0
    centers = []
    for i, (name, strat, lines) in enumerate(players):
        cx = margin + cardw / 2 + i * (cardw + gap)
        centers.append(cx)
        col = PLAYER_COLORS[name]
        _box(ax, cx, cy, cardw, cardh, f"{name}", [f"〔{strat}〕"] + lines,
             fc="white", ec=col, title_color=col, body_color="#333333",
             title_fs=13.5, body_fs=10.2)

    # 阵营分组底纹标注（闭源 / 开放权重 / 开源）
    ax.text((centers[0] + centers[1]) / 2, 87.2, "闭源阵营", ha="center",
            color=C_CLOSED, fontsize=12.5, fontweight="bold")
    ax.text(centers[2], 87.2, "开放权重", ha="center",
            color=C_GOLD, fontsize=12.5, fontweight="bold")
    ax.text((centers[3] + centers[4]) / 2, 87.2, "开源阵营", ha="center",
            color=C_GREEN, fontsize=12.5, fontweight="bold")

    # ---------------- 第二层：基础博弈 ----------------
    ax.text(50, 67.0, "第二层　基础博弈与均衡", ha="center", va="center",
            fontsize=14.5, fontweight="bold", color="#333333")

    gw = 40
    gh = 13.5
    gy = 57.5
    # 静态博弈
    _box(ax, 28, gy, gw, gh, "静态博弈（图2）",
         ["三方同时选择开源/闭源；支付由 §2.4 支付函数计算",
          "可占优求解，唯一纳什均衡 (C, O, O)，支付 (13.1, 6.5, 8.8)"],
         fc=C_LIGHT, ec=C_PRIMARY_2, title_color=C_PRIMARY, body_color="#222222",
         title_fs=13, body_fs=10.4)
    # 序贯博弈
    _box(ax, 72, gy, gw, gh, "序贯博弈（图3）",
         ["OpenAI 先动 → Meta → DeepSeek，逆向归纳",
          "子博弈完美均衡路径与纳什一致： (C, O, O)"],
         fc=C_LIGHT, ec=C_PRIMARY_2, title_color=C_PRIMARY, body_color="#222222",
         title_fs=13, body_fs=10.4)

    # 均衡结论条
    _box(ax, 50, 47.5, 60, 5.6, "",
         ["核心均衡： (闭源, 开源, 开源) = (OpenAI 闭源, Meta 开源, DeepSeek 开源)"],
         fc=C_ACCENT, ec=C_ACCENT, body_color="white", body_fs=12,
         draw_title_rule=False, body_valign="center", body_y_shift=0.3)

    # 参与人 → 基础博弈 连接
    for cx in centers:
        _arrow(ax, cx, cy - cardh / 2 - 0.2, 50, 64.6, color="#B8C4D0", lw=1.2)

    # ---------------- 第三层：三项扩展改进 ----------------
    ax.text(50, 41.3, "第三层　三项扩展改进与均衡变化", ha="center", va="center",
            fontsize=14.5, fontweight="bold", color="#333333")

    iw = 30
    ih = 17.5
    iy = 28.5
    icx = [18.5, 50, 81.5]
    _box(ax, icx[0], iy, iw, ih, "改进①　演化博弈 + 监管（图4）",
         ["群体复制动态 dx/dt = x(1-x)[π_O-π_C]",
          "演化稳定策略 ESS（开源比例）：",
          "基线 0.667　欧盟 0.333",
          "中国 0.867　美国 0.600"],
         fc="white", ec=C_GREEN, title_color=C_GREEN, body_color="#222222",
         title_fs=11.8, body_fs=10)
    _box(ax, icx[1], iy, iw, ih, "改进②　贝叶斯信号（图5）",
         ["DeepSeek 成本类型不完全信息",
          "技术报告 + 全球复现作为可验证信号",
          "成本类型后验信念：",
          "0.10 → 1.00（Spence 分离均衡）"],
         fc="white", ec=C_GOLD, title_color="#B8860B", body_color="#222222",
         title_fs=11.8, body_fs=10)
    _box(ax, icx[2], iy, iw, ih, "改进③　重复博弈（图6）",
         ["差异化伯特兰推导单期支付",
          "临界贴现因子 δ* = 0.529",
          "双因子 δ_eff = δ_base(1-I)(1-λ)",
          "临界颠覆强度 I* = 0.377"],
         fc="white", ec=C_ACCENT, title_color=C_ACCENT, body_color="#222222",
         title_fs=11.8, body_fs=10)

    # 均衡结论条 → 三改进 连接
    for cx in icx:
        _arrow(ax, 50, 44.6, cx, iy + ih / 2 + 0.2, color="#B8C4D0", lw=1.3)

    # ---------------- 页脚 ----------------
    ax.add_patch(FancyBboxPatch((6, 4.2), 88, 6.2,
                                boxstyle="round,pad=0.2,rounding_size=2.0",
                                linewidth=1.0, edgecolor=C_GREY, facecolor="#F7F9FC",
                                zorder=1))
    ax.text(50, 8.4, "数据截止日：2026 年 5 月 28 日　｜　结论：开源已成不可逆均衡力量，闭源前沿与开源生态长期并存",
            ha="center", va="center", fontsize=11.8, color=C_PRIMARY, fontweight="bold")
    ax.text(50, 5.9, "全部图表均为中文标注，可由 代码/ 目录下脚本（01–06）独立运行、1:1 复现；关键事实均有公开来源（见 数据来源.md）",
            ha="center", va="center", fontsize=10.2, color=C_GREY)

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig = make_figure()
    save_fig(fig, "fig1_overview.png")
    print("[完成] 框架总览图已生成")
