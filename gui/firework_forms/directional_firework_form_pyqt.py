from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.lib import basic_fireworks
from gui.templates.firework_form_base import FireworkFormBase
from gui.components.validators import Validators
from gui.selection.select_traj import TrajectorySelect
from gui.lib.global_storage import horizontal_angle_step_default, vertical_angle_step_default

# 默认参数定义
DEFAULT_START_COLOR = (255, 0, 0)
DEFAULT_END_COLOR = (255, 0, 0)
DEFAULT_EXPLODE_DURATION = "1.5"
DEFAULT_EXPLODE_SPEED = "30"
DEFAULT_PARTICLE_LIFETIME = "1.0"
DEFAULT_DIRECTION_HORIZONTAL = "0"
DEFAULT_DIRECTION_VERTICAL = "0"
DEFAULT_SPREAD_ANGLE = "15"
DEFAULT_TRACK_COUNT = "5"

class DirectionalFireworkForm(FireworkFormBase):
    """定向烟花表单类"""
    
    def __init__(self, parent=None, traj_end_data=None, style=None):
        """
        初始化定向烟花表单
        
        参数:
            parent: 父窗口
            traj_end_data: 轨迹终点数据，格式为(tick, x, y, z)
            style: 样式字典，如果为None则创建默认样式
        """
        # 设置窗口标题（供父类初始化使用）
        self.title = "定向烟花设置"
        
        # 先检查参数
        if traj_end_data is None:
            traj_end_data = (60, 0.0, 100.0, 0.0)  # 使用默认值
        
        if not isinstance(traj_end_data, tuple) or len(traj_end_data) != 4:
            traj_end_data = (60, 0.0, 100.0, 0.0)  # 使用默认值
        
        # 调用父类初始化
        super().__init__(parent=parent, traj_end_data=traj_end_data, style=style)
        
        # 创建颜色设置区域
        self.setup_color_section(DEFAULT_START_COLOR, DEFAULT_END_COLOR)
        
        # 设置爆炸参数
        explosion_params = [
            '烟花持续时间 (秒)', 
            '爆炸速度 (m/s)', 
            '粒子生存时间 (秒)',
            '水平方向角度 (°)',
            '垂直方向角度 (°)',
            '扩散角度 (°)',
            '轨迹数量'
        ]
        explosion_defaults = [
            DEFAULT_EXPLODE_DURATION, 
            DEFAULT_EXPLODE_SPEED, 
            DEFAULT_PARTICLE_LIFETIME,
            DEFAULT_DIRECTION_HORIZONTAL,
            DEFAULT_DIRECTION_VERTICAL,
            DEFAULT_SPREAD_ANGLE,
            DEFAULT_TRACK_COUNT
        ]
        self.setup_explosion_section(explosion_params, explosion_defaults)
        
        # 设置提交按钮
        self.setup_submit_button("生成定向烟花")
    
    def process_data(self):
        """处理表单数据，返回处理结果
        
        返回:
            tuple: (x, y, z) 烟花位置
        """
        # 使用基类方法获取颜色
        start_color, end_color, is_gradient = self.get_color_values()
            
        # 获取角度参数
        # horizontal_angle_step = int(self.entries['水平角度间隔 (°)'].text())
        # vertical_angle_step = int(self.entries['垂直角度间隔 (°)'].text())
            
        # 获取其他参数
        duration = float(self.entries['烟花持续时间 (秒)'].text())
        speed = float(self.entries['爆炸速度 (m/s)'].text())
        lifetime = float(self.entries['粒子生存时间 (秒)'].text())
        direction_h = float(self.entries['水平方向角度 (°)'].text())
        direction_v = float(self.entries['垂直方向角度 (°)'].text())
        spread_angle = float(self.entries['扩散角度 (°)'].text())
        track_count = int(self.entries['轨迹数量'].text())
        
        # 验证表单输入
        validation_map = self.get_basic_validation_map()
        validation_map.update({
            '水平方向角度 (°)': Validators.angle,
            '垂直方向角度 (°)': Validators.angle,
            '扩散角度 (°)': Validators.positive_angle,
            '轨迹数量': Validators.positive_integer
        })
        
        valid = self.validate_entries(validation_map)
        if not valid:
            raise ValueError("输入验证失败，请检查参数")
            
        # 生成烟花
        basic_fireworks.directional_firework(
            self.tick,  # tick
            self.x,  # x
            self.y,  # y
            self.z,  # z
            start_color,
            end_color if is_gradient else start_color,
            speed,
            # horizontal_angle_step,
            # vertical_angle_step,
            direction_h,
            direction_v,
            spread_angle,
            track_count,
            duration,
            lifetime
        )
        
        # 询问是否继续
        continuing = QMessageBox.question(self, 'DynFirework', 
                                       f'烟花已生成\n位置: ({self.x}, {self.y}, {self.z})\n\n是否继续创建新的烟花?',
                                       QMessageBox.Yes | QMessageBox.No)
        
        if continuing == QMessageBox.No:
            # 导出并关闭
            self.close()  # 关闭当前窗口
            
            # 如果有父窗口，也关闭它
            if self.parent_window:
                self.parent_window.close()
                
            # 导出数据
            from gui.datapack_form import datapack_namespace, output_dir
            from gui.lib import export_mcfunction
            export_mcfunction.schedule_next_tick(datapack_namespace)
            export_mcfunction.export_mcfunction(output_dir)
        else:
            # 关闭当前窗口
            self.close()
            
            # 如果有父窗口，也关闭它
            if self.parent_window:
                self.parent_window.close()
                
            # 创建轨迹选择界面
            traj_select = TrajectorySelect(style=self.style)
            
            # 传递命名空间和输出目录
            if hasattr(self, 'datapack_namespace'):
                traj_select.datapack_namespace = self.datapack_namespace
            if hasattr(self, 'output_dir'):
                traj_select.output_dir = self.output_dir
                
            # 显示新窗口
            traj_select.show()
        
        return (self.x, self.y, self.z)

# 测试代码
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = DirectionalFireworkForm(traj_end_data=(60, 0, 100, 0))
    window.show()
    sys.exit(app.exec_()) 