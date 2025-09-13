# coding: utf-8
import os
import sys
import subprocess
import winreg
from pathlib import Path
from .logging_config import get_logger

logger = get_logger(__name__)


class StartupManager:
    """开机启动管理器"""
    
    def __init__(self):
        self.app_name = "XiaoZhiAI"
        self.startup_folder = Path(os.getenv('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        self.shortcut_name = "XiaoZhiAI.lnk"
        
    def is_startup_enabled(self) -> bool:
        """检查是否已启用开机启动"""
        try:
            shortcut_path = self.startup_folder / self.shortcut_name
            exists = shortcut_path.exists()
            if exists:
                logger.info(f"找到开机启动快捷方式: {shortcut_path}")
            else:
                logger.info(f"未找到开机启动快捷方式: {shortcut_path}")
            return exists
        except Exception as e:
            logger.error(f"检查开机启动状态失败: {e}")
            return False
    
    def enable_startup(self) -> bool:
        """启用开机启动"""
        try:
            # 获取项目根目录的exe文件
            project_root = Path(__file__).parent.parent.parent
            exe_path = project_root / 'Xiaozhi-ai.exe'
            
            if not exe_path.exists():
                logger.error(f"exe文件不存在: {exe_path}")
                return False
            
            # 确保启动文件夹存在
            self.startup_folder.mkdir(parents=True, exist_ok=True)
            
            # 创建快捷方式
            shortcut_path = self.startup_folder / self.shortcut_name
            logger.info(f"创建快捷方式: {shortcut_path} -> {exe_path}")
            
            # 使用PowerShell创建快捷方式
            ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{exe_path}"
$Shortcut.Save()
'''
            
            result = subprocess.run(
                ["powershell", "-WindowStyle", "Hidden", "-Command", ps_script],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                logger.info(f"已启用开机启动: {shortcut_path}")
                return True
            else:
                logger.error(f"创建快捷方式失败: {result.stderr}")
                return False
            
        except Exception as e:
            logger.error(f"启用开机启动失败: {e}", exc_info=True)
            return False
    
    def disable_startup(self) -> bool:
        """禁用开机启动"""
        try:
            shortcut_path = self.startup_folder / self.shortcut_name
            
            if shortcut_path.exists():
                shortcut_path.unlink()
                logger.info(f"已删除开机启动快捷方式: {shortcut_path}")
                return True
            else:
                logger.info("开机启动快捷方式不存在，无需禁用")
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