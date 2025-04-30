from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.lib import basic_fireworks
from gui.templates.firework_form_base import FireworkFormBase
from gui.components.validators import Validators

# 默认参数定义
DEFAULT_START_COLOR = (255, 0, 0)
DEFAULT_END_COLOR = (255, 0, 0)
DEFAULT_HORIZONTAL_ANGLE = "45"
DEFAULT_VERTICAL_ANGLE = "45"
DEFAULT_EXPLODE_DURATION = "1.5"
DEFAULT_EXPLODE_SPEED = "25"
DEFAULT_PARTICLE_LIFETIME = "1.0"
DEFAULT_SPREAD_ANGLE = "15"
DEFAULT_TRACK_COUNT = "5"  # 添加默认轨迹数量

class ClusteredFireworkForm(FireworkFormBase):
    """集束烟花表单类"""
    
    def __init__(self, parent=None, traj_end_data=None, style=None):
        """
        初始化集束烟花表单
        
        参数:
            parent: 父窗口
            traj_end_data: 轨迹终点数据，格式为(tick, x, y, z)
            style: 样式字典，如果为None则创建默认样式
        """
        # 设置窗口标题（供父类初始化使用）
        self.title = "集束烟花设置"
        
        # 先检查参数
        if traj_end_data is None:
            traj_end_data = (60, 0.0, 100.0, 0.0)  # 使用默认值
        
        if not isinstance(traj_end_data, tuple) or len(traj_end_data) != 4:
            traj_end_data = (60, 0.0, 100.0, 0.0)  # 使用默认值
        
        # 调用父类初始化
        super().__init__(parent=parent, traj_end_data=traj_end_data, style=style)
        
        # 创建颜色设置区域
        self.setup_color_section(DEFAULT_START_COLOR, DEFAULT_END_COLOR)
        
        # 设置角度参数
        self.setup_angle_section(DEFAULT_HORIZONTAL_ANGLE, DEFAULT_VERTICAL_ANGLE)
        
        # 设置爆炸参数
        explosion_params = [
            '烟花持续时间 (秒)',
            '爆炸速度 (m/s)',
            '粒子生存时间 (秒)',
            '散射角度 (°)',
            '轨迹数量'  # 添加轨迹数量参数
        ]
        explosion_defaults = [
            DEFAULT_EXPLODE_DURATION,
            DEFAULT_EXPLODE_SPEED,
            DEFAULT_PARTICLE_LIFETIME,
            DEFAULT_SPREAD_ANGLE,
            DEFAULT_TRACK_COUNT  # 添加轨迹数量默认值
        ]
        self.setup_explosion_section(explosion_params, explosion_defaults)
        
        # 设置提交按钮
        self.setup_submit_button("生成集束烟花")
    
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
        duration = float(self.entries['烟花持续时间 (秒)'].text())  # 爆炸持续时间
        speed = float(self.entries['爆炸速度 (m/s)'].text())   # 爆炸速度
        lifetime = float(self.entries['粒子生存时间 (秒)'].text())  # 粒子生存时间
        spread_angle = float(self.entries['散射角度 (°)'].text())  # 散射角度
        track_count = int(self.entries['轨迹数量'].text())  # 每个方向的轨迹数量
        
        # 验证表单输入
        validation_map = self.get_basic_validation_map()
        validation_map.update({
            '散射角度 (°)': Validators.positive_number,
            '轨迹数量': Validators.positive_integer
        })
        
        valid = self.validate_entries(validation_map)
        if not valid:
            raise ValueError("输入验证失败，请检查参数")
            
        # 生成烟花 - 调用 clustered_firework 函数
        # 参数顺序：tick, x, y, z, start_color, end_color, speed, horizontal_angle_step, vertical_angle_step,
        #          track_count, spread_angle, duration, lifetime
        basic_fireworks.clustered_firework(
            self.tick,                               # tick - 游戏刻
            self.x,                                  # x - x坐标
            self.y,                                  # y - y坐标
            self.z,                                  # z - z坐标
            start_color,                             # start_color - 开始颜色
            end_color if is_gradient else start_color, # end_color - 结束颜色（渐变或与开始颜色相同）
            speed,                                   # speed - 爆炸速度
            horizontal_angle_step,                   # horizontal_angle_step - 水平角度步长
            vertical_angle_step,                     # vertical_angle_step - 垂直角度步长
            track_count,                             # track_count - 每个方向的轨迹数量
            spread_angle,                            # spread_angle - 散射角度
            duration,                                # duration - 爆炸持续时间
            lifetime                                 # lifetime - 粒子生存时间
        )
        
        return (self.x, self.y, self.z)

# 测试代码
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ClusteredFireworkForm(traj_end_data=(60, 0, 100, 0))
    window.show()
    sys.exit(app.exec_()) 