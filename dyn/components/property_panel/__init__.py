"""属性面板包 按后端模块化.
DF: 注册表驱动 16 种表单
CB: 硬编码路由 10 种表单
"""
from dyn.components.cb.property_panel.panel import CbPropertyPanel
from dyn.components.property_panel.panel import PropertyPanel

__all__ = ["PropertyPanel", "CbPropertyPanel"]
