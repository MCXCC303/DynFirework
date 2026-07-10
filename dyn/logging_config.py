"""
全局日志配置.

    DYN_LOG_LEVEL=debug    # 控制台输出 DEBUG 及以上
    DYN_LOG_LEVEL=warning  # 仅输出 WARNING 和 ERROR
    DYN_LOG_FILE=/tmp/dyn.log  # 自定义日志文件路径（默认 logs/dynfirework.log）
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

# 环境变量名
ENV_LOG_LEVEL = "DYN_LOG_LEVEL"
ENV_LOG_FILE = "DYN_LOG_FILE"

_LEVEL_MAP: dict[str, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "warn": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def _resolve_console_level() -> int:
    """从环境变量解析控制台日志级别，默认 INFO."""
    raw = os.environ.get(ENV_LOG_LEVEL, "").strip().lower()
    if raw in _LEVEL_MAP:
        return _LEVEL_MAP[raw]
    if raw:
        print(f"Skipping env DYN_LOG_LEVEL='{raw}'", file=sys.stderr)
    return logging.INFO


def _resolve_log_file() -> Path:
    """从环境变量或默认路径获取日志文件路径."""
    raw = os.environ.get(ENV_LOG_FILE, "").strip()
    if raw:
        return Path(raw)
    return Path(__file__).parent.parent / "logs" / "dynfirework.log"


def setup_logging(level: int = logging.DEBUG) -> None:
    """
    配置根日志器，输出到 stderr 和文件.
    """
    root = logging.getLogger("dyn")
    root.setLevel(level)

    if root.handlers:
        return  # 已配置

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-5s %(name)-28s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_level = _resolve_console_level()
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(console_level)
    console.setFormatter(fmt)
    root.addHandler(console)

    try:
        log_file = _resolve_log_file()
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)
    except Exception:
        pass


def get_logger(name: str) -> logging.Logger:
    if name.startswith("dyn."):
        return logging.getLogger(name)
    return logging.getLogger(f"dyn.{name}")
