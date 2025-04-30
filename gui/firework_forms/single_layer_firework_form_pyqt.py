from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.lib import basic_fireworks
from gui.templates.firework_form_base import FireworkFormBase
from gui.components.validators import Validators

# 默认参数定义
DEFAULT_START_COLOR = (255, 0, 0)
DEFAULT_END_COLOR = (255, 0, 0)
DEFAULT_HORIZONTAL_ANGLE = "30"
DEFAULT_VERTICAL_ANGLE = "30"
DEFAULT_EXPLODE_DURATION = "1.5"
DEFAULT_EXPLODE_SPEED = "30"
DEFAULT_PARTICLE_LIFETIME = "1.0"

class SingleLayerFireworkForm(FireworkFormBase):
    """单层烟花表单类"""
    
    def __init__(self, parent=None, traj_end_data=None, style=None):
        """
        初始化单层烟花表单
        
        参数:
            parent: 父窗口
            traj_end_data: 轨迹终点数据，格式为(tick, x, y, z)
            style: 样式字典，如果为None则创建默认样式
        """
        # 设置窗口标题（供父类初始化使用）
        self.title = "单层烟花设置"
        
        # 先检查参数
        if traj_end_data is None:
            traj_end_data = (60, 0.0, 100.0, 0.0)  # 使用默认值
        
        if not isinstance(traj_end_data, tuple) or len(traj_end_data) != 4:
            traj_end_data = (60, 0.0, 100.0, 0.0)  # 使用默认值
        
        try:
            # 调用父类初始化
            super().__init__(parent=parent, traj_end_data=traj_end_data, style=style)
            
            # 创建颜色设置区域
            self.setup_color_section(DEFAULT_START_COLOR, DEFAULT_END_COLOR)
            
            # 设置角度参数
            self.setup_angle_section(DEFAULT_HORIZONTAL_ANGLE, DEFAULT_VERTICAL_ANGLE)
            
            # 设置爆炸参数
            explosion_params = ['烟花持续时间 (秒)', '爆炸速度 (m/s)', '粒子生存时间 (秒)']
            explosion_defaults = [DEFAULT_EXPLODE_DURATION, DEFAULT_EXPLODE_SPEED, DEFAULT_PARTICLE_LIFETIME]
            self.setup_explosion_section(explosion_params, explosion_defaults)
            
            # 设置提交按钮
            self.setup_submit_button("生成单层烟花")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def process_data(self):
        """处理表单数据，返回处理结果
        
        返回:
            tuple: (x, y, z) 烟花位置
        """
        # 使用基类方法获取颜色
        start_color, end_color, is_gradient = self.get_color_values()
            
        # 获取角度参数
        horizontal_angle_step = int(self.entries['水平角度间隔 (°)'].text())
        vertical_angle_step = int(self.entries['垂直角度间隔 (°)'].text())
            
        # 获取其他参数
        duration = float(self.entries['烟花持续时间 (秒)'].text())
        speed = float(self.entries['爆炸速度 (m/s)'].text())
        lifetime = float(self.entries['粒子生存时间 (秒)'].text())
        
        # 验证参数
        validation_map = self.get_basic_validation_map()
        valid = self.validate_entries(validation_map)
        if not valid:
            raise ValueError("输入验证失败，请检查参数")
            
        # 生成烟花
        basic_fireworks.basic_single_layer_firework(
            self.tick,  # tick
            self.x,  # x
            self.y,  # y
            self.z,  # z
            start_color,
            end_color if is_gradient else start_color,
            speed,
            horizontal_angle_step,
            vertical_angle_step,
            duration,
            lifetime
        )
        
        return (self.x, self.y, self.z)

# 测试代码
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    from gui.style.style_factory import StyleFactory
    window = SingleLayerFireworkForm(traj_end_data=(60, 0, 100, 0))
    window.show()
    sys.exit(app.exec_()) 