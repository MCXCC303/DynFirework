from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QFrame, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt

class PositionWidget(QWidget):
    """位置输入组件，用于创建X、Y、Z三维坐标输入框"""
    
    def __init__(self, parent=None, position=(0, 0, 0), title=None, style=None):
        """
        初始化位置输入组件
        
        参数:
            parent: 父窗口
            position: 初始位置，格式为(x, y, z)
            title: 位置标题，如"起始位置"、"终止位置"等
            style: 样式字典，如果为None则使用默认样式
        """
        super().__init__(parent)
        
        # 应用样式
        if style is None:
            from gui.style.style_factory import StyleFactory
            self.style = StyleFactory.create_style()
        else:
            self.style = style
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        
        # 设置样式以避免灰色底色
        pos_frame_style = f"background-color: {self.style['card_color']};"
        self.setStyleSheet(pos_frame_style)
        
        # 添加标题（如果提供）
        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont(self.style["font_family"], self.style["body_font_size"]))
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet(pos_frame_style)
            self.main_layout.addWidget(title_label)
        
        # 创建坐标网格布局
        coord_layout = QGridLayout()
        coord_layout.setHorizontalSpacing(10)
        coord_layout.setVerticalSpacing(5)
        
        # 创建坐标输入框
        self.position_entries = {}
        
        for i, label in enumerate(['X', 'Y', 'Z']):
            # 添加标签
            label_widget = QLabel(label)
            label_widget.setAlignment(Qt.AlignCenter)
            label_widget.setStyleSheet(pos_frame_style)
            coord_layout.addWidget(label_widget, 0, i)
            
            # 添加输入框
            entry = QLineEdit()
            entry.setFixedWidth(60)
            entry.setText(str(position[i]))
            entry.setValidator(QIntValidator(-30000000, 30000000))
            entry.setAlignment(Qt.AlignCenter)
            entry.setStyleSheet(pos_frame_style)
            coord_layout.addWidget(entry, 1, i)
            
            self.position_entries[label] = entry
        
        # 将坐标网格添加到主布局
        self.main_layout.addLayout(coord_layout)
    
    def get_position(self):
        """
        获取位置坐标值
        
        返回:
            tuple: (x, y, z) 坐标值
        """
        try:
            x = int(self.position_entries['X'].text() or 0)
            y = int(self.position_entries['Y'].text() or 0)
            z = int(self.position_entries['Z'].text() or 0)
            
            return (x, y, z)
        except (ValueError, AttributeError):
            return (0, 0, 0)
    
    def set_position(self, position):
        """
        设置位置坐标值
        
        参数:
            position: (x, y, z) 坐标值
        """
        try:
            self.position_entries['X'].setText(str(position[0]))
            self.position_entries['Y'].setText(str(position[1]))
            self.position_entries['Z'].setText(str(position[2]))
        except (IndexError, KeyError):
            pass 