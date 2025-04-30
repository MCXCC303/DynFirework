from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.lib import firework_trajectories
from gui.templates.trajectory_form_base import TrajectoryFormBase
from gui.components.validators import Validators

# 全局默认值
DEFAULT_END_TICK = 100
DEFAULT_START_POS = (0, 0, 0)
DEFAULT_END_POS = (50, 100, 30)
DEFAULT_DURATION = 4.0
DEFAULT_SPARK_DURATION = 3.0
DEFAULT_SPARK_COUNT = 5
DEFAULT_M0 = 2.0
DEFAULT_K = 1.2
DEFAULT_LIFETIME = 0.5
DEFAULT_RHO = 1.0
DEFAULT_START_COLOR = (255, 255, 255)
DEFAULT_END_COLOR = (255, 255, 255)

class LaunchSparkTrajForm(TrajectoryFormBase):
    """火花发射轨迹表单"""
    
    def __init__(self, parent=None, style=None):
        """
        初始化火花发射轨迹表单
        
        参数:
            parent: 父窗口
            style: 样式字典，如果为None则创建默认样式
        """
        # 调用基类初始化
        super().__init__(
            parent=parent, 
            title="火花发射轨迹设置", 
            start_pos=DEFAULT_START_POS,
            end_pos=DEFAULT_END_POS,
            start_color=DEFAULT_START_COLOR,
            end_color=DEFAULT_END_COLOR,
            style=style
        )
        
        # 创建颜色设置区域
        self.setup_color_section()
        
        # 计算默认参数
        # self.end_tick = DEFAULT_END_TICK # 不再需要
        # 修改参数标签和默认值
        params = [
            '结束时间 (Tick)', 
            '轨迹持续时间 (秒)', 
            '粒子质量 (m0)',
            '空气阻力系数 (k)',
            '粒子存活时间 (秒)',
            # '粒子密度系数 (rho)', # Spark轨迹不需要rho
            '火花数量',
            '火花持续时间 (秒)'
        ]
        defaults = [
            DEFAULT_END_TICK,  # 结束时间
            DEFAULT_DURATION,  # 轨迹持续时间
            DEFAULT_M0,  # 粒子质量
            DEFAULT_K,  # 空气阻力系数
            DEFAULT_LIFETIME,  # 粒子存活时间
            # DEFAULT_RHO,  # Spark轨迹不需要rho
            DEFAULT_SPARK_COUNT,  # 火花数量
            DEFAULT_SPARK_DURATION  # 火花持续时间
        ]
        
        # 设置物理参数区域
        self.setup_physics_section(params, defaults)
        
        # 设置提交按钮
        self.setup_submit_button()
    
    def process_data(self):
        """处理表单数据，返回处理结果
        
        返回:
            tuple: (end_tick, x1, y1, z1) 轨迹终点数据
        """
        # 获取表单数据
        # 直接从新的输入框获取end_tick
        end_tick = int(self.entries['结束时间 (Tick)'].text())
        
        # 使用基类方法获取位置
        (x0, y0, z0), (x1, y1, z1) = self.get_position_values()
        
        # 获取其他参数
        # 直接从新的输入框获取duration
        duration = float(self.entries['轨迹持续时间 (秒)'].text())
        m0 = float(self.entries['粒子质量 (m0)'].text())
        k = float(self.entries['空气阻力系数 (k)'].text())
        lifetime = float(self.entries['粒子存活时间 (秒)'].text())
        spark_count = int(float(self.entries['火花数量'].text()))
        spark_duration = float(self.entries['火花持续时间 (秒)'].text()) # 获取火花持续时间，虽然看起来没用，但保留

        # 验证表单输入
        # 更新验证映射
        validation_map = {
            '结束时间 (Tick)': Validators.positive_integer,
            '轨迹持续时间 (秒)': Validators.positive_number,
            '粒子质量 (m0)': Validators.positive_number,
            '空气阻力系数 (k)': Validators.positive_number,
            '粒子存活时间 (秒)': Validators.positive_number,
            # '粒子密度系数 (rho)': Validators.positive_number, # Spark轨迹不需要rho
            '火花数量': Validators.positive_integer,
            '火花持续时间 (秒)': Validators.positive_number
        }
        
        valid = self.validate_entries(validation_map)
        if not valid:
            raise ValueError("输入验证失败，请检查参数")
        
        # 生成轨迹
        firework_trajectories.launch_spark_trajectory(
            end_tick=end_tick,
            x0=x0, y0=y0, z0=z0,
            x1=x1, y1=y1, z1=z1,
            duration=duration,
            k=k,
            m0=m0,
            lifetime=lifetime,
            particle_count=spark_count
        )
        
        return (end_tick, x1, y1, z1)

# 测试代码
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    from gui.style.style_factory import StyleFactory
    style = StyleFactory.create_style()
    StyleFactory.apply_application_style(app)
    window = LaunchSparkTrajForm(style=style)
    window.show()
    sys.exit(app.exec_()) 