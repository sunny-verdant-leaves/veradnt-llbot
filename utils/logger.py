from pathlib import Path
from datetime import datetime
from typing import Union
from enum import IntEnum, Enum
import threading
import queue


class Level(IntEnum):
    """日志级别"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40


class Preset(Enum):
    """日志级别"""
    Main = "[Main]"
    Mismatch = "Trying to pass parameters of non-specified types into the target."


class Logger:
    """
    异步日期滚动日志
    后台线程消费队列，按日期分文件写入，自动创建目录
    用法：
        log = Logger("./logs")
        log.write("my_app", "启动服务", Level.INFO)
        log.info("my_app", "普通信息")
        log.error("my_app", "错误信息")
    """
    
    def __init__(self, base_path: Union[str, Path] = "./logs", level: Level = Level.INFO):
        """
        初始化日志器，启动后台写入线程
        
        Args:
            base_path: 日志根目录
            level: 最低记录级别，低于此级别的日志被忽略
        """
        self._level = level
        self._queue = queue.Queue()
        self._running = True
        
        self._worker = threading.Thread(
            target=self._loop,
            args=(Path(base_path),),
            daemon=True
        )
        self._worker.start()
    
    def _loop(self, base_path: Path):
        """
        后台线程主循环：从队列取数据，按日期写入文件
        
        Args:
            base_path: 日志根目录（由 __init__ 传入）
        """
        file = None
        current_date = None
        
        while self._running:
            try:
                prog, msg, level = self._queue.get(timeout=1.0)
                if prog is None:
                    break
                
                if level < self._level:
                    continue
                
                now = datetime.now()
                date = now.strftime("%Y-%m-%d")
                
                # 日期变化时切换文件
                if date != current_date:
                    if file:
                        file.close()
                    (base_path / prog).mkdir(parents=True, exist_ok=True)
                    file = open(base_path / prog / f"{date}.log", 'a', encoding='utf-8')
                    current_date = date
                
                line = f"[{now.strftime('%H:%M:%S.%f')[:-3]}] [{level.name}] {msg}\n"
                file.write(line)
                file.flush()
                
            except queue.Empty:
                pass
        
        if file:
            file.close()
    
    def write(self, prog: str, msg: str, level: Level = Level.INFO):
        """
        写入日志（异步，立即返回）
        
        Args:
            prog: 程序名，决定子目录
            msg: 日志内容
            level: 日志级别
        """
        self._queue.put((prog, msg, level))
    
    def debug(self, prog: str, msg: str):
        """DEBUG 级别日志"""
        self.write(prog, msg, Level.DEBUG)
    
    def info(self, prog: str, msg: str):
        """INFO 级别日志"""
        self.write(prog, msg, Level.INFO)
    
    def warning(self, prog: str, msg: str):
        """WARNING 级别日志"""
        self.write(prog, msg, Level.WARNING)
    
    def error(self, prog: str, msg: str):
        """ERROR 级别日志"""
        self.write(prog, msg, Level.ERROR)
    
    def close(self):
        """关闭日志器，等待后台线程结束"""
        self._running = False
        self._queue.put((None, None, Level.INFO))
        self._worker.join(timeout=5.0)

# 日志全局快捷函数
_log = Logger()

def log_configure(path: Union[str, Path] = "./logs", level: Level = Level.INFO):
    """配置全局日志器"""
    global _log
    _log = Logger(path, level)

def log_debug(prog: str, msg: str):
    """全局 DEBUG 日志"""
    _log.debug(prog, msg)

def log_info(prog: str, msg: str):
    """全局 INFO 日志"""
    _log.info(prog, msg)

def log_warning(prog: str, msg: str):
    """全局 WARNING 日志"""
    _log.warning(prog, msg)

def log_error(prog: str, msg: str):
    """全局 ERROR 日志"""
    _log.error(prog, msg)

def log_close():
    """关闭全局日志器"""
    _log.close()
