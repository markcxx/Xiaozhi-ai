# coding:utf-8
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    CardWidget, BodyLabel, PrimaryPushButton, ToolButton, FluentIcon as FIF,
    SubtitleLabel, CaptionLabel, PushButton
)
from qfluentwidgets.components.dialog_box.message_box_base import MessageBoxBase
from qfluentwidgets.common.style_sheet import themeColor, FluentStyleSheet, isDarkTheme
from qfluentwidgets.common.font import setFont
from qfluentwidgets.common.config import qconfig
from app.common.style_sheet import setCustomStyleSheetFromFile
from app.common import resource_rc


class ShortcutKeyButton(PrimaryPushButton):
    """快捷键按钮，禁用状态保持主题色背景"""
    
    def __init__(self, text="", parent=None):
        
        QPushButton.__init__(self, text, parent)
        
        self.isPressed = False
        self.isHover = False
        self._icon = QIcon()  # 使用空的QIcon而不是None
        self.setIconSize(QSize(16, 16))
        setFont(self)
        
        FluentStyleSheet.BUTTON.apply(self)
        
        # 设置为主要按钮样式
        self.setObjectName('PrimaryPushButton')
        
        # 应用自定义禁用样式
        self._updateDisabledStyle()
    
    def _updateDisabledStyle(self):
        """更新禁用状态样式"""
        # 设置按钮尺寸
        text = self.text()
        if text.lower() == 'space':
            self.setFixedSize(80, 40)  # 空格键最宽
        elif text.lower() in ['shift', 'ctrl']:
            self.setFixedSize(60, 40)  # 较宽的按钮
        elif text.lower() == 'meta':
            self.setFixedSize(40, 40)  # Windows键
            # 设置Windows SVG图标
            icon = QIcon(":/images/images/windows.svg")
            self.setIcon(icon)
            self.setIconSize(QSize(12, 12))
            self.setText("")  # 清空文本，只显示图标
            # 设置hasIcon属性以应用正确的样式
            self.setProperty('hasIcon', True)
            self.setStyle(self.style())  # 刷新样式
        else:
            self.setFixedSize(40, 40)  # 正方形按钮
        
        # 使用项目的QSS文件加载样式
        setCustomStyleSheetFromFile(self, 'shortcut_picker')


class ShortcutDialog(MessageBoxBase):
    """快捷键设置对话框"""
    
    def __init__(self, parent=None, current_shortcut="", default_shortcut="Ctrl+Shift+A"):
        super().__init__(parent)
        self.setWindowTitle("设置快捷键")
        self.widget.setFixedSize(400, 350)
        
        self.shortcut_text = current_shortcut or default_shortcut
        self.default_shortcut = default_shortcut
        self.shortcut_parts = []
        
        # 初始化UI组件
        # 标题标签
        self.titleLabel = SubtitleLabel("激活快捷键")
        self.titleLabel.setAlignment(Qt.AlignLeft)
        self.viewLayout.addWidget(self.titleLabel)
        
        # 提示标签
        self.tipLabel = CaptionLabel("按组合键以更改快捷键")
        self.tipLabel.setAlignment(Qt.AlignLeft)
        self.viewLayout.addWidget(self.tipLabel)
        
        # 添加间距
        self.viewLayout.addSpacing(10)
        
        # 快捷键显示区域容器
        self.shortcutContainer = QWidget()
        self.shortcutContainer.setFixedHeight(120)
        
        # 快捷键显示布局
        self.shortcutLayout = QHBoxLayout(self.shortcutContainer)
        self.shortcutLayout.setSpacing(8)
        self.shortcutLayout.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.shortcutLayout.setContentsMargins(20, 0, 20, 0)
        
        self.viewLayout.addWidget(self.shortcutContainer)
        
        # 隐藏默认按钮并添加自定义按钮
        self.yesButton.hide()
        self.cancelButton.hide()
        
        # 自定义按钮布局
        self.customButtonLayout = QHBoxLayout()
        self.customButtonLayout.setSpacing(12)
        
        # 保存按钮
        self.saveButton = PrimaryPushButton("保存")
        self.saveButton.clicked.connect(self.accept)
        self.saveButton.setAutoDefault(False)
        self.saveButton.setDefault(False)
        
        # 重置按钮
        self.resetButton = PushButton("重置")
        self.resetButton.clicked.connect(self._onResetClicked)
        self.resetButton.setAutoDefault(False)
        self.resetButton.setDefault(False)
        
        # 取消按钮
        self.cancelBtn = PushButton("取消")
        self.cancelBtn.clicked.connect(self.reject)
        self.cancelBtn.setAutoDefault(False)
        self.cancelBtn.setDefault(False)
        
        self.customButtonLayout.addWidget(self.saveButton)
        self.customButtonLayout.addWidget(self.resetButton)
        self.customButtonLayout.addWidget(self.cancelBtn)
        
        # 添加到按钮组
        self.buttonLayout.addLayout(self.customButtonLayout)
        
        self._updateShortcutDisplay()
        
        # 设置对话框焦点策略
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
    def keyPressEvent(self, event):
        """对话框键盘事件处理"""
        key = event.key()
        modifiers = event.modifiers()
        
        # 忽略单独的修饰键
        if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            return
            
        # 阻止所有按键的默认行为
        event.accept()
            
        # 构建快捷键文本
        key_parts = []
        
        if modifiers & Qt.ControlModifier:
            key_parts.append("Ctrl")
        if modifiers & Qt.ShiftModifier:
            key_parts.append("Shift")
        if modifiers & Qt.AltModifier:
            key_parts.append("Alt")
        if modifiers & Qt.MetaModifier:
            key_parts.append("Meta")
            
        # 添加主键
        if key == Qt.Key_Space:
            key_parts.append("Space")
        elif key == Qt.Key_Escape:
            # ESC键关闭对话框
            self.reject()
            return
        else:
            key_text = QKeySequence(key).toString()
            if key_text:
                key_parts.append(key_text)
            
        if key_parts:
            self.shortcut_text = "+".join(key_parts)
            self._updateShortcutDisplay()
         
    def _updateShortcutDisplay(self):
        """更新快捷键显示"""
        # 清除现有按钮
        for i in reversed(range(self.shortcutLayout.count())):
            child = self.shortcutLayout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if not self.shortcut_text:
            # 显示"无"按钮
            empty_btn = ShortcutKeyButton("")
            empty_btn.setEnabled(False)
            self.shortcutLayout.addWidget(empty_btn)
        else:
            # 分割快捷键并创建按钮
            parts = self.shortcut_text.split("+")
            for part in parts:
                btn = ShortcutKeyButton(part.strip())
                btn.setEnabled(False)
                self.shortcutLayout.addWidget(btn, 0, Qt.AlignmentFlag.AlignCenter)
        

        
    def _onResetClicked(self):
        """重置按钮点击事件"""
        self.shortcut_text = self.default_shortcut
        self._updateShortcutDisplay()
    
    def getShortcut(self):
        """获取设置的快捷键"""
        return self.shortcut_text


