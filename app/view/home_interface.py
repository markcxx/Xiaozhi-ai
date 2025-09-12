# coding:utf-8
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy

from qfluentwidgets import (
    CardWidget, SubtitleLabel, BodyLabel, PushButton, LineEdit, ScrollArea,
    FluentIcon as FIF, InfoBar, InfoBarPosition
)

from ..common import resource_rc
from ..common.style_sheet import setStyleSheet
from ..common.signal_bus import signalBus


class EmotionCard(CardWidget):
    """表情显示卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(250)
        
        # 创建布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)
        
        # 表情标签
        self.emotionLabel = QLabel(self)
        self.emotionLabel.setAlignment(Qt.AlignCenter)
        self.emotionLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.emotionLabel.setScaledContents(False)
        
        # 添加到布局
        self.vBoxLayout.addWidget(self.emotionLabel)
        
        # 表情管理
        self.currentMovie = None
        self._emotionCache = {}
        
        # 初始化默认表情
        self.updateEmotion("neutral")
    
    def _getEmotionAssetPath(self, emotionName: str) -> str:
        """获取表情资源文件路径"""
        if emotionName in self._emotionCache:
            return self._emotionCache[emotionName]
        
        # 使用Qt资源系统路径
        candidates = [
            f":/images/emojis/{emotionName}.gif",
            f":/images/emojis/{emotionName}.png",
            f":/images/emojis/{emotionName}.jpg"
        ]
        
        # 检查资源是否存在
        from PyQt5.QtCore import QFile
        found = None
        for candidate in candidates:
            if QFile.exists(candidate):
                found = candidate
                break
        
        # 如果没找到，尝试neutral
        if not found:
            neutralCandidates = [
                ":/images/emojis/neutral.gif",
                ":/images/emojis/neutral.png"
            ]
            for candidate in neutralCandidates:
                if QFile.exists(candidate):
                    found = candidate
                    break
        
        self._emotionCache[emotionName] = found
        return found
    
    def updateEmotion(self, emotionName: str):
        """更新表情显示"""
        assetPath = self._getEmotionAssetPath(emotionName)
        
        if not assetPath:
            return
        
        try:
            if assetPath.lower().endswith(".gif"):
                # 停止当前动画
                if self.currentMovie:
                    self.currentMovie.stop()
                
                # 创建新的GIF动画
                movie = QMovie(assetPath)
                if movie.isValid():
                    movie.setCacheMode(QMovie.CacheAll)
                    self.currentMovie = movie
                    self.emotionLabel.setMovie(movie)
                    movie.setSpeed(105)
                    movie.start()
            else:
                # 静态图片
                if self.currentMovie:
                    self.currentMovie.stop()
                    self.currentMovie = None
                
                pixmap = QPixmap(assetPath)
                if not pixmap.isNull():
                    self.emotionLabel.setPixmap(pixmap)
        except Exception as e:
            print(f"设置表情失败: {e}")


class StatusTextCard(CardWidget):
    """状态和文本显示卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setFixedHeight(120)
        
        # 创建布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 15, 20, 15)
        self.vBoxLayout.setSpacing(10)
        
        # 状态标签
        self.statusLabel = SubtitleLabel("状态: 未连接", self)
        self.statusLabel.setAlignment(Qt.AlignCenter)
        
        # 文本显示标签
        self.textLabel = BodyLabel("待命", self)
        self.textLabel.setAlignment(Qt.AlignCenter)
        self.textLabel.setWordWrap(True)
        
        # 添加到布局
        self.vBoxLayout.addWidget(self.statusLabel)
        self.vBoxLayout.addWidget(self.textLabel)
    
    def updateStatus(self, status: str, connected: bool = True):
        """更新状态"""
        self.statusLabel.setText(f"状态: {status}")
    
    def updateText(self, text: str):
        """更新文本"""
        self.textLabel.setText(text)


