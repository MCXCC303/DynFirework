"""
兼容层：将旧的基于tkinter的SelectionBase转发到新的基于PyQt5的SelectionBase
作为过渡使用，最终将完全迁移到PyQt5版本
"""

from gui.templates.selection_base import SelectionBase as PyQt5SelectionBase
from PyQt5.QtWidgets import QApplication
import sys

class SelectionBase:
    """
    兼容层SelectionBase类，将旧接口映射到新的基于PyQt5的实现
    """
    
    def __init__(self, root, title, style=None):
        """
        初始化兼容层
        
        参数：
            root: 旧版tkinter主窗口对象（不再使用）
            title: 界面标题
            style: 样式对象（将转换为PyQt5样式）
        """
        # 警告信息
        import warnings
        warnings.warn(
            "使用了已废弃的基于tkinter的SelectionBase类，请迁移到PyQt5版本",
            DeprecationWarning, 
            stacklevel=2
        )
        
        # 检查QApplication是否已初始化
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
            
        # 创建PyQt5版本的SelectionBase
        self.pyqt_selection = PyQt5SelectionBase(title=title, style=style)
        
        # 保存参数以兼容旧版接口
        self.root = root
        self.style = style
        
            
    def load_images(self, image_paths, size=(180, 180)):
        """兼容方法：加载图片（转发到PyQt5版本）"""
        # 此方法在PyQt5版本中已自动处理
        return image_paths  # 返回路径列表而非实际图片对象
        
    def create_card_grid(self, scrollable_frame, items_info, cols=2, card_clicked_handler=None):
        """
        兼容方法：创建卡片网格
        
        参数：
            scrollable_frame: 滚动框架对象（不再使用）
            items_info: 包含(标题, 描述, 图片)元组的列表
            cols: 每行的列数
            card_clicked_handler: 卡片点击处理函数
        """
        # 将旧格式转换为新的PyQt5格式并创建卡片
        col_num = 0
        row_num = 0
        
        for i, (item_title, description, image_path) in enumerate(items_info):
            self.pyqt_selection.create_card(
                title=item_title,
                description=description,
                on_click=lambda t=item_title: card_clicked_handler(t) if card_clicked_handler else None,
                icon_path=image_path
            )
            
            # 添加到布局
            self.pyqt_selection.grid_layout.addWidget(
                self.pyqt_selection.grid_layout.itemAt(i).widget(),
                row_num, col_num
            )
            
            # 更新行和列
            col_num += 1
            if col_num >= cols:
                col_num = 0
                row_num += 1
                
    def clear_screen(self):
        """清空界面"""
        # 关闭PyQt窗口
        self.pyqt_selection.close()
        
    def show(self):
        """显示窗口"""
        self.pyqt_selection.show()
        
        # 如果是独立运行，启动事件循环
        if not self.pyqt_selection.parent():
            self.app.exec_() 