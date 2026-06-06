#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the site data layer consumed by index.html."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / "代码"
OUT_FILE = ROOT / "site-data.js"


def load_json(name: str) -> dict:
    with (CODE_DIR / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


mod1 = load_json("results_module1.json")
mod2 = load_json("results_module2.json")
mod3 = load_json("results_module3.json")
mod4 = load_json("results_module4.json")
mod5 = load_json("results_module5.json")

players = ["OpenAI", "Meta", "DeepSeek"]
p1 = mod1["primitives"]

site_data = {
    "meta": {
        "title": "开源，还是闭源？",
        "subtitle": "大模型公司战略选择的博弈论分析",
        "courseLabel": "博弈论课程论文展示",
        "dataCutoff": mod1["data_cutoff"],
        "dataCutoffDisplay": "2026 年 5 月 28 日",
        "repoUrl": "https://github.com/M0onesy/OpenSource_Game_Analysis",
        "repoLabel": "github.com/M0onesy/OpenSource_Game_Analysis",
        "paperUrl": "./论文/大模型博弈论分析_论文.md",
        "paperLabel": "论文 Markdown",
        "dataUrl": "./数据来源.md",
        "dataLabel": "数据来源清单",
        "resultBasePath": "./代码/",
    },
    "slides": [
        {"id": "cover", "name": "封面", "paperSection": "摘要 / 导入", "figure": "图 1", "model": "总览"},
        {"id": "question", "name": "问题", "paperSection": "§1.2", "figure": "—", "model": "研究问题"},
        {"id": "roadmap", "name": "路线图", "paperSection": "全文结构", "figure": "图 1", "model": "分析路线"},
        {"id": "players", "name": "玩家", "paperSection": "§2.1", "figure": "表 1", "model": "参与人"},
        {"id": "timeline", "name": "转折", "paperSection": "§1.1", "figure": "—", "model": "产业演进"},
        {"id": "stats", "name": "数字", "paperSection": "附录 B", "figure": "—", "model": "关键事实"},
        {"id": "payoff-function", "name": "支付函数", "paperSection": "§2.4", "figure": "—", "model": "支付函数"},
        {"id": "parameterization", "name": "参数标定", "paperSection": "§2.4 / 表 2-0", "figure": "—", "model": "参数标定"},
        {"id": "static-game", "name": "静态博弈", "paperSection": "§3.1", "figure": "图 2", "model": "模型一"},
        {"id": "dominance", "name": "占优求解", "paperSection": "§3.1", "figure": "图 2", "model": "模型一"},
        {"id": "sequential-game", "name": "序贯博弈", "paperSection": "§3.2", "figure": "图 3", "model": "模型二"},
        {"id": "evolutionary-game", "name": "演化博弈", "paperSection": "§4", "figure": "图 4", "model": "模型三"},
        {"id": "evolutionary-compare", "name": "演化对照", "paperSection": "§4 / 表 3", "figure": "图 4", "model": "模型三"},
        {"id": "signal-game", "name": "信号博弈", "paperSection": "§5", "figure": "图 5", "model": "模型四"},
        {"id": "price-timeline", "name": "价格时间线", "paperSection": "§5", "figure": "图 5", "model": "现实印证"},
        {"id": "repeated-game", "name": "重复博弈", "paperSection": "§6", "figure": "图 6", "model": "模型五"},
        {"id": "comparison", "name": "模型对比", "paperSection": "§7", "figure": "—", "model": "综合"},
        {"id": "prediction", "name": "预测", "paperSection": "§7", "figure": "—", "model": "趋势研判"},
        {"id": "credibility", "name": "可信度", "paperSection": "研究局限", "figure": "—", "model": "方法评价"},
        {"id": "closing", "name": "结束", "paperSection": "附录 A / B", "figure": "图 1-6", "model": "资料入口"},
    ],
    "stats": [
        {
            "value": -589,
            "prefix": "$",
            "suffix": "B",
            "decimals": 0,
            "cap": "英伟达 1 月 27 日单日蒸发的市值",
            "src": "Bloomberg / CNBC",
        },
        {
            "value": 5.576,
            "prefix": "$",
            "suffix": "M",
            "decimals": 3,
            "cap": "DeepSeek-V3 披露的训练成本，约为 GPT-4 的 1/14",
            "src": "arXiv:2412.19437",
        },
        {
            "value": 95.8,
            "prefix": "",
            "suffix": "%",
            "decimals": 1,
            "cap": "GPT-5 输入价相对 GPT-4 的降幅",
            "src": "$30 → $1.25",
        },
        {
            "value": 1.7,
            "prefix": "",
            "suffix": "pp",
            "decimals": 1,
            "cap": "最强开源与最强闭源的能力差距",
            "src": "已收敛至约 1.7 个百分点",
        },
    ],
    "industryTimeline": [
        {
            "year": "2023",
            "phase": "闭源主导",
            "title": "闭源模式确立",
            "body": "OpenAI 以 GPT-4 确立“闭源 API + 高价”模式，与 Anthropic、Google 共同维持高位价格协调。同年 Meta 发布 Llama 2 开放权重，开源路线起步。",
        },
        {
            "year": "2024",
            "phase": "开源逼近前沿",
            "title": "能力差距收窄",
            "body": "Meta 接连发布 Llama 3，阿里 Qwen 全面开源。12 月 26 日 DeepSeek 在 V3 技术报告中披露训练成本约 557.6 万美元，开源阵营首次在能力而非可得性上逼近闭源前沿。",
        },
        {
            "year": "25–26",
            "phase": "价格战与监管分化",
            "title": "格局重排",
            "body": "R1 发布后英伟达 1 月 27 日单日下跌约 17%。OpenAI 发布 gpt-oss，并将 GPT-5 输入价降至 1.25 美元（较 GPT-4 下降约 95.8%）。各辖区监管走向分化；2026 年 5 月 28 日 Anthropic 估值反超 OpenAI。",
        },
    ],
    "resources": {
        "documents": [
            {
                "label": "论文 Markdown",
                "href": "./论文/大模型博弈论分析_论文.md",
                "kind": "论文正文",
                "desc": "完整论文正文与附录。",
            },
            {
                "label": "数据来源清单",
                "href": "./数据来源.md",
                "kind": "事实核验",
                "desc": "关键事实、文献与监管出处。",
            },
            {
                "label": "仓库主页",
                "href": "https://github.com/M0onesy/OpenSource_Game_Analysis",
                "kind": "开源仓库",
                "desc": "网站、代码与论文资源总入口。",
            },
            {
                "label": "模块结果 JSON",
                "href": "./代码/results_module1.json",
                "kind": "结果文件",
                "desc": "模型计算结果基线，另含 module2-5。",
            },
        ],
        "figures": [
            {"label": "图 1 · 模型总览", "href": "./图表/fig1_overview.png"},
            {"label": "图 2 · 静态博弈", "href": "./图表/fig2_payoff_matrix.png"},
            {"label": "图 3 · 序贯博弈", "href": "./图表/fig3_game_tree.png"},
            {"label": "图 4 · 演化博弈", "href": "./图表/fig4_evolutionary.png"},
            {"label": "图 5 · 信号博弈", "href": "./图表/fig5_bayesian_signal.png"},
            {"label": "图 6 · 重复博弈", "href": "./图表/fig6_repeated_game.png"},
        ],
        "results": [
            {"label": "module1", "href": "./代码/results_module1.json"},
            {"label": "module2", "href": "./代码/results_module2.json"},
            {"label": "module3", "href": "./代码/results_module3.json"},
            {"label": "module4", "href": "./代码/results_module4.json"},
            {"label": "module5", "href": "./代码/results_module5.json"},
        ],
    },
    "sources": {
        "stats": [
            {
                "type": "事实数据",
                "title": "NVIDIA 单日蒸发约 $589B",
                "detail": "对应 2025-01-27 DeepSeek-R1 冲击后的市场反应。",
                "href": "./数据来源.md",
            },
            {
                "type": "事实数据",
                "title": "DeepSeek-V3 训练成本 $5.576M",
                "detail": "来自 arXiv:2412.19437 披露的 2.788M H800 GPU 小时。",
                "href": "./数据来源.md",
            },
            {
                "type": "事实数据",
                "title": "GPT-5 输入价较 GPT-4 下降 95.8%",
                "detail": "论文与数据来源清单统一按 $30 → $1.25 口径计算。",
                "href": "./数据来源.md",
            },
            {
                "type": "事实数据",
                "title": "开源与闭源能力差收敛至约 1.7pp",
                "detail": "采用 Stanford AI Index 2025 更正后的口径。",
                "href": "./数据来源.md",
            },
        ],
        "evolution": [
            {
                "type": "模型设定",
                "title": "复制动态与四个监管情景",
                "detail": "稳态由 module5 的 ESS 结果生成，表中数值与 `results_module5.json` 同步。",
                "href": "./代码/results_module5.json",
            },
            {
                "type": "事实数据",
                "title": "EU AI Act / SB53 / EO 14179 / “AI+” 行动",
                "detail": "reg 的方向性标定来自论文与数据来源中的政策梳理，不是实测统计值。",
                "href": "./数据来源.md",
            },
            {
                "type": "模型推论",
                "title": "0.33–0.87 的区域稳态",
                "detail": "网站展示的是模型推导结果，用来和现实区域格局作对照，不等同于观测数据。",
                "href": "./论文/大模型博弈论分析_论文.md",
            },
        ],
        "price": [
            {
                "type": "事实数据",
                "title": "价格时间线",
                "detail": "GPT-4、Turbo、4o、GPT-5 的输入价口径沿用论文与数据来源清单。",
                "href": "./数据来源.md",
            },
            {
                "type": "模型设定",
                "title": "信号失效的价格解释",
                "detail": "本页的解释承接 module3 的后验信念跃迁，而非单纯市场叙事。",
                "href": "./代码/results_module3.json",
            },
            {
                "type": "模型推论",
                "title": "高价=高质量信号被击穿",
                "detail": "这是论文对价格战的博弈论解释，区别于原始事实本身。",
                "href": "./论文/大模型博弈论分析_论文.md",
            },
        ],
        "closing": [
            {
                "type": "事实数据",
                "title": "数据截至 2026-05-28",
                "detail": "所有产业事实与关键事件统一按该日期口径核实。",
                "href": "./数据来源.md",
            },
            {
                "type": "模型设定",
                "title": "交互默认值即论文基线",
                "detail": "静态、序贯、演化、信号、重复博弈的默认参数与结果文件逐一对应。",
                "href": "./代码/results_module1.json",
            },
            {
                "type": "复现说明",
                "title": "代码与图表可 1:1 复现",
                "detail": "图 1-6 与 `run_all.py` / `build_paper.py` 构成完整复现链。",
                "href": "./README.md",
            },
        ],
    },
    "module1": {
        "dataCutoff": mod1["data_cutoff"],
        "defaultProfile": "COO",
        "defaultProfileLabel": "(闭, 开, 开)",
        "defaultProfileText": "OpenAI 闭源 · Meta 开源 · DeepSeek 开源",
        "nashPayoff": mod1["nash_payoff"],
        "payoffMatrix": mod1["payoff_matrix"],
        "defaults": {
            "base": [p1["BASE_API"][name] for name in players],
            "alpha": [p1["ALPHA"][name] for name in players],
            "Vo": [p1["V_OPEN"][name] for name in players],
            "Vc": [p1["V_CLOSED"][name] for name in players],
            "cost": [p1["C_TRAIN_USD_million"][name] for name in players],
            "costRatio": [p1["cost_ratio"][name] for name in players],
            "E0": p1["E0"],
            "tau": p1["TAU"],
            "kappa": p1["KAPPA"],
            "mC": p1["M_CLOSED"],
            "mO": p1["M_OPEN"],
        },
        "highlights": {
            "openaiClosed": mod1["payoff_matrix"]["COO"][0],
            "openaiOpen": mod1["payoff_matrix"]["OOO"][0],
            "metaOpen": mod1["payoff_matrix"]["COO"][1],
            "metaClosed": mod1["payoff_matrix"]["CCO"][1],
            "deepseekOpen": mod1["payoff_matrix"]["COO"][2],
            "deepseekClosed": mod1["payoff_matrix"]["COC"][2],
        },
    },
    "module2": {
        "dataCutoff": mod2["data_cutoff"],
        "spePath": mod2["spe_path"],
        "spePayoff": mod2["spe_payoff"],
        "dsChoice": mod2["ds_choice"],
        "metaChoice": mod2["meta_choice"],
        "openaiChoice": mod2["openai_choice"],
    },
    "module3": {
        "dataCutoff": mod3["data_cutoff"],
        "prior": mod3["prior"],
        "deltaU": mod3["delta_U"],
        "beliefPath": mod3["belief_path"],
        "finalPosterior": mod3["final_posterior"],
        "events": [
            {"t": "2024-Q1", "nm": "2024 年初先验", "sub": "尚无证据", "lS": None, "lW": None},
            {"t": "2024-05", "nm": "V2 论文 (MoE+MLA)", "sub": "架构创新", "lS": 0.50, "lW": 0.15},
            {"t": "2024-12", "nm": "V3 + 技术报告", "sub": "$5.576M · 可复现", "lS": 0.85, "lW": 0.10},
            {"t": "2025-01", "nm": "R1 / R1-Zero", "sub": "强推理", "lS": 0.95, "lW": 0.05},
            {"t": "2025-02", "nm": "全球复现 + 登顶", "sub": "App Store 第一", "lS": 0.99, "lW": 0.01},
        ],
        "cases": [
            {"nm": "DeepSeek V3", "cS": 1.5, "cW": 7.5},
            {"nm": "Llama 3.1-405B", "cS": 1.0, "cW": 8.5},
            {"nm": "Qwen3", "cS": 2.0, "cW": 9.0},
            {"nm": "营销夸大的小模型", "cS": 0.6, "cW": 1.8},
            {"nm": "无差异化跟随者", "cS": 6.0, "cW": 6.6},
        ],
    },
    "module4": {
        "dataCutoff": mod4["data_cutoff"],
        "defaults": {
            "a": mod4["bertrand_primitives"]["a"],
            "g": mod4["bertrand_primitives"]["g"],
            "db": mod4["delta_base"],
            "I": mod4["I_disruption"],
            "lam": mod4["lambda_ipo"],
        },
        "singlePeriod": mod4["single_period_payoffs"],
        "prices": mod4["bertrand_prices"],
        "criticalDelta": mod4["critical_delta"],
        "deltaEffective": mod4["delta_effective"],
        "criticalDisruption": mod4["I_star_critical_disruption"],
        "priceTimeline": [
            {"dt": "2023.03", "nm": "GPT-4", "sub": "闭源旗舰确立高价", "price": "$30 /M", "width": 100},
            {"dt": "2023.11", "nm": "GPT-4 Turbo", "sub": "", "price": "$10 /M", "width": 33},
            {"dt": "2024.05", "nm": "GPT-4o", "sub": "", "price": "$5 /M", "width": 17},
            {"dt": "2025.08", "nm": "GPT-5", "sub": "较 GPT-4 下降约 95.8%", "price": "$1.25 /M", "width": 4},
        ],
    },
    "module5": {
        "dataCutoff": mod5["data_cutoff"],
        "params": mod5["params"],
        "scenarios": [
            {
                "name": "欧盟",
                "policy": "GPAI 义务严管",
                "reg": -0.5,
                "ess": 0.3333,
                "reality": "闭源主导，开源仅余长尾（Mistral 商业化转向）。",
                "color": "closed",
            },
            {
                "name": "美国",
                "policy": "中性偏支持",
                "reg": -0.1,
                "ess": 0.6,
                "reality": "两阵营基本平分（OpenAI 闭源、Meta 开源、gpt-oss 边缘开放）。",
                "color": "ind",
            },
            {
                "name": "基线",
                "policy": "无监管",
                "reg": 0.0,
                "ess": 0.6667,
                "reality": "开源主导，闭源占据高端。",
                "color": "open",
            },
            {
                "name": "中国",
                "policy": "“AI+”鼓励开源",
                "reg": 0.3,
                "ess": 0.8667,
                "reality": "开源压倒性（DeepSeek / Qwen / GLM / Kimi 全开源）。",
                "color": "hot",
            },
        ],
    },
}

OUT_FILE.write_text(
    "window.SITE_DATA = " + json.dumps(site_data, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8",
)

print(f"Wrote {OUT_FILE}")
