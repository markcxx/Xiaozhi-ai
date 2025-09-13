# coding: utf-8
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import InfoBar, InfoBarIcon, InfoBarPosition
from qfluentwidgets.components.widgets.info_badge import InfoLevel


class ProgressToast(InfoBar):
    """带进度条的Toast提示组件"""
    
    def __init__(self, icon, title, content="", orient=Qt.Horizontal, 
                 isClosable=True, duration=5000, position=InfoBarPosition.TOP_RIGHT, parent=None):
        super().__init__(icon, title, content, orient, isClosable, duration, position, parent)
        self._progress = 0
        self._level = InfoLevel.INFOAMTION
        
    @classmethod
    def create(cls, icon=InfoBarIcon.INFORMATION, title="", content="", 
               isClosable=True, level=InfoLevel.INFOAMTION, position=InfoBarPosition.TOP_RIGHT, 
               parent=None):
        """创建ProgressToast实例"""
        toast = cls(icon, title, content, Qt.Horizontal, isClosable, -1, position, parent)
        toast._level = level
        toast.show()
        return toast
    
    def setValue(self, value: int):
        """设置进度值 (0-100)"""
        self._progress = max(0, min(100, value))
        self.update()  # 触发重绘
    
    def value(self) -> int:
        """获取当前进度值"""
        return self._progress
    
    def setTitle(self, title: str):
        """设置标题"""
        self.title = title
        self.titleLabel.setText(title)
    
    def setContent(self, content: str):
        """设置内容"""
        self.content = content
        self.contentLabel.setText(content)
    
    def setLevel(self, level: InfoLevel):
        """设置状态级别并更新图标"""
        self._level = level
        # 更新图标
        icon_map = {
            InfoLevel.INFOAMTION: InfoBarIcon.INFORMATION,
            InfoLevel.SUCCESS: InfoBarIcon.SUCCESS,
            InfoLevel.WARNING: InfoBarIcon.WARNING,
            InfoLevel.ERROR: InfoBarIcon.ERROR,
        }
        new_icon = icon_map.get(level, InfoBarIcon.INFORMATION)
        self.iconWidget.icon = new_icon
        self.iconWidget.update()  # 触发图标重绘
        self.update()  # 触发进度条重绘
    
    def success(self, duration=3000):
        """标记为成功状态"""
        self.setLevel(InfoLevel.SUCCESS)
        if duration > 0:
            QTimer.singleShot(duration, self.close)
    
    def paintEvent(self, event):
        """重写绘制事件，添加进度条"""
        super().paintEvent(event)
        
        # 绘制进度条
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 获取进度条颜色
        color = self._getProgressColor()
        
        # 计算进度条位置和大小
        rect = self.rect()
        progress_width = int(rect.width() * (self._progress / 100.0))
        progress_height = 5
        
        # 绘制进度条背景
        bg_pen = QPen(QColor(200, 200, 200, 100))
        bg_pen.setWidth(progress_height)
        painter.setPen(bg_pen)
        painter.drawLine(0, rect.height() - progress_height // 2, 
                        rect.width(), rect.height() - progress_height // 2)
        
        # 绘制进度条
        if progress_width > 0:
            progress_pen = QPen(color)
            progress_pen.setWidth(progress_height)
            painter.setPen(progress_pen)
            painter.drawLine(0, rect.height() - progress_height // 2, 
                           progress_width, rect.height() - progress_height // 2)
    
    def _getProgressColor(self) -> QColor:
        """根据InfoLevel获取进度条颜色"""
        color_map = {
            InfoLevel.INFOAMTION: QColor(0, 159, 170),
            InfoLevel.SUCCESS: QColor(15, 123, 15),
            InfoLevel.WARNING: QColor(157, 93, 0),
            InfoLevel.ERROR: QColor(196, 43, 28),
        }
        return color_map.get(self._level, QColor(0, 159, 170))
