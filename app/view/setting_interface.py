# coding:utf-8
import os
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QStackedWidget, QFileDialog

from qfluentwidgets import (
    ScrollArea, SegmentedWidget, SettingCardGroup, SwitchSettingCard, 
    OptionsSettingCard, PushSettingCard, HyperlinkCard, PrimaryPushSettingCard,
    ComboBoxSettingCard, ExpandLayout, CustomColorSettingCard, RangeSettingCard,
    setTheme, setThemeColor, FluentIcon as FIF, InfoBar, TitleLabel, qconfig, InfoBarPosition,
    BodyLabel
)

from ..common.config import config
from ..common.style_sheet import setStyleSheet
from ..common.signal_bus import signalBus
from ..common import resource_rc


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
        self.pivot.addItem("other", self.tr("其他设置"), icon=FIF.SETTING)
        self.pivot.addItem("about", self.tr("关于作者"), icon=FIF.INFO)
        self.pivot.setCurrentItem("personal")
        
        # 添加页面到堆叠窗口
        self.stackedWidget.addWidget(self.personalPage)
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
        
        self.__initLayout()
    
    def __initLayout(self):
        self.updateGroup.addSettingCard(self.updateOnStartUpCard)
        
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(0, 0, 0, 0)
        self.expandLayout.addWidget(self.updateGroup)


class AboutAuthorPage(QWidget):
    """ 关于作者页面 """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("about")
        self.expandLayout = ExpandLayout(self)
        
        # 关于组
        self.aboutGroup = SettingCardGroup(self.tr('关于'), self)
        
        self.helpCard = HyperlinkCard(
            "https://github.com/",
            self.tr('打开帮助页面'),
            FIF.HELP,
            self.tr('帮助'),
            self.tr('获取使用帮助和常见问题解答'),
            self.aboutGroup
        )
        
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('提供反馈'),
            FIF.FEEDBACK,
            self.tr('提供反馈'),
            self.tr('通过提供反馈帮助我们改进XiaoZhi AI'),
            self.aboutGroup
        )
        
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('检查更新'),
            FIF.INFO,
            self.tr('关于'),
            '© ' + self.tr('版权所有') + ' 2024, XiaoZhi AI开发团队. ' +
            self.tr('版本') + ' 1.0.0',
            self.aboutGroup
        )
        
        self.__initLayout()
        self.__connectSignalToSlot()
    
    def __initLayout(self):
        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)
        
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(0, 0, 0, 0)
        self.expandLayout.addWidget(self.aboutGroup)
    
    def __connectSignalToSlot(self):
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/")))

    def tr(self, text):
        return text