from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

class BaseWindow(QMainWindow):
    """基础窗口模板，所有主窗口的基类"""
    
    def __init__(self, title="DynFirework", size=(900, 700), style=None):
        """
        初始化基础窗口
        
        参数:
            title: 窗口标题
            size: 窗口大小，格式为(宽度, 高度)
            style: 样式字典，如果为None则创建默认样式
        """
        try:
            # 调用父类QMainWindow的初始化方法
            super().__init__()
            
            # 设置窗口标题
            self.setWindowTitle(f"DynFirework - {title}")
            
            # 设置窗口大小
            self.resize(*size)
            
            # 应用样式
            if style is None:
                from gui.style.style_factory import StyleFactory
                self.style = StyleFactory.create_style()
            else:
                self.style = style
                
            # 创建中央部件
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            
            # 创建主布局
            self.main_layout = QVBoxLayout(self.central_widget)
            self.main_layout.setContentsMargins(
                self.style["margin_large"], 
                self.style["margin_large"], 
                self.style["margin_large"], 
                self.style["margin_large"]
            )
            self.main_layout.setSpacing(self.style["margin_medium"])
            
            # 确保窗口可见性
            self.setWindowFlags(self.windowFlags() | Qt.Window)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
        
    def create_title(self, title_text):
        """创建标题标签
        
        参数:
            title_text: 标题文本
            
        返回:
            QLabel: 标题标签
        """
        title_label = QLabel(title_text)
        # 增大标题字体
        title_font = QFont(self.style["font_family"], self.style["title_font_size"] + 2)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        # 添加一些边距使标题更加醒目
        title_label.setContentsMargins(0, 10, 0, 20)
        # 添加底边框样式使标题更醒目
        title_label.setStyleSheet(f"""
            color: {self.style['text_color']};
            padding-bottom: 10px;
            border-bottom: 1px solid {self.style['border_color']};
            margin-bottom: 10px;
        """)
        self.main_layout.addWidget(title_label)
        return title_label
        
    def showEvent(self, event):
        """窗口显示事件，用于居中窗口
        
        参数:
            event: 显示事件
        """
        try:
            # 先调用父类方法
            super().showEvent(event)
            
            # 居中窗口
            screen_geometry = self.screen().availableGeometry()
            window_geometry = self.frameGeometry()
            window_geometry.moveCenter(screen_geometry.center())
            self.move(window_geometry.topLeft())
            
            # 确保窗口在所有窗口之上显示
            self.raise_()
            self.activateWindow()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
        
    def closeEvent(self, event):
        """窗口关闭事件，可在子类中重写以添加确认对话框
        
        参数:
            event: 关闭事件
        """
        # 默认接受关闭事件
        event.accept() 