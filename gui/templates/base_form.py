from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from gui.templates.base_window import BaseWindow

class BaseForm(BaseWindow):
    """表单基础模板，所有表单的基类"""
    
    def __init__(self, title="表单", size=(900, 700), style=None):
        """
        初始化表单基础模板
        
        参数:
            title: 表单标题
            size: 窗口大小，格式为(宽度, 高度)
            style: 样式字典，如果为None则创建默认样式
        """
        try:
            # 调用父类初始化
            super().__init__(title, size, style)
            
            # 显式设置为独立窗口
            self.setWindowFlags(Qt.Window)
            
            # 创建标题
            self.create_title(title)
            
            # 创建滚动区域
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setFrameShape(QScrollArea.NoFrame)
            
            # 创建表单容器
            self.form_container = QWidget()
            self.form_layout = QVBoxLayout(self.form_container)
            self.form_layout.setContentsMargins(
                self.style["padding_medium"], 
                self.style["padding_medium"], 
                self.style["padding_medium"], 
                self.style["padding_medium"]
            )
            self.form_layout.setSpacing(self.style["padding_large"])
            
            self.scroll_area.setWidget(self.form_container)
            self.main_layout.addWidget(self.scroll_area)
            
            # 创建按钮区域
            self.button_layout = QHBoxLayout()
            self.button_layout.setContentsMargins(0, self.style["padding_medium"], 0, 0)
            self.button_layout.addStretch()
            self.main_layout.addLayout(self.button_layout)
            
            # 初始化entries字典，用于存储表单控件
            self.entries = {}
            
        except Exception as e:
            import traceback
            traceback.print_exc()
        
    def create_section(self, title):
        """创建表单分区
        
        参数:
            title: 分区标题
            
        返回:
            tuple: (QGroupBox, QVBoxLayout) 分区和分区内布局
        """
        section = QGroupBox(title)
        section.setStyleSheet(f"""
            QGroupBox {{
                font-family: {self.style["font_family"]};
                font-size: {self.style["subtitle_font_size"]}px;
                font-weight: bold;
                padding-top: 16px;
                margin-top: 8px;
                border: 1px solid {self.style["border_color"]};
                border-radius: {self.style["border_radius"]}px;
                background-color: {self.style["card_color"]};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;  /* 标题居中 */
                padding: 0 5px;
                background-color: {self.style["card_color"]};  /* 确保标题背景与分区一致 */
            }}
        """)
        
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(
            self.style["padding_large"], 
            self.style["padding_large"], 
            self.style["padding_large"], 
            self.style["padding_large"]
        )
        section_layout.setSpacing(self.style["padding_medium"])
        
        self.form_layout.addWidget(section)
        return section, section_layout
        
    def create_submit_button(self, text="提交", callback=None):
        """创建提交按钮
        
        参数:
            text: 按钮文本
            callback: 按钮点击回调函数
            
        返回:
            QPushButton: 提交按钮
        """
        submit_button = QPushButton(text)
        submit_button.setMinimumSize(120, 40)
        submit_button.setCursor(Qt.PointingHandCursor)
        submit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.style["primary_color"]};
                color: {self.style["button_text_color"]};
                border: none;
                border-radius: {self.style["border_radius"]}px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: {self.style["subtitle_font_size"]}px;
            }}
            QPushButton:hover {{
                background-color: {self.style["button_hover_color"]};
            }}
            QPushButton:pressed {{
                background-color: {self.style["button_pressed_color"]};
            }}
        """)
        
        if callback:
            submit_button.clicked.connect(callback)
            
        self.button_layout.addWidget(submit_button)
        return submit_button
        
    def create_cancel_button(self, text="取消", callback=None):
        """创建取消按钮
        
        参数:
            text: 按钮文本
            callback: 按钮点击回调函数
            
        返回:
            QPushButton: 取消按钮
        """
        cancel_button = QPushButton(text)
        cancel_button.setMinimumSize(120, 40)
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.style["text_color"]};
                border: 1px solid {self.style["border_color"]};
                border-radius: {self.style["border_radius"]}px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: {self.style["subtitle_font_size"]}px;
            }}
            QPushButton:hover {{
                background-color: {self.style["secondary_color"]};
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
        """)
        
        if callback:
            cancel_button.clicked.connect(callback)
        else:
            cancel_button.clicked.connect(self.close)
            
        self.button_layout.addWidget(cancel_button)
        return cancel_button
    
    def validate_entries(self, validation_map):
        """验证表单输入
        
        参数:
            validation_map: 验证映射字典，格式为 {字段名: 验证函数}
                           验证函数应返回 (valid, message) 元组
                           
        返回:
            bool: 验证结果，True为验证通过，False为验证失败
        """
        for field, validator in validation_map.items():
            if field not in self.entries:
                continue
                
            value = self.entries[field].text()
            valid, message = validator(value)
            
            if not valid:
                QMessageBox.warning(self, "输入验证", message)
                self.entries[field].setFocus()
                return False
                
        return True
    
    def submit_form(self):
        """
        提交表单的通用方法
        需要在子类中重写
        """
        QMessageBox.information(self, "提交", "表单提交方法需要在子类中实现")
        
    def clear_form(self):
        """清空表单内容"""
        for entry in self.entries.values():
            if hasattr(entry, "setText"):
                entry.setText("")
            elif hasattr(entry, "setChecked"):
                entry.setChecked(False)
            elif hasattr(entry, "setCurrentIndex"):
                entry.setCurrentIndex(0) 