class ShortcutPicker(CardWidget):
    """快捷键选择器组件"""
    
    # 信号定义
    shortcutChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        
        self._current_shortcut = ""
        self._default_shortcut = "Ctrl+Shift+A"
        
        # 初始化UI组件
        # 主布局
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(20, 15, 20, 15)
        self.hBoxLayout.setSpacing(15)
        
        # 左侧快捷键显示区域
        self.shortcutLayout = QHBoxLayout()
        self.shortcutLayout.setSpacing(8)
        self.shortcutLayout.setAlignment(Qt.AlignLeft)
        
        # 右侧修改按钮（只显示图标）
        self.editButton = ToolButton(FIF.EDIT, self)
        self.editButton.setFixedSize(40, 40)
        self.editButton.clicked.connect(self._onEditClicked)
        
        # 添加到布局
        self.hBoxLayout.addLayout(self.shortcutLayout)
        self.hBoxLayout.addStretch()
        self.hBoxLayout.addWidget(self.editButton)
        
        # 初始显示
        self._updateShortcutDisplay()
        

        
    def _onEditClicked(self):
        """编辑按钮点击事件"""
        # 获取顶层窗口作为父窗口
        parent_window = self.window()
        dialog = ShortcutDialog(parent_window, self._current_shortcut, self._default_shortcut)
        if dialog.exec_() == dialog.Accepted:
            new_shortcut = dialog.getShortcut()
            if new_shortcut != self._current_shortcut:
                self.setShortcut(new_shortcut)
                self.shortcutChanged.emit(new_shortcut)
    
    def _updateShortcutDisplay(self):
        """更新快捷键显示"""
        # 清除现有按钮
        for i in reversed(range(self.shortcutLayout.count())):
            child = self.shortcutLayout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 使用当前快捷键或默认快捷键
        display_shortcut = self._current_shortcut or self._default_shortcut
        
        # 分割快捷键并创建按钮
        if display_shortcut:
            parts = display_shortcut.split("+")
            for part in parts:
                btn = ShortcutKeyButton(part.strip())
                btn.setEnabled(False)
                self.shortcutLayout.addWidget(btn)
                
    def setShortcut(self, shortcut: str):
        """设置快捷键"""
        self._current_shortcut = shortcut
        self._updateShortcutDisplay()
        
    def getShortcut(self) -> str:
        """获取当前快捷键"""
        return self._current_shortcut
        
    def setDefaultShortcut(self, shortcut: str):
        """设置默认快捷键"""
        self._default_shortcut = shortcut
        if not self._current_shortcut:
            self.setShortcut(shortcut)
            
    def getDefaultShortcut(self) -> str:
        """获取默认快捷键"""
        return self._default_shortcut
        
    def resetToDefault(self):
        """重置为默认快捷键"""
        if self._default_shortcut:
            self.setShortcut(self._default_shortcut)
            self.shortcutChanged.emit(self._default_shortcut)