class VoiceControlCard(CardWidget):
    """语音控制卡片"""
    
    # 信号定义
    manualPressed = pyqtSignal()
    manualReleased = pyqtSignal()
    autoClicked = pyqtSignal()
    abortClicked = pyqtSignal()
    modeClicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setFixedHeight(120)
        
        # 创建布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 15, 20, 15)
        self.vBoxLayout.setSpacing(10)
        
        # 标题
        self.titleLabel = BodyLabel("语音控制", self)
        # self.titleLabel.setStyleSheet("color: #888888;")
        
        # 按钮布局
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(10)
        
        # 按住说话按钮
        self.manualBtn = PushButton("按住后说话", self, FIF.MICROPHONE)
        self.manualBtn.pressed.connect(self.manualPressed.emit)
        self.manualBtn.released.connect(self.manualReleased.emit)
        
        # 打断对话按钮
        self.abortBtn = PushButton("打断对话", self, FIF.CANCEL)
        self.abortBtn.clicked.connect(self.abortClicked.emit)
        
        # 开始对话按钮
        self.autoBtn = PushButton("开始对话", self, FIF.PLAY)
        self.autoBtn.clicked.connect(self.autoClicked.emit)
        
        # 模式切换按钮
        self.modeBtn = PushButton("手动对话", self, FIF.SETTING)
        self.modeBtn.clicked.connect(self.modeClicked.emit)
        
        # 添加按钮到布局
        self.buttonLayout.addWidget(self.manualBtn)
        self.buttonLayout.addWidget(self.abortBtn)
        self.buttonLayout.addWidget(self.autoBtn)
        self.buttonLayout.addWidget(self.modeBtn)
        
        # 添加到主布局
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addLayout(self.buttonLayout)
        
        # 初始状态
        self.autoMode = False
        self.autoBtn.hide()
    
    def updateModeButton(self, text: str):
        """更新模式按钮文本"""
        self.modeBtn.setText(text)
    
    def updateAutoButton(self, text: str):
        """更新自动对话按钮文本"""
        self.autoBtn.setText(text)
    
    def switchToAutoMode(self):
        """切换到自动模式"""
        self.autoMode = True
        self.manualBtn.hide()
        self.autoBtn.show()
    
    def switchToManualMode(self):
        """切换到手动模式"""
        self.autoMode = False
        self.autoBtn.hide()
        self.manualBtn.show()


class TextInputCard(CardWidget):
    """文字输入卡片"""
    
    # 信号定义
    textSent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setFixedHeight(100)
        
        # 创建布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 15, 20, 15)
        self.vBoxLayout.setSpacing(10)
        
        # 标题
        self.titleLabel = BodyLabel("文字输入", self)
        # self.titleLabel.setStyleSheet("color: #888888;")
        
        # 输入布局
        self.inputLayout = QHBoxLayout()
        self.inputLayout.setSpacing(10)
        
        # 文本输入框
        self.textInput = LineEdit(self)
        self.textInput.setPlaceholderText("输入文字...")
        self.textInput.returnPressed.connect(self._onSendClicked)
        
        # 发送按钮
        self.sendBtn = PushButton("发送", self, FIF.SEND)
        self.sendBtn.clicked.connect(self._onSendClicked)
        
        # 添加到输入布局
        self.inputLayout.addWidget(self.textInput)
        self.inputLayout.addWidget(self.sendBtn)
        
        # 添加到主布局
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addLayout(self.inputLayout)
    
    def _onSendClicked(self):
        """发送按钮点击事件"""
        text = self.textInput.text().strip()
        if text:
            self.textSent.emit(text)
            self.textInput.clear()


