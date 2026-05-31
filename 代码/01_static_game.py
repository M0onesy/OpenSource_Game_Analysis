"""
========================================================================
模块 1：基础静态博弈与纳什均衡求解  →  生成 图2（fig2_payoff_matrix.png）

数据截止日：2026 年 5 月 28 日

【本版升级】支付不再外生赋值，而是由论文 §2.4 的支付函数实例化后计算得到：
  U_i(s_i, s_{-i}) = R_i^API·1[s_i=C]  +  α_i·E(n_O)·1[s_i=O]
                     +  V_i(s_i)  −  κ·(c_i^train / c_ref)·m(s_i)
其中各分量按真实产业数据或公开证据标定（见下方 PARAMS 注释与论文 §3.1）。
随后由迭代剔除严格劣势策略证明博弈"可占优求解"，给出唯一纯策略纳什均衡 (C,O,O)。

参数标定依据：
  - 训练算力成本 c^train：OpenAI≈$78M(Epoch AI)、Meta Llama3.1-405B≈$170M
    (Stanford AI Index 2025)、DeepSeek-V3=$5.576M(技术报告 arXiv:2412.19437)，
    比值 OpenAI:Meta:DeepSeek ≈ 14:30:1（代码内由原始美元值实时计算）。
  - API 货币化强度 base、生态权重 α、品牌价值 V：按市场地位与公开战略证据标定，
    其"序数排序"为稳健结论（详见论文 §3.1 表）。
========================================================================
"""

import json
import os
from itertools import product

import numpy as np
from _cjk_support import configure_matplotlib_backend_for_batch

configure_matplotlib_backend_for_batch()

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from _style import C_ACCENT, save_fig

# ----------------------------------------------------------------------
# 1. 支付函数的原始量（PRIMITIVES）—— §2.4 的实例化
# ----------------------------------------------------------------------
PLAYERS = ["OpenAI", "Meta", "DeepSeek"]
STRATS = ["O", "C"]                       # O=开源, C=闭源
STRAT_CN = {"O": "开源", "C": "闭源"}

# (a) 训练算力成本（百万美元，真实数据）→ 以 DeepSeek 为基准取比值 ≈ 14:30:1
C_TRAIN_USD = {"OpenAI": 78.0, "Meta": 170.0, "DeepSeek": 5.576}
C_REF = C_TRAIN_USD["DeepSeek"]
C_RATIO = {k: v / C_REF for k, v in C_TRAIN_USD.items()}

# (b) API 货币化强度 base_i：独家闭源时可获取的高端 API 利润（效用单位）
#     标定依据：OpenAI 消费端约 8 亿周活 + 先发分发；Meta 具备但以广告为主；
#     DeepSeek 为后入场者、缺乏企业级分发，闭源变现能力最弱。
BASE_API = {"OpenAI": 12.0, "Meta": 7.0, "DeepSeek": 4.0}

# (c) 生态权重 α_i：开源生态对该公司主营的战略价值（"互补品商品化"程度）
ALPHA = {"OpenAI": 0.5, "Meta": 1.4, "DeepSeek": 1.2}

# (d) 品牌/战略价值 V_i(策略)
V_OPEN = {"OpenAI": 1.0, "Meta": 2.0, "DeepSeek": 3.5}     # 开源品牌（颠覆叙事放大 DeepSeek）
V_CLOSED = {"OpenAI": 2.5, "Meta": 0.5, "DeepSeek": 0.3}   # 闭源前沿领导者品牌

# (e) 共享标定参数
E0, TAU = 6.0, 1.5            # 独家开源生态价值 / 每多一家开源者的拥挤折损
KAPPA = 0.10                  # 成本权重：将 14:30:1 缩放到与其它效用项可比
M_CLOSED, M_OPEN = 1.0, 0.6   # 维护乘子：闭源需全额前沿研发+推理基建；开源约 40% 由社区分担


# ----------------------------------------------------------------------
# 2. 由支付函数计算每个策略组合的支付
# ----------------------------------------------------------------------
def payoff_components(i, profile):
    """返回参与人 i 在 profile 下的各支付分量（用于论文逐项展示）。"""
    name = PLAYERS[i]
    s_i = profile[i]
    n_closed = sum(1 for s in profile if s == "C")
    n_open = 3 - n_closed
    r_api = (BASE_API[name] / n_closed) if s_i == "C" else 0.0
    eco = ALPHA[name] * max(0.0, E0 - TAU * (n_open - 1)) if s_i == "O" else 0.0
    v = V_OPEN[name] if s_i == "O" else V_CLOSED[name]
    cost = KAPPA * C_RATIO[name] * (M_OPEN if s_i == "O" else M_CLOSED)
    return r_api, eco, v, cost


def payoff(i, profile):
    r_api, eco, v, cost = payoff_components(i, profile)
    return r_api + eco + v - cost


