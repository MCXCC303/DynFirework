from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QMessageBox, QFormLayout, QHBoxLayout, QGroupBox, QPushButton, QCheckBox, QScrollArea, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from gui.templates.base_form import BaseForm
from gui.components.color_setting import ColorSettingWidget
from gui.components.validators import Validators
import re
from gui.lib.global_storage import horizontal_angle_step_default, vertical_angle_step_default
import os

class FireworkFormBase(BaseForm):
    """烟花表单基类，所有烟花表单的基类"""
    
    def __init__(self, parent=None, traj_end_data=None, style=None):
        """
        初始化烟花表单基类
        
        参数:
            parent: 父窗口，通常是FireworkSelect实例
            traj_end_data: 轨迹终点数据 (tick, x, y, z)
            style: 样式表对象
        """
        # 初始化标题，使用子类设置后的title，如果没有则使用默认值
        title = getattr(self, "title", "烟花表单")
        
        try:
            # 调用BaseForm的初始化方法，但不设置parent
            super().__init__(title, (800, 600), style)
            
            # 只保存父窗口引用，但不设置Qt的parent关系
            self.parent_window = parent
            
            # 从parent获取命名空间和输出目录
            self.datapack_namespace = getattr(parent, 'datapack_namespace', None)
            self.output_dir = getattr(parent, 'output_dir', None)
            
            # 初始化轨迹信息
            self.tick = 60  # 默认值
            self.x = 0.0
            self.y = 100.0
            self.z = 0.0
            
            # 从全局设置中获取默认角度步长
            self.horizontal_angle_step = horizontal_angle_step_default
            self.vertical_angle_step = vertical_angle_step_default
            
            # 处理轨迹终点数据 - 添加显式类型转换和更健壮的错误处理
            if traj_end_data is not None and isinstance(traj_end_data, tuple) and len(traj_end_data) == 4:
                try:
                    # 尝试解包并进行类型转换
                    tick_val, x_val, y_val, z_val = traj_end_data
                    self.tick = int(tick_val)
                    self.x = float(x_val)
                    self.y = float(y_val)
                    self.z = float(z_val)
                except (ValueError, TypeError) as e:
                    # 如果转换失败，记录错误并使用默认值（初始化的值）
                    pass
            # else: # 如果 traj_end_data 格式不对或为 None，则默认值已在初始化时设置
                # pass
            
            # 确保表单是顶级窗口
            if not self.isWindow():
                self.setWindowFlags(Qt.Window)
            
            # 添加关闭标志，用于区分正常关闭和提交后关闭
            self._is_submitted = False
            self._is_redirected = False
            
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def get_style(self, key, default=None):
        """安全地获取样式值
        
        参数:
            key: 样式键
            default: 默认值，如果键不存在则返回此值
            
        返回:
            样式值或默认值
        """
        # 预定义的样式默认值
        defaults = {
            "font_family": "Arial",
            "title_font_size": 18,
            "subtitle_font_size": 14,
            "body_font_size": 12,
            "button_font_size": 14,
            "primary_color": "#4287f5",
            "secondary_color": "#f0f0f0",
            "text_color": "#333333",
            "button_text_color": "#ffffff",
            "button_hover_color": "#5a9afa",
            "button_pressed_color": "#3276e4",
            "background_color": "#f9f9f9",
            "card_color": "#ffffff",
            "border_color": "#dddddd",
            "border_radius": 6,
            "hover_color": "#5a9afa",
            "active_color": "#3276e4",
            "padding_small": 5,
            "padding_medium": 10,
            "padding_large": 15,
            "margin_small": 5,
            "margin_medium": 10,
            "margin_large": 15
        }
        
        # 尝试从样式字典获取值
        if self.style and key in self.style:
            return self.style[key]
        
        # 如果不存在，尝试使用预定义的默认值
        if key in defaults:
            if self.style:
                # 将默认值添加到样式字典中
                self.style[key] = defaults[key]
            return defaults[key]
        
        # 否则返回指定的默认值
        return default
    
    def set_data(self):
        """设置数据，可在子类中重写此方法以设置特定数据"""
        pass
    
    def setup_color_section(self, start_color=(255, 0, 0), end_color=(255, 0, 0), with_gradient=True):
        """设置颜色区域
        
        参数:
            start_color: 开始颜色，格式为(r,g,b)，默认为红色
            end_color: 结束颜色，格式为(r,g,b)，默认为红色
            with_gradient: 是否显示渐变色设置，默认为True
        """
        # 创建颜色设置区域
        section, section_layout = self.create_section("颜色设置")
        
        # 使用ColorSettingWidget创建颜色设置组件
        color_setting = ColorSettingWidget(
            parent=self,  # 传递self作为父窗口
            start_color=start_color, 
            end_color=end_color, 
            enable_gradient=with_gradient,
            style=self.style
        )
        section_layout.addWidget(color_setting)
        
        # 添加到entries
        self.entries.update(color_setting.get_entries())
    
    def setup_angle_section(self, default_horizontal_angle="30", default_vertical_angle="30"):
        """设置角度区域
        
        参数:
            default_horizontal_angle: 默认水平角度间隔，字符串类型
            default_vertical_angle: 默认垂直角度间隔，字符串类型
        """
        section, section_layout = self.create_section("角度设置")
        
        # 创建表单布局
        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(10)
        section_layout.addLayout(form_layout)
        
        # 创建水平角度输入框
        h_angle_label = QLabel("水平角度间隔 (°)")
        h_angle_label.setStyleSheet(f"font-family: {self.get_style('font_family')}; font-size: {self.get_style('body_font_size')}px;")
        
        h_angle_edit = QLineEdit(default_horizontal_angle)
        h_angle_edit.setStyleSheet(f"""
            QLineEdit {{
                padding: 5px;
                border-radius: {self.get_style('border_radius')}px;
                border: 1px solid {self.get_style('border_color')};
                background-color: white;
                font-family: {self.get_style('font_family')};
                font-size: {self.get_style('body_font_size')}px;
            }}
            QLineEdit:focus {{
                border: 1px solid {self.get_style('primary_color')};
            }}
        """)
        form_layout.addRow(h_angle_label, h_angle_edit)
        self.entries['水平角度间隔 (°)'] = h_angle_edit
        
        # 创建垂直角度输入框
        v_angle_label = QLabel("垂直角度间隔 (°)")
        v_angle_label.setStyleSheet(f"font-family: {self.get_style('font_family')}; font-size: {self.get_style('body_font_size')}px;")
        
        v_angle_edit = QLineEdit(default_vertical_angle)
        v_angle_edit.setStyleSheet(f"""
            QLineEdit {{
                padding: 5px;
                border-radius: {self.get_style('border_radius')}px;
                border: 1px solid {self.get_style('border_color')};
                background-color: white;
                font-family: {self.get_style('font_family')};
                font-size: {self.get_style('body_font_size')}px;
            }}
            QLineEdit:focus {{
                border: 1px solid {self.get_style('primary_color')};
            }}
        """)
        form_layout.addRow(v_angle_label, v_angle_edit)
        self.entries['垂直角度间隔 (°)'] = v_angle_edit
    
    def setup_explosion_section(self, params, defaults):
        """设置爆炸参数区域
        
        参数:
            params: 参数名称列表，例如['爆炸时间 (秒)', '爆炸速度 (m/s)']
            defaults: 默认值列表，与params长度相同
        """
        section, section_layout = self.create_section("爆炸参数")
        
        # 创建表单布局
        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(10)
        section_layout.addLayout(form_layout)
        
        # 为每个参数创建输入框
        for param, default in zip(params, defaults):
            label = QLabel(param)
            label.setStyleSheet(f"font-family: {self.get_style('font_family')}; font-size: {self.get_style('body_font_size')}px;")
            
            edit = QLineEdit(str(default))
            edit.setStyleSheet(f"""
                QLineEdit {{
                    padding: 5px;
                    border-radius: {self.get_style('border_radius')}px;
                    border: 1px solid {self.get_style('border_color')};
                    background-color: white;
                    font-family: {self.get_style('font_family')};
                    font-size: {self.get_style('body_font_size')}px;
                }}
                QLineEdit:focus {{
                    border: 1px solid {self.get_style('primary_color')};
                }}
            """)
            form_layout.addRow(label, edit)
            self.entries[param] = edit
    
    def setup_submit_button(self, text="生成烟花"):
        """设置提交按钮
        
        参数:
            text: 按钮文本
        """
        self.create_submit_button(text, self.submit)
        self.create_cancel_button("返回", self.go_back)
    
    def go_back(self):
        """返回到烟花选择界面"""
        # 如果已提交或已重定向，直接关闭
        if getattr(self, '_is_submitted', False) or getattr(self, '_is_redirected', False):
            self.close()
            return
            
        # 显示确认对话框
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 
            '确认返回', 
            '返回将丢失当前未保存的内容，确定要返回吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 用户确认返回，关闭当前窗口
            self.close()
        else:
            # 用户取消返回，不执行任何操作
            pass
    
    def get_color_values(self):
        """获取颜色值
        
        返回:
            tuple: (开始颜色, 结束颜色, 是否渐变)
        """
        # 使用静态方法从entries中获取颜色值
        return ColorSettingWidget.get_color_values_from_entries(self.entries)
    
    def get_basic_validation_map(self):
        """获取基本验证规则
        
        返回:
            dict: 验证规则映射
        """
        return {
            '水平角度间隔 (°)': Validators.angle,
            '垂直角度间隔 (°)': Validators.angle,
            '烟花持续时间 (秒)': Validators.positive_number,
            '粒子生存时间 (秒)': Validators.positive_number
        }
    
    def process_data(self):
        """处理表单数据，返回处理结果，需要在子类中实现
        
        返回:
            任意类型: 处理结果
        """
        raise NotImplementedError("process_data方法需要在子类中实现")
    
    def submit(self):
        """提交表单"""
        from PyQt5.QtWidgets import QMessageBox
        try:
            # 调用数据处理方法
            result = self.process_data()
            
            # 显示成功消息 - 直接使用 self.x, self.y, self.z
            message = f"烟花已生成\n位置: ({self.x}, {self.y}, {self.z})"
            
            # 保存数据包信息，避免在关闭窗口后丢失
            datapack_namespace = getattr(self, 'datapack_namespace', None)
            output_dir = getattr(self, 'output_dir', None)
            
            # 询问是否继续创建
            
            # 创建自定义按钮的消息框
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle('操作成功')
            msgBox.setText(message)
            msgBox.setInformativeText('请选择后续操作')
            
            # 添加自定义按钮
            continueButton = msgBox.addButton('继续创建轨迹', QMessageBox.ActionRole)
            exportButton = msgBox.addButton('导出并退出', QMessageBox.ActionRole)
            
            msgBox.setDefaultButton(continueButton)
            msgBox.exec_()
            
            clickedButton = msgBox.clickedButton()
            
            # 设置提交标志，避免触发确认退出对话框
            self._is_submitted = True
            
            if clickedButton == continueButton:
                # 选择"继续创建"：直接创建轨迹选择界面，不显示确认对话框
                from gui.selection.select_traj import TrajectorySelect
                
                # 设置重定向标志
                self._is_redirected = True
                
                # 创建新的轨迹选择界面
                traj_select = TrajectorySelect(parent=None, style=self.style)
                
                # 传递数据包信息
                if datapack_namespace is not None:
                    traj_select.datapack_namespace = datapack_namespace
                if output_dir is not None:
                    traj_select.output_dir = output_dir
                
                # 显示轨迹选择界面
                traj_select.show()
                
                # 先关闭当前窗口
                self.close()
                
                # 如果有烟花选择窗口，也关闭它
                if self.parent_window:
                    self.parent_window.close()
            else:
                # 选择"导出并退出"：导出数据包后直接退出，不再显示确认对话框
                
                # 创建默认输出目录（如果需要）
                if output_dir is None:
                    from gui.lib import global_storage
                    import os
                    
                    datapack_name = "DynFirework"
                    if datapack_namespace is None:
                        datapack_namespace = "firework"
                    
                    # 构建路径
                    constructed_dir = os.path.join(global_storage.project_dir, f"{datapack_name}/data/{datapack_namespace}/functions/")
                    # 规范化路径
                    output_dir = os.path.normpath(constructed_dir)
                    
                    if not os.path.exists(output_dir):
                        try:
                            os.makedirs(output_dir)
                        except Exception as e:
                            QMessageBox.warning(self, "警告", f"创建输出目录失败: {e}")
                            # 关闭所有窗口
                            self.close()
                            if self.parent_window:
                                self.parent_window.close()
                            return
                
                # 导出数据包
                from gui.lib import export_mcfunction
                success = export_mcfunction.schedule_next_tick(datapack_namespace)
                success = export_mcfunction.export_mcfunction(output_dir)
                if success:
                    # 显示规范化的路径
                    QMessageBox.information(self, "成功", f"数据包导出成功！\n保存位置: {os.path.normpath(output_dir)}")
                else:
                    QMessageBox.warning(self, "警告", "导出数据包失败，请检查输出路径。")
                
                # 关闭所有窗口，不显示确认对话框
                self.close()
                if self.parent_window:
                    self.parent_window.close()
                
        except ValueError as ve:
            QMessageBox.warning(self, "警告", str(ve))
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"处理表单数据时出错: {e}")
    
    def show(self):
        """显示窗口，添加更多日志记录"""
        try:
            # 确保窗口位于屏幕中心
            screen_geometry = self.screen().availableGeometry()
            window_geometry = self.frameGeometry()
            window_geometry.moveCenter(screen_geometry.center())
            self.move(window_geometry.topLeft())
            
            # 调用父类的show方法
            super().show()
            
            # 确保窗口在所有窗口之上显示
            self.raise_()
            self.activateWindow()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            
    def closeEvent(self, event):
        """处理窗口关闭事件 - 当用户点击 X 按钮时"""
        
        # 如果是通过提交表单关闭的，直接接受关闭事件
        if self._is_submitted:
            event.accept()
            return
        
        # 创建和显示确认对话框
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            '确认退出',
            '是否要退出？退出将丢失当前进度。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 接受关闭事件，关闭窗口
            # 返回烟花选择界面（如果存在）
            if self.parent_window and not self._is_redirected:
                self.parent_window.show()
            event.accept()
        else:
            # 拒绝关闭事件，窗口保持打开
            event.ignore() 