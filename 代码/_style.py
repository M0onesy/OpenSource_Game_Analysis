"""
========================================================================
_style.py — 全项目统一绘图样式（中文字体 + 学术配色 + 保存辅助）

所有图表脚本通过 `from _style import *` 导入本模块，以保证：
  1. 全部图表内文字统一使用中文（Noto Sans CJK SC，环境已内置）；
  2. 全部图表共用同一套配色与排版规范，风格一致；
  3. 每张图均可由对应脚本独立运行、1:1 复现。

字体说明：本环境已内置 Noto Sans CJK SC（思源黑体简体），
可完整渲染简体中文与常用数学符号；axes.unicode_minus=False 修复负号。
========================================================================
"""

import os
from _cjk_support import (
    configure_console_utf8,
    configure_matplotlib_backend_for_batch,
    pick_cjk_font,
)
from _png_support import strip_incorrect_iccp_chunk

configure_console_utf8()
configure_matplotlib_backend_for_batch()

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.legend import Legend
from matplotlib.text import Annotation, Text

# ----------------------------------------------------------------------
# 1. 中文字体注册与全局 rcParams
# ----------------------------------------------------------------------
CJK_FONT = pick_cjk_font()

mpl.rcParams["font.sans-serif"] = [CJK_FONT, "DejaVu Sans"]
mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["axes.unicode_minus"] = False          # 正确显示负号
mpl.rcParams["figure.dpi"] = 120
mpl.rcParams["savefig.dpi"] = 200
mpl.rcParams["savefig.bbox"] = "tight"
mpl.rcParams["figure.facecolor"] = "white"
mpl.rcParams["savefig.facecolor"] = "white"
mpl.rcParams["axes.titlesize"] = 17
mpl.rcParams["axes.labelsize"] = 15
mpl.rcParams["xtick.labelsize"] = 13
mpl.rcParams["ytick.labelsize"] = 13
mpl.rcParams["legend.fontsize"] = 12.5
mpl.rcParams["axes.titleweight"] = "bold"
mpl.rcParams["axes.edgecolor"] = "#444444"
mpl.rcParams["axes.linewidth"] = 1.0
mpl.rcParams["grid.color"] = "#D9D9D9"
mpl.rcParams["grid.linewidth"] = 0.8

# ----------------------------------------------------------------------
# 2. 统一配色板
# ----------------------------------------------------------------------
# 主色（学术蓝）与强调色
C_PRIMARY   = "#1F4E79"   # 主蓝（标题、主框）
C_PRIMARY_2 = "#2E6DA4"   # 次蓝
C_ACCENT    = "#C0504D"   # 强调红（均衡 / 关键值）
C_GOLD      = "#E0A82E"   # 强调金
C_GREEN     = "#3C8C5A"   # 绿（开源 / 合作）
C_GREY      = "#7F7F7F"   # 中性灰
C_LIGHT     = "#F2F6FB"   # 浅蓝底
C_INK       = "#222222"   # 正文墨色

# 五大参与人专属色（与论文表格一致）
PLAYER_COLORS = {
    "OpenAI":   "#10A37F",   # OpenAI 品牌绿
    "Anthropic":"#CC785C",   # Anthropic 品牌赭
    "Meta":     "#1877F2",   # Meta 蓝
    "DeepSeek": "#4D6BFE",   # DeepSeek 蓝紫
    "阿里通义": "#FF6A00",   # 阿里橙
}

# 策略色：开源 / 闭源
C_OPEN   = "#3C8C5A"   # 开源（绿）
C_CLOSED = "#C0504D"   # 闭源（红）

# 蓝色系连续色图（用于热力图）
CMAP_BLUE = "Blues"

# 统一图层常量：文字始终高于线、面、节点等非文字元素。
Z_BG = 0
Z_GUIDE = 2
Z_SHAPE = 4
Z_MARKER = 6
Z_TEXT = 30
Z_LEGEND = 31


# ----------------------------------------------------------------------
# 3. 通用辅助函数
# ----------------------------------------------------------------------
def figure_dir():
    """返回 ../图表 的绝对路径（脚本位于 代码/ 目录时）。"""
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.normpath(os.path.join(here, "..", "图表"))
    os.makedirs(d, exist_ok=True)
    return d


def promote_text_artists(
    fig,
    text_zorder=Z_TEXT,
    legend_zorder=Z_LEGEND,
    annotation_arrow_zorder=Z_TEXT - 1,
):
    """保存前统一提升整张图内文字层级，避免被线条和色块盖住。"""
    for artist in fig.findobj(match=Text):
        target = text_zorder
        if isinstance(artist, Annotation) and artist.arrow_patch is not None:
            artist.arrow_patch.set_zorder(
                max(artist.arrow_patch.get_zorder(), annotation_arrow_zorder)
            )
            target = max(target, artist.arrow_patch.get_zorder() + 1)
        artist.set_zorder(max(artist.get_zorder(), target))

    for legend in fig.findobj(match=Legend):
        legend.set_zorder(max(legend.get_zorder(), legend_zorder))
        frame = legend.get_frame()
        if frame is not None:
            frame.set_zorder(max(frame.get_zorder(), legend_zorder))
        title = legend.get_title()
        if title is not None:
            title.set_zorder(max(title.get_zorder(), legend_zorder))
        for text in legend.get_texts():
            text.set_zorder(max(text.get_zorder(), legend_zorder))

    return fig


def save_fig(fig, filename):
    """统一保存到 ../图表/，dpi=200、白底、紧边距。"""
    path = os.path.join(figure_dir(), filename)
    promote_text_artists(fig)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    strip_incorrect_iccp_chunk(path)
    print(f"[已保存] {path}")
    return path


def style_axes(ax, grid=True, grid_axis="both"):
    """对单个坐标轴应用统一外观：去顶/右边框、浅网格。"""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid:
        ax.grid(True, axis=grid_axis, linestyle="--", alpha=0.45, zorder=Z_BG)
        ax.set_axisbelow(True)
    return ax
