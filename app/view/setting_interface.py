# coding:utf-8
import os
import asyncio
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QTimer, QThread
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QStackedWidget, QFileDialog

from qfluentwidgets import (
    ScrollArea, SegmentedWidget, SettingCardGroup, SwitchSettingCard, 
    OptionsSettingCard, PushSettingCard, HyperlinkCard, PrimaryPushSettingCard,
    ComboBoxSettingCard, ExpandLayout, CustomColorSettingCard, RangeSettingCard,
    setTheme, setThemeColor, FluentIcon as FIF, InfoBar, TitleLabel, qconfig, InfoBarPosition,
    BodyLabel, MessageBox
)

from ..common.config import config, APP_NAME, VERSION, AUTHOR, COPYRIGHT, COPYYEAR, APP_URL, FALLBACK_URL, CONTACT_EMAIL, BLOG_URL, DONATE_URL
from ..common.style_sheet import setStyleSheet
from ..common.signal_bus import signalBus
from ..common import resource_rc
from ..common.common_utils import copy_to_clipboard
from ..common.device_activator import DeviceActivator
from ..common.config_manager import ConfigManager


class ActivationThread(QThread):
    """设备激活线程"""
    activation_completed = pyqtSignal(bool)
    activation_error = pyqtSignal(str)
    
    def __init__(self, device_activator, activation_data):
        super().__init__()
        self.device_activator = device_activator
        self.activation_data = activation_data
    
    def run(self):
        try:
            # 在新线程中创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self.device_activator.process_activation(self.activation_data)
                )
                self.activation_completed.emit(result)
            finally:
                loop.close()
                
        except Exception as e:
            self.activation_error.emit(str(e))


