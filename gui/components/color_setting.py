from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QCheckBox, QGridLayout
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt
import traceback

class ColorSettingWidget(QWidget):
    """颜色设置组件，用于创建颜色选择区域"""
    
    def __init__(self, parent=None, start_color=(255, 0, 0), end_color=(255, 0, 0), 
                enable_gradient=True, style=None):
        """
        初始化颜色设置组件
        
        参数:
            parent: 父窗口
            start_color: 起始颜色，格式为(r, g, b)
            end_color: 终止颜色，格式为(r, g, b)
            enable_gradient: 是否启用渐变色选项
            style: 样式字典，如果为None则使用默认样式
        """
        super().__init__(parent)
        self.parent = parent
        
        # 应用样式
        if style is None:
            from gui.style.style_factory import StyleFactory
            self.style = StyleFactory.create_style()
        else:
            self.style = style
            
        # 确保style字典包含所需的所有键
        if 'input_bg_color' not in self.style:
            self.style['input_bg_color'] = self.style.get('card_color', '#ffffff')
            
        # 保存初始颜色
        self.initial_start_color = start_color
        self.initial_end_color = end_color
        self.current_end_color = end_color if end_color else start_color  # 确保有默认值
        
        # 创建主布局
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(20)
        
        # 设置整个部件的背景色
        self.setStyleSheet(f"background-color: {self.style['card_color']};")
        
        # 创建起始颜色区域
        self.start_frame = QFrame()
        self.start_frame.setStyleSheet(f"background-color: {self.style['card_color']};")
        start_layout = QVBoxLayout(self.start_frame)
        start_layout.setContentsMargins(0, 0, 0, 0)
        start_layout.setSpacing(8)
        
        start_label = QLabel("起始颜色")
        start_label.setFont(QFont(self.style["font_family"], self.style["body_font_size"]))
        start_layout.addWidget(start_label, alignment=Qt.AlignCenter)
        
        # 颜色预览
        from gui.components.color_preview import ColorPreview
        self.start_preview = ColorPreview(color=start_color)
        start_layout.addWidget(self.start_preview, alignment=Qt.AlignCenter)
        
        # 背景色样式
        rgb_frame_style = f"background-color: {self.style['card_color']};"
        
        # RGB输入框 - 使用网格布局确保对齐
        start_rgb_grid = QGridLayout()
        start_rgb_grid.setHorizontalSpacing(10)
        start_rgb_grid.setVerticalSpacing(5)
        
        self.start_entries = {}
        for i, label in enumerate(['R', 'G', 'B']):
            # 添加标签
            label_widget = QLabel(label)
            label_widget.setAlignment(Qt.AlignCenter)
            label_widget.setStyleSheet(rgb_frame_style)
            start_rgb_grid.addWidget(label_widget, 0, i)
            
            # 添加输入框
            entry = QLineEdit()
            entry.setFixedWidth(50)
            entry.setText(str(start_color[i]))
            entry.setValidator(QIntValidator(0, 255))
            entry.textChanged.connect(self.update_start_color)
            entry.setAlignment(Qt.AlignCenter)
            entry.setStyleSheet(f"background-color: {self.style['input_bg_color']};")
            start_rgb_grid.addWidget(entry, 1, i)
            
            self.start_entries[f"start_{label}"] = entry
            
        # 添加RGB网格布局
        start_layout.addLayout(start_rgb_grid)
        
        # 将起始颜色区域添加到主布局
        self.main_layout.addWidget(self.start_frame)
        
        # 渐变选项
        if enable_gradient:
            # 创建渐变复选框和终止颜色区域
            gradient_frame = QFrame()
            gradient_frame.setStyleSheet(f"background-color: {self.style['card_color']};")
            gradient_layout = QVBoxLayout(gradient_frame)
            gradient_layout.setContentsMargins(0, 0, 0, 0)
            
            self.gradient_checkbox = QCheckBox("启用颜色渐变")
            self.gradient_checkbox.setFont(QFont(self.style["font_family"], self.style["body_font_size"]))
            self.gradient_checkbox.setChecked(False)
            self.gradient_checkbox.stateChanged.connect(self.toggle_gradient)
            self.gradient_checkbox.setStyleSheet(f"background-color: {self.style['card_color']};")
            
            gradient_layout.addWidget(self.gradient_checkbox, alignment=Qt.AlignCenter)
            gradient_layout.addStretch()
            
            self.main_layout.addWidget(gradient_frame)
            
            # 创建终止颜色区域
            self.end_frame = QFrame()
            self.end_frame.setStyleSheet(f"background-color: {self.style['card_color']};")
            end_layout = QVBoxLayout(self.end_frame)
            end_layout.setContentsMargins(0, 0, 0, 0)
            end_layout.setSpacing(8)
            
            # 终止颜色标题和状态标签布局
            end_title_layout = QHBoxLayout()
            end_title_layout.setAlignment(Qt.AlignCenter)  # 整体居中
            
            # 创建一个容器来包含标题和状态
            title_container = QWidget()
            title_container_layout = QHBoxLayout(title_container)
            title_container_layout.setContentsMargins(0, 0, 0, 0)
            title_container_layout.setSpacing(5)
            
            self.end_label = QLabel("终止颜色")
            self.end_label.setFont(QFont(self.style["font_family"], self.style["body_font_size"]))
            title_container_layout.addWidget(self.end_label)
            
            # 添加状态标签
            self.disabled_label = QLabel("[已禁用]")
            self.disabled_label.setFont(QFont(self.style["font_family"], 9))
            self.disabled_label.setStyleSheet("color: #ff0000;")  # 红色文字
            title_container_layout.addWidget(self.disabled_label)
            
            # 将容器添加到布局中
            end_title_layout.addWidget(title_container)
            end_layout.addLayout(end_title_layout)
            
            # 颜色预览
            self.end_preview = ColorPreview(color=end_color)
            end_layout.addWidget(self.end_preview, alignment=Qt.AlignCenter)
            
            # RGB输入框 - 使用网格布局确保对齐
            end_rgb_grid = QGridLayout()
            end_rgb_grid.setHorizontalSpacing(10)
            end_rgb_grid.setVerticalSpacing(5)
            
            self.end_entries = {}
            for i, label in enumerate(['R', 'G', 'B']):
                # 添加标签
                label_widget = QLabel(label)
                label_widget.setAlignment(Qt.AlignCenter)
                label_widget.setStyleSheet(rgb_frame_style)
                end_rgb_grid.addWidget(label_widget, 0, i)
                
                # 添加输入框
                entry = QLineEdit()
                entry.setFixedWidth(50)
                entry.setText(str(end_color[i]))
                entry.setValidator(QIntValidator(0, 255))
                entry.textChanged.connect(self.update_end_color)
                entry.setAlignment(Qt.AlignCenter)
                entry.setStyleSheet(f"background-color: {self.style['input_bg_color']};")
                end_rgb_grid.addWidget(entry, 1, i)
                
                self.end_entries[f"end_{label}"] = entry
            
            # 添加RGB网格布局
            end_layout.addLayout(end_rgb_grid)
            self.main_layout.addWidget(self.end_frame)
            
            # 初始状态设置为禁用
            self.disabled_label.hide()  # 初始化时隐藏禁用标签
            self.toggle_gradient(False)  # 初始化为禁用状态
        
        # 将所有输入控件添加到父窗口的entries字典中
        if parent and hasattr(parent, 'entries'):
            entries = self.get_entries()
            parent.entries.update(entries)
        
        # 初始化颜色预览
        self.update_start_color()
        if enable_gradient:
            self.update_end_color()
            
    def update_start_color(self):
        """更新起始颜色预览"""
        try:
            r = int(self.start_entries['start_R'].text() or 0)
            g = int(self.start_entries['start_G'].text() or 0)
            b = int(self.start_entries['start_B'].text() or 0)
            
            # 更新颜色预览
            self.start_preview.set_color((r, g, b))
            
            # 如果终止颜色渐变未启用，同时更新终止颜色预览
            if hasattr(self, 'gradient_checkbox') and not self.gradient_checkbox.isChecked() and hasattr(self, 'end_preview'):
                self.end_preview.set_color((r, g, b))
            
        except (ValueError, AttributeError):
            pass
            
    def update_end_color(self):
        """更新终止颜色预览"""
        try:
            r = int(self.end_entries['end_R'].text() or 0)
            g = int(self.end_entries['end_G'].text() or 0)
            b = int(self.end_entries['end_B'].text() or 0)
            
            # 保存当前终止颜色值（用于在渐变禁用时保留）
            self.current_end_color = (r, g, b)
            
            # 更新颜色预览
            if hasattr(self, 'gradient_checkbox') and self.gradient_checkbox.isChecked():
                self.end_preview.set_color((r, g, b))
        except (ValueError, AttributeError):
            pass
            
    def toggle_gradient(self, state):
        """启用/禁用渐变
        
        参数:
            state: 复选框状态，True为选中，False为未选中
        """
        is_enabled = bool(state)
        
        # 设置终止颜色输入框状态
        for entry in self.end_entries.values():
            entry.setEnabled(is_enabled)
            
        # 修改终止颜色区域的视觉样式，提供明显的状态反馈
        if not is_enabled:
            # 禁用状态：只添加灰色背景
            self.end_frame.setStyleSheet(f"""
                background-color: #f0f0f0;  /* 使用灰色背景表示禁用 */
            """)
            # 显示禁用标签
            self.disabled_label.show()
            
            # 禁用时，终止颜色显示仍为当前设置的颜色，而不是修改为起始颜色
            # 我们不需要在这里修改颜色预览，因为即使禁用，值仍然有效
        else:
            # 启用状态：恢复正常样式
            self.end_frame.setStyleSheet(f"background-color: {self.style['card_color']};")
            # 隐藏禁用标签
            self.disabled_label.hide()
            
            # 更新终止颜色预览（颜色值保持不变）
            try:
                r = int(self.end_entries['end_R'].text() or 0)
                g = int(self.end_entries['end_G'].text() or 0)
                b = int(self.end_entries['end_B'].text() or 0)
                self.end_preview.set_color((r, g, b))
            except (ValueError, AttributeError):
                pass
                
    def get_colors(self):
        """获取颜色值
        
        返回:
            tuple: (start_color, end_color, is_gradient)
            其中:
                start_color: 起始颜色，格式为(r, g, b)
                end_color: 终止颜色，格式为(r, g, b)，如果禁用渐变则保留终止颜色的设置值
                is_gradient: 是否启用渐变，布尔值
        """
        # 获取起始颜色
        r = int(self.start_entries['start_R'].text())
        g = int(self.start_entries['start_G'].text())
        b = int(self.start_entries['start_B'].text())
        start_color = (r, g, b)
        
        # 判断渐变状态
        is_gradient = False
        if hasattr(self, 'gradient_checkbox'):
            is_gradient = self.gradient_checkbox.isChecked()
        
        # 获取终止颜色（无论是否启用渐变，都获取真实设置的终止颜色）
        r = int(self.end_entries['end_R'].text())
        g = int(self.end_entries['end_G'].text())
        b = int(self.end_entries['end_B'].text())
        end_color = (r, g, b)
            
        return start_color, end_color, is_gradient
        
    @staticmethod
    def get_color_values_from_entries(entries):
        """从表单entries字典中获取颜色值
        
        参数:
            entries: 表单entries字典
            
        返回:
            tuple: (start_color, end_color, is_gradient)
            其中:
                start_color: 起始颜色，格式为(r, g, b)
                end_color: 终止颜色，格式为(r, g, b)
                is_gradient: 是否启用渐变，布尔值
        """
        try:
            # 获取起始颜色
            start_r_entry = entries.get('start_R', entries.get('R'))
            start_g_entry = entries.get('start_G', entries.get('G')) 
            start_b_entry = entries.get('start_B', entries.get('B'))
            
            # 从QLineEdit中获取文本值
            if hasattr(start_r_entry, 'text'):
                start_r = int(start_r_entry.text())
                start_g = int(start_g_entry.text())
                start_b = int(start_b_entry.text())
            else:
                # 如果不是QLineEdit对象，尝试直接转换
                start_r = int(start_r_entry or 0)
                start_g = int(start_g_entry or 0) 
                start_b = int(start_b_entry or 0)
                
            start_color = (start_r, start_g, start_b)
            
            # 获取是否使用渐变
            is_gradient = False
            gradient_checkbox = entries.get('启用颜色渐变')
            if gradient_checkbox and hasattr(gradient_checkbox, 'isChecked'):
                is_gradient = gradient_checkbox.isChecked()
            
            # 获取终止颜色（无论是否启用渐变）
            end_r_entry = entries.get('end_R', entries.get('R'))
            end_g_entry = entries.get('end_G', entries.get('G'))
            end_b_entry = entries.get('end_B', entries.get('B'))
            
            # 从QLineEdit中获取文本值
            if hasattr(end_r_entry, 'text'):
                end_r = int(end_r_entry.text())
                end_g = int(end_g_entry.text())
                end_b = int(end_b_entry.text())
            else:
                # 如果不是QLineEdit对象，尝试直接转换
                end_r = int(end_r_entry or 0)
                end_g = int(end_g_entry or 0)
                end_b = int(end_b_entry or 0)
                
            end_color = (end_r, end_g, end_b)
            
            return start_color, end_color, is_gradient
            
        except (ValueError, KeyError, AttributeError) as e:
            # 如果发生异常，返回默认值
            traceback.print_exc()
            return (255, 0, 0), (255, 0, 0), False

    def set_colors(self, start_color, end_color=None, is_gradient=False):
        """设置颜色值
        
        参数:
            start_color: 起始颜色，格式为(r, g, b)
            end_color: 终止颜色，格式为(r, g, b)，如果为None则与起始颜色相同
            is_gradient: 是否启用渐变色
        """
        if end_color is None:
            end_color = start_color
            
        # 设置起始颜色
        self.start_preview.set_color(start_color)
        self.start_entries['start_R'].setText(str(start_color[0]))
        self.start_entries['start_G'].setText(str(start_color[1]))
        self.start_entries['start_B'].setText(str(start_color[2]))
        
        # 如果有渐变选项
        if hasattr(self, 'gradient_checkbox'):
            # 设置终止颜色
            self.end_preview.set_color(end_color)
            self.end_entries['end_R'].setText(str(end_color[0]))
            self.end_entries['end_G'].setText(str(end_color[1]))
            self.end_entries['end_B'].setText(str(end_color[2]))
            
            # 设置渐变启用状态
            self.gradient_checkbox.setChecked(is_gradient)
            self.toggle_gradient(is_gradient)

    def get_entries(self):
        """获取组件中的所有输入控件
        
        返回:
            dict: 输入控件字典
        """
        entries = {}
        
        # 添加起始颜色输入框
        entries.update(self.start_entries)
        
        # 如果有渐变选项，添加渐变复选框和终止颜色输入框
        if hasattr(self, 'gradient_checkbox'):
            entries['启用颜色渐变'] = self.gradient_checkbox
            entries.update(self.end_entries)
            
        return entries 