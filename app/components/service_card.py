# coding:utf-8
from typing import Union
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from qfluentwidgets import (
    ElevatedCardWidget, BodyLabel, CaptionLabel, PrimaryPushButton, 
    FluentIconBase, IconWidget, FluentIcon as FIF
)
from qfluentwidgets.common.font import setFont


class ServiceCard(ElevatedCardWidget):
    """服务卡片组件，模仿参考文件中的卡片样式"""
    
    buttonClicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.setObjectName("ServiceCard")
        
        # 主布局
        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setContentsMargins(16, 12, 16, 12)
        self.mainLayout.setSpacing(16)
        
        # 图标容器
        self.iconContainer = QWidget()
        self.iconContainer.setFixedSize(48, 48)
        self.iconContainer.setObjectName("iconContainer")
        
        # 图标布局
        self.iconLayout = QHBoxLayout(self.iconContainer)
        self.iconLayout.setContentsMargins(0, 0, 0, 0)
        self.iconLayout.setAlignment(Qt.AlignCenter)
        
        # 图标组件
        self.iconWidget = IconWidget(FIF.APPLICATION, self.iconContainer)
        self.iconWidget.setFixedSize(28, 28)
        self.iconLayout.addWidget(self.iconWidget)
        
        # 内容区域
        self.contentWidget = QWidget()
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(2)
        
        # 标题和状态标签容器
        self.titleContainer = QWidget()
        self.titleLayout = QHBoxLayout(self.titleContainer)
        self.titleLayout.setContentsMargins(0, 0, 0, 0)
        self.titleLayout.setSpacing(12)
        
        # 标题
        self.titleLabel = BodyLabel("服务名称")
        self.titleLabel.setObjectName("titleLabel")
        setFont(self.titleLabel, 14)
        
        # 状态标签
        self.statusLabel = CaptionLabel("官方")
        self.statusLabel.setObjectName("statusLabel")
        setFont(self.statusLabel, 11)
        
        self.titleLayout.addWidget(self.titleLabel)
        self.titleLayout.addWidget(self.statusLabel)
        self.titleLayout.addStretch()
        
        # 描述
        self.descriptionLabel = CaptionLabel("服务描述信息")
        self.descriptionLabel.setObjectName("descriptionLabel")
        setFont(self.descriptionLabel, 12)
        
        self.contentLayout.addWidget(self.titleContainer)
        self.contentLayout.addWidget(self.descriptionLabel)
        
        # 右侧区域 - 只保留按钮
        self.rightWidget = QWidget()
        self.rightLayout = QVBoxLayout(self.rightWidget)
        self.rightLayout.setContentsMargins(0, 0, 0, 0)
        self.rightLayout.setAlignment(Qt.AlignCenter)
        
        # 操作按钮
        self.actionButton = PrimaryPushButton("操作")
        self.actionButton.setFixedSize(80, 32)
        setFont(self.actionButton, 12)
        
        self.rightLayout.addWidget(self.actionButton)
        
        # 添加到主布局
        self.mainLayout.addWidget(self.iconContainer)
        self.mainLayout.addWidget(self.contentWidget, 1)
        self.mainLayout.addWidget(self.rightWidget)
        
        # 连接信号
        self.actionButton.clicked.connect(self.buttonClicked.emit)
        

        
    def setIcon(self, icon: Union[QIcon, FluentIconBase]):
        """设置图标"""
        self.iconWidget.setIcon(icon)
        
    def setTitle(self, title: str):
        """设置标题"""
        self.titleLabel.setText(title)
        
    def setDescription(self, description: str):
        """设置描述"""
        self.descriptionLabel.setText(description)
        
    def setStatus(self, status: str):
        """设置状态标签，只支持'官方'和'mark'两种类型"""
        self.statusLabel.setText(status)
        if status == "官方":
            self.statusLabel.setProperty("statusType", "official")
        elif status == "mark":
            self.statusLabel.setProperty("statusType", "mark")
        else:
            self.statusLabel.setProperty("statusType", "official")
        self.statusLabel.setStyle(self.statusLabel.style())
        

    def setButtonText(self, text: str):
        """设置按钮文字"""
        self.actionButton.setText(text)
        
    def setCardColorScheme(self, scheme: str):
        """设置卡片颜色方案"""
        self.setProperty("colorScheme", scheme)
        self.iconContainer.setProperty("colorScheme", scheme)
        self.setStyle(self.style())
        
    def setIconColors(self, icon_color: str):
        """设置图标颜色"""
        self.iconWidget.setStyleSheet(f"color: {icon_color};")
