# coding:utf-8
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon
from qfluentwidgets import Action, SystemTrayMenu
from qfluentwidgets import FluentIcon as FIF
from ..common.signal_bus import signalBus


class SystemTrayIcon(QSystemTrayIcon):
    """
    系统托盘图标
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(parent.windowIcon())
        self.setToolTip('XiaoZhi AI')

        self.menu = SystemTrayMenu(parent=parent)
        self.menu.addActions([
            Action(
                FIF.HOME,
                '显示主窗口',
                triggered=lambda: signalBus.appMessageSig.emit("show")
            ),
            Action(
                FIF.SETTING,
                '参数配置',
                triggered=lambda: signalBus.appMessageSig.emit("settings")
            ),
            Action(
                FIF.CLOSE,
                '退出程序',
                triggered=QApplication.instance().exit
            ),
        ])
        self.setContextMenu(self.menu)
        
        # 连接双击事件
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason):
        """
        处理托盘图标激活事件.
        """
        if reason == QSystemTrayIcon.DoubleClick:
            signalBus.appMessageSig.emit("show")
