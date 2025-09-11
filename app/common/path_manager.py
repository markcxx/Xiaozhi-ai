"""路径管理器 - 简化版本

提供统一的路径管理功能，专为XiaoZhi AI项目设计。
"""

import os
import sys
from pathlib import Path
from typing import Optional, Union

from app.common.logging_config import get_logger

logger = get_logger(__name__)

# 应用名称
APP_NAME = "XiaoZhi AI"


class PathManager:
    """路径管理器 - 简化版本"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化路径管理器"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            logger.debug(f"路径管理器初始化，应用名: {APP_NAME}")

    def get_project_root(self) -> Path:
        """获取项目根目录
        
        Returns:
            项目根目录路径
        """
        return Path(__file__).parent.parent.parent

    def get_app_resource_dir(self) -> Path:
        """获取应用资源目录
        
        Returns:
            app/resource目录路径
        """
        return self.get_project_root() / "app" / "resource"

    def get_config_dir(self) -> Path:
        """获取用户配置目录
        
        Returns:
            用户配置目录路径 (AppData/Roaming/XiaoZhi AI)
        """
        if sys.platform == "win32":
            config_dir = Path(os.environ['APPDATA']) / APP_NAME
        elif sys.platform == "darwin":
            config_dir = Path.home() / "Library" / "Application Support" / APP_NAME
        else:
            config_dir = Path.home() / ".config" / APP_NAME
        
        return config_dir

    def get_cache_dir(self) -> Path:
        """获取用户缓存目录
        
        Returns:
            用户缓存目录路径 (AppData/Local/XiaoZhi AI)
        """
        if sys.platform == "win32":
            cache_dir = Path(os.environ['LOCALAPPDATA']) / APP_NAME
        elif sys.platform == "darwin":
            cache_dir = Path.home() / "Library" / "Caches" / APP_NAME
        else:
            cache_dir = Path.home() / ".cache" / APP_NAME
        
        return cache_dir

    def get_activation_config_dir(self) -> Path:
        """获取激活配置目录
        
        Returns:
            激活配置目录路径 (用户配置目录/config)
        """
        return self.get_config_dir() / "config"

    def get_user_config_file(self) -> Path:
        """获取用户配置文件路径
        
        Returns:
            用户配置文件路径 (用户配置目录/config.json)
        """
        return self.get_config_dir() / "config.json"

    def get_activation_config_file(self) -> Path:
        """获取激活配置文件路径
        
        Returns:
            激活配置文件路径 (激活配置目录/config.json)
        """
        return self.get_activation_config_dir() / "config.json"

    def get_efuse_file(self) -> Path:
        """获取efuse文件路径
        
        Returns:
            efuse文件路径 (激活配置目录/efuse.json)
        """
        return self.get_activation_config_dir() / "efuse.json"

    def find_resource(self, resource_path: Union[str, Path]) -> Optional[Path]:
        """在资源目录中查找资源文件
        
        Args:
            resource_path: 相对于app/resource的资源路径
            
        Returns:
            找到的资源绝对路径，未找到返回None
        """
        resource_path = Path(resource_path)
        full_path = self.get_app_resource_dir() / resource_path
        
        if full_path.exists():
            logger.debug(f"✓ 找到资源: {full_path}")
            return full_path
        
        logger.warning(f"✗ 未找到资源: {resource_path}")
        return None

    def find_file(self, file_path: Union[str, Path]) -> Optional[Path]:
        """查找资源文件
        
        Args:
            file_path: 相对于app/resource的文件路径
            
        Returns:
            找到的文件绝对路径，未找到返回None
        """
        found_path = self.find_resource(file_path)
        if found_path and found_path.is_file():
            return found_path
        return None

    def find_directory(self, dir_path: Union[str, Path]) -> Optional[Path]:
        """查找资源目录
        
        Args:
            dir_path: 相对于app/resource的目录路径
            
        Returns:
            找到的目录绝对路径，未找到返回None
        """
        found_path = self.find_resource(dir_path)
        if found_path and found_path.is_dir():
            return found_path
        return None

    def ensure_dir(self, dir_path: Path) -> bool:
        """确保目录存在
        
        Args:
            dir_path: 目录路径
            
        Returns:
            是否成功创建或目录已存在
        """
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"创建目录失败 {dir_path}: {e}")
            return False

    def get_app_name(self) -> str:
        """获取应用名称
        
        Returns:
            应用名称
        """
        return APP_NAME


# 全局单例实例
path_manager = PathManager()


# 便捷函数
def find_file(file_path: Union[str, Path]) -> Optional[Path]:
    """查找资源文件的便捷函数"""
    return path_manager.find_file(file_path)


def find_directory(dir_path: Union[str, Path]) -> Optional[Path]:
    """查找资源目录的便捷函数"""
    return path_manager.find_directory(dir_path)


def get_project_root() -> Path:
    """获取项目根目录的便捷函数"""
    return path_manager.get_project_root()


def get_app_resource_dir() -> Path:
    """获取应用资源目录的便捷函数"""
    return path_manager.get_app_resource_dir()


def get_config_dir() -> Path:
    """获取用户配置目录的便捷函数"""
    return path_manager.get_config_dir()


def get_cache_dir() -> Path:
    """获取用户缓存目录的便捷函数"""
    return path_manager.get_cache_dir()


def get_user_data_dir(create: bool = True) -> Path:
    """获取用户数据目录的便捷函数（兼容旧接口）"""
    data_dir = path_manager.get_config_dir()
    if create:
        path_manager.ensure_dir(data_dir)
    return data_dir


def get_user_cache_dir(create: bool = True) -> Path:
    """获取用户缓存目录的便捷函数（兼容旧接口）"""
    cache_dir = path_manager.get_cache_dir()
    if create:
        path_manager.ensure_dir(cache_dir)
    return cache_dir


def get_app_name() -> str:
    """获取应用名称的便捷函数"""
    return path_manager.get_app_name()


def get_app_path() -> Path:
    """获取应用程序基础路径的便捷函数（兼容旧接口）"""
    return path_manager.get_project_root()


# 兼容旧接口的函数
def find_models_dir() -> Optional[Path]:
    """查找models目录的便捷函数（兼容旧接口）"""
    return find_directory("models")


def find_config_dir() -> Optional[Path]:
    """查找config目录的便捷函数（兼容旧接口）"""
    return find_directory("config")


def find_assets_dir() -> Optional[Path]:
    """查找assets目录的便捷函数（兼容旧接口）"""
    return find_directory("assets")


def find_libs_dir(system: str = None, arch: str = None) -> Optional[Path]:
    """查找libs目录的便捷函数（兼容旧接口）"""
    # 直接在项目根目录查找libs目录
    project_root = path_manager.get_project_root()
    libs_dir = project_root / "libs"
    
    if not libs_dir.exists():
        logger.warning(f"✗ 未找到libs目录: {libs_dir}")
        return None
    
    # 如果指定了系统和架构，查找具体的子目录
    if system and arch:
        specific_dir = libs_dir / system / arch
        if specific_dir.is_dir():
            return specific_dir
    elif system:
        system_dir = libs_dir / system
        if system_dir.is_dir():
            return system_dir
    
    return libs_dir