#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_all.py — 一键复现：依次运行 6 个博弈模块（重生成全部图表与 results_*.json），
            可选随后调用 build_paper.py 生成 Word 文档。

用法：
    cd 代码/
    python run_all.py            # 只重算模型 + 重生成 6 张图 + 5 个 JSON
    python run_all.py --paper    # 在上述基础上，额外生成 Word 文档

说明：
  - 模块文件名以数字开头（01_…、02_…），无法用普通 import，故用 runpy 逐个执行。
  - 图号按正文出现顺序为 图1…图6；脚本编号与图号不一一对应
    （01→图2、02→图3、03→图5、04→图6、05→图4、06→图1）。
  - 支付一致性：02 序贯博弈在运行时通过 importlib 复用 01 的支付字典；
    因此先后顺序不影响结果，但建议按下方默认顺序执行以便日志清晰。
"""

import os
import sys
import runpy
import time
from _cjk_support import configure_console_utf8, configure_matplotlib_backend_for_batch

configure_console_utf8()
configure_matplotlib_backend_for_batch()

HERE = os.path.dirname(os.path.abspath(__file__))

# (脚本文件, 产出图, 一句话说明)
MODULES = [
    ("01_static_game.py",          "图2 fig2_payoff_matrix", "静态博弈：由支付函数计算支付，可占优求解唯一纳什均衡 (C,O,O)"),
    ("02_sequential_game.py",      "图3 fig3_game_tree",      "序贯博弈：逆向归纳 SPE=(C,O,O)，支付复用模块 1"),
    ("03_bayesian_signal.py",      "图5 fig5_bayesian_signal","贝叶斯信号：先验 0.10 → 后验 ≈1.00，Spence 三区域"),
    ("04_repeated_game.py",        "图6 fig6_repeated_game",  "重复博弈：伯特兰推导单期支付，δ*≈0.529，I*≈0.377"),
    ("05_evolutionary_regulator.py","图4 fig4_evolutionary",  "演化博弈：四监管情景 ESS（0.33 / 0.60 / 0.667 / 0.867）"),
    ("06_overview.py",             "图1 fig1_overview",       "框架总览图（汇总五类博弈与三项改进）"),
]


def run_modules():
    print("=" * 70)
    print("一键复现：依次运行 6 个博弈模块")
    print("=" * 70)
    t0 = time.time()
    for i, (fname, fig, desc) in enumerate(MODULES, 1):
        path = os.path.join(HERE, fname)
        print(f"\n[{i}/{len(MODULES)}] {fname}  →  {fig}")
        print(f"      {desc}")
        if not os.path.exists(path):
            print(f"      [跳过] 未找到 {fname}")
            continue
        # 切换工作目录到 代码/，保证脚本内相对路径（../图表、results_*.json）正确
        cwd = os.getcwd()
        os.chdir(HERE)
        try:
            runpy.run_path(path, run_name="__main__")
            print(f"      [完成] {fname}")
        except Exception as exc:
            print(f"      [失败] {fname}: {exc}")
            raise
        finally:
            os.chdir(cwd)
    print(f"\n全部模块完成，用时 {time.time() - t0:.1f}s。"
          f"图表已更新至 ../图表/，结果已写入 results_module1-5.json。")


def run_paper():
    print("\n" + "=" * 70)
    print("生成 Word 文档（build_paper.py）")
    print("=" * 70)
    cwd = os.getcwd()
    os.chdir(HERE)
    try:
        runpy.run_path(os.path.join(HERE, "build_paper.py"), run_name="__main__")
    finally:
        os.chdir(cwd)


def main():
    want_paper = "--paper" in sys.argv[1:]
    run_modules()
    if want_paper:
        run_paper()
        print("\n文档已生成：../论文/大模型博弈论分析_论文.docx")
    else:
        print("\n提示：加 --paper 可一并生成 Word 文档（python run_all.py --paper）。")


if __name__ == "__main__":
    main()
