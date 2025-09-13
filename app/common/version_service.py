# coding: utf-8
import re
import requests
import os
from PyQt5.QtCore import QThread, pyqtSignal, QVersionNumber
from .config import VERSION
from .logging_config import get_logger
from .path_manager import get_user_downloads_dir

logger = get_logger(__name__)


class VersionCheckThread(QThread):
    """版本检测线程"""
    
    # 信号定义
    versionChecked = pyqtSignal(str, bool, str)  # (latest_version, has_new_version, download_url)
    checkFailed = pyqtSignal(str)  # error_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentVersion = VERSION
        self.versionPattern = re.compile(r'v(\d+)\.(\d+)\.(\d+)')
        
    def run(self):
        """执行版本检测"""
        try:
            latest_version, download_url = self._getLatestVersion()
            has_new = self._hasNewVersion(latest_version)
            self.versionChecked.emit(latest_version, has_new, download_url)
        except Exception as e:
            logger.error(f"版本检测失败: {e}")
            self.checkFailed.emit(str(e))
    
    def _getLatestVersion(self):
        """获取最新版本和下载链接"""
        url = "https://api.github.com/repos/markcxx/Xiaozhi-ai/releases/latest"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        data = response.json()
        
        # 解析版本号
        version = data['tag_name']  # type: str
        match = self.versionPattern.search(version)
        if not match:
            return VERSION, ""
        
        version_str = version[1:] if version.startswith('v') else version
        
        # 解析下载链接
        download_url = self._parseDownloadUrl(data.get('body', ''))
        
        return version_str, download_url
    
    def _parseDownloadUrl(self, body: str) -> str:
        """从发布说明中解析国内下载链接"""
        # 使用正则表达式匹配国内下载链接
        pattern = r'国内下载链接[：:](\s*)([^\s\r\n]+)'
        match = re.search(pattern, body)
        if match:
            return match.group(2).strip()
        return ""
    
    def _hasNewVersion(self, latest_version: str) -> bool:
        """检查是否有新版本"""
        try:
            latest = QVersionNumber.fromString(latest_version)
            current = QVersionNumber.fromString(self.currentVersion)
            return latest > current
        except Exception as e:
            logger.warning(f"版本比较失败: {e}")
            return False


class DownloadThread(QThread):
    """文件下载线程"""
    
    # 信号定义
    progressChanged = pyqtSignal(int)  # 下载进度 (0-100)
    downloadCompleted = pyqtSignal(str)  # 下载完成，返回文件路径
    downloadFailed = pyqtSignal(str)  # 下载失败，返回错误信息
    
    def __init__(self, url: str, filename: str, parent=None):
        super().__init__(parent)
        self.url = url
        self.filename = filename
        self.download_dir = get_user_downloads_dir()
        self.file_path = self.download_dir / filename
        
    def run(self):
        """执行下载"""
        try:
            # 确保下载目录存在
            self.download_dir.mkdir(parents=True, exist_ok=True)
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            }
            
            response = requests.get(self.url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(self.file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 计算并发送进度
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.progressChanged.emit(progress)
            
            self.downloadCompleted.emit(str(self.file_path))
            
        except Exception as e:
            logger.error(f"下载失败: {e}")
            self.downloadFailed.emit(str(e))


class VersionService:
    """版本服务"""
    
    def __init__(self):
        self.currentVersion = VERSION
        self._checkThread = None
        
    def checkVersion(self, callback=None, error_callback=None):
        """检查版本更新
        
        Args:
            callback: 检测完成回调函数 (latest_version, has_new_version)
            error_callback: 检测失败回调函数 (error_message)
        """
        if self._checkThread and self._checkThread.isRunning():
            logger.warning("版本检测已在进行中")
            return
            
        self._checkThread = VersionCheckThread()
        
        if callback:
            self._checkThread.versionChecked.connect(callback)
        if error_callback:
            self._checkThread.checkFailed.connect(error_callback)
            
        self._checkThread.start()
        
    def getCurrentVersion(self) -> str:
        """获取当前版本"""
        return self.currentVersion


# 全局版本服务实例
_version_service = None


def get_version_service() -> VersionService:
    """获取版本服务单例"""
    global _version_service
    if _version_service is None:
        _version_service = VersionService()
    return _version_service