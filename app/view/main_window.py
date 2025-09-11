# coding:utf-8
import sys

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, FluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont, InfoBadge,
                            InfoBadgePosition, FluentBackgroundTheme)
from qfluentwidgets import FluentIcon as FIF
from .setting_interface import SettingInterface
from .home_interface import HomeInterface
from ..common.signal_bus import signalBus
from ..common.style_sheet import setStyleSheet


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class Window(FluentWindow):

    def __init__(self):
        super().__init__()

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.settingInterface = SettingInterface(self)

        self.initNavigation()
        self.initWindow()
        
        # 连接信号
        self._connectSignalToSlot()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('XiaoZhi AI', 'app/resource/images/avatar.png'),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )

        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

        # 设置导航栏展开宽度
        self.navigationInterface.setExpandWidth(200)

        # NOTE: enable acrylic effect
        # self.navigationInterface.setAcrylicEnabled(True)

    def initWindow(self):
        self.setMinimumSize(700, 650)
        self.resize(700, 650)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('XiaoZhi AI')

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)


        # set the minimum window width that allows the navigation panel to be expanded
        # self.navigationInterface.setMinimumExpandWidth(900)
        # self.navigationInterface.expand(useAni=False)

    def showMessageBox(self):
        w = MessageBox(
            'XiaoZhi AI',
            '欢迎使用XiaoZhi AI智能助手！',
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        w.exec()
    
    def _connectSignalToSlot(self):
        """连接信号到槽函数"""
        # 主题变化信号
        signalBus.themeChangedSig.connect(self._refreshInterface)
    
    def _refreshInterface(self):
        """刷新界面样式"""
        # 更新窗口背景样式
        self.setQss()
    
    def setQss(self):
        """设置样式表"""
        setStyleSheet(self, 'main_window')