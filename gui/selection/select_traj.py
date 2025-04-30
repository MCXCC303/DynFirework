from PyQt5.QtWidgets import QApplication
from gui.templates.selection_base import SelectionBase
import os

# 轨迹类型数据
trajectory_types = [
    '基础曲线发射轨迹',
    '火花发射轨迹',
    '随机扰动发射轨迹',
    '粗随机扰动发射轨迹',
    '扩散随机扰动发射轨迹'
]

trajectory_descriptions = [
    '模拟抛物线运动的基础烟花发射轨迹',
    '带有散射火花效果的发射轨迹',
    '带有随机位置偏移的发射轨迹',
    '带有随机位置偏移的粗壮发射轨迹',
    '带有向外扩散效果的发射轨迹'
]

trajectory_image_paths = [
    'gui/selection/traj_image/lt.png',
    'gui/selection/traj_image/lst.png',
    'gui/selection/traj_image/t_wro.png',
    'gui/selection/traj_image/tt_wro.png',
    'gui/selection/traj_image/et_wro.png'
]

class TrajectorySelect(SelectionBase):
    """轨迹选择界面"""
    
    def __init__(self, parent=None, style=None):
        """
        初始化轨迹选择界面
        
        参数:
            parent: 父窗口
            style: 样式字典，如果为None则创建默认样式
        """
        super().__init__("选择轨迹", (1050, 700), style)
        self.parent = parent
        
        # 准备卡片数据
        card_data = []
        for i, (title, description, image_path) in enumerate(zip(
                trajectory_types, trajectory_descriptions, trajectory_image_paths)):
            
            # 确保图片路径存在
            if not os.path.exists(image_path):
                image_path = None
                
            # 创建卡片数据
            card_data.append({
                "title": title,
                "description": description,
                "icon_path": image_path,
                "on_click": lambda t=title: self.on_trajectory_select(t)
            })
        
        # 填充卡片网格
        self.populate_cards(card_data, columns=3)
        
    def on_trajectory_select(self, trajectory_type):
        """
        轨迹选择事件处理
        
        参数:
            trajectory_type: 选择的轨迹类型
        """
        # 延迟导入表单类，避免循环导入问题
        from gui.traj_forms import (
            LaunchTrajForm, LaunchSparkTrajForm, TrajWithIntervalForm,
            ThickTrajWithIntervalForm, ExpdTrajWithIntervalForm
        )
        
        # 根据选择的轨迹类型打开对应的表单
        if trajectory_type == '基础曲线发射轨迹':
            self.open_form(LaunchTrajForm)
            
        elif trajectory_type == '火花发射轨迹':
            self.open_form(LaunchSparkTrajForm)
            
        elif trajectory_type == '随机扰动发射轨迹':
            self.open_form(TrajWithIntervalForm)
            
        elif trajectory_type == '粗随机扰动发射轨迹':
            self.open_form(ThickTrajWithIntervalForm)
            
        elif trajectory_type == '扩散随机扰动发射轨迹':
            self.open_form(ExpdTrajWithIntervalForm)
    
    def open_form(self, form_class):
        """
        打开表单界面
        
        参数:
            form_class: 表单类
        """
        # 传递当前窗口的datapack_namespace和output_dir到父窗口对象，以便后续使用
        if hasattr(self, 'datapack_namespace') and hasattr(self, 'output_dir'):
            self.form = form_class(self, self.style)
            self.form.parent.datapack_namespace = self.datapack_namespace
            self.form.parent.output_dir = self.output_dir
        else:
            self.form = form_class(self, self.style)
        
        self.form.show()
        self.hide()

# 测试代码
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    from gui.style.style_factory import StyleFactory
    style = StyleFactory.create_style()
    StyleFactory.apply_application_style(app)
    window = TrajectorySelect(style=style)
    window.show()
    sys.exit(app.exec_())
