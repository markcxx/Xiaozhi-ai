# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from qfluentwidgets import (
    ScrollArea, CardWidget, TitleLabel, BodyLabel, CaptionLabel,
    FluentIcon as FIF
)
from ..components.service_card import ServiceCard
from ..components.service_detail_dialog import ServiceDetailDialog
from ..common.style_sheet import setStyleSheet, getStyleSheet, setCustomStyleSheetFromFile
from ..common.signal_bus import signalBus
from ..common import resource_rc


class MCPInterface(ScrollArea):
    """MCP服务界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        # 创建MCP介绍卡片
        self.introCard = MCPIntroCard(self.scrollWidget)
        
        # 创建服务卡片列表
        self.serviceCards = []
        self._createServiceCards()
        
        self._initWidget()
        self._initLayout()
        self._connectSignals()
    
    def _initWidget(self):
        """初始化组件"""
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 20, 0, 20)
        self.setWidget(self.scrollWidget)
        self.enableTransparentBackground()
        self.setWidgetResizable(True)
        self.setObjectName('mcpInterface')
        
        # 设置样式
        self.scrollWidget.setObjectName('scrollWidget')
        self.setQss()
        
        # 连接主题变化信号
        signalBus.themeChangedSig.connect(self._refreshInterface)
    
    def _initLayout(self):
        """初始化布局"""
        
        self.vBoxLayout.setContentsMargins(36, 10, 36, 0)
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.addWidget(self.introCard)
        
        # 添加服务卡片
        for card in self.serviceCards:
            self.vBoxLayout.addWidget(card)
        
        # 添加底部间距
        self.vBoxLayout.addStretch()
    
    def _createServiceCards(self):
        """创建服务卡片"""
        services = [
            {
                "title": "天气查询",
                "description": "获取实时天气信息和预报，支持全球主要城市的天气数据查询",
                "icon": ":images/mcp_interface/weather.svg",
                "status": "官方",
                "color_scheme": "blue",
                "icon_color": "rgb(37, 99, 235)"
            },
            {
                "title": "音乐播放",
                "description": "智能音乐推荐和播放控制，支持多种音乐平台集成",
                "icon": ":images/mcp_interface/Music.svg",
                "status": "Mark",
                "color_scheme": "purple",
                "icon_color": "rgb(124, 58, 237)"
            },
            {
                "title": "系统服务",
                "description": "系统信息查询和基础操作，包括文件管理和系统监控",
                "icon": ":images/mcp_interface/system.svg",
                "status": "官方",
                "color_scheme": "green",
                "icon_color": "rgb(22, 163, 74)"
            },
            {
                "title": "笑话服务",
                "description": "提供各种类型的笑话和幽默内容，让对话更加轻松有趣",
                "icon": ":images/mcp_interface/laugh.svg",
                "status": "官方",
                "color_scheme": "orange",
                "icon_color": "rgb(234, 88, 12)"
            }
        ]
        
        for service in services:
            card = ServiceCard()
            card.setIcon(service["icon"])
            card.setTitle(service["title"])
            card.setDescription(service["description"])
            card.setStatus(service["status"])
            card.setButtonText("查看")
            card.setCardColorScheme(service["color_scheme"])
            card.setIconColors(service["icon_color"])
            
            # 应用ServiceCard样式
            qss_content = getStyleSheet('service_card')
            card.setStyleSheet(qss_content)
            
            # 为CaptionLabel组件应用自定义样式
            caption_labels = card.findChildren(CaptionLabel)
            for label in caption_labels:
                if label.objectName() == "descriptionLabel":
                    setCustomStyleSheetFromFile(label, 'service_card')
            
            # 连接按钮点击事件
            card.buttonClicked.connect(lambda t=service["title"]: self._onServiceCardClicked(t))
            
            self.serviceCards.append(card)
    
    def _connectSignals(self):
        """连接信号"""
        pass
    
    def _refreshInterface(self):
        """刷新界面样式"""
        self.setQss()
        self.introCard.setQss()
    
    def setQss(self):
        """设置样式表"""
        setStyleSheet(self, 'mcp_interface')
        
        # 为CaptionLabel组件应用自定义样式
        caption_labels = self.findChildren(CaptionLabel)
        for label in caption_labels:
            if label.objectName() == "featureDesc":
                setCustomStyleSheetFromFile(label, 'mcp_interface')
    
    def _onServiceCardClicked(self, title: str):
        """服务卡片点击事件"""
        # 查找对应的服务信息
        service_info = self._getServiceInfo(title)
        if service_info:
            dialog = ServiceDetailDialog(service_info, self.window())
            dialog.exec_()
    
    def _getServiceInfo(self, title: str):
        """获取服务详细信息"""
        services_detail = {
            "天气查询": {
                "title": "天气查询",
                "description": "获取实时天气信息和预报，支持全球主要城市的天气数据查询",
                "usage": "直接询问任何城市的天气情况，如'北京今天天气如何？'或'明天上海会下雨吗？'",
                "features": ["实时天气数据", "7天天气预报", "空气质量指数", "紫外线指数", "降水概率"],
                "examples": ["今天北京天气怎么样？", "明天适合出门吗？", "这周末会下雨吗？"]
            },
            "音乐播放": {
                "title": "音乐播放",
                "description": "智能音乐推荐和播放控制，支持多种音乐平台集成",
                "usage": "告诉我你想听什么类型的音乐，或者让我为你推荐适合当前心情的歌曲",
                "features": ["智能推荐", "情绪识别", "多平台支持", "歌词显示", "播放列表管理"],
                "examples": ["我想听邓紫棋的唯一", "推荐适合工作的背景音乐", "我想听周杰伦的晴天"]
            },
            "系统服务": {
                "title": "系统服务",
                "description": "系统信息查询和基础操作，包括文件管理和系统监控",
                "usage": "查询系统状态、管理文件或监控系统性能",
                "features": ["系统监控", "文件管理", "进程管理", "性能分析", "日志查看"],
                "examples": ["帮我调高音量", "帮我打开谷歌浏览器和微信", "监控CPU使用率"]
            },
            "笑话服务": {
                "title": "笑话服务",
                "description": "提供各种类型的笑话和幽默内容，让对话更加轻松有趣",
                "usage": "请求笑话或幽默内容来放松心情",
                "features": ["冷笑话", "脑筋急转弯", "幽默故事", "每日笑话"],
                "examples": ["讲个笑话", "来个脑筋急转弯", "分享个搞笑故事"]
            }
        }
        return services_detail.get(title)


class MCPIntroCard(CardWidget):
    """MCP介绍卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mcpIntroCard")
        
        # 主布局
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(32, 24, 32, 24)
        self.mainLayout.setSpacing(16)
        
        # 标题区域
        self.titleLayout = QHBoxLayout()
        self.titleLayout.setSpacing(12)
        
        # 标题
        self.titleLabel = TitleLabel("MCP 服务生态")
        self.titleLabel.setObjectName("introTitle")
        
        # 副标题
        self.subtitleLabel = BodyLabel(
            "MCP (Model Context Protocol) 是一个开放标准，让AI助手能够安全地连接和使用各种外部工具和服务。"
        )
        self.subtitleLabel.setObjectName("introSubtitle")
        self.subtitleLabel.setWordWrap(True)
        
        # 特性区域
        self.featuresLayout = QHBoxLayout()
        self.featuresLayout.setSpacing(20)
        
        # 创建特性卡片
        self.feature1 = self._createFeatureCard("🔌 即插即用", "无需复杂配置，服务自动集成到对话中")
        self.feature2 = self._createFeatureCard("🛡️ 安全可靠", "严格的权限控制和数据保护机制")
        self.feature3 = self._createFeatureCard("🚀 持续扩展", "不断添加新服务，功能越来越强大")
        
        self.featuresLayout.addWidget(self.feature1)
        self.featuresLayout.addWidget(self.feature2)
        self.featuresLayout.addWidget(self.feature3)
        
        # 添加到主布局
        self.titleLayout.addWidget(self.titleLabel)
        self.titleLayout.addStretch()
        
        self.mainLayout.addLayout(self.titleLayout)
        self.mainLayout.addWidget(self.subtitleLabel)
        self.mainLayout.addLayout(self.featuresLayout)
        
        # 设置样式
        self.setQss()
    
    def _createFeatureCard(self, title: str, description: str) -> QWidget:
        """创建特性卡片"""
        card = QWidget()
        card.setObjectName("featureCard")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        titleLabel = BodyLabel(title)
        titleLabel.setObjectName("featureTitle")
        
        descLabel = CaptionLabel(description)
        descLabel.setObjectName("featureDesc")
        descLabel.setWordWrap(True)
        
        layout.addWidget(titleLabel)
        layout.addWidget(descLabel)
        
        return card
    
    def setQss(self):
        """设置样式表"""
        setStyleSheet(self, 'mcp_interface')