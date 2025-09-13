# coding: utf-8
import os
import sys
import winreg
from pathlib import Path
from .logging_config import get_logger

logger = get_logger(__name__)


class StartupManager:
    """开机启动管理器"""
    
    def __init__(self):
        self.app_name = "XiaoZhiAI"
        self.registry_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        
    def is_startup_enabled(self) -> bool:
        """检查是否已启用开机启动"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_key, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, self.app_name)
                logger.info(f"找到开机启动项: {self.app_name} = {value}")
                return True
        except FileNotFoundError:
            logger.info(f"未找到开机启动项: {self.app_name}")
            return False
        except Exception as e:
            logger.error(f"检查开机启动状态失败: {e}")
            return False
    
    def enable_startup(self) -> bool:
        """启用开机启动"""
        try:
            # 获取项目根目录
            project_root = Path(__file__).parent.parent.parent
            xiaozhi_exe = project_root / 'Xiaozhi-ai.exe'
            
            logger.info(f"项目根目录: {project_root}")
            logger.info(f"查找exe文件: {xiaozhi_exe}")
            logger.info(f"exe文件是否存在: {xiaozhi_exe.exists()}")
            
            # 检查根目录下是否存在Xiaozhi-ai.exe
            if xiaozhi_exe.exists():
                exe_path = str(xiaozhi_exe.absolute())
                logger.info(f"使用根目录exe文件: {exe_path}")
            else:
                # 如果根目录没有，使用当前执行文件
                exe_path = sys.executable
                logger.info(f"使用当前执行文件: {exe_path}")
            
            # 添加到注册表 - 使用CreateKeyEx确保键存在
            logger.info(f"准备添加到注册表: {self.registry_key}")
            logger.info(f"应用名称: {self.app_name}")
            logger.info(f"exe路径: {exe_path}")
            
            # 创建或打开注册表键
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, self.registry_key, 0, winreg.KEY_WRITE)
            try:
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, exe_path)
                logger.info(f"已启用开机启动: {exe_path}")
                return True
            finally:
                winreg.CloseKey(key)
            
        except Exception as e:
            logger.error(f"启用开机启动失败: {e}", exc_info=True)
            return False
    
    def disable_startup(self) -> bool:
        """禁用开机启动"""
        try:
            # 尝试打开注册表键
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_key, 0, winreg.KEY_WRITE)
            try:
                winreg.DeleteValue(key, self.app_name)
                logger.info("已禁用开机启动")
                return True
            finally:
                winreg.CloseKey(key)
            
        except FileNotFoundError:
            # 注册表项不存在，说明本来就没有启用
            logger.info("开机启动项不存在，无需禁用")
            return True
        except Exception as e:
            logger.error(f"禁用开机启动失败: {e}")
            return False
    
    def toggle_startup(self, enable: bool) -> bool:
        """切换开机启动状态"""
        if enable:
            return self.enable_startup()
        else:
            return self.disable_startup()


# 全局实例
_startup_manager = None


def get_startup_manager() -> StartupManager:
    """获取开机启动管理器实例"""
    global _startup_manager
    if _startup_manager is None:
        _startup_manager = StartupManager()
    return _startup_manager