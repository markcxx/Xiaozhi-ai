# coding:utf-8
import os
import sys
import tempfile
from enum import Enum
from pathlib import Path

from PyQt5.QtCore import QLocale
from qfluentwidgets import ConfigItem, OptionsConfigItem, OptionsValidator, BoolValidator, FolderValidator, \
    FolderListValidator, QConfig, ConfigSerializer, setTheme, Theme, qconfig

# 应用程序信息
APP_NAME = "XiaoZhi AI"
VERSION = "1.0.1"
AUTHOR = "markcxx"
COPYRIGHT = "markcxx"
COPYYEAR = "2025"
APP_URL = "https://github.com/markcxx/Xiaozhi-ai"
FALLBACK_URL = "https://github.com/markcxx/Xiaozhi-ai/issues"
CONTACT_EMAIL = "2811016860@qq.com"
BLOG_URL = "https://www.markqq.com"
DONATE_URL = "https://ifdian.net/a/markingchen"

# 获取应用程序配置目录（跨平台兼容）
if sys.platform == "win32":
    CONFIG_DIR = Path(os.environ['APPDATA']) / APP_NAME
elif sys.platform == "darwin":
    CONFIG_DIR = Path.home() / "Library" / "Application Support" / APP_NAME
else:
    CONFIG_DIR = Path.home() / ".config" / APP_NAME

# 确保配置目录存在
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# 配置文件路径
CONFIG_FILE_PATH = CONFIG_DIR / "config.json"


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = "zh"
    CHINESE_TRADITIONAL = "hk"
    ENGLISH = "en"
    AUTO = "Auto"


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    """ Config of application """

    # dpiScale
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    # language
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)

    # theme configurations are built-in to qfluentwidgets
    
    # startup and system
    startupOnBoot = ConfigItem("System", "StartupOnBoot", False, BoolValidator())
    minimizeToTray = ConfigItem("System", "MinimizeToTray", True, BoolValidator())
    
    # software update
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())
    
    # shortcut keys
    recordShortcut = ConfigItem("Shortcuts", "RecordShortcut", "Space", restart=False)
    interruptShortcut = ConfigItem("Shortcuts", "InterruptShortcut", "Ctrl+I", restart=False)


config = Config()
config.themeMode.value = Theme.AUTO
qconfig.load(str(CONFIG_FILE_PATH), config)


def get_config_dir() -> Path:
    """获取应用程序配置目录路径"""
    return CONFIG_DIR


def get_config_file_path(filename: str) -> Path:
    """获取指定配置文件的完整路径"""
    return CONFIG_DIR / filename