class HomeInterface(ScrollArea):
    """首页界面"""
    
    # 对外信号定义
    manualPressed = pyqtSignal()
    manualReleased = pyqtSignal()
    autoClicked = pyqtSignal()
    abortClicked = pyqtSignal()
    modeClicked = pyqtSignal()
    textSent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homeInterface")
        self.enableTransparentBackground()
        
        # 创建滚动区域的内容widget
        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName("scrollWidget")
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        
        # 创建主布局
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        self.vBoxLayout.setContentsMargins(10, 10, 10, 0)
        self.vBoxLayout.setSpacing(10)
        
        # 创建卡片
        self.emotionCard = EmotionCard(self)
        self.statusTextCard = StatusTextCard(self)
        self.voiceCard = VoiceControlCard(self)
        self.textCard = TextInputCard(self)
        
        # 添加到布局
        self.vBoxLayout.addWidget(self.emotionCard)
        self.vBoxLayout.addWidget(self.statusTextCard)
        self.vBoxLayout.addWidget(self.voiceCard)
        self.vBoxLayout.addWidget(self.textCard)
        self.vBoxLayout.addStretch()
        
        # 设置样式
        self.setQss()
        
        # 连接信号
        self._connectSignals()
        
        # 初始化状态
        self.statusTextCard.updateStatus("未连接", False)
        self.emotionCard.updateEmotion("neutral")
        self.statusTextCard.updateText("待命")
    
    def setQss(self):
        """设置样式表"""
        setStyleSheet(self, 'home_interface')
    
    def _connectSignals(self):
        """连接信号"""
        # 语音控制卡片信号 - 直接转发到对外信号
        self.voiceCard.manualPressed.connect(self.manualPressed.emit)
        self.voiceCard.manualReleased.connect(self.manualReleased.emit)
        self.voiceCard.autoClicked.connect(self.autoClicked.emit)
        self.voiceCard.abortClicked.connect(self.abortClicked.emit)
        self.voiceCard.modeClicked.connect(self.modeClicked.emit)
        
        # 文本输入卡片信号 - 直接转发到对外信号
        self.textCard.textSent.connect(self.textSent.emit)
        
        # 内部信号处理
        self.voiceCard.manualPressed.connect(self._onManualPressed)
        self.voiceCard.manualReleased.connect(self._onManualReleased)
        self.voiceCard.autoClicked.connect(self._onAutoClicked)
        self.voiceCard.abortClicked.connect(self._onAbortClicked)
        self.voiceCard.modeClicked.connect(self._onModeClicked)
        
        # 主题变化信号
        signalBus.themeChangedSig.connect(self._refreshInterface)
    
    def _refreshInterface(self):
        """刷新界面样式"""
        self.setQss()
    
    def _onManualPressed(self):
        """手动按钮按下"""
        self.voiceCard.manualBtn.setText("正在录音...")
    
    def _onManualReleased(self):
        """手动按钮释放"""
        self.voiceCard.manualBtn.setText("按住后说话")
    
    def _onAutoClicked(self):
        """自动对话按钮点击"""
        InfoBar.info(
            title="自动对话",
            content="自动对话功能暂未实现",
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
    
    def _onAbortClicked(self):
        """打断对话按钮点击"""
        pass
    
    def _onModeClicked(self):
        """模式切换按钮点击"""
        if self.voiceCard.autoMode:
            self.voiceCard.switchToManualMode()
            self.voiceCard.updateModeButton("手动对话")
            InfoBar.info(
                title="模式切换",
                content="已切换到手动对话模式",
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.window()
            )
        else:
            self.voiceCard.switchToAutoMode()
            self.voiceCard.updateModeButton("自动对话")
            InfoBar.info(
                title="模式切换",
                content="已切换到自动对话模式",
                position=InfoBarPosition.TOP,
                duration=1500,
                parent=self.window()
            )
    
    # 公共接口方法
    def updateStatus(self, status: str, connected: bool = True):
        """更新状态"""
        self.statusTextCard.updateStatus(status, connected)
    
    def updateEmotion(self, emotion: str):
        """更新表情"""
        self.emotionCard.updateEmotion(emotion)
    
    def updateText(self, text: str):
        """更新显示文本"""
        self.statusTextCard.updateText(text)