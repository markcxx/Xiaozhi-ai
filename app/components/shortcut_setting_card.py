# coding:utf-8
from typing import Union
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from qfluentwidgets.components.settings.setting_card import SettingCard
from qfluentwidgets.common.icon import FluentIconBase
from qfluentwidgets.common.config import ConfigItem, qconfig
from .shortcut_picker import ShortcutPicker


class ShortcutSettingCard(SettingCard):
    """快捷键设置卡片"""
    
    shortcutChanged = pyqtSignal(str)
    
    def __init__(self, configItem: ConfigItem, icon: Union[str, QIcon, FluentIconBase], 
                 title: str, content: str = None, parent=None):
        """
        Parameters
        ----------
        configItem: ConfigItem
            configuration item operated by the card
            
        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        
        self.configItem = configItem
        
        # 创建快捷键选择器
        self.shortcutPicker = ShortcutPicker(self)
        
        # 设置当前快捷键值
        current_shortcut = qconfig.get(configItem)
        self.shortcutPicker.setShortcut(current_shortcut)
        self.shortcutPicker.setDefaultShortcut(current_shortcut)
        
        # 添加到布局
        self.hBoxLayout.addWidget(self.shortcutPicker, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        
        # 连接信号
        self.shortcutPicker.shortcutChanged.connect(self._onShortcutChanged)
        configItem.valueChanged.connect(self.setValue)
    
    def _onShortcutChanged(self, shortcut: str):
        """快捷键改变事件"""
        qconfig.set(self.configItem, shortcut)
        self.shortcutChanged.emit(shortcut)
    
    def setValue(self, shortcut: str):
        """设置快捷键值"""
        self.shortcutPicker.setShortcut(shortcut)
        qconfig.set(self.configItem, shortcut)
    
    def getShortcut(self) -> str:
        """获取当前快捷键"""
        return self.shortcutPicker.getCurrentShortcut()