class SettingInterface(ScrollArea):
    """ Setting interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        
        # 设置标题
        self.settingLabel = TitleLabel(self.tr("设置"), self)
        
        # 创建分段控件
        self.pivot = SegmentedWidget(self.scrollWidget)
        
        # 创建堆叠窗口
        self.stackedWidget = QStackedWidget(self.scrollWidget)
        
        # 创建各个子页面
        self.personalPage = PersonalizationPage(self.scrollWidget)
        self.activationPage = ActivationSettingsPage(self.scrollWidget)
        self.otherPage = OtherSettingsPage(self.scrollWidget)
        self.aboutPage = AboutAuthorPage(self.scrollWidget)
        
        self.__initWidget()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initWidget(self):
        # self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 50, 0, 20)
        self.setWidget(self.scrollWidget)
        self.enableTransparentBackground()
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')
        
        # 初始化分段控件
        self.pivot.addItem("personal", self.tr("个性化"), icon=FIF.PALETTE)
        self.pivot.addItem("activation", self.tr("激活设置"), icon=FIF.CERTIFICATE)
        self.pivot.addItem("other", self.tr("其他设置"), icon=FIF.SETTING)
        self.pivot.addItem("about", self.tr("关于作者"), icon=FIF.INFO)
        self.pivot.setCurrentItem("personal")
        
        # 添加页面到堆叠窗口
        self.stackedWidget.addWidget(self.personalPage)
        self.stackedWidget.addWidget(self.activationPage)
        self.stackedWidget.addWidget(self.otherPage)
        self.stackedWidget.addWidget(self.aboutPage)
        
        # 设置样式
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        self.setQss()
        
        # 连接主题变化信号
        signalBus.themeChangedSig.connect(self._refreshInterface)
    
    def _refreshInterface(self):
        """刷新界面样式"""
        self.setQss()
    
    def setQss(self):
        """设置样式表"""
        setStyleSheet(self, 'setting_interface')

    def __initLayout(self):
        self.settingLabel.move(36, 10)
        
        self.vBoxLayout.setContentsMargins(10, 10, 10, 0)
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.stackedWidget)

    def __connectSignalToSlot(self):
        self.pivot.currentItemChanged.connect(
            lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))


class PersonalizationPage(QWidget):
    """ 个性化页面 """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("personal")
        self.expandLayout = ExpandLayout(self)
        
        # 主题设置组
        self.themeGroup = SettingCardGroup(self.tr('主题设置'), self)
        
        self.themeCard = OptionsSettingCard(
            qconfig.themeMode,
            FIF.BRUSH,
            self.tr('应用主题'),
            self.tr("更改应用程序的外观"),
            texts=[
                self.tr('浅色'), self.tr('深色'),
                self.tr('跟随系统设置')
            ],
            parent=self.themeGroup
        )
        
        self.themeColorCard = CustomColorSettingCard(
            qconfig.themeColor,
            FIF.PALETTE,
            self.tr('主题色'),
            self.tr('更改应用程序的主题颜色'),
            self.themeGroup
        )
        
        # 界面设置组
        self.interfaceGroup = SettingCardGroup(self.tr('界面设置'), self)
        
        self.zoomCard = OptionsSettingCard(
            config.dpiScale,
            FIF.ZOOM,
            self.tr("界面缩放"),
            self.tr("更改小部件和字体的大小"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("跟随系统设置")
            ],
            parent=self.interfaceGroup
        )
        
        self.languageCard = ComboBoxSettingCard(
            config.language,
            FIF.LANGUAGE,
            self.tr('语言'),
            self.tr('设置界面显示语言'),
            texts=['简体中文', '繁體中文', 'English', self.tr('跟随系统设置')],
            parent=self.interfaceGroup
        )
        
        # 系统设置组
        self.systemGroup = SettingCardGroup(self.tr('系统设置'), self)
        
        self.startupCard = SwitchSettingCard(
            FIF.POWER_BUTTON,
            self.tr('开机自启动'),
            self.tr('开机时自动启动应用程序'),
            config.startupOnBoot,
            self.systemGroup
        )
        
        self.trayCard = SwitchSettingCard(
            FIF.MINIMIZE,
            self.tr('最小化到托盘'),
            self.tr('关闭窗口时最小化到系统托盘'),
            config.minimizeToTray,
            self.systemGroup
        )
        
        self.__initLayout()
        self.__connectSignalToSlot()
    
    def __initLayout(self):
        # 添加卡片到组
        self.themeGroup.addSettingCard(self.themeCard)
        self.themeGroup.addSettingCard(self.themeColorCard)
        
        self.interfaceGroup.addSettingCard(self.zoomCard)
        self.interfaceGroup.addSettingCard(self.languageCard)
        
        self.systemGroup.addSettingCard(self.startupCard)
        self.systemGroup.addSettingCard(self.trayCard)
        
        # 添加组到布局
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(0, 0, 0, 0)
        self.expandLayout.addWidget(self.themeGroup)
        self.expandLayout.addWidget(self.interfaceGroup)
        self.expandLayout.addWidget(self.systemGroup)
    
    def __connectSignalToSlot(self):
        qconfig.themeChanged.connect(setTheme)
        qconfig.themeChanged.connect(self._onThemeChanged)
        self.themeColorCard.colorChanged.connect(lambda c: setThemeColor(c))
        qconfig.appRestartSig.connect(self.__showRestartTooltip)
        self.themeCard.optionChanged.connect(lambda: setTheme(qconfig.get(qconfig.themeMode)))
        self.themeCard.optionChanged.connect(self._onThemeChanged)
        self.zoomCard.optionChanged.connect(self.__showRestartTooltip)
    
    def _onThemeChanged(self):
        """主题变化处理"""
        # 发送主题变化信号
        signalBus.themeChangedSig.emit()
    
    def __showRestartTooltip(self):
        """ 显示重启提示 """
        InfoBar.success(
            self.tr('更新成功'),
            self.tr('配置在重启后生效'),
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=1500,
            parent=self.window()
        )


class OtherSettingsPage(QWidget):
    """ 其他设置页面 """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("other")
        self.expandLayout = ExpandLayout(self)
        
        # 更新设置组
        self.updateGroup = SettingCardGroup(self.tr('软件更新'), self)
        
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.tr('启动时检查更新'),
            self.tr('应用程序启动时检查新版本'),
            config.checkUpdateAtStartUp,
            parent=self.updateGroup
        )
        
        self.checkUpdateCard = PrimaryPushSettingCard(
            self.tr('检查更新'),
            FIF.INFO,
            self.tr('检查更新'),
            self.tr('检查是否有新版本可用'),
            self.updateGroup
        )
        
        self.__initLayout()
        self.__connectSignalToSlot()
    
    def __initLayout(self):
        self.updateGroup.addSettingCard(self.updateOnStartUpCard)
        self.updateGroup.addSettingCard(self.checkUpdateCard)
        
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(0, 0, 0, 0)
        self.expandLayout.addWidget(self.updateGroup)
    
    def __connectSignalToSlot(self):
        """连接信号到槽函数"""
        self.checkUpdateCard.clicked.connect(self._onCheckUpdateClicked)
    
    def _onCheckUpdateClicked(self):
        """检查更新按钮点击事件"""
        # 获取主窗口实例并调用版本检测
        main_window = self.window()
        if hasattr(main_window, 'checkVersionUpdate'):
            main_window.checkVersionUpdate(is_startup=False)
    
    def tr(self, text):
        return text


class AboutAuthorPage(QWidget):
    """ 关于作者页面 """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("about")
        self.expandLayout = ExpandLayout(self)
        
        # 关于组
        self.aboutGroup = SettingCardGroup(self.tr('关于'), self)
        
        self.helpCard = HyperlinkCard(
            APP_URL,
            self.tr('打开项目主页'),
            FIF.HELP,
            self.tr('帮助'),
            self.tr('获取使用帮助和常见问题解答'),
            self.aboutGroup
        )
        
        self.feedbackCard = HyperlinkCard(
            FALLBACK_URL,
            self.tr('提供反馈'),
            FIF.FEEDBACK,
            self.tr('提供反馈'),
            self.tr('通过提供反馈帮助我们改进') + f' {APP_NAME}',
            self.aboutGroup
        )
        
        self.aboutCard = HyperlinkCard(
            APP_URL,
            self.tr('查看项目'),
            FIF.INFO,
            self.tr('关于'),
            f'© {self.tr("版权所有")} {COPYYEAR}, {AUTHOR}. {self.tr("版本")} {VERSION}',
            self.aboutGroup
        )
        
        self.blogCard = HyperlinkCard(
            BLOG_URL,
            self.tr('访问博客'),
            FIF.LINK,
            self.tr('作者博客'),
            self.tr('访问作者的个人博客'),
            self.aboutGroup
        )
        
        self.contactCard = HyperlinkCard(
            f'mailto:{CONTACT_EMAIL}',
            self.tr('发送邮件'),
            FIF.MAIL,
            self.tr('联系作者'),
            f'{self.tr("邮箱")}: {CONTACT_EMAIL}',
            self.aboutGroup
        )
        
        self.__initLayout()
        self.__connectSignalToSlot()
    
    def __initLayout(self):
        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)
        self.aboutGroup.addSettingCard(self.blogCard)
        self.aboutGroup.addSettingCard(self.contactCard)
        
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(0, 0, 0, 0)
        self.expandLayout.addWidget(self.aboutGroup)
    
    def __connectSignalToSlot(self):
        pass

    def tr(self, text):
        return text


class ActivationSettingsPage(QWidget):
    """ 激活设置页面 """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("activation")
        self.expandLayout = ExpandLayout(self)
        
        # 激活管理组
        self.activationGroup = SettingCardGroup(self.tr('激活管理'), self)
        
        # 激活操作
        self.generateCodeCard = PushSettingCard(
            self.tr('生成验证码'),
            FIF.CERTIFICATE,
            self.tr('生成激活验证码'),
            self.tr('点击生成验证码并自动复制到剪贴板'),
            self.activationGroup
        )
        
        self.__initLayout()
        self.__connectSignalToSlot()
    
    def __initLayout(self):
        # 添加激活操作
        self.activationGroup.addSettingCard(self.generateCodeCard)
        
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(0, 0, 0, 0)
        self.expandLayout.addWidget(self.activationGroup)
    
    def __connectSignalToSlot(self):
        """连接信号到槽函数"""
        # 连接按钮点击事件
        self.generateCodeCard.clicked.connect(self.__onGenerateCodeClicked)
    
    def __onGenerateCodeClicked(self):
        """生成验证码按钮点击事件 - 基于py-xiaozhi逻辑"""
        try:
            self.generateCodeCard.setEnabled(False)
            self.generateCodeCard.setContent(self.tr('生成中...'))
            
            # 获取配置管理器
            config_manager = ConfigManager.get_instance()
            
            # 创建设备激活器（按照py-xiaozhi逻辑）
            device_activator = DeviceActivator(config_manager)
            
            # 检查是否已激活
            if device_activator.is_activated():
                InfoBar.success(
                    self.tr('设备已激活'),
                    self.tr('设备已经激活，无需重复激活'),
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=3000,
                    parent=self.window()
                )
                self.generateCodeCard.setEnabled(True)
                self.generateCodeCard.setContent(self.tr('设备已激活'))
                return
            
            # 获取OTA配置数据（按照py-xiaozhi逻辑）
            activation_data = device_activator.get_activation_data()
            
            if activation_data and "activation" in activation_data:
                # 服务器返回激活信息，说明设备未激活
                activation_info = activation_data["activation"]
                if activation_info.get("code"):
                    verification_code = activation_info["code"]
                    
                    # 复制到剪贴板
                    if copy_to_clipboard(verification_code):
                        InfoBar.success(
                            self.tr('验证码已生成'),
                            self.tr(f'验证码 {verification_code} 已复制到剪贴板'),
                            position=InfoBarPosition.BOTTOM_RIGHT,
                            duration=8000,
                            parent=self.window()
                        )
                    
                    self.generateCodeCard.setContent(self.tr(f'验证码: {verification_code}'))
                    
                    # 启动激活流程（按照py-xiaozhi逻辑）
                    self.__startActivationProcess(device_activator, activation_info)
                else:
                    InfoBar.error(
                        self.tr('错误'),
                        self.tr('服务器返回的激活数据中缺少验证码'),
                        position=InfoBarPosition.BOTTOM_RIGHT,
                        duration=3000,
                        parent=self.window()
                    )
            elif activation_data and "activation" not in activation_data:
                # 服务器没有返回activation字段，说明设备已激活
                InfoBar.info(
                    self.tr('设备已激活'),
                    self.tr('设备已经激活，无需重复激活'),
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=3000,
                    parent=self.window()
                )
                self.generateCodeCard.setContent(self.tr('设备已激活'))
                self.generateCodeCard.setEnabled(False)
            else:
                InfoBar.error(
                    self.tr('网络错误'),
                    self.tr('无法获取激活数据，请检查网络连接'),
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=3000,
                    parent=self.window()
                )
            
        except Exception as e:
            InfoBar.error(
                self.tr('错误'),
                self.tr(f'生成验证码失败: {str(e)}'),
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=3000,
                parent=self.window()
            )
        finally:
            self.generateCodeCard.setEnabled(True)
    
    def __startActivationProcess(self, device_activator, activation_data):
        """启动激活流程 - 基于py-xiaozhi逻辑"""
        def on_activation_completed(success):
            if success:
                InfoBar.success(
                    self.tr('激活成功'),
                    self.tr('设备已成功激活！'),
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=3000,
                    parent=self.window()
                )
                self.generateCodeCard.setContent(self.tr('设备已激活'))
                self.generateCodeCard.setEnabled(False)
            else:
                InfoBar.info(
                    self.tr('激活进行中'),
                    self.tr('激活流程已启动，请等待激活完成'),
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=3000,
                    parent=self.window()
                )
                # 启动状态检测
                self.__startActivationCheck(device_activator)
        
        def on_activation_error(error_msg):
            InfoBar.error(
                self.tr('激活错误'),
                self.tr(f'激活流程异常: {error_msg}'),
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=3000,
                parent=self.window()
            )
        
        # 创建并启动激活线程
        self.activation_thread = ActivationThread(device_activator, activation_data)
        self.activation_thread.activation_completed.connect(on_activation_completed)
        self.activation_thread.activation_error.connect(on_activation_error)
        self.activation_thread.start()
    
    def __startActivationCheck(self, device_activator):
        """启动激活状态检测"""
        # 保存device_activator引用
        self.device_activator = device_activator
        
        # 创建定时器检测激活状态
        self.activationTimer = QTimer()
        self.activationTimer.timeout.connect(self.__checkActivationStatus)
        self.activationTimer.start(5000)  # 每5秒检测一次
        
        # 60秒后停止检测
        QTimer.singleShot(60000, self.activationTimer.stop)
    
    def __checkActivationStatus(self):
        """检测激活状态"""
        try:
            if not (hasattr(self, 'device_activator') and self.device_activator):
                # 没有device_activator引用，停止检测
                self._stopActivationTimer()
                return
            
            # 检查本地激活状态
            if self.device_activator.is_activated():
                self._handleActivationSuccess()
                return
            
            # 检查服务器激活状态
            self._checkServerActivationStatus()
                
        except Exception as e:
            print(f"[状态检测] 激活状态检测异常: {e}")
    
    def _stopActivationTimer(self):
        """停止激活状态检测定时器"""
        if hasattr(self, 'activationTimer'):
            self.activationTimer.stop()
    
    def _handleActivationSuccess(self):
        """处理激活成功"""
        self._stopActivationTimer()
        InfoBar.success(
            self.tr('激活成功'),
            self.tr('设备已成功激活！'),
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=3000,
            parent=self.window()
        )
        self.generateCodeCard.setContent(self.tr('设备已激活'))
        self.generateCodeCard.setEnabled(False)
    
    def _checkServerActivationStatus(self):
        """检查服务器激活状态"""
        try:
            activation_data = self.device_activator.get_activation_data()
            if activation_data and "activation" not in activation_data:
                # 服务器端已激活，更新本地状态
                self.device_activator.set_activation_status(True)
                self._handleActivationSuccess()
        except Exception as e:
            print(f"[状态检测] 检查服务器状态失败: {e}")
            # 网络错误时不影响主流程，继续等待
    

    
    def tr(self, text):
        return text