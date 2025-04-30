from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QMessageBox
from PyQt5.QtCore import Qt
from gui.templates.base_form import BaseForm
from gui.components.position_setting import PositionSettingWidget
from gui.components.color_setting import ColorSettingWidget
import os

class TrajectoryFormBase(BaseForm):
    """轨迹表单基类，所有轨迹表单的基类"""
    
    def __init__(self, parent=None, title="轨迹表单", start_pos=(0, 0, 0), end_pos=(50, 100, 30), 
                start_color=(255, 255, 255), end_color=(255, 255, 255), style=None):
        """
        初始化轨迹表单基类
        
        参数:
            parent: 父窗口
            title: 表单标题
            start_pos: 起始位置，格式为(x, y, z)
            end_pos: 终止位置，格式为(x, y, z)
            start_color: 起始颜色，格式为(r, g, b)
            end_color: 终止颜色，格式为(r, g, b)
            style: 样式字典，如果为None则创建默认样式
        """
        super().__init__(title, (900, 700), style)
        
        # 保存父窗口引用
        self.parent_window = parent
        
        # 初始化数据包信息
        self.datapack_namespace = getattr(parent, 'datapack_namespace', None)
        self.output_dir = getattr(parent, 'output_dir', None)
        
        # 保存通用参数
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.start_color = start_color
        self.end_color = end_color
        
        # 创建位置设置组件
        self.setup_position_section()
        
        # 添加关闭标志，用于区分正常关闭和提交后关闭
        self._is_submitted = False
        self._is_redirected = False
    
    def setup_position_section(self):
        """设置位置区域"""
        # 创建位置设置分区
        position_section, position_layout = self.create_section("位置设置")
        
        # 创建位置设置组件
        self.position_widget = PositionSettingWidget(
            start_pos=self.start_pos,
            end_pos=self.end_pos,
            style=self.style
        )
        
        # 添加到布局
        position_layout.addWidget(self.position_widget)
    
    def setup_color_section(self, with_gradient=True):
        """设置颜色区域
        
        参数:
            with_gradient: 是否启用渐变色选项
        """
        # 创建颜色设置分区
        color_section, color_layout = self.create_section("颜色设置")
        
        # 创建颜色设置组件
        self.color_widget = ColorSettingWidget(
            start_color=self.start_color,
            end_color=self.end_color,
            enable_gradient=with_gradient,
            style=self.style
        )
        
        # 添加到布局
        color_layout.addWidget(self.color_widget)
    
    def setup_physics_section(self, params, defaults):
        """设置其它参数区域 (原物理参数)
        
        参数:
            params: 参数标签列表
            defaults: 参数默认值列表
        """
        # 创建其它参数分区
        physics_section, physics_layout = self.create_section("其它参数")
        
        # 创建网格布局
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(10)
        
        # 添加参数输入
        for i, (label, default) in enumerate(zip(params, defaults)):
            # 创建标签
            label_widget = QLabel(label)
            label_widget.setStyleSheet(f"""
                font-family: {self.style["font_family"]};
                font-size: {self.style["body_font_size"]}px;
                color: {self.style["text_color"]};
            """)
            
            # 创建输入框
            entry = QLineEdit()
            entry.setText(str(default))
            entry.setFixedWidth(150)
            entry.setAlignment(Qt.AlignCenter)
            entry.setStyleSheet(f"""
                background-color: {self.style["card_color"]};
                color: {self.style["text_color"]};
                border: 1px solid {self.style["border_color"]};
                border-radius: {self.style["border_radius"]}px;
                padding: 5px;
            """)
            
            # 添加到网格布局
            grid.addWidget(label_widget, i, 0, alignment=Qt.AlignRight)
            grid.addWidget(entry, i, 1, alignment=Qt.AlignLeft)
            
            # 保存到entries字典
            self.entries[label] = entry
        
        # 添加网格布局到分区
        physics_layout.addLayout(grid)
    
    def setup_submit_button(self, text="生成轨迹"):
        """设置提交按钮
        
        参数:
            text: 按钮文本
        """
        # 创建提交按钮和取消按钮
        submit_button = self.create_submit_button(text, self.submit)
        cancel_button = self.create_cancel_button("返回", self.go_back)
    
    def go_back(self):
        """返回到轨迹选择界面"""
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
    
    def closeEvent(self, event):
        """处理窗口关闭事件 - 当用户点击 X 按钮时"""
        # 如果是通过提交表单关闭的，直接接受关闭事件
        if self._is_submitted:
            event.accept()
            return
            
        # 如果是通过点击X按钮关闭的，显示确认对话框
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
            event.accept()
            # 返回轨迹选择界面（如果存在）
            if self.parent_window and not self._is_redirected:
                self.parent_window.show()
        else:
            # 拒绝关闭事件，窗口保持打开
            event.ignore()
    
    def get_position_values(self):
        """获取位置值
        
        返回:
            tuple: (start_pos, end_pos)
        """
        return self.position_widget.get_positions()
    
    def get_color_values(self):
        """获取颜色值
        
        返回:
            tuple: (start_color, end_color)，始终返回真实设置的两个颜色
        """
        start_color, end_color, is_gradient = self.color_widget.get_colors()
        return start_color, end_color
    
    def process_data(self):
        """处理表单数据，需要在子类中实现"""
        raise NotImplementedError("子类必须实现process_data方法")
    
    def submit(self):
        """提交表单"""
        from PyQt5.QtWidgets import QMessageBox
        try:
            # 调用数据处理方法
            result = self.process_data()
            
            # 显示成功消息 - 正确处理长度为4的元组
            if isinstance(result, tuple) and len(result) == 4:
                end_tick, x, y, z = result
                message = f"轨迹已生成\n终点Tick: {end_tick}\n终点位置: ({x}, {y}, {z})"
            else:
                # 如果返回结果格式不正确，显示通用消息
                message = "轨迹已生成 (无法获取详细坐标)"
                
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
            continueButton = msgBox.addButton('继续创建烟花', QMessageBox.ActionRole)
            exportButton = msgBox.addButton('导出并退出', QMessageBox.ActionRole)
            
            msgBox.setDefaultButton(continueButton)
            msgBox.exec_()
            
            clickedButton = msgBox.clickedButton()
            
            # 设置提交标志，避免触发确认退出对话框
            self._is_submitted = True
            
            if clickedButton == continueButton:
                # 选择"继续创建"：直接创建烟花选择界面，不显示确认对话框
                from gui.selection.select_firework import FireworkSelect
                
                # 设置重定向标志
                self._is_redirected = True
                
                # 创建新的烟花选择界面 - 传递轨迹数据 result 给 traj_info
                firework_select = FireworkSelect(parent=None, traj_info=result, style=self.style)
                
                # 传递数据包信息
                if datapack_namespace is not None:
                    firework_select.datapack_namespace = datapack_namespace
                if output_dir is not None:
                    firework_select.output_dir = output_dir
                
                # 显示烟花选择界面
                firework_select.show()
                
                # 关闭当前窗口
                self.close()
                
                # 如果有轨迹选择窗口，也关闭它
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