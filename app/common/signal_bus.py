# coding: utf-8
from PyQt5.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    """ Signal bus """

    # 应用消息信号
    appMessageSig = pyqtSignal(str)
    appErrorSig = pyqtSignal(str)

    # 主题变化信号
    themeChangedSig = pyqtSignal()
    
    # 界面刷新信号
    refreshInterfaceSig = pyqtSignal()


signalBus = SignalBus()