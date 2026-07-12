# pylint: skip-file
# flake8: noqa
from PyQt5.QtWidgets import (QApplication, QLabel, QLineEdit, QTextEdit, QGridLayout, 
                          QGroupBox, QMessageBox, QWidget, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from gui.templates.base_window import BaseWindow
from gui.lib import export_mcfunction, global_storage
import re
import os

datapack_name = ''
datapack_namespace = None
datapack_description = ''
output_dir = None

class DatapackForm(BaseWindow):
    """数据包创建界面"""
    
    def __init__(self, parent=None, style=None):
        """
        初始化数据包创建界面
        
        参数:
            parent: 父窗口
            style: 样式字典，如果为None则创建默认样式
        """
        super().__init__("创建数据包", (800, 600), style)
        self.parent = parent
        
        # 创建标题
        self.title_label = self.create_title("DynFirework 数据包生成器")
        
        # 创建数据包信息分组
        info_group = QGroupBox("数据包信息")
        info_group.setStyleSheet(f"""
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
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: {self.style["card_color"]};
            }}
        """)
        
        # 创建网格布局
        grid_layout = QGridLayout(info_group)
        grid_layout.setContentsMargins(
            self.style["padding_large"], 
            self.style["padding_large"], 
            self.style["padding_large"], 
            self.style["padding_large"]
        )
        grid_layout.setSpacing(self.style["padding_medium"])
        
        # 添加到主布局
        self.main_layout.addWidget(info_group)
        
        # 创建表单字段
        self.entries = {}
        labels = ['数据包名称', '命名空间 (*)', '数据包描述']
        default_values = ['DynFirework', 'firework', 'DynFirework生成的烟花']
        tooltips = ['', '只能包含小写字母、数字、下划线和点', '']
        
        # 创建标签和输入框
        for i, field_name in enumerate(labels):
            # 创建标签
            label = QLabel(field_name)
            label.setFont(QFont(self.style["font_family"], self.style["body_font_size"]))
            label.setStyleSheet(f"color: {self.style['text_color']};")
            grid_layout.addWidget(label, i, 0, 1, 1)
            
            # 创建输入框
            if field_name == '数据包描述':
                # 多行文本框
                entry = QTextEdit()
                entry.setMinimumHeight(100)
                entry.setText(default_values[i])
                entry.setStyleSheet(f"""
                    QTextEdit {{
                        border: 1px solid {self.style["border_color"]};
                        border-radius: {self.style["border_radius"]}px;
                        padding: 5px;
                        background-color: {self.style["input_bg_color"]};
                    }}
                """)
            else:
                # 单行文本框
                entry = QLineEdit()
                entry.setText(default_values[i])
                entry.setMinimumWidth(300)
                entry.setStyleSheet(f"""
                    QLineEdit {{
                        border: 1px solid {self.style["border_color"]};
                        border-radius: {self.style["border_radius"]}px;
                        padding: 8px;
                        background-color: {self.style["input_bg_color"]};
                    }}
                """)
            
            # 设置工具提示    
            if tooltips[i]:
                tip_label = QLabel(tooltips[i])
                tip_label.setStyleSheet(f"color: #666666; background-color: transparent;")
                grid_layout.addWidget(tip_label, i, 2, 1, 1)
                
            grid_layout.addWidget(entry, i, 1, 1, 1)
            self.entries[field_name] = entry
        
        # 调整列宽度
        grid_layout.setColumnStretch(1, 1)
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, self.style["padding_large"], 0, 0)
        button_layout.addStretch()
        
        # 创建提交按钮
        submit_button = QPushButton("创建数据包")
        submit_button.setMinimumSize(180, 45)
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
        submit_button.clicked.connect(self.submit)
        
        button_layout.addWidget(submit_button)
        self.main_layout.addLayout(button_layout)
        
        # 添加一些空间，使布局更加美观
        self.main_layout.addStretch()
    
    def submit(self):
        """提交表单数据"""
        submits = {}
        
        # 获取表单数据
        for key, entry in self.entries.items():
            if key == '数据包描述':
                # 从QTextEdit获取文本
                submits[key] = entry.toPlainText().strip()
            else:
                # 从QLineEdit获取文本
                submits[key] = entry.text().strip()
        
        # 全局变量设置
        global datapack_name, datapack_namespace, datapack_description, output_dir
        
        datapack_name = submits["数据包名称"]
        datapack_namespace = submits["命名空间 (*)"]
        datapack_description = submits["数据包描述"]
        
        # 验证命名空间
        if not re.match(r'^[a-z0-9_\.]+$', datapack_namespace):
            QMessageBox.critical(self, '错误', '命名空间只能包含小写字母、数字、下划线和点')
            self.entries['命名空间 (*)'].setFocus()
            return
        
        # 生成数据包文件
        success, new_output_dir = export_mcfunction.generate_data_pack(datapack_name, datapack_namespace, datapack_description)
        
        if not success:
            QMessageBox.critical(self, '错误', '创建数据包失败，请检查路径权限和磁盘空间')
            return
            
        # 更新输出目录
        output_dir = new_output_dir
        
        # 显示成功消息
        QMessageBox.information(
            self, 
            'DynFirework',
            f'成功创建Minecraft 1.16.5数据包\n数据包名称: {datapack_name}\n命名空间: {datapack_namespace}'
        )
        
        # 跳转到轨迹选择界面
        self.open_trajectory_select()
    
    def open_trajectory_select(self):
        """打开轨迹选择界面"""
        from gui.selection.select_traj import TrajectorySelect
        
        # 创建轨迹选择界面
        self.traj_select = TrajectorySelect(self, self.style)
        self.traj_select.show()
        
        # 隐藏当前窗口
        self.hide()

# 测试代码
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    from gui.style.style_factory import StyleFactory
    style = StyleFactory.create_style()
    StyleFactory.apply_application_style(app)
    window = DatapackForm(style=style)
    window.show()
    sys.exit(app.exec_())
