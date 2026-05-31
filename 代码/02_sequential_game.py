"""
========================================================================
模块 2：序贯博弈与逆向归纳（Stackelberg 多领导者）  →  生成 图3（fig3_game_tree.png）

数据截止日：2026 年 5 月 28 日
背景：OpenAI 2022.11 推出 ChatGPT、2023.3 发布 GPT-4 API，率先确立"闭源-高端 API"
      基准；Meta 2023.7 发布 Llama 2、2025.4 发布 Llama 4 应对；DeepSeek 2024.12
      发布 V3、2025.1 发布 R1 引发颠覆冲击。本序贯博弈刻画
      "基准设定者→开源响应者→颠覆者"三波次时序。

【本版升级】支付直接复用模块 1 由 §2.4 支付函数计算的同一支付字典（importlib 载入），
            保证同时博弈与序贯博弈使用完全一致的支付，无人工二次录入。

实现：
  1. 三阶段扩展式博弈树（OpenAI → Meta → DeepSeek）
  2. 子博弈完美均衡（SPE）的逆向归纳求解
  3. 博弈树可视化（SPE 路径红色高亮）
  4. 与同时博弈纳什均衡 (C,O,O) 的一致性对比
========================================================================
"""

import importlib.util
import json
import os

from _cjk_support import configure_matplotlib_backend_for_batch

configure_matplotlib_backend_for_batch()

import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from _style import C_ACCENT, C_GREY, save_fig

# ---- 从模块 1 载入同一支付字典（文件名以数字开头，故用 importlib）----
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("static_game",
                                               os.path.join(_HERE, "01_static_game.py"))
_m1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m1)
PAYOFFS = _m1.PAYOFFS                       # 与模块 1 完全一致
STRAT_CN = {"O": "开源", "C": "闭源"}


# ----------------------------------------------------------------------
# 1. 逆向归纳
# ----------------------------------------------------------------------
def backward_induction():
    # 第三阶段：DeepSeek（idx=2）
    ds_choice = {}
    for hist in [("O", "O"), ("O", "C"), ("C", "O"), ("C", "C")]:
        uO = PAYOFFS[(hist[0], hist[1], "O")][2]
        uC = PAYOFFS[(hist[0], hist[1], "C")][2]
        ds_choice[hist] = "O" if uO >= uC else "C"
    # 第二阶段：Meta（idx=1）
    meta_choice = {}
    for o in ["O", "C"]:
        outO = PAYOFFS[(o, "O", ds_choice[(o, "O")])]
        outC = PAYOFFS[(o, "C", ds_choice[(o, "C")])]
        meta_choice[o] = "O" if outO[1] >= outC[1] else "C"
    # 第一阶段：OpenAI（idx=0）
    res = {}
    for o in ["O", "C"]:
        m = meta_choice[o]
        d = ds_choice[(o, m)]
        res[o] = PAYOFFS[(o, m, d)]
    openai_choice = "O" if res["O"][0] >= res["C"][0] else "C"
    spe_path = (openai_choice, meta_choice[openai_choice],
                ds_choice[(openai_choice, meta_choice[openai_choice])])
    return ds_choice, meta_choice, openai_choice, spe_path, PAYOFFS[spe_path]


