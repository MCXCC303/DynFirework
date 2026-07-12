"""元素浏览器 按模组模块化.
DF (默认): 4列 4分类 注册表驱动 类型列
CB: 3列 3分类 TF 子节点
"""
from dyn.components.cb.element_browser import CbElementBrowserModel
from dyn.components.df.element_browser import DfElementBrowserModel
from ._base import BaseNode, GroupNode, ElementNode, ProxyNode

ElementBrowserModel = DfElementBrowserModel

__all__ = [
	"ElementBrowserModel", "DfElementBrowserModel", "CbElementBrowserModel",
	"BaseNode", "GroupNode", "ElementNode", "ProxyNode",
]
