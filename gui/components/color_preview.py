from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QRect

class ColorPreview(QWidget):
    """颜色预览组件，用于显示颜色"""
    
    def __init__(self, parent=None, color=(255, 0, 0), size=(60, 30), style=None):
        """
        初始化颜色预览组件
        
        参数:
            parent: 父窗口
            color: 颜色，格式为(r, g, b)
            size: 组件大小，格式为(宽度, 高度)
            style: 样式字典，如果为None则创建默认样式
        """
        super().__init__(parent)
        
        # 设置组件大小
        self.setFixedSize(*size)
        
        # 保存样式
        self.style = style or {
            "border_color": "#cccccc",
            "border_radius": 5,
            "border_width": 1
        }
        
        # 设置颜色
        self.set_color(color)
    
    def set_color(self, color):
        """
        设置颜色
        
        参数:
            color: 颜色，格式为(r, g, b)
        """
        # 确保RGB分量在0-255范围内
        r = max(0, min(255, color[0]))
        g = max(0, min(255, color[1]))
        b = max(0, min(255, color[2]))
        
        self.color = QColor(r, g, b)
        self.update()  # 触发重绘
    
    def setColor(self, color):
        """setColor方法作为set_color的别名，用于兼容旧代码"""
        return self.set_color(color)
    
    def paintEvent(self, event):
        """绘制颜色预览"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 设置画笔颜色（边框）
        painter.setPen(QColor(self.style["border_color"]))
        
        # 设置画刷颜色（填充）
        painter.setBrush(QBrush(self.color))
        
        # 绘制圆角矩形
        rect = QRect(
            self.style["border_width"], 
            self.style["border_width"], 
            self.width() - 2 * self.style["border_width"], 
            self.height() - 2 * self.style["border_width"]
        )
        painter.drawRoundedRect(
            rect, 
            self.style["border_radius"], 
            self.style["border_radius"]
        )

    def getColor(self):
        """获取当前颜色
        
        返回:
            tuple: (r, g, b) 颜色值
        """
        return (self.color.red(), self.color.green(), self.color.blue()) 