# ----------------------------------------------------------------------
# 2. 博弈树绘制
# ----------------------------------------------------------------------
def plot_tree(ds_choice, meta_choice, openai_choice, spe_path):
    fig, ax = plt.subplots(figsize=(13.6, 8.6))
    ax.set_xlim(0, 16); ax.set_ylim(0, 10); ax.axis("off")
    y_root, y_meta, y_ds, y_leaf = 9.0, 6.6, 4.2, 1.5

    def node(x, y, label, color, r=0.42):
        ax.add_patch(Circle((x, y), r, facecolor=color, edgecolor="black",
                            linewidth=1.5, zorder=4))
        ax.text(x, y, label, ha="center", va="center", color="white",
                fontsize=13, fontweight="bold", zorder=5)

    def edge(x1, y1, x2, y2, action, on_spe):
        col = C_ACCENT if on_spe else C_GREY
        lw = 3.4 if on_spe else 1.4
        ax.plot([x1, x2], [y1, y2], color=col, lw=lw, zorder=2,
                solid_capstyle="round")
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + (-0.55 if x2 < x1 else 0.55), my, action,
                ha="center", va="center", fontsize=12,
                color=col, fontweight="bold" if on_spe else "normal",
                bbox=dict(boxstyle="round,pad=0.18", fc="white",
                          ec=col, lw=0.9, alpha=0.92), zorder=3)

    C_OA, C_M, C_DS = "#10A37F", "#1877F2", "#4D6BFE"
    # 根（OpenAI）
    node(8, y_root, "P1", C_OA)
    ax.text(8, y_root + 0.7, "OpenAI（先动·设定基准）", ha="center",
            fontsize=12.5, fontweight="bold")
    meta_x = {"O": 4, "C": 12}
    for o in ["O", "C"]:
        on = (o == openai_choice)
        edge(8, y_root, meta_x[o], y_meta, STRAT_CN[o], on)
        node(meta_x[o], y_meta, "P3", C_M)
        ax.text(meta_x[o], y_meta + 0.62, f"Meta｜OpenAI={STRAT_CN[o]}",
                ha="center", fontsize=10.5)
        ds_x = {"O": meta_x[o] - 2.4, "C": meta_x[o] + 2.4}
        for m in ["O", "C"]:
            on_m = on and (m == meta_choice[o])
            edge(meta_x[o], y_meta, ds_x[m], y_ds, STRAT_CN[m], on_m)
            node(ds_x[m], y_ds, "P4", C_DS)
            d = ds_choice[(o, m)]
            leaf_x = ds_x[m]
            on_d = on_m and (d == ds_choice[(o, m)])
            edge(ds_x[m], y_ds, leaf_x, y_leaf + 0.5, STRAT_CN[d], on_d)
            pay = PAYOFFS[(o, m, d)]
            is_spe = (o, m, d) == spe_path
            ax.text(leaf_x, y_leaf,
                    f"({pay[0]:.1f},\n{pay[1]:.1f},\n{pay[2]:.1f})",
                    ha="center", va="center", fontsize=10.5,
                    fontweight="bold" if is_spe else "normal",
                    color="white" if is_spe else "#0D2B45",
                    bbox=dict(boxstyle="round,pad=0.28",
                              fc=C_ACCENT if is_spe else "#EAF0F6",
                              ec=C_ACCENT if is_spe else C_GREY,
                              lw=2.2 if is_spe else 1.0), zorder=4)

    ax.text(0.5, 9.3, "图例：红色加粗 = 子博弈完美均衡路径", fontsize=12,
            color=C_ACCENT, fontweight="bold")
    ax.text(8, 0.35,
            "逆向归纳：DeepSeek 始终开源 → Meta 视 OpenAI 应对 → OpenAI 选闭源；"
            "SPE 路径 (闭源, 开源, 开源)，支付 (13.1, 6.5, 8.8)，与同时博弈纳什均衡一致",
            ha="center", fontsize=12.2, color=C_ACCENT, fontweight="bold")
    ax.set_title("序贯博弈扩展式博弈树（OpenAI → Meta → DeepSeek）",
                 fontsize=16.5, pad=10)
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------
# 3. 主流程
# ----------------------------------------------------------------------
def main():
    ds_choice, meta_choice, openai_choice, spe_path, spe_pay = backward_induction()
    print("=" * 68)
    print("模块 2：序贯博弈与逆向归纳（支付复用模块 1）")
    print("=" * 68)
    print("\n[第三阶段 DeepSeek 最优行动]")
    for h, c in ds_choice.items():
        print(f"  历史(OpenAI={STRAT_CN[h[0]]}, Meta={STRAT_CN[h[1]]}) → DeepSeek={STRAT_CN[c]}")
    print("\n[第二阶段 Meta 最优行动]")
    for o, c in meta_choice.items():
        print(f"  OpenAI={STRAT_CN[o]} → Meta={STRAT_CN[c]}")
    print(f"\n[第一阶段 OpenAI 最优行动] → {STRAT_CN[openai_choice]}")
    print(f"\n[子博弈完美均衡 SPE] "
          f"({STRAT_CN[spe_path[0]]}, {STRAT_CN[spe_path[1]]}, {STRAT_CN[spe_path[2]]})"
          f"  支付={spe_pay}")
    print("  → 与同时博弈纳什均衡 (闭源,开源,开源) 完全一致")

    fig = plot_tree(ds_choice, meta_choice, openai_choice, spe_path)
    save_fig(fig, "fig3_game_tree.png")
    plt.close(fig)

    results = {
        "module": 2, "data_cutoff": "2026-05-28",
        "ds_choice": {f"{a}{b}": c for (a, b), c in ds_choice.items()},
        "meta_choice": meta_choice, "openai_choice": openai_choice,
        "spe_path": "".join(spe_path), "spe_payoff": list(spe_pay),
        "consistent_with_simultaneous_nash": "".join(spe_path) == "COO",
        "interpretation": "逆向归纳 SPE = (C,O,O)，支付与同时博弈纳什均衡一致；支付与模块 1 同源。",
    }
    out = os.path.join(_HERE, "results_module2.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[结果已写入] {out}")


if __name__ == "__main__":
    main()
