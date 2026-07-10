"""全局日志配置."""

from __future__ import annotations

import logging
import sys
from pathlib import Path


def setup_logging(level: int = logging.DEBUG) -> None:
    """配置根日志器，输出到 stderr 和文件."""
    root = logging.getLogger("dyn")
    root.setLevel(level)

    if root.handlers:
        return  # 已配置

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-5s %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # stderr（INFO 以上）
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    root.addHandler(console)

    # 文件（DEBUG 以上，写入项目根目录）
    try:
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "dynfirework.log", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)
    except Exception:
        pass


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"dyn.{name}")
