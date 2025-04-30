from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.templates.selection_base import SelectionBase
import os
import traceback
from PyQt5.QtCore import Qt

# 烟花类型数据
firework_types = [
    '单层烟花',
    '双层烟花',
    '集束烟花',
    '定向烟花'
]

firework_descriptions = [
    '基础的单层爆炸效果烟花',
    '具有内外两层爆炸效果的烟花',
    '多点聚集爆发的烟花',
    '朝特定方向爆发的烟花'
]

firework_image_paths = [
    'gui/selection/firework_image/slf.png',
    'gui/selection/firework_image/dlf.png',
    'gui/selection/firework_image/cf.png',
    'gui/selection/firework_image/df.png'
]

class FireworkSelect(SelectionBase):
    """烟花选择界面"""
    
    def __init__(self, parent=None, traj_info=None, style=None):
        """
        初始化烟花选择界面
        
        参数:
            parent: 父窗口
            traj_info: 轨迹信息数据，格式为(end_tick, x, y, z)
            style: 样式字典，如果为None则创建默认样式
        """
        # 调用父类初始化
        super().__init__("选择烟花", (1050, 700), style)
        
        # 保存父窗口
        self.parent = parent
        
        # 保存并验证轨迹信息
        if traj_info is not None and isinstance(traj_info, tuple) and len(traj_info) == 4:
            try:
                end_tick, x, y, z = traj_info
                self.traj_info = (
                    int(end_tick),
                    float(x),
                    float(y),
                    float(z)
                )
            except (ValueError, TypeError) as e:
                self.traj_info = (60, 0.0, 100.0, 0.0)  # 使用默认值
        else:
            self.traj_info = (60, 0.0, 100.0, 0.0)
        
        # 从父窗口获取数据包信息
        if parent:
            self.datapack_namespace = getattr(parent, 'datapack_namespace', None)
            self.output_dir = getattr(parent, 'output_dir', None)
        
        # 准备卡片数据
        card_data = []
        for title, description, image_path in zip(firework_types, firework_descriptions, firework_image_paths):
            # 确保图片路径存在
            if not os.path.exists(image_path):
                image_path = None
            
            # 创建卡片数据，使用命名参数避免闭包问题
            card_data.append({
                "title": title,
                "description": description,
                "icon_path": image_path,
                "on_click": lambda t=title: self.on_firework_select(t)
            })
        
        # 填充卡片网格
        self.populate_cards(card_data, columns=2)
        
    def on_firework_select(self, firework_type):
        """
        烟花选择事件处理
        
        参数:
            firework_type: 选择的烟花类型
        """
        # 延迟导入表单类，避免循环导入问题
        from gui.firework_forms import (
            SingleLayerFireworkForm, DoubleLayerFireworkForm,
            ClusteredFireworkForm, DirectionalFireworkForm
        )
        
        # 根据选择的烟花类型打开对应的表单
        try:
            form_class = None
            if firework_type == '单层烟花':
                form_class = SingleLayerFireworkForm
            elif firework_type == '双层烟花':
                form_class = DoubleLayerFireworkForm
            elif firework_type == '集束烟花':
                form_class = ClusteredFireworkForm
            elif firework_type == '定向烟花':
                form_class = DirectionalFireworkForm
            else:
                QMessageBox.warning(self, "警告", f"未知的烟花类型: {firework_type}")
                return
                
            # 直接在这里创建表单，而不是通过open_form方法
            # 使用非模态对话框方式创建表单
            form = form_class(parent=None, traj_end_data=self.traj_info, style=self.style)
            
            # 传递命名空间和输出目录
            if hasattr(self, 'datapack_namespace'):
                form.datapack_namespace = self.datapack_namespace
            if hasattr(self, 'output_dir'):
                form.output_dir = self.output_dir
                
            # 设置窗口之间的逻辑关系
            form.parent_window = self
            
            # 确保窗口是顶级窗口
            form.setWindowFlags(Qt.Window)
            # 在修改窗口标志后，需要重新显示窗口以应用更改
            form.hide()
            
            # 使用模态对话框方式显示窗口
            self.hide()  # 先隐藏当前窗口
            # 模态显示表单窗口
            form.show()
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"打开表单失败: {e}")

# 测试代码
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    from gui.style.style_factory import StyleFactory
    style = StyleFactory.create_style()
    StyleFactory.apply_application_style(app)
    window = FireworkSelect(traj_info=(60, 0, 100, 0), style=style)
    window.show()
    sys.exit(app.exec_())
