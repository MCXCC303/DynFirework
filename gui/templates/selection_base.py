from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QGridLayout, QFrame, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from gui.templates.base_window import BaseWindow
import os

class SelectionBase(BaseWindow):
    """选择界面基类，用于创建卡片式选择界面"""
    
    def __init__(self, title="选择", size=(1050, 700), style=None):
        """
        初始化选择界面基类
        
        参数:
            title: 选择界面标题
            size: 窗口大小，格式为(宽度, 高度)
            style: 样式字典，如果为None则创建默认样式
        """
        super().__init__(title, size, style)
        
        # 创建标题
        self.title_label = self.create_title(title)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # 创建卡片容器
        self.card_container = QWidget()
        self.grid_layout = QGridLayout(self.card_container)
        self.grid_layout.setContentsMargins(
            self.style["padding_large"], 
            self.style["padding_large"], 
            self.style["padding_large"], 
            self.style["padding_large"]
        )
        self.grid_layout.setSpacing(self.style["padding_large"] + 5)  # 增加卡片之间的间距
        
        self.scroll_area.setWidget(self.card_container)
        self.main_layout.addWidget(self.scroll_area)
        
    def create_card(self, title, description, on_click=None, icon_path=None, status=None):
        """创建选择卡片
        
        参数:
            title: 卡片标题
            description: 卡片描述
            on_click: 卡片点击回调函数
            icon_path: 卡片图标路径(可选)
            status: 卡片状态(可选)，用于显示不同状态的卡片样式
            
        返回:
            QFrame: 卡片框架
        """
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)  # 使用样式化的面板
        card.setObjectName("card")  # 设置对象名，便于样式表选择
        
        # 设置卡片样式（使用边框代替阴影）
        if status == "disabled":
            card.setStyleSheet(f"""
                #card {{
                    background-color: {self.style["secondary_color"]};
                    border-radius: {self.style["border_radius"]}px;
                    border: 1px solid {self.style["border_color"]};
                }}
            """)
        else:
            card.setStyleSheet(f"""
                #card {{
                    background-color: {self.style["card_color"]};
                    border-radius: {self.style["border_radius"]}px;
                    border: 1px solid {self.style["border_color"]};
                }}
                #card:hover {{
                    background-color: {self.style["card_hover_color"]};
                    border: 2px solid {self.style["primary_color"]};
                }}
            """)
        
        # 调整卡片宽度，确保能够在1050px宽的窗口中放下3列
        card.setMinimumSize(300, 240)  # 增加一些高度容纳更大的图片
        card.setMaximumWidth(320)
        
        # 卡片布局
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            self.style["padding_medium"], 
            self.style["padding_medium"], 
            self.style["padding_medium"], 
            self.style["padding_medium"]
        )
        card_layout.setSpacing(self.style["padding_medium"])
        
        # 卡片标题
        title_label = QLabel(title)
        title_font = QFont(self.style["font_family"], self.style["subtitle_font_size"])
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)  # 标题居中
        card_layout.addWidget(title_label)
        
        # 添加图片（如果提供）
        image_label = None
        if icon_path and os.path.exists(icon_path):
            image_label = QLabel()
            pixmap = QPixmap(icon_path)
            
            # 增大图片尺寸
            max_height = 160  # 进一步增大图片
            if pixmap.height() > 0:
                pixmap = pixmap.scaledToHeight(max_height, Qt.SmoothTransformation)
            
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(image_label)
        
        # 卡片描述
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)  # 描述居中
        desc_label.setStyleSheet(f"""
            color: {self.style['text_color']};
            background-color: transparent;
            border: none;
        """)
        card_layout.addWidget(desc_label)
        
        # 添加间隔
        card_layout.addStretch()
        
        # 创建底部按钮区域（居中对齐）
        bottom_layout = QHBoxLayout()
        bottom_layout.setAlignment(Qt.AlignCenter)  # 居中对齐
        
        # 卡片按钮
        select_button = QPushButton("选择")
        select_button.setCursor(Qt.PointingHandCursor)
        select_button.setFixedWidth(120)  # 设置固定宽度
        
        # 设置按钮样式
        if status == "disabled":
            select_button.setEnabled(False)
            select_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #aaaaaa;
                    color: #dddddd;
                    border: none;
                    border-radius: {self.style["border_radius"]}px;
                    padding: 8px 15px;
                    font-weight: bold;
                }}
            """)
        else:
            select_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.style["primary_color"]};
                    color: {self.style["button_text_color"]};
                    border: none;
                    border-radius: {self.style["border_radius"]}px;
                    padding: 8px 15px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.style["button_hover_color"]};
                }}
                QPushButton:pressed {{
                    background-color: {self.style["button_pressed_color"]};
                }}
            """)
        
        if on_click and status != "disabled":
            # 创建一个不会被垃圾回收的回调函数
            def button_clicked():
                on_click()
            
            # 确保按钮点击事件正确绑定
            select_button.clicked.connect(button_clicked)
            
            # 让整个卡片可点击
            if image_label:
                image_label.setCursor(Qt.PointingHandCursor)
                image_label.mousePressEvent = lambda event: on_click()
            
            title_label.setCursor(Qt.PointingHandCursor)
            title_label.mousePressEvent = lambda event: on_click()
            
            desc_label.setCursor(Qt.PointingHandCursor)
            desc_label.mousePressEvent = lambda event: on_click()
            
            # 设置卡片的点击事件
            card.setCursor(Qt.PointingHandCursor)
            card.mousePressEvent = lambda event: on_click()
        
        # 添加按钮到底部布局    
        bottom_layout.addWidget(select_button)
        
        # 添加底部布局到卡片
        card_layout.addLayout(bottom_layout)
        
        return card
        
    def add_card_to_grid(self, card, row, col):
        """添加卡片到网格
        
        参数:
            card: 卡片框架
            row: 行索引
            col: 列索引
        """
        self.grid_layout.addWidget(card, row, col)
        
    def populate_cards(self, card_data, columns=2):
        """填充卡片网格
        
        参数:
            card_data: 卡片数据列表，每个元素为包含卡片信息的字典
                      字典格式: {
                          "title": "卡片标题",
                          "description": "卡片描述",
                          "on_click": 点击回调函数,
                          "icon_path": "图标路径"(可选),
                          "status": "状态"(可选)
                      }
            columns: 每行显示的卡片数量
        """
        row, col = 0, 0
        for card_info in card_data:
            card = self.create_card(
                card_info["title"],
                card_info["description"],
                card_info.get("on_click"),
                card_info.get("icon_path"),
                card_info.get("status")
            )
            self.add_card_to_grid(card, row, col)
            
            # 更新行列位置
            col += 1
            if col >= columns:
                col = 0
                row += 1 