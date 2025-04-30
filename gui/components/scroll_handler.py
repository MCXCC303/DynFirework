from PyQt5.QtCore import Qt, QEvent, QObject
from PyQt5.QtWidgets import QScrollArea, QWidget, QApplication

class MouseWheelHandler(QObject):
    """PyQt5版本的鼠标滚轮事件处理类"""
    
    def __init__(self, scroll_area):
        """
        初始化鼠标滚轮处理器
        
        参数:
            scroll_area: QScrollArea对象
        """
        super().__init__(scroll_area)
        self.scroll_area = scroll_area
        self.scroll_area.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        """事件过滤器，处理鼠标滚轮事件"""
        if obj is self.scroll_area and event.type() == QEvent.Wheel:
            # 自定义滚轮处理逻辑
            delta = event.angleDelta().y()
            
            # 检查Shift键是否按下，按下时进行横向滚动
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                # 横向滚动
                scrollbar = self.scroll_area.horizontalScrollBar()
                scrollbar.setValue(scrollbar.value() - delta // 2)  # 调整滚动速度
            else:
                # 垂直滚动
                scrollbar = self.scroll_area.verticalScrollBar()
                scrollbar.setValue(scrollbar.value() - delta // 2)  # 调整滚动速度
            
            # 防止事件继续传播
            return True
            
        # 其他事件继续传播
        return super().eventFilter(obj, event)
    
    @staticmethod
    def bind_mousewheel(scroll_area):
        """
        绑定鼠标滚轮事件处理器
        
        参数:
            scroll_area: QScrollArea对象
        返回:
            MouseWheelHandler: 处理器实例
        """
        return MouseWheelHandler(scroll_area)
    
    @staticmethod
    def unbind_mousewheel(handler):
        """
        解绑鼠标滚轮事件处理器
        
        参数:
            handler: MouseWheelHandler实例
        """
        if handler and isinstance(handler, MouseWheelHandler):
            handler.scroll_area.removeEventFilter(handler)
            handler.deleteLater() 