# 由函数构建支付字典（键：(s_OpenAI, s_Meta, s_DeepSeek)；值：三元组）
PAYOFFS = {prof: tuple(round(payoff(i, prof), 2) for i in range(3))
           for prof in product(STRATS, repeat=3)}


# ----------------------------------------------------------------------
# 3. 纳什均衡、占优与"可占优求解"验证
# ----------------------------------------------------------------------
def find_pure_nash():
    eq = []
    for prof in product(STRATS, repeat=3):
        ok = True
        for i in range(3):
            cur = payoff(i, prof)
            for alt in STRATS:
                if alt == prof[i]:
                    continue
                new = list(prof); new[i] = alt
                if payoff(i, tuple(new)) > cur + 1e-9:
                    ok = False; break
            if not ok:
                break
        if ok:
            eq.append(prof)
    return eq


def deepseek_dominance():
    rows = []
    for combo in product(STRATS, repeat=2):
        uO = payoff(2, (combo[0], combo[1], "O"))
        uC = payoff(2, (combo[0], combo[1], "C"))
        rows.append((combo, uO, uC, uO > uC + 1e-9))
    return rows


def iterated_dominance():
    """迭代剔除严格劣势策略：返回三步结论是否成立。"""
    # Step1：DeepSeek 开源严格占优
    ds_dom = all(payoff(2, (a, b, "O")) > payoff(2, (a, b, "C")) + 1e-9
                 for a, b in product(STRATS, repeat=2))
    # Step2：给定 DeepSeek=O，OpenAI 闭源对开源严格占优
    oa_dom = all(payoff(0, ("C", m, "O")) > payoff(0, ("O", m, "O")) + 1e-9
                 for m in STRATS)
    # Step3：给定 OpenAI=C、DeepSeek=O，Meta 开源严格优于闭源
    meta_pick = payoff(1, ("C", "O", "O")) > payoff(1, ("C", "C", "O")) + 1e-9
    return ds_dom, oa_dom, meta_pick


# ----------------------------------------------------------------------
# 4. 绘图：固定 DeepSeek=开源 的 2×2 支付热力图（按推导值）
# ----------------------------------------------------------------------
def plot_payoff_matrix(nash_set):
    fig, ax = plt.subplots(figsize=(8.8, 7.2))
    cells = [("O", "O"), ("O", "C"), ("C", "O"), ("C", "C")]
    grid = np.zeros((2, 2))
    for sO, sM in cells:
        grid[STRATS.index(sO), STRATS.index(sM)] = PAYOFFS[(sO, sM, "O")][0]

    im = ax.imshow(grid, cmap="Blues", vmin=1, vmax=13, alpha=0.92)
    for k in range(3):
        ax.axhline(k - 0.5, color="white", linewidth=3)
        ax.axvline(k - 0.5, color="white", linewidth=3)

    for sO, sM in cells:
        r, c = STRATS.index(sO), STRATS.index(sM)
        pay = PAYOFFS[(sO, sM, "O")]
        is_nash = (sO, sM, "O") in nash_set
        uO_alt = PAYOFFS[("C" if sO == "O" else "O", sM, "O")][0]
        uM_alt = PAYOFFS[(sO, "C" if sM == "O" else "O", "O")][1]
        openai_br = pay[0] >= uO_alt - 1e-9
        meta_br = pay[1] >= uM_alt - 1e-9
        txt_color = "#0D2B45" if grid[r, c] < 8 else "white"
        ax.text(c, r - 0.16, f"({pay[0]:.1f}, {pay[1]:.1f}, {pay[2]:.1f})",
                ha="center", va="center", fontsize=18.5, fontweight="bold",
                color=txt_color)
        tags = []
        if openai_br:
            tags.append("OpenAI")
        if meta_br:
            tags.append("Meta")
        if tags:
            label = "、".join(tags) + " 最优反应"
            ax.text(c, r + 0.16, label, ha="center", va="center",
                    fontsize=11.5, color=txt_color, style="italic")
        if is_nash:
            ax.add_patch(Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False,
                                   edgecolor=C_ACCENT, linewidth=4, zorder=5))
            ax.text(c + 0.34, r - 0.34, "★", ha="center", va="center",
                    fontsize=20, color=C_ACCENT, zorder=6)

    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["Meta：开源", "Meta：闭源"], fontsize=15)
    ax.set_yticklabels(["OpenAI：开源", "OpenAI：闭源"], fontsize=15,
                       rotation=90, va="center")
    ax.tick_params(length=0)
    ax.set_title("三方静态博弈支付矩阵（固定 DeepSeek＝开源）\n"
                 "三元组＝(OpenAI, Meta, DeepSeek)，由 §2.4 支付函数计算；红框★为唯一纳什均衡",
                 fontsize=15.5, pad=16)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("OpenAI 支付（效用单位）", fontsize=13)
    ax.text(0.5, -0.16,
            "唯一纯策略纳什均衡（闭源, 开源, 开源），支付 (13.1, 6.5, 8.8)，由迭代剔除严格劣势策略可占优求解",
            transform=ax.transAxes, ha="center", va="top", fontsize=12.5,
            color=C_ACCENT, fontweight="bold")
    fig.tight_layout()
    return fig


