"""元素浏览器共享基类 重导出 shim 实际定义在 base/browser_model.py."""
from __future__ import annotations

from dyn.components.base.browser_model import (
	BaseNode, GroupNode, ElementNode, ProxyNode,
	BaseBrowserModel, format_time_sec, format_cb_time,
)

__all__ = [
	"BaseNode", "GroupNode", "ElementNode", "ProxyNode",
	"BaseBrowserModel", "format_time_sec", "format_cb_time",
]
