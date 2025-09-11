# coding:utf-8
import asyncio
import sys
from pathlib import Path

# 设置工作目录为脚本所在目录
import os
from inspect import getsourcefile
os.chdir(Path(getsourcefile(lambda: 0)).resolve().parent)

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
import qasync

from app.common.application import Application
from app.common.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


async def handle_activation() -> bool:
    """处理设备激活流程，依赖已有事件循环.

    Returns:
        bool: 激活是否成功
    """
    try:
        from app.common.system_initializer import SystemInitializer

        logger.info("开始设备激活流程检查...")

        system_initializer = SystemInitializer()
        # 统一使用 SystemInitializer 内的激活处理，GUI模式
        result = await system_initializer.handle_activation_process(mode="gui")
        success = bool(result.get("is_activated", False))
        logger.info(f"激活流程完成，结果: {success}")
        return success
    except Exception as e:
        logger.error(f"激活流程异常: {e}", exc_info=True)
        return False


async def start_app() -> int:
    """
    启动应用的统一入口（在已有事件循环中执行）.
    """

    # 处理激活流程
    activation_success = await handle_activation()
    if not activation_success:
        logger.error("设备激活失败，程序退出")
        return 1

    # 创建并启动应用程序
    app = Application.get_instance()
    return await app.run(protocol="websocket")


def main():
    """主函数"""
    exit_code = 1
    loop = None
    qt_app = None
    
    try:
        setup_logging()
        
        # 抑制nanobind警告
        import warnings
        warnings.filterwarnings("ignore", category=UserWarning, module="nanobind")
        
        # 启用高DPI缩放
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

        # 创建QApplication实例
        qt_app = QApplication.instance() or QApplication(sys.argv)

        # 创建qasync事件循环
        loop = qasync.QEventLoop(qt_app)
        asyncio.set_event_loop(loop)

        # 运行应用
        with loop:
            try:
                exit_code = loop.run_until_complete(start_app())
            except RuntimeError as e:
                if "Event loop stopped" in str(e):
                    exit_code = 0
                else:
                    raise

    except KeyboardInterrupt:
        exit_code = 0
    except Exception as e:
        exit_code = 1
    finally:
        # 优雅关闭
        try:
            if loop and not loop.is_closed():
                # 取消所有待处理的任务
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                
                # 等待任务取消完成
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
                loop.close()
        except Exception:
            pass
        
        import gc
        gc.collect()
        
        sys.exit(exit_code)


if __name__ == "__main__":
    main()