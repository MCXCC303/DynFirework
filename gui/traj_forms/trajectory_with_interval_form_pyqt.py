from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.lib import firework_trajectories
from gui.templates.trajectory_form_base import TrajectoryFormBase
from gui.components.validators import Validators

# 全局默认值
DEFAULT_END_TICK = 100
DEFAULT_START_POS = (0, 0, 0)
DEFAULT_END_POS = (50, 100, 30)
DEFAULT_DURATION = 4.0
DEFAULT_INTERVAL = 5
DEFAULT_POINTS_PER_TICK = 5
DEFAULT_M0 = 2.0
DEFAULT_K = 1.2
DEFAULT_LIFETIME = 1.0
DEFAULT_RHO = 1.0
DEFAULT_START_COLOR = (255, 255, 255)
DEFAULT_END_COLOR = (255, 255, 255)

class TrajWithIntervalForm(TrajectoryFormBase):
    """随机扰动发射轨迹表单"""
    
    def __init__(self, parent=None, style=None):
        """
        初始化随机扰动发射轨迹表单
        
        参数:
            parent: 父窗口
            style: 样式字典，如果为None则创建默认样式
        """
        # 调用基类初始化
        super().__init__(
            parent=parent, 
            title="随机扰动发射轨迹设置", 
            start_pos=DEFAULT_START_POS,
            end_pos=DEFAULT_END_POS,
            start_color=DEFAULT_START_COLOR,
            end_color=DEFAULT_END_COLOR,
            style=style
        )
        
        # 创建颜色设置区域
        self.setup_color_section()
        
        # 计算默认参数
        params = [
            '结束时间 (Tick)', 
            '轨迹持续时间 (秒)', 
            '粒子质量 (m0)',
            '空气阻力系数 (k)',
            '粒子存活时间 (秒)',
            '随机位置间隔 (Tick)',
            '每Tick点数'
        ]
        defaults = [
            DEFAULT_END_TICK,  # 结束时间
            DEFAULT_DURATION,  # 轨迹持续时间
            DEFAULT_M0,  # 粒子质量
            DEFAULT_K,  # 空气阻力系数
            DEFAULT_LIFETIME,  # 粒子存活时间
            DEFAULT_INTERVAL,  # 随机位置间隔
            DEFAULT_POINTS_PER_TICK
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
        end_tick = int(self.entries['结束时间 (Tick)'].text())
        
        # 使用基类方法获取位置
        (x0, y0, z0), (x1, y1, z1) = self.get_position_values()
        
        # 获取其他参数
        duration = float(self.entries['轨迹持续时间 (秒)'].text())
        m0 = float(self.entries['粒子质量 (m0)'].text())
        k = float(self.entries['空气阻力系数 (k)'].text())
        lifetime = float(self.entries['粒子存活时间 (秒)'].text())
        interval = int(self.entries['随机位置间隔 (Tick)'].text())
        points_per_tick = int(self.entries['每Tick点数'].text())
        
        # 验证表单输入
        validation_map = {
            '结束时间 (Tick)': Validators.positive_integer,
            '轨迹持续时间 (秒)': Validators.positive_number,
            '粒子质量 (m0)': Validators.positive_number,
            '空气阻力系数 (k)': Validators.positive_number,
            '粒子存活时间 (秒)': Validators.positive_number,
            '随机位置间隔 (Tick)': Validators.positive_integer,
            '每Tick点数': Validators.positive_integer
        }
        
        valid = self.validate_entries(validation_map)
        if not valid:
            raise ValueError("输入验证失败，请检查参数")
        
        # 生成轨迹
        firework_trajectories.trajectory_with_random_offset(
            end_tick=end_tick,
            x0=x0, y0=y0, z0=z0,
            x1=x1, y1=y1, z1=z1,
            k=k,
            m0=m0,
            duration=duration,
            lifetime=lifetime,
            interval_ticks=interval,
            points_per_tick=points_per_tick
        )
        
        return (end_tick, x1, y1, z1)

# 测试代码
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    from gui.style.style_factory import StyleFactory
    style = StyleFactory.create_style()
    StyleFactory.apply_application_style(app)
    window = TrajWithIntervalForm(style=style)
    window.show()
    sys.exit(app.exec_()) 