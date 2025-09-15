# coding:utf-8
import sys
import asyncio
import subprocess
import os
from abc import ABCMeta

from PyQt5.QtCore import Qt, QUrl, QObject, QTimer
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QSystemTrayIcon
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, FluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont, InfoBadge,
                            InfoBadgePosition, FluentBackgroundTheme, InfoBar, InfoBarPosition,
                            InfoBarIcon)
from qfluentwidgets.components.widgets.info_badge import InfoLevel
from qfluentwidgets import FluentIcon as FIF

from .setting_interface import SettingInterface
from .home_interface import HomeInterface
from .mcp_interface import MCPInterface
from .system_tray import SystemTrayIcon
from ..common.signal_bus import signalBus
from ..common.style_sheet import setStyleSheet
from ..common.base_display import BaseDisplay
from ..common.config import config, DONATE_URL, VERSION
from ..common.version_service import get_version_service, DownloadThread
from ..components.progress_toast import ProgressToast
from ..components.shortcut_manager import ShortcutManager
from ..common.device_activator import DeviceActivator
from ..common.config_manager import ConfigManager
from ..common.logging_config import get_logger
from ..common.application import Application

logger = get_logger(__name__)


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
        self.mcpInterface = MCPInterface(self)
        self.settingInterface = SettingInterface(self)
        
        # 系统托盘组件
        self.systemTray = None
        
        # 快捷键管理器
        self.shortcutManager = None

        self.initNavigation()
        self.initWindow()
        
        # 连接信号
        self.connectSignalToSlot()
        
        # 初始化系统托盘
        self.initSystemTray()
        
        # 初始化快捷键管理器
        self.initShortcutManager()
        
        # 检查设备激活状态
        self.checkActivationStatus()
        
        # 启动版本检测
        self.initVersionCheck()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '聊天')
        self.addSubInterface(self.mcpInterface, FIF.APPLICATION, 'MCP服务')

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
    
    def initShortcutManager(self):
        """初始化快捷键管理器"""
        try:
            self.shortcutManager = ShortcutManager()
            logger.info("快捷键管理器初始化成功")
        except Exception as e:
            logger.error(f"快捷键管理器初始化失败: {e}", exc_info=True)
            self.shortcutManager = None
    
    def checkActivationStatus(self):
        """
        检查设备激活状态，如果未激活则显示提示信息.
        """
        config_manager = ConfigManager.get_instance()
        activator = DeviceActivator(config_manager)
        
        if not activator.is_activated():
            InfoBar.warning(
                title="设备未激活",
                content="请前往设置界面生成验证码进行设备激活",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=8000,
                parent=self
            )
    
    def initVersionCheck(self):
        """
        初始化版本检测.
        """
        if config.checkUpdateAtStartUp.value:
            self.checkVersionUpdate(is_startup=True)
    
    def checkVersionUpdate(self, is_startup=False):
        """
        检查版本更新.
        
        Args:
            is_startup: 是否为启动时检测
        """
        version_service = get_version_service()
        version_service.checkVersion(
            callback=lambda latest, has_new, download_url: self.onVersionChecked(latest, has_new, download_url, is_startup),
            error_callback=lambda error: self.onVersionCheckFailed(error, is_startup)
        )
    
    def onVersionChecked(self, latest_version: str, has_new_version: bool, download_url: str, is_startup: bool):
        """
        版本检测完成回调.
        """
        if has_new_version:
            self.showUpdateDialog(latest_version, download_url)
        elif not is_startup:
            # 手动检测且无新版本时显示提示
            InfoBar.success(
                title="检测成功",
                content=f"当前版本 {VERSION} 已是最新版本",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def onVersionCheckFailed(self, error_message: str, is_startup: bool):
        """
        版本检测失败回调.
        """
        if not is_startup:
            # 只在手动检测时显示错误信息
            InfoBar.error(
                title="检查更新失败",
                content="网络连接异常，请稍后重试",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def showUpdateDialog(self, latest_version: str, download_url: str):
        """
        显示更新对话框.
        """
        w = MessageBox(
            '发现新版本 🎉',
            f'检测到新版本 {latest_version}，是否立即下载更新？\n\n更新内容请查看项目发布页面了解详情。',
            self
        )
        w.yesButton.setText('立即下载')
        w.cancelButton.setText('下次更新')
        
        if w.exec():
            self.startDownload(latest_version, download_url)
    
    def startDownload(self, version: str, download_url: str):
        """
        开始下载更新文件.
        """
        if not download_url:
            InfoBar.error(
                title="下载失败",
                content="未找到下载链接，请手动前往官网下载",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        
        # 生成文件名
        filename = f"XiaozhiAI-v{version}-Windows-x86_64-Setup.exe"
        
        # 创建进度提示
        self.progress_toast = ProgressToast.create(
             icon=InfoBarIcon.INFORMATION,
             title="正在下载",
             content="喝杯茶休息一下吧",
             isClosable=True,
             level=InfoLevel.INFOAMTION,
             position=InfoBarPosition.TOP_RIGHT,
             parent=self
         )
        
        # 创建下载线程
        self.download_thread = DownloadThread(download_url, filename, self)
        self.download_thread.progressChanged.connect(self.onDownloadProgress)
        self.download_thread.downloadCompleted.connect(self.onDownloadCompleted)
        self.download_thread.downloadFailed.connect(self.onDownloadFailed)
        self.download_thread.start()
    
    def onDownloadProgress(self, progress: int):
        """
        下载进度更新回调.
        """
        self.progress_toast.setValue(progress)
    
    def onDownloadCompleted(self, file_path: str):
        """
        下载完成回调.
        """
        if hasattr(self, 'progress_toast'):
            self.progress_toast.setTitle("文件下载成功")
            self.progress_toast.setContent("更新文件已保存")
            self.progress_toast.success(duration=3000)
        # 延迟3秒后启动安装程序并退出
        QTimer.singleShot(3000, lambda: self.startInstallAndExit(file_path))
    
    def startInstallAndExit(self, file_path: str):
        """
        启动安装程序并退出当前应用.
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"安装文件不存在: {file_path}")
            return
        
        try:
            # 启动安装程序
            subprocess.Popen([file_path], shell=True)
            logger.info(f"已启动安装程序: {file_path}")
            
            # 退出当前应用程序
            QTimer.singleShot(1000, self.quitApplication)
            
        except Exception as e:
            logger.error(f"启动安装程序失败: {e}")
            InfoBar.error(
                title="启动失败",
                content=f"无法启动安装程序: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
    
    def onDownloadFailed(self, error_message: str):
        """
        下载失败回调.
        """
        if hasattr(self, 'progress_toast'):
            self.progress_toast.setTitle("下载失败")
            self.progress_toast.setLevel(InfoLevel.ERROR)
            QTimer.singleShot(5000, self.progress_toast.close)
        
        InfoBar.error(
            title="下载失败",
            content=f"下载更新文件失败：{error_message}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )

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
        
        # 快捷键变更信号
        signalBus.recordShortcutChanged.connect(self.onRecordShortcutChanged)
        signalBus.interruptShortcutChanged.connect(self.onInterruptShortcutChanged)
        
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
        
        # 启动快捷键管理器
        if self.shortcutManager:
            try:
                await self.shortcutManager.start()
                logger.info("快捷键管理器启动成功")
            except Exception as e:
                logger.error(f"快捷键管理器启动失败: {e}", exc_info=True)
    
    def closeWindow(self):
        """关闭窗口处理"""
        # 停止快捷键管理器
        if hasattr(self, 'shortcutManager') and self.shortcutManager:
            try:
                asyncio.create_task(self.shortcutManager.stop())
            except Exception as e:
                logger.error(f"停止快捷键管理器失败: {e}")
        
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
            if asyncio.iscoroutinefunction(self.sendTextCallback):
                asyncio.create_task(self.sendTextCallback(text))
            else:
                self.sendTextCallback(text)
    
    def onRecordShortcutChanged(self, shortcut: str):
        """录音快捷键变更事件"""
        logger.info(f"录音快捷键已更改为: {shortcut}")
        if self.shortcutManager:
            self.shortcutManager.reload_shortcuts()
    
    def onInterruptShortcutChanged(self, shortcut: str):
        """打断快捷键变更事件"""
        logger.info(f"打断快捷键已更改为: {shortcut}")
        if self.shortcutManager:
            self.shortcutManager.reload_shortcuts()
    
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
        app = Application.get_instance()
        if app:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 创建关闭任务，但设置超时机制
                shutdown_task = asyncio.create_task(app.shutdown())
                
                # 设置超时后强制退出
                def force_quit():
                    if not shutdown_task.done():
                        logger.warning("关闭超时，强制退出")
                        shutdown_task.cancel()
                    QApplication.quit()
                
                # 3秒后强制退出
                QTimer.singleShot(3000, force_quit)
                
                # 当shutdown完成时正常退出
                def on_shutdown_complete(task):
                    if not task.cancelled():
                        if task.exception():
                            logger.error(f"应用程序关闭异常: {task.exception()}")
                        else:
                            logger.info("应用程序正常关闭")
                        QApplication.quit()
                
                shutdown_task.add_done_callback(on_shutdown_complete)
            else:
                QApplication.quit()
        else:
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
