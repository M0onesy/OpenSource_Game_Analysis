"""Shared helpers for console, font, and batch plotting setup."""

from __future__ import annotations

import ctypes
import os
import platform
import sys
from functools import lru_cache
from pathlib import Path


_PLATFORM = platform.system()

_FONT_CANDIDATES = {
    "Windows": [
        "Microsoft YaHei",
        "SimHei",
        "DengXian",
        "SimSun",
    ],
    "Darwin": [
        "PingFang SC",
        "Hiragino Sans GB",
        "Heiti SC",
        "Songti SC",
    ],
    "Linux": [
        "Noto Sans CJK SC",
        "Noto Sans SC",
        "Source Han Sans SC",
        "WenQuanYi Zen Hei",
    ],
}

_FONT_PATH_CANDIDATES = {
    "Windows": [
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "msyh.ttc",
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "msyhbd.ttc",
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "simhei.ttf",
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "Deng.ttf",
        Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "simsun.ttc",
    ],
    "Darwin": [
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
        Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
    ],
    "Linux": [
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansSC-Regular.otf"),
        Path("/usr/share/fonts/opentype/adobe-source-han-sans/SourceHanSansSC-Regular.otf"),
        Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
    ],
}


def _platform_candidates() -> list[str]:
    return _FONT_CANDIDATES.get(_PLATFORM, _FONT_CANDIDATES["Linux"])


@lru_cache(maxsize=1)
def _font_manager_module():
    from matplotlib import font_manager

    return font_manager


def _register_font_paths() -> None:
    font_manager = _font_manager_module()
    seen: set[str] = set()
    for path in _FONT_PATH_CANDIDATES.get(_PLATFORM, []):
        if not path.exists():
            continue
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        try:
            font_manager.fontManager.addfont(key)
        except Exception:
            continue


def _font_exists(font_name: str) -> bool:
    font_manager = _font_manager_module()
    prop = font_manager.FontProperties(family=font_name)
    try:
        font_manager.findfont(prop, fallback_to_default=False)
    except ValueError:
        return False
    return True


@lru_cache(maxsize=1)
def configure_matplotlib_backend_for_batch() -> str:
    """Force the non-GUI Agg backend for batch plotting scripts."""
    os.environ["MPLBACKEND"] = "Agg"

    import matplotlib

    if "matplotlib.pyplot" not in sys.modules:
        matplotlib.use("Agg", force=True)
    return str(matplotlib.get_backend())


@lru_cache(maxsize=1)
def pick_cjk_font() -> str:
    """Return the first available CJK font for the current platform."""
    _register_font_paths()
    for font_name in _platform_candidates():
        if _font_exists(font_name):
            return font_name

    options = " / ".join(_platform_candidates())
    raise RuntimeError(
        "未找到可用的中文字体，无法继续绘图或生成文档。"
        f"当前平台：{_PLATFORM}。请安装以下任意字体后重试：{options}"
    )


def _reconfigure_stream(stream: object) -> None:
    if stream is None or not hasattr(stream, "isatty"):
        return
    try:
        if not stream.isatty():
            return
    except Exception:
        return
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def configure_console_utf8() -> None:
    """Best-effort UTF-8 console output for interactive Windows terminals."""
    if os.name != "nt":
        return

    streams = [sys.stdout, sys.stderr]
    try:
        any_tty = any(stream is not None and stream.isatty() for stream in streams)
    except Exception:
        any_tty = False
    if not any_tty:
        return

    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass

    for stream in streams:
        _reconfigure_stream(stream)
