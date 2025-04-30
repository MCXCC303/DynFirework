from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

class StyleFactory:
    """样式工厂类，负责创建和管理应用样式"""
    
    @staticmethod
    def create_style(theme="light"):
        """创建应用样式
        
        参数:
            theme: 主题名称，可选值为"light"或"dark"
            
        返回:
            包含样式配置的字典
        """
        # 基础样式（浅色主题）
        style = {
            # 颜色
            "primary_color": "#4287f5",
            "secondary_color": "#f0f0f0",
            "text_color": "#333333",
            "button_text_color": "#ffffff",
            "button_hover_color": "#5a9afa",
            "button_pressed_color": "#3276e4",
            "background_color": "#f9f9f9",
            "card_color": "#ffffff",
            "card_hover_color": "#f7f9ff",  # 卡片悬停颜色
            "card_shadow_color": "rgba(0, 0, 0, 0.1)",  # 卡片阴影颜色
            "border_color": "#dddddd",
            "success_color": "#28a745",
            "warning_color": "#ffc107",
            "danger_color": "#dc3545",
            "info_color": "#17a2b8",
            "input_bg_color": "#ffffff",
            
            # 字体
            "font_family": "Microsoft YaHei UI",
            "title_font_size": 18,  # 增大标题字体
            "subtitle_font_size": 14,
            "body_font_size": 12,
            "small_font_size": 10,
            
            # 间距
            "padding_small": 5,
            "padding_medium": 10,
            "padding_large": 15,
            "margin_small": 5,
            "margin_medium": 10,
            "margin_large": 15,
            
            # 边框
            "border_radius": 6,  # 增大圆角半径
            "border_width": 1,
            
            # 其他
            "card_elevation": 3,  # 增强卡片阴影
            "transition_time": 0.2,
        }
        
        # 暗色主题
        if theme == "dark":
            style.update({
                "primary_color": "#3a7ce2",
                "secondary_color": "#2d2d2d",
                "text_color": "#ffffff",
                "button_text_color": "#ffffff",
                "button_hover_color": "#4b8bf5",
                "button_pressed_color": "#2d6ad1",
                "background_color": "#1e1e1e",
                "card_color": "#2d2d2d",
                "card_hover_color": "#363636",  # 卡片悬停颜色
                "card_shadow_color": "rgba(0, 0, 0, 0.3)",  # 卡片阴影颜色
                "border_color": "#3d3d3d",
                "success_color": "#28a745",
                "warning_color": "#ffc107",
                "danger_color": "#dc3545",
                "info_color": "#17a2b8",
                "input_bg_color": "#3d3d3d",
            })
            
        return style
    
    @staticmethod
    def apply_application_style(app, theme="light"):
        """应用全局应用程序样式
        
        参数:
            app: QApplication实例
            theme: 主题名称，可选值为"light"或"dark"
        """
        style = StyleFactory.create_style(theme)
        
        # 设置全局字体
        app.setFont(QFont(style["font_family"], style["body_font_size"]))
        
        # 应用全局样式表
        app.setStyleSheet(f"""
            QWidget {{
                font-family: {style["font_family"]};
                color: {style["text_color"]};
                background-color: {style["background_color"]};
            }}
            
            QLabel {{
                color: {style["text_color"]};
                background-color: transparent;
            }}
            
            QPushButton {{
                background-color: {style["primary_color"]};
                color: {style["button_text_color"]};
                border: none;
                border-radius: {style["border_radius"]}px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {style["button_hover_color"]};
            }}
            
            QPushButton:pressed {{
                background-color: {style["button_pressed_color"]};
            }}
            
            QLineEdit {{
                border: {style["border_width"]}px solid {style["border_color"]};
                border-radius: {style["border_radius"]}px;
                padding: 5px;
                background-color: {style["card_color"]};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: {style["border_width"]}px solid {style["border_color"]};
                border-radius: {style["border_radius"]}px;
                margin-top: 1em;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }}
            
            QCheckBox {{
                color: {style["text_color"]};
                spacing: 5px;
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: {style["secondary_color"]};
                width: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {style["primary_color"]};
                min-height: 20px;
                border-radius: 6px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: {style["secondary_color"]};
                height: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {style["primary_color"]};
                min-width: 20px;
                border-radius: 6px;
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            QComboBox {{
                border: {style["border_width"]}px solid {style["border_color"]};
                border-radius: {style["border_radius"]}px;
                padding: 5px;
                background-color: {style["card_color"]};
            }}
        """)
        
        return style 