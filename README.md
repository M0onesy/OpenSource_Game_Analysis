# 大模型公司「开源 vs 闭源」战略博弈分析

> 博弈论课程大作业 · 完整可复现项目包
> 数据基线：2025 年 1 月（DeepSeek-R1 冲击）— 2026 年 5 月 28 日（Anthropic 以约 $965B 估值反超 OpenAI、Claude Opus 4.8 发布、GPT-5.5、DeepSeek V4、Qwen 3.5 均已发布）

本项目以全球大模型产业 2023–2026 年的「开源 vs 闭源」战略分化为对象，构建多层博弈论分析框架：用三方静态博弈识别基础纳什均衡，再从**参与人 / 信息结构 / 行动顺序**三个维度扩展为演化博弈、贝叶斯信号博弈与无限期重复博弈。全部结论均由代码 1:1 复现，全部产业数据均标注来源并经核实。

---

## 一、目录结构

```
大模型博弈论分析/
├── README.md                      ← 本文件
├── 数据来源.md                    ← 全部产业数据与参考文献的可核验出处
├── 论文/
│   ├── 大模型博弈论分析_论文.md   ← 完整论文（Markdown，约 600 行，含全部论述与附录）
│   ├── 大模型博弈论分析_论文.docx ← 提交版 Word 文档（US Letter，≤10 页，含封面与 6 图）
│   └── 大模型博弈论分析_论文.pdf  ← 由 docx 转换的预览版（便于直接查看，无需 Word）
├── 代码/
│   ├── _style.py                  ← 统一中文字体与配色（所有脚本共享）
│   ├── 01_static_game.py          ← 静态博弈（支付由支付函数计算）→ 图 2 + results_module1.json
│   ├── 02_sequential_game.py      ← 序贯博弈（支付复用模块 1）    → 图 3 + results_module2.json
│   ├── 03_bayesian_signal.py      ← 贝叶斯信号博弈              → 图 5 + results_module3.json
│   ├── 04_repeated_game.py        ← 重复博弈（伯特兰推导支付）   → 图 6 + results_module4.json
│   ├── 05_evolutionary_regulator.py ← 演化博弈 + 监管者          → 图 4 + results_module5.json
│   ├── 06_overview.py             ← 模型架构总览              → 图 1
│   ├── run_all.py                 ← 一键复现：顺序运行 6 模块（可选 --paper 生成文档）
│   ├── build_paper.py             ← 生成 Word 文档（python-docx，窄边距，无高亮框）
│   └── results_module1-5.json     ← 各模块关键计算结果（供论文与复现核对）
└── 图表/
    ├── fig1_overview.png          ← 三层框架总览（全中文）
    ├── fig2_payoff_matrix.png     ← 三方支付矩阵热力图（红框标注纳什均衡）
    ├── fig3_game_tree.png         ← 序贯博弈树（红色 SPE 路径）
    ├── fig4_evolutionary.png      ← 复制动态相图 + 四监管情景轨迹
    ├── fig5_bayesian_signal.png   ← 贝叶斯信念演化 + Spence 三区域
    └── fig6_repeated_game.png     ← 双因子贴现瀑布图 + 前沿价格时间线
```

---

## 二、图号约定（重要）

为保证每一张图都能由代码 **1:1 复现**，本项目采用统一规则：

> **图片按其在正文中出现的先后顺序统一编号为图 1…图 6，图片文件名（`figN_*.png`）与图号一致。**

各图由哪个脚本生成见下表（脚本编号与图号不必相同，例如 `01_static_game.py` 生成图 2）。

| 图号 | 图片文件 | 生成脚本 | 结果文件 | 出现章节 |
|------|----------|----------|----------|----------|
| 图 1 | fig1_overview.png | 06_overview.py | （无） | §1.2 |
| 图 2 | fig2_payoff_matrix.png | 01_static_game.py | results_module1.json | §3.1 |
| 图 3 | fig3_game_tree.png | 02_sequential_game.py | results_module2.json | §3.2 |
| 图 4 | fig4_evolutionary.png | 05_evolutionary_regulator.py | results_module5.json | §四（改进一）|
| 图 5 | fig5_bayesian_signal.png | 03_bayesian_signal.py | results_module3.json | §五（改进二）|
| 图 6 | fig6_repeated_game.png | 04_repeated_game.py | results_module4.json | §六（改进三）|

---

## 三、运行方式

环境依赖（Python 3.10+）：

```bash
pip install numpy matplotlib scipy pillow python-docx
```

> 中文显示依赖系统安装的中文字体。项目会按平台自动探测常见字体（Windows：`Microsoft YaHei` / `SimHei` / `DengXian` / `SimSun`；macOS：`PingFang SC` / `Hiragino Sans GB` / `Heiti SC` / `Songti SC`；Linux：`Noto Sans CJK SC` / `Noto Sans SC` / `Source Han Sans SC` / `WenQuanYi Zen Hei`）。若仍提示缺少中文字体，请按错误信息安装任一候选字体后重试。
> 图表脚本默认使用 Matplotlib 的 `Agg` 非交互后端批量生成 PNG，不会弹出 GUI 图窗；若需要查看效果，请直接打开 `图表/` 下生成的图片。

复现全部图表——推荐用一键脚本：

```bash
cd 代码/
python run_all.py            # 顺序运行 6 个模块，重生成全部 6 张图 + 5 个 JSON
python run_all.py --paper    # 在上述基础上，额外生成 Word 文档
```

也可单独运行各脚本（彼此独立，02 在运行时会复用 01 的支付）：

