"""元素浏览器 按模组模块化.
DF (默认): 4列 4分类 注册表驱动 类型列
ParticleEx: 3列 3分类 TF 子节点
"""
from ._base import BaseNode, GroupNode, ElementNode, ProxyNode
from .df import DfElementBrowserModel
from .particleex import ParticleexElementBrowserModel

# 默认使用 DF 浏览器
ElementBrowserModel = DfElementBrowserModel

__all__ = [
	"ElementBrowserModel", "DfElementBrowserModel", "ParticleexElementBrowserModel",
	"BaseNode", "GroupNode", "ElementNode", "ProxyNode",
]
