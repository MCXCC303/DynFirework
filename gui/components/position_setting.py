from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtGui import QFont, QIntValidator, QDoubleValidator
from PyQt5.QtCore import Qt

class PositionSettingWidget(QWidget):
    """位置设置组件，用于创建位置输入区域"""
    
    def __init__(self, parent=None, start_pos=(0, 0, 0), end_pos=(50, 100, 30), style=None):
        """
        初始化位置设置组件
        
        参数:
            parent: 父窗口
            start_pos: 起始位置，格式为(x, y, z)
            end_pos: 终止位置，格式为(x, y, z)
            style: 样式字典，如果为None则使用默认样式
        """
        super().__init__(parent)
        
        # 应用样式
        if style is None:
            from gui.style.style_factory import StyleFactory
            self.style = StyleFactory.create_style()
        else:
            self.style = style
            
        # 确保style字典包含所需的所有键
        if 'input_bg_color' not in self.style:
            self.style['input_bg_color'] = self.style.get('card_color', '#ffffff')
            
        # 保存初始位置
        self.initial_start_pos = start_pos
        self.initial_end_pos = end_pos
        
        # 创建主布局
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(20)
        
        # 设置整个部件的背景色
        self.setStyleSheet(f"background-color: {self.style['card_color']};")
        
        # 创建起始位置区域
        self.start_frame = QFrame()
        self.start_frame.setStyleSheet(f"background-color: {self.style['card_color']};")
        start_layout = QVBoxLayout(self.start_frame)
        start_layout.setContentsMargins(0, 0, 0, 0)
        start_layout.setSpacing(8)
        
        start_label = QLabel("起始位置")
        start_label.setFont(QFont(self.style["font_family"], self.style["body_font_size"]))
        start_layout.addWidget(start_label, alignment=Qt.AlignCenter)
        
        # 背景色样式
        input_frame_style = f"background-color: {self.style['card_color']};"
        
        # 坐标输入框 - 使用网格布局确保对齐
        start_pos_grid = QGridLayout()
        start_pos_grid.setHorizontalSpacing(10)
        start_pos_grid.setVerticalSpacing(5)
        
        self.start_entries = {}
        for i, label in enumerate(['X', 'Y', 'Z']):
            # 添加标签
            label_widget = QLabel(label)
            label_widget.setAlignment(Qt.AlignCenter)
            label_widget.setStyleSheet(input_frame_style)
            start_pos_grid.addWidget(label_widget, 0, i)
            
            # 添加输入框
            entry = QLineEdit()
            entry.setFixedWidth(60)
            entry.setText(str(start_pos[i]))
            entry.setValidator(QDoubleValidator())  # 允许浮点数
            entry.setAlignment(Qt.AlignCenter)
            entry.setStyleSheet(f"background-color: {self.style['input_bg_color']};")
            start_pos_grid.addWidget(entry, 1, i)
            
            self.start_entries[label] = entry
            
        # 添加坐标网格布局
        start_layout.addLayout(start_pos_grid)
        
        # 将起始位置区域添加到主布局
        self.main_layout.addWidget(self.start_frame)
        
        # 创建终止位置区域
        self.end_frame = QFrame()
        self.end_frame.setStyleSheet(f"background-color: {self.style['card_color']};")
        end_layout = QVBoxLayout(self.end_frame)
        end_layout.setContentsMargins(0, 0, 0, 0)
        end_layout.setSpacing(8)
        
        end_label = QLabel("终止位置")
        end_label.setFont(QFont(self.style["font_family"], self.style["body_font_size"]))
        end_layout.addWidget(end_label, alignment=Qt.AlignCenter)
        
        # 坐标输入框 - 使用网格布局确保对齐
        end_pos_grid = QGridLayout()
        end_pos_grid.setHorizontalSpacing(10)
        end_pos_grid.setVerticalSpacing(5)
        
        self.end_entries = {}
        for i, label in enumerate(['X', 'Y', 'Z']):
            # 添加标签
            label_widget = QLabel(label)
            label_widget.setAlignment(Qt.AlignCenter)
            label_widget.setStyleSheet(input_frame_style)
            end_pos_grid.addWidget(label_widget, 0, i)
            
            # 添加输入框
            entry = QLineEdit()
            entry.setFixedWidth(60)
            entry.setText(str(end_pos[i]))
            entry.setValidator(QDoubleValidator())  # 允许浮点数
            entry.setAlignment(Qt.AlignCenter)
            entry.setStyleSheet(f"background-color: {self.style['input_bg_color']};")
            end_pos_grid.addWidget(entry, 1, i)
            
            self.end_entries[label] = entry
            
        # 添加坐标网格布局
        end_layout.addLayout(end_pos_grid)
        
        # 将终止位置区域添加到主布局
        self.main_layout.addWidget(self.end_frame)
            
    def get_positions(self):
        """获取位置值
        
        返回:
            tuple: (start_pos, end_pos)
            其中:
                start_pos: 起始位置，格式为(x, y, z)
                end_pos: 终止位置，格式为(x, y, z)
        """
        start_pos = (
            float(self.start_entries['X'].text() or 0),
            float(self.start_entries['Y'].text() or 0),
            float(self.start_entries['Z'].text() or 0)
        )
        
        end_pos = (
            float(self.end_entries['X'].text() or 0),
            float(self.end_entries['Y'].text() or 0),
            float(self.end_entries['Z'].text() or 0)
        )
        
        return start_pos, end_pos
    
    def set_positions(self, start_pos, end_pos):
        """设置位置值
        
        参数:
            start_pos: 起始位置，格式为(x, y, z)
            end_pos: 终止位置，格式为(x, y, z)
        """
        # 设置起始位置
        self.start_entries['X'].setText(str(start_pos[0]))
        self.start_entries['Y'].setText(str(start_pos[1]))
        self.start_entries['Z'].setText(str(start_pos[2]))
        
        # 设置终止位置
        self.end_entries['X'].setText(str(end_pos[0]))
        self.end_entries['Y'].setText(str(end_pos[1]))
        self.end_entries['Z'].setText(str(end_pos[2])) 