# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from qfluentwidgets import (
    ScrollArea, CardWidget, TitleLabel, BodyLabel, CaptionLabel,
    MessageBox, InfoBadge, ElevatedCardWidget
)
from qfluentwidgets.common.font import setFont
from ..common.style_sheet import getStyleSheet, setCustomStyleSheetFromFile
from ..common.signal_bus import signalBus


class ServiceDetailDialog(MessageBox):
    """服务详情弹窗"""
    
    def __init__(self, service_info: dict, parent=None):
        # 创建内容字符串
        content = f"{service_info['description']}\n\n点击查看详细信息..."
        super().__init__(service_info["title"], content, parent)
        
        # 设置弹窗大小
        self.widget.setFixedSize(650, 550)
        
        # 隐藏取消按钮，只保留确定按钮
        self.cancelButton.hide()
        self.yesButton.setText("关闭")
        
        # 设置内容标签可滚动
        self._setupScrollableContent(service_info)
        
        # 连接主题变化信号 - 在初始化时就连接
        signalBus.themeChangedSig.connect(self._refreshDialogInterface)
    
    def _setupScrollableContent(self, service_info: dict):
        """设置可滚动的详细内容"""
        # 移除原有的内容标签
        self.contentLabel.hide()
        
        # 创建滚动区域 - 使用qfluentwidgets的ScrollArea
        scroll_area = ScrollArea(self.widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.enableTransparentBackground()
        scroll_area.setObjectName("dialogScrollArea")
        
        # 创建内容容器
        content_widget = QWidget()
        content_widget.setObjectName("dialogContentWidget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # 添加服务头部信息卡片
        header_card = self._createHeaderCard(service_info)
        content_layout.addWidget(header_card)
        
        # 添加使用方法卡片
        usage_card = self._createUsageCard(service_info["usage"])
        content_layout.addWidget(usage_card)
        
        # 添加主要功能卡片
        features_card = self._createFeaturesCard(service_info["features"])
        content_layout.addWidget(features_card)
        
        # 添加使用示例卡片
        examples_card = self._createExamplesCard(service_info["examples"])
        content_layout.addWidget(examples_card)
        
        content_layout.addStretch()
        
        # 设置滚动区域
        scroll_area.setWidget(content_widget)
        
        # 将滚动区域添加到弹窗布局中
        self.textLayout.addWidget(scroll_area)
        
        # 应用样式 - 参考MCPInterface的方式
        self._applyDialogStyles()
    
    def _refreshDialogInterface(self):
        """刷新弹窗界面样式"""
        self._applyDialogStyles()
    
    def _createHeaderCard(self, service_info: dict) -> CardWidget:
        """创建服务头部信息卡片"""
        card = CardWidget()
        card.setObjectName("dialogHeaderCard")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # 标题和状态标签
        title_layout = QHBoxLayout()
        title_label = TitleLabel(service_info["title"])
        title_label.setObjectName("dialogTitle")
        setFont(title_label, 20, QFont.Weight.Bold)
        
        # 根据服务类型设置状态标签
        status_text = "官方" if service_info["title"] in ["天气查询", "系统服务"] else "Mark"
        status_badge = InfoBadge.success(status_text) if status_text == "官方" else InfoBadge.custom(status_text, "#8b5cf6", "#f3e8ff")
        status_badge.setObjectName("dialogStatusBadge")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(status_badge)
        title_layout.addStretch()
        
        # 描述
        desc_label = BodyLabel(service_info["description"])
        desc_label.setWordWrap(True)
        desc_label.setObjectName("dialogHeaderDesc")
        setFont(desc_label, 14)
        
        layout.addLayout(title_layout)
        layout.addWidget(desc_label)
        
        return card
    
    def _createUsageCard(self, usage: str) -> CardWidget:
        """创建使用方法卡片"""
        card = CardWidget()
        card.setObjectName("dialogUsageCard")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        
        title = BodyLabel("如何使用")
        title.setObjectName("dialogCardTitle")
        setFont(title, 16, QFont.Weight.DemiBold)
        
        content = CaptionLabel(usage)
        content.setWordWrap(True)
        content.setObjectName("dialogCardContent")
        setFont(content, 13)
        
        layout.addWidget(title)
        layout.addWidget(content)
        
        return card
    
    def _createFeaturesCard(self, features: list) -> CardWidget:
        """创建主要功能卡片"""
        card = CardWidget()
        card.setObjectName("dialogFeaturesCard")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        title = BodyLabel("主要功能")
        title.setObjectName("dialogCardTitle")
        setFont(title, 16, QFont.Weight.DemiBold)
        layout.addWidget(title)
        
        # 创建功能网格
        features_layout = QVBoxLayout()
        features_layout.setSpacing(10)
        
        for i in range(0, len(features), 2):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(16)
            
            # 第一个功能
            feature1_widget = self._createFeatureItem(features[i])
            row_layout.addWidget(feature1_widget)
            
            # 第二个功能（如果存在）
            if i + 1 < len(features):
                feature2_widget = self._createFeatureItem(features[i + 1])
                row_layout.addWidget(feature2_widget)
            else:
                row_layout.addStretch()
            
            features_layout.addLayout(row_layout)
        
        layout.addLayout(features_layout)
        
        return card
    
    def _createFeatureItem(self, feature: str) -> QWidget:
        """创建单个功能项"""
        widget = QWidget()
        widget.setObjectName("dialogFeatureItem")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        # 功能点图标
        icon_label = CaptionLabel("•")
        icon_label.setObjectName("dialogFeatureIcon")
        
        # 功能文字
        text_label = CaptionLabel(feature)
        text_label.setObjectName("dialogFeatureText")
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()
        
        return widget
    
    def _createExamplesCard(self, examples: list) -> CardWidget:
        """创建使用示例卡片"""
        card = CardWidget()
        card.setObjectName("dialogExamplesCard")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        title = BodyLabel("使用示例")
        title.setObjectName("dialogCardTitle")
        setFont(title, 16, QFont.Weight.DemiBold)
        layout.addWidget(title)
        
        # 添加示例
        for example in examples:
            example_widget = self._createExampleItem(example)
            layout.addWidget(example_widget)
        
        return card
    
    def _createExampleItem(self, example: str) -> ElevatedCardWidget:
        """创建单个示例项"""
        widget = ElevatedCardWidget()
        widget.setObjectName("dialogExampleItem")
        
        # 设置边框色属性 - 参考service_card.py的实现
        widget.setProperty("exampleType", "code")
        widget.setStyle(widget.style())
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # 示例文字
        text_label = CaptionLabel(f'\"{ example}\"')
        text_label.setWordWrap(True)
        text_label.setObjectName("dialogExampleText")
        setFont(text_label, 13)
        
        layout.addWidget(text_label)
        
        return widget
    
    def _applyDialogStyles(self):
        """应用弹窗样式"""
        # 应用样式到弹窗主体
        self.widget.setStyleSheet(getStyleSheet('service_detail_dialog'))
        
        # 为ScrollArea使用自定义样式
        scroll_area = self.widget.findChild(ScrollArea, "dialogScrollArea")
        if scroll_area:
            setCustomStyleSheetFromFile(scroll_area, 'service_detail_dialog')
            
            # 应用到内容容器
            content_widget = scroll_area.widget()
            if content_widget:
                content_widget.setStyleSheet(getStyleSheet('service_detail_dialog'))
                
                # 为所有qfluentwidgets组件应用自定义样式
                self._applyCustomStyles(content_widget)
    
    def _applyCustomStyles(self, parent_widget):
        """为qfluentwidgets组件应用自定义样式"""
        # 查找所有CaptionLabel组件并应用自定义样式
        caption_labels = parent_widget.findChildren(CaptionLabel)
        for label in caption_labels:
            if label.objectName() in ["dialogExampleText", "featureDesc", "dialogCardContent"]:
                setCustomStyleSheetFromFile(label, 'service_detail_dialog')
        
        # 查找所有BodyLabel组件并应用自定义样式
        body_labels = parent_widget.findChildren(BodyLabel)
        for label in body_labels:
            if label.objectName() == "dialogHeaderDesc":
                setCustomStyleSheetFromFile(label, 'service_detail_dialog')