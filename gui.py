import sys
from PyQt5.QtWidgets import QApplication
from gui.style.style_factory import StyleFactory
from gui.datapack_form import DatapackForm

# 稍后实现的数据包表单
# from gui.forms.datapack_form import DatapackForm

if __name__ == "__main__":
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("DynFirework - Minecraft烟花生成器")
    
    # 应用全局样式
    style = StyleFactory.apply_application_style(app)
    
    # 创建主窗口（数据包表单）
    main_window = DatapackForm(style=style)
    main_window.show()
    
    # 启动应用程序主循环
    sys.exit(app.exec_())

