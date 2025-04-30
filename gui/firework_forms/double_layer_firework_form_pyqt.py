from PyQt5.QtWidgets import QApplication, QVBoxLayout, QGroupBox
from gui.lib import basic_fireworks
from gui.templates.firework_form_base import FireworkFormBase
from gui.components.validators import Validators
from gui.components.color_setting import ColorSettingWidget

# 默认参数定义
DEFAULT_LAYER1_START_COLOR = (255, 0, 0)
DEFAULT_LAYER1_END_COLOR = (255, 0, 0)
DEFAULT_LAYER2_START_COLOR = (0, 0, 255)
DEFAULT_LAYER2_END_COLOR = (0, 0, 255)
DEFAULT_HORIZONTAL_ANGLE = "30"
DEFAULT_VERTICAL_ANGLE = "30"
DEFAULT_EXPLODE_DURATION = "1.5"
DEFAULT_EXPLODE_TIME_OFFSET = "0.5"
DEFAULT_LAYER1_HEIGHT = "0"
DEFAULT_LAYER2_HEIGHT = "20"
DEFAULT_PARTICLE_LIFETIME = "1.0"

class DoubleLayerFireworkForm(FireworkFormBase):
    """双层烟花表单类"""
    
    def __init__(self, parent=None, traj_end_data=None, style=None):
        """
        初始化双层烟花表单
        
        参数:
            parent: 父窗口
            traj_end_data: 轨迹终点数据，格式为(tick, x, y, z)
            style: 样式字典，如果为None则创建默认样式
        """
        # 设置窗口标题（供父类初始化使用）
        self.title = "双层烟花设置"
        
        # 先检查参数
        if traj_end_data is None:
            traj_end_data = (60, 0.0, 100.0, 0.0)  # 使用默认值
        
        if not isinstance(traj_end_data, tuple) or len(traj_end_data) != 4:
            traj_end_data = (60, 0.0, 100.0, 0.0)  # 使用默认值
        
        try:
            # 调用父类初始化
            super().__init__(parent=parent, traj_end_data=traj_end_data, style=style)
            
            # 创建两层颜色设置区域
            self.setup_double_color_section()
            
            # 设置角度参数
            self.setup_angle_section(DEFAULT_HORIZONTAL_ANGLE, DEFAULT_VERTICAL_ANGLE)
            
            # 设置爆炸参数
            explosion_params = [
                '烟花持续时间 (秒)', 
                '粒子生存时间 (秒)',
                '内层速度 (m/s)',
                '外层速度 (m/s)',
            ]
            explosion_defaults = [
                DEFAULT_EXPLODE_DURATION, 
                DEFAULT_PARTICLE_LIFETIME,
                "15",
                "25",
            ]
            self.setup_explosion_section(explosion_params, explosion_defaults)
            
            # 设置提交按钮
            self.setup_submit_button("生成双层烟花")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def setup_double_color_section(self):
        """设置双层颜色区域"""
        # 创建颜色设置分区
        color_section, color_layout = self.create_section("颜色设置")
        
        # 创建内部分组
        layer1_group = QGroupBox("第一层颜色")
        layer1_group.setStyleSheet(f"""
            QGroupBox {{
                font-family: {self.get_style("font_family")};
                font-size: {self.get_style("body_font_size")}px;
                font-weight: bold;
                padding-top: 16px;
                margin-top: 8px;
                border: 1px solid {self.get_style("border_color")};
                border-radius: {self.get_style("border_radius")}px;
                background-color: {self.get_style("card_color")};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: {self.get_style("card_color")};
            }}
        """)
        layer1_layout = QVBoxLayout(layer1_group)
        
        # 第一层颜色设置组件
        self.layer1_color_widget = ColorSettingWidget(
            parent=self,  # 传递self作为父窗口
            start_color=DEFAULT_LAYER1_START_COLOR,
            end_color=DEFAULT_LAYER1_END_COLOR,
            enable_gradient=True,
            style=self.style
        )
        layer1_layout.addWidget(self.layer1_color_widget)
        
        # 获取层1的entries并添加前缀
        layer1_entries = self.layer1_color_widget.get_entries()
        layer1_prefixed_entries = {}
        for key, entry in layer1_entries.items():
            if key == '启用颜色渐变':
                layer1_prefixed_entries['layer1_' + key] = entry
            else:
                layer1_prefixed_entries['layer1_' + key] = entry
        
        # 添加到表单entries
        self.entries.update(layer1_prefixed_entries)
        
        # 创建第二层分组
        layer2_group = QGroupBox("第二层颜色")
        layer2_group.setStyleSheet(f"""
            QGroupBox {{
                font-family: {self.get_style("font_family")};
                font-size: {self.get_style("body_font_size")}px;
                font-weight: bold;
                padding-top: 16px;
                margin-top: 8px;
                border: 1px solid {self.get_style("border_color")};
                border-radius: {self.get_style("border_radius")}px;
                background-color: {self.get_style("card_color")};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: {self.get_style("card_color")};
            }}
        """)
        layer2_layout = QVBoxLayout(layer2_group)
        
        # 第二层颜色设置组件
        self.layer2_color_widget = ColorSettingWidget(
            parent=self,  # 传递self作为父窗口
            start_color=DEFAULT_LAYER2_START_COLOR,
            end_color=DEFAULT_LAYER2_END_COLOR,
            enable_gradient=True,
            style=self.style
        )
        layer2_layout.addWidget(self.layer2_color_widget)
        
        # 获取层2的entries并添加前缀
        layer2_entries = self.layer2_color_widget.get_entries()
        layer2_prefixed_entries = {}
        for key, entry in layer2_entries.items():
            if key == '启用颜色渐变':
                layer2_prefixed_entries['layer2_' + key] = entry
            else:
                layer2_prefixed_entries['layer2_' + key] = entry
        
        # 添加到表单entries
        self.entries.update(layer2_prefixed_entries)
        
        # 添加到主布局
        color_layout.addWidget(layer1_group)
        color_layout.addWidget(layer2_group)
    
    def get_double_color_values(self):
        """获取双层颜色值
        
        返回:
            tuple: ((layer1_start_color, layer1_end_color, is_layer1_gradient), (layer2_start_color, layer2_end_color, is_layer2_gradient))
        """
        # 创建层1的entries副本
        layer1_entries = {}
        for key, entry in self.entries.items():
            if key.startswith('layer1_'):
                modified_key = key.replace('layer1_', '')
                layer1_entries[modified_key] = entry
        
        # 创建层2的entries副本
        layer2_entries = {}
        for key, entry in self.entries.items():
            if key.startswith('layer2_'):
                modified_key = key.replace('layer2_', '')
                layer2_entries[modified_key] = entry
        
        # 使用ColorSettingWidget的静态方法获取颜色值
        layer1_colors = ColorSettingWidget.get_color_values_from_entries(layer1_entries)
        layer2_colors = ColorSettingWidget.get_color_values_from_entries(layer2_entries)
        
        return (layer1_colors, layer2_colors)
    
    def process_data(self):
        """处理表单数据，返回处理结果
        
        返回:
            tuple: (x, y, z) 烟花位置
        """
        # 获取双层颜色
        (layer1_start_color, layer1_end_color, is_layer1_gradient), (layer2_start_color, layer2_end_color, is_layer2_gradient) = self.get_double_color_values()
        
        # 获取角度参数
        horizontal_angle_step = int(self.entries['水平角度间隔 (°)'].text())
        vertical_angle_step = int(self.entries['垂直角度间隔 (°)'].text())
        
        # 获取其他参数
        duration = float(self.entries['烟花持续时间 (秒)'].text())
        lifetime = float(self.entries['粒子生存时间 (秒)'].text())
        inner_speed = float(self.entries['内层速度 (m/s)'].text())
        outer_speed = float(self.entries['外层速度 (m/s)'].text())
        
        # 验证表单输入
        validation_map = self.get_basic_validation_map()
        validation_map.update({
            '内层速度 (m/s)': Validators.positive_number,
            '外层速度 (m/s)': Validators.positive_number
        })
        
        valid = self.validate_entries(validation_map)
        if not valid:
            raise ValueError("输入验证失败，请检查参数")
        
        # 生成烟花 - 注意函数名称是basic_double_layer_firework
        basic_fireworks.basic_double_layer_firework(
            self.tick,  # tick
            self.x,  # x
            self.y,  # y
            self.z,  # z
            layer1_start_color,  # inner_start_color
            layer1_end_color if is_layer1_gradient else layer1_start_color,  # inner_end_color
            layer2_start_color,  # outer_start_color
            layer2_end_color if is_layer2_gradient else layer2_start_color,  # outer_end_color
            inner_speed,  # inner_speed
            outer_speed,  # outer_speed
            horizontal_angle_step,  # outer_horizontal_angle_step
            vertical_angle_step,  # outer_vertical_angle_step
            duration,  # duration
            lifetime   # lifetime
        )
        
        return (self.x, self.y, self.z)

# 测试代码
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = DoubleLayerFireworkForm(traj_end_data=(60, 0, 100, 0))
    window.show()
    sys.exit(app.exec_()) 