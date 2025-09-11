"""基于QMediaPlayer的音乐播放器实现.

使用PyQt5的QMediaPlayer替换pygame进行音频播放。
"""

import asyncio
import shutil
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from PyQt5.QtCore import QObject, QUrl, pyqtSignal, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from app.common.constants import AudioConfig
from app.common.logging_config import get_logger
from app.common.resource_finder import get_user_cache_dir

# 尝试导入音乐元数据库
try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError

    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

logger = get_logger(__name__)


class MusicMetadata:
    """音乐元数据类."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.filename = file_path.name
        self.file_id = file_path.stem  # 文件名去掉扩展名，即歌曲ID
        self.file_size = file_path.stat().st_size

        # 从文件提取的元数据
        self.title = None
        self.artist = None
        self.album = None
        self.duration = None  # 秒数

    def extract_metadata(self) -> bool:
        """提取音乐元数据."""
        if not MUTAGEN_AVAILABLE:
            return False

        try:
            audio_file = MutagenFile(str(self.file_path))
            if audio_file is None:
                return False

            # 提取基本信息
            if hasattr(audio_file, "info") and audio_file.info:
                self.duration = getattr(audio_file.info, "length", None)

            # 提取标签信息
            if hasattr(audio_file, "tags") and audio_file.tags:
                tags = audio_file.tags
                self.title = self._get_tag_value(tags, ["TIT2", "TITLE", "\xa9nam"])
                self.artist = self._get_tag_value(tags, ["TPE1", "ARTIST", "\xa9ART"])
                self.album = self._get_tag_value(tags, ["TALB", "ALBUM", "\xa9alb"])

            return True

        except Exception as e:
            logger.debug(f"提取元数据失败: {e}")
            return False

    def _get_tag_value(self, tags, keys: List[str]) -> Optional[str]:
        """从标签中获取值."""
        for key in keys:
            if key in tags:
                value = tags[key]
                if isinstance(value, list) and value:
                    return str(value[0])
                elif isinstance(value, str):
                    return value
        return None


class QtMusicPlayer(QObject):
    """基于QMediaPlayer的音乐播放器."""

    # 信号定义
    positionChanged = pyqtSignal(int)
    durationChanged = pyqtSignal(int)
    stateChanged = pyqtSignal(QMediaPlayer.State)
    mediaStatusChanged = pyqtSignal(QMediaPlayer.MediaStatus)

    def __init__(self):
        super().__init__()
        
        # 初始化QMediaPlayer
        self.player = QMediaPlayer()
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.stateChanged.connect(self._on_state_changed)
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        
        # 核心播放状态
        self.current_song = ""
        self.current_url = ""
        self.song_id = ""
        self.total_duration = 0
        self.is_playing = False
        self.paused = False
        self.current_position = 0
        self.start_play_time = 0

        # 歌词相关
        self.lyrics = []  # 歌词列表，格式为 [(时间, 文本), ...]
        self.current_lyric_index = -1  # 当前歌词索引

        # 缓存目录设置 - 使用用户缓存目录确保可写
        user_cache_dir = get_user_cache_dir()
        self.cache_dir = user_cache_dir / "music"
        self.temp_cache_dir = self.cache_dir / "temp"
        self._init_cache_dirs()

        # API配置
        self.config = {
            "SEARCH_URL": "http://search.kuwo.cn/r.s",
            "PLAY_URL": "http://api.xiaodaokg.com/kuwo.php",
            "LYRIC_URL": "https://api.xiaodaokg.com/kw/kwlyric.php",
            "HEADERS": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36"
                ),
                "Accept": "*/*",
                "Connection": "keep-alive",
            },
        }

        # 清理临时缓存
        self._clean_temp_cache()

        # 获取应用程序实例
        self.app = None
        self._initialize_app_reference()

        # 本地歌单缓存
        self._local_playlist = None
        self._last_scan_time = 0

        logger.info("Qt音乐播放器初始化完成")

    def _on_state_changed(self, state):
        """播放状态变化处理."""
        if state == QMediaPlayer.PlayingState:
            self.is_playing = True
            self.paused = False
        elif state == QMediaPlayer.PausedState:
            self.is_playing = True
            self.paused = True
        elif state == QMediaPlayer.StoppedState:
            self.is_playing = False
            self.paused = False

    def _on_media_status_changed(self, status):
        """媒体状态变化处理."""
        if status == QMediaPlayer.EndOfMedia:
            asyncio.create_task(self._handle_playback_finished())

    def _on_duration_changed(self, duration):
        """时长变化处理."""
        self.total_duration = duration / 1000.0  # 转换为秒

    def _on_position_changed(self, position):
        """位置变化处理."""
        self.current_position = position / 1000.0  # 转换为秒

    def _init_cache_dirs(self):
        """初始化缓存目录."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.temp_cache_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"缓存目录初始化完成: {self.cache_dir}")
        except Exception as e:
            logger.error(f"创建缓存目录失败: {e}")

    def _clean_temp_cache(self):
        """清理临时缓存."""
        try:
            if self.temp_cache_dir.exists():
                for file in self.temp_cache_dir.iterdir():
                    if file.is_file():
                        file.unlink()
                logger.debug("临时缓存清理完成")
        except Exception as e:
            logger.warning(f"清理临时缓存失败: {e}")

    def _initialize_app_reference(self):
        """初始化应用程序引用."""
        try:
            from app.common.application import Application
            self.app = Application.get_instance()
        except Exception as e:
            logger.debug(f"获取应用程序实例失败: {e}")

    async def play_url(self, url: str) -> dict:
        """播放指定URL的音频."""
        try:
            # 停止当前播放
            if self.is_playing:
                self.player.stop()

            # 设置媒体内容
            media_content = QMediaContent(QUrl(url))
            self.player.setMedia(media_content)
            
            # 开始播放
            self.player.play()
            
            self.current_url = url
            self.start_play_time = time.time()
            
            logger.info(f"开始播放URL: {url}")
            
            return {
                "status": "success",
                "message": f"开始播放: {url}",
            }
            
        except Exception as e:
            logger.error(f"播放URL失败: {e}")
            return {"status": "error", "message": f"播放失败: {str(e)}"}

    async def play_local_file(self, file_path: str) -> dict:
        """播放本地文件."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {"status": "error", "message": f"文件不存在: {file_path}"}

            # 获取歌曲信息
            metadata = MusicMetadata(file_path)
            if MUTAGEN_AVAILABLE:
                metadata.extract_metadata()

            # 停止当前播放
            if self.is_playing:
                self.player.stop()

            # 设置媒体内容
            media_content = QMediaContent(QUrl.fromLocalFile(str(file_path)))
            self.player.setMedia(media_content)
            
            # 开始播放
            self.player.play()

            # 更新播放状态
            title = metadata.title or "未知标题"
            artist = metadata.artist or "未知艺术家"
            self.current_song = f"{title} - {artist}"
            self.song_id = file_path.stem
            self.current_url = str(file_path)
            self.start_play_time = time.time()
            self.current_lyric_index = -1
            self.lyrics = []  # 本地文件暂不支持歌词

            logger.info(f"开始播放本地音乐: {self.current_song}")

            # 更新UI
            if self.app and hasattr(self.app, "set_chat_message"):
                await self._safe_update_ui(f"正在播放本地音乐: {self.current_song}")

            return {
                "status": "success",
                "message": f"正在播放本地音乐: {self.current_song}",
            }

        except Exception as e:
            logger.error(f"播放本地音乐失败: {e}")
            return {"status": "error", "message": f"播放失败: {str(e)}"}

    async def pause_resume(self) -> dict:
        """播放/暂停切换."""
        try:
            if not self.is_playing and self.current_url:
                # 重新播放
                if self.current_url.startswith("http"):
                    return await self.play_url(self.current_url)
                else:
                    return await self.play_local_file(self.current_url)

            elif self.is_playing and self.paused:
                # 恢复播放
                self.player.play()
                
                # 更新UI
                if self.app and hasattr(self.app, "set_chat_message"):
                    await self._safe_update_ui(f"继续播放: {self.current_song}")

                return {
                    "status": "success",
                    "message": f"继续播放: {self.current_song}",
                }

            elif self.is_playing and not self.paused:
                # 暂停播放
                self.player.pause()
                
                # 更新UI
                if self.app and hasattr(self.app, "set_chat_message"):
                    pos_str = self._format_time(self.current_position)
                    dur_str = self._format_time(self.total_duration)
                    await self._safe_update_ui(
                        f"已暂停: {self.current_song} [{pos_str}/{dur_str}]"
                    )

                return {"status": "success", "message": f"已暂停: {self.current_song}"}

            else:
                return {"status": "error", "message": "没有可播放的歌曲"}

        except Exception as e:
            logger.error(f"播放暂停操作失败: {e}")
            return {"status": "error", "message": f"操作失败: {str(e)}"}

    async def stop(self) -> dict:
        """停止播放."""
        try:
            if not self.is_playing:
                return {"status": "info", "message": "没有正在播放的歌曲"}

            self.player.stop()
            current_song = self.current_song
            self.current_position = 0

            # 更新UI
            if self.app and hasattr(self.app, "set_chat_message"):
                await self._safe_update_ui(f"已停止: {current_song}")

            return {"status": "success", "message": f"已停止: {current_song}"}

        except Exception as e:
            logger.error(f"停止播放失败: {e}")
            return {"status": "error", "message": f"停止失败: {str(e)}"}

    async def seek(self, position: float) -> dict:
        """跳转到指定位置."""
        try:
            if not self.is_playing:
                return {"status": "error", "message": "没有正在播放的歌曲"}

            position = max(0, min(position, self.total_duration))
            
            # 设置播放位置（QMediaPlayer使用毫秒）
            self.player.setPosition(int(position * 1000))

            # 更新UI
            pos_str = self._format_time(position)
            dur_str = self._format_time(self.total_duration)
            if self.app and hasattr(self.app, "set_chat_message"):
                await self._safe_update_ui(f"已跳转到: {pos_str}/{dur_str}")

            return {"status": "success", "message": f"已跳转到: {position:.1f}秒"}

        except Exception as e:
            logger.error(f"跳转失败: {e}")
            return {"status": "error", "message": f"跳转失败: {str(e)}"}

    def _format_time(self, seconds: float) -> str:
        """格式化时间显示."""
        if seconds <= 0:
            return "00:00"
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    async def _safe_update_ui(self, message: str):
        """安全更新UI."""
        try:
            if self.app and hasattr(self.app, "set_chat_message"):
                await self.app.set_chat_message(message)
        except Exception as e:
            logger.debug(f"更新UI失败: {e}")

    async def _handle_playback_finished(self):
        """处理播放完成."""
        if self.is_playing:
            logger.info(f"歌曲播放完成: {self.current_song}")
            self.current_position = self.total_duration

            # 更新UI显示完成状态
            if self.app and hasattr(self.app, "set_chat_message"):
                dur_str = self._format_time(self.total_duration)
                await self._safe_update_ui(
                    f"播放完成: {self.current_song} [{dur_str}]"
                )

    # 属性getter方法
    async def get_current_song(self):
        return self.current_song

    async def get_is_playing(self):
        return self.is_playing

    async def get_paused(self):
        return self.paused

    async def get_duration(self):
        return self.total_duration

    async def get_position(self):
        return self.current_position

    async def get_progress(self):
        """获取播放进度百分比."""
        if self.total_duration <= 0:
            return 0
        return round(self.current_position * 100 / self.total_duration, 1)


# 单例实例
_music_player_instance = None


def get_music_player() -> QtMusicPlayer:
    """获取音乐播放器单例."""
    global _music_player_instance
    if _music_player_instance is None:
        _music_player_instance = QtMusicPlayer()
    return _music_player_instance