# ----------------------------------------------------------------------
# 5. 主流程
# ----------------------------------------------------------------------
def main():
    nash = find_pure_nash()
    nash_set = set(nash)
    dom = deepseek_dominance()
    ds_dom, oa_dom, meta_pick = iterated_dominance()

    print("=" * 68)
    print("模块 1：三方静态博弈（支付由 §2.4 支付函数实例化计算）")
    print("=" * 68)
    print(f"\n训练成本比 (OpenAI:Meta:DeepSeek) = "
          f"{C_RATIO['OpenAI']:.1f} : {C_RATIO['Meta']:.1f} : {C_RATIO['DeepSeek']:.1f}")
    print("\n[全部 8 个策略组合的推导支付]（OpenAI, Meta, DeepSeek）")
    for prof in product(STRATS, repeat=3):
        mark = "  ← 纳什均衡" if prof in nash_set else ""
        print(f"  ({STRAT_CN[prof[0]]},{STRAT_CN[prof[1]]},{STRAT_CN[prof[2]]}) "
              f"= {PAYOFFS[prof]}{mark}")

    print("\n[纳什均衡支付的逐项分解]（以 (闭源, 开源, 开源) 为例）")
    for i, prof_lbl in zip(range(3), ["OpenAI(C)", "Meta(O)", "DeepSeek(O)"]):
        r_api, eco, v, cost = payoff_components(i, ("C", "O", "O"))
        print(f"  {prof_lbl}: API={r_api:.2f} + 生态={eco:.2f} + 品牌={v:.2f} "
              f"− 成本={cost:.2f} = {r_api + eco + v - cost:.2f}")

    print("\n[纯策略纳什均衡]")
    for ne in nash:
        print(f"  ({STRAT_CN[ne[0]]}, {STRAT_CN[ne[1]]}, {STRAT_CN[ne[2]]})"
              f"  支付={PAYOFFS[ne]}")

    print("\n[DeepSeek 占优性验证]")
    for combo, uO, uC, strict in dom:
        print(f"  对手(OpenAI={STRAT_CN[combo[0]]}, Meta={STRAT_CN[combo[1]]}): "
              f"开源={uO:.2f} vs 闭源={uC:.2f} → "
              f"{'开源严格占优' if strict else '非严格'}")

    print("\n[可占优求解 / 迭代剔除严格劣势]")
    print(f"  ① DeepSeek 开源严格占优 = {ds_dom} → 剔除 DeepSeek 闭源")
    print(f"  ② 给定 DeepSeek=开源，OpenAI 闭源严格占优 = {oa_dom} → 剔除 OpenAI 开源")
    print(f"  ③ 给定 OpenAI=闭源、DeepSeek=开源，Meta 选开源 = {meta_pick}")
    print(f"  ⇒ 博弈可占优求解，唯一纳什均衡 (C,O,O)，故不存在混合策略纳什均衡")

    fig = plot_payoff_matrix(nash_set)
    save_fig(fig, "fig2_payoff_matrix.png")
    plt.close(fig)

    results = {
        "module": 1,
        "data_cutoff": "2026-05-28",
        "payoff_function": "U_i = R_api*1[C] + alpha*E(n_O)*1[O] + V_i(s) - kappa*(c_i/c_ref)*m(s)",
        "primitives": {
            "C_TRAIN_USD_million": C_TRAIN_USD,
            "cost_ratio": {k: round(v, 2) for k, v in C_RATIO.items()},
            "BASE_API": BASE_API, "ALPHA": ALPHA,
            "V_OPEN": V_OPEN, "V_CLOSED": V_CLOSED,
            "E0": E0, "TAU": TAU, "KAPPA": KAPPA,
            "M_CLOSED": M_CLOSED, "M_OPEN": M_OPEN,
        },
        "payoff_matrix": {"".join(k): list(v) for k, v in PAYOFFS.items()},
        "pure_nash_equilibria": ["".join(ne) for ne in nash],
        "nash_payoff": list(PAYOFFS[nash[0]]) if nash else None,
        "deepseek_open_strictly_dominant": all(t[3] for t in dom),
        "dominance_solvable": bool(ds_dom and oa_dom and meta_pick),
        "interpretation": "支付由支付函数计算；博弈可占优求解，唯一纳什均衡 (C,O,O)，与现实格局吻合",
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_module1.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[结果已写入] {out}")


if __name__ == "__main__":
    main()