```bash
cd 代码/
python 01_static_game.py            # → ../图表/fig2_payoff_matrix.png
python 02_sequential_game.py        # → ../图表/fig3_game_tree.png
python 03_bayesian_signal.py        # → ../图表/fig5_bayesian_signal.png
python 04_repeated_game.py          # → ../图表/fig6_repeated_game.png
python 05_evolutionary_regulator.py # → ../图表/fig4_evolutionary.png
python 06_overview.py               # → ../图表/fig1_overview.png
```

生成 Word 文档（US Letter、窄边距 0.5"、无高亮框、内嵌 6 图，不含摘要与参考文献）：

```bash
cd 代码/
python build_paper.py               # → ../论文/大模型博弈论分析_论文.docx
```

每个模块脚本运行后会：(1) 在控制台打印关键计算结果；(2) 在 `图表/` 保存对应 PNG；(3) 在 `代码/` 保存 `results_moduleN.json`（总览图除外）。

---

## 四、核心结论速览

**基础博弈**：三方静态博弈（OpenAI / Meta / DeepSeek，策略 {O, C}）的支付由 §2.4 支付函数实例化计算（而非外生赋值），经迭代剔除严格劣势策略可占优求解，得**唯一纯策略纳什均衡 (C, O, O)**，支付 **(13.1, 6.5, 8.8)**——OpenAI 闭源、Meta 与 DeepSeek 开源，与 2026 年现实格局完全吻合；序贯博弈逆向归纳给出一致的子博弈完美均衡。

**改进一 · 演化博弈 + 监管者**：复制动态 `dx/dt = x(1−x)[π_O − π_C]` 存在唯一内部 ESS `x* = (α−γ+reg)/(β+δ)`。四种监管情景给出区域性 ESS：

| 情景 | reg | 稳态 x\* |
|------|-----|----------|
| 基线 | +0.0 | 0.667 |
| 欧盟（GPAI 严管）| −0.5 | 0.333 |
| 中国（鼓励开源）| +0.3 | 0.867 |
| 美国（中性偏支持）| −0.1 | 0.600 |

**改进二 · 贝叶斯信号博弈**：分离均衡条件 `c_S < ΔU < c_W`（ΔU = 4）。市场对 DeepSeek「低成本类型」的后验信念随四个事件由 **0.10 → 0.270 → 0.759 → 0.984 → ≈1.000**。

**改进三 · 无限期重复博弈**：单期支付由差异化伯特兰定价模型推导（需求 `q_i = a − p_i + g·p_j`，取 a=12、g=0.5、mc=0，得合谋 π_C=72 / 背叛 π_D=81 / 价格战 π_P=64 / 被背叛 π_S=54，满足 D>C>P>S）。临界贴现因子 `δ* = (π_D−π_C)/(π_D−π_P) = (81−72)/(81−64) = 9/17 ≈ 0.529`。双因子有效贴现 `δ_eff = δ_base(1−I)(1−λ)`：取 δ_base=0.85、I=0.30、λ=0.30 得 δ_eff ≈ 0.416 < δ*，合谋破裂；单因子临界颠覆强度 `I* = 1 − δ*/δ_base ≈ 0.377`。

**现实印证**：2025.1.27 NVIDIA 单日 −17%（约 −$589B）、OpenAI 2025.8 发布 gpt-oss 开放权重模型、GPT-5 输入价较 GPT-4 下降约 95.8%、Qwen 累计下载 2026.1 破 7 亿居全球开源之首、2026.5.28 Anthropic 以约 $965B 估值反超 OpenAI（约 $852B）——均可由本框架给出博弈论解释。

---

## 五、本版本相对早期稿的主要修订

1. **更新至 2026 年 5 月最新格局**：Anthropic 以约 $965B 估值反超 OpenAI（约 $852B）、run-rate 营收约 $47B；新旗舰 GPT-5.5 / Claude Opus 4.8 / DeepSeek V4（MIT，1M 上下文）/ Qwen 3.5。
2. **修正错误事实**：删除「Qwen 转闭源」的不实表述（阿里 Qwen 截至 2026.5 仍全面开源，占全球开源下载 50%+，衍生模型数自 2025.10 起超越 Llama）。
3. **修正数据口径**：临界颠覆强度 I\* ≈ 0.377（由伯特兰模型推导的 δ\*≈0.529 得出）；Stanford 开闭源能力差距更正为收敛至约 1.7pp（早期流传的「17.5pp」为口径误读）；GPT-5 输入价降幅 95.8%。
4. **支付由外生赋值升级为推导**：静态博弈支付改由 §2.4 支付函数实例化计算（参数表见正文表 2-0），并以迭代剔除严格劣势策略证明博弈可占优求解；重复博弈四个单期支付改由差异化伯特兰定价模型推导（δ\* 由 0.444 更新为 0.529、I\* 由 0.477 更新为 0.377）。
5. **升级重复博弈模型**：由单因子升级为「颠覆侵蚀 I + IPO 短视 λ」双因子模型，呼应 2026 年两家头部公司筹备上市的真实背景。
6. **图表全面中文化**：6 张图标题、坐标轴、图例、标注全部为中文。
7. **精简参考文献**：删除未能核实的条目，保留的每条均有 DOI / arXiv 编号 / 官方发布 / 权威媒体可供核验（详见 `数据来源.md`）。

---

## 六、范围说明

本包为**干净、自洽的核心交付物**：完整论文（Markdown + Word + PDF 预览）、6 张可复现中文图、全部生成代码与计算结果、数据来源清单。为避免与正文不一致，本版本**未包含早期的演示 PPT 与讲解手册**——所有论述均以论文与本 README 为准。

---

*学术诚信声明：本项目所有产业数据均标注来源并经核实；所有图表与结论均可由 `代码/` 中脚本独立 1:1 复现；论文正文区分了已证实事实与模型推断，并对个别早期错误口径作了显式更正。*
