# coding:utf-8
import sys
from abc import ABCMeta

from PyQt5.QtCore import Qt, QUrl, QObject
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QSystemTrayIcon
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, FluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont, InfoBadge,
                            InfoBadgePosition, FluentBackgroundTheme)
from qfluentwidgets import FluentIcon as FIF

from .setting_interface import SettingInterface
from .home_interface import HomeInterface
from .system_tray import SystemTrayIcon
from ..common.signal_bus import signalBus
from ..common.style_sheet import setStyleSheet
from ..common.base_display import BaseDisplay
from ..common.config import config, DONATE_URL


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


# 创建兼容的元类
class CombinedMeta(type(QObject), ABCMeta):
    pass


class Window(FluentWindow, BaseDisplay, metaclass=CombinedMeta):

    def __init__(self):
        FluentWindow.__init__(self)
        BaseDisplay.__init__(self)
        
        # 状态管理
        self.autoMode = False
        self.currentStatus = ""
        self.isConnected = True
        
        # 回调函数
        self.buttonPressCallback = None
        self.buttonReleaseCallback = None
        self.modeCallback = None
        self.autoCallback = None
        self.abortCallback = None
        self.sendTextCallback = None
        
        # 表情管理
        self.emotionMovie = None
        self.emotionCache = {}
        self.lastEmotionName = None

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.settingInterface = SettingInterface(self)
        
        # 系统托盘组件
        self.systemTray = None

        self.initNavigation()
        self.initWindow()
        
        # 连接信号
        self.connectSignalToSlot()
        
        # 初始化系统托盘
        self.initSystemTray()
        
        # 检查设备激活状态
        self.checkActivationStatus()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '聊天')

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('XiaoZhi AI', ':/images/LOGO.svg'),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )

        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

        # 设置导航栏展开宽度
        self.navigationInterface.setExpandWidth(200)

    def initWindow(self):
        self.setMinimumSize(700, 650)
        self.resize(700, 650)
        self.setWindowIcon(QIcon(':/images/LOGO.svg'))
        self.setWindowTitle('XiaoZhi AI')
        
        # 设置退出行为
        # QApplication.setQuitOnLastWindowClosed(False)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def initSystemTray(self):
        """初始化系统托盘"""
        # 检查系统是否支持系统托盘
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.warning("系统不支持系统托盘功能")
            return
            
        self.systemTray = SystemTrayIcon(self)
        self.systemTray.show()
    
    def checkActivationStatus(self):
        """检查设备激活状态"""
        try:
            from ..common.device_fingerprint import DeviceFingerprint
            from qfluentwidgets import InfoBar, InfoBarPosition
            
            device_fingerprint = DeviceFingerprint.get_instance()
            
            # 检查设备是否已激活
            if not device_fingerprint.is_activated():
                # 显示未激活提示
                InfoBar.warning(
                    title='设备未激活',
                    content='设备尚未激活，请前往设置界面生成验证码完成激活',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=8000,
                    parent=self
                )
        except Exception as e:
            print(f"检查激活状态失败: {e}")

    def showMessageBox(self):
        w = MessageBox(
            '支持作者🥰',
            '个人开发不易，如果这个项目帮助到了您，可以考虑请作者喝一瓶快乐水🥤。您的支持就是作者开发和维护项目的动力🚀',
            self
        )
        w.yesButton.setText('来啦老弟')
        w.cancelButton.setText('下次一定')
        
        if w.exec():
            QDesktopServices.openUrl(QUrl(DONATE_URL))
    
    def connectSignalToSlot(self):
        """连接信号到槽函数"""
        # 主题变化信号
        signalBus.themeChangedSig.connect(self.refreshInterface)
        
        # 应用消息信号
        signalBus.appMessageSig.connect(self.onAppMessage)
        
        # 连接home interface的信号
        self.homeInterface.manualPressed.connect(self.onManualButtonPress)
        self.homeInterface.manualReleased.connect(self.onManualButtonRelease)
        self.homeInterface.autoClicked.connect(self.onAutoButtonClick)
        self.homeInterface.abortClicked.connect(self.onAbortButtonClick)
        self.homeInterface.modeClicked.connect(self.onModeButtonClick)
        self.homeInterface.textSent.connect(self.onTextSent)
    
    def refreshInterface(self):
        """刷新界面样式"""
        self.setQss()
    
    def setQss(self):
        """设置样式表"""
        setStyleSheet(self, 'main_window')
    
    # BaseDisplay接口实现
    async def set_callbacks(self, press_callback=None, release_callback=None, 
                          mode_callback=None, auto_callback=None, 
                          abort_callback=None, send_text_callback=None):
        """设置回调函数"""
        self.buttonPressCallback = press_callback
        self.buttonReleaseCallback = release_callback
        self.modeCallback = mode_callback
        self.autoCallback = auto_callback
        self.abortCallback = abort_callback
        self.sendTextCallback = send_text_callback
    
    async def update_status(self, status: str, connected: bool):
        """更新状态文本并处理相关逻辑"""
        statusChanged = status != self.currentStatus
        connectedChanged = connected != self.isConnected

        if statusChanged:
            self.currentStatus = status
        if connectedChanged:
            self.isConnected = connected

        # 通过homeInterface更新状态
        self.homeInterface.updateStatus(status, connected)

        # 更新系统托盘
        if statusChanged or connectedChanged:
            self.updateSystemTray(status)
    
    async def update_text(self, text: str):
        """更新TTS文本"""
        self.homeInterface.updateText(text)
    
    async def update_emotion(self, emotionName: str):
        """更新表情显示"""
        if emotionName == self.lastEmotionName:
            return

        self.lastEmotionName = emotionName
        self.homeInterface.updateEmotion(emotionName)
    
    async def update_button_status(self, text: str):
        """更新按钮状态"""
        if self.autoMode and hasattr(self.homeInterface, 'voiceCard'):
            self.homeInterface.voiceCard.updateAutoButton(text)
    
    async def start(self):
        """启动GUI"""
        self.show()
    
    def closeWindow(self):
        """关闭窗口处理"""
        if hasattr(self, 'systemTray') and self.systemTray:
            self.systemTray.hide()
        super().close()
    
    # 事件处理方法
    def onManualButtonPress(self):
        """手动模式按钮按下事件处理"""
        if self.buttonPressCallback:
            self.buttonPressCallback()

    def onManualButtonRelease(self):
        """手动模式按钮释放事件处理"""
        if self.buttonReleaseCallback:
            self.buttonReleaseCallback()

    def onAutoButtonClick(self):
        """自动模式按钮点击事件处理"""
        if self.autoCallback:
            self.autoCallback()

    def onAbortButtonClick(self):
        """处理中止按钮点击事件"""
        if self.abortCallback:
            self.abortCallback()

    def onModeButtonClick(self):
        """对话模式切换按钮点击事件"""
        if self.modeCallback:
            if not self.modeCallback():
                return

        self.autoMode = not self.autoMode

        if self.autoMode:
            self.updateModeButtonStatus("自动对话")
            self.switchToAutoMode()
        else:
            self.updateModeButtonStatus("手动对话")
            self.switchToManualMode()

    def onTextSent(self, text: str):
        """文本发送事件"""
        if self.sendTextCallback:
            import asyncio
            if asyncio.iscoroutinefunction(self.sendTextCallback):
                asyncio.create_task(self.sendTextCallback(text))
            else:
                self.sendTextCallback(text)
    
    def switchToAutoMode(self):
        """切换到自动模式的UI更新"""
        if hasattr(self.homeInterface, 'voiceCard'):
            self.homeInterface.voiceCard.switchToAutoMode()

    def switchToManualMode(self):
        """切换到手动模式的UI更新"""
        if hasattr(self.homeInterface, 'voiceCard'):
            self.homeInterface.voiceCard.switchToManualMode()
    
    def updateModeButtonStatus(self, text: str):
        """更新模式按钮状态"""
        if hasattr(self.homeInterface, 'voiceCard'):
            self.homeInterface.voiceCard.updateModeButton(text)
    
    def updateSystemTray(self, status):
        """更新系统托盘状态"""
        if hasattr(self, 'systemTray') and self.systemTray:
            tooltip = f"XiaoZhi AI - {status}"
            if not self.isConnected:
                tooltip += " (未连接)"
            self.systemTray.setToolTip(tooltip)
    
    def onAppMessage(self, message: str):
        """处理应用消息"""
        if message == "show":
            self.showMainWindow()
        elif message == "settings":
            self.onSettingsButtonClick()
    
    def showMainWindow(self):
        """显示主窗口"""
        if self.windowState() & Qt.WindowMinimized:
            self.showNormal()
        else:
            self.show()
            self.raise_()
    
    def onSettingsButtonClick(self):
        """处理设置按钮点击事件"""
        self.switchTo(self.settingInterface)
    
    def quitApplication(self):
        """退出应用程序"""
        if hasattr(self, 'systemTray') and self.systemTray:
            self.systemTray.hide()
        
        # 调用Application的shutdown方法进行优雅关闭
        try:
            from app.common.application import Application
            app = Application.get_instance()
            if app:
                import asyncio
                from PyQt5.QtCore import QTimer
                
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 创建关闭任务，但设置超时机制
                    shutdown_task = asyncio.create_task(app.shutdown())
                    
                    # 设置超时后强制退出
                    def force_quit():
                        if not shutdown_task.done():
                            self.logger.warning("关闭超时，强制退出")
                            shutdown_task.cancel()
                        QApplication.quit()
                    
                    # 3秒后强制退出
                    QTimer.singleShot(3000, force_quit)
                    
                    # 当shutdown完成时正常退出
                    def on_shutdown_complete(task):
                        if not task.cancelled():
                            if task.exception():
                                self.logger.error(f"应用程序关闭异常: {task.exception()}")
                            else:
                                self.logger.info("应用程序正常关闭")
                            QApplication.quit()
                    
                    shutdown_task.add_done_callback(on_shutdown_complete)
                else:
                    QApplication.quit()
            else:
                QApplication.quit()
        except Exception as e:
            self.logger.error(f"关闭应用程序失败: {e}")
            QApplication.quit()
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 检查是否启用最小化到托盘且系统托盘可用
        if (hasattr(self, 'systemTray') and self.systemTray and 
            config.get(config.minimizeToTray) and 
            SystemTrayIcon.isSystemTrayAvailable()):
            # 最小化到托盘
            self.hide()
            # 显示托盘通知
            if hasattr(self.systemTray, 'show_message'):
                self.systemTray.show_message(
                    "XiaoZhi AI", 
                    "应用程序已最小化到系统托盘", 
                    duration=2000
                )
            event.ignore()
        else:
            # 直接退出程序
            self.quitApplication()
            event.accept()
    
    async def toggle_mode(self):
        """切换模式"""
        if self.modeCallback:
            self.onModeButtonClick()

    async def toggle_window_visibility(self):
        """切换窗口可见性"""
        if self.isVisible():
            self.hide()
        else:
            self.showMainWindow()
