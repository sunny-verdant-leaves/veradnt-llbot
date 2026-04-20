# 统一文件IO入口

from pathlib import Path
from dataclasses import dataclass
from typing import Any, Union
from .storage_backends import StorageBackend, JSONBackend


@dataclass
class FileIO:
    """
    文件IO统一入口
    
    用法：
        # 使用默认JSON后端
        io = FileIO()
        io.save("data.json", {"key": "value"})
        data = io.load("data.json")
        
        # 切换后端（比如存Python对象）
        io = FileIO(backend=PickleBackend())
        io.save("obj.pkl", my_object)
    """
    
    backend: StorageBackend = None
    
    def __post_init__(self):
        if self.backend is None:
            self.backend = JSONBackend()  # 默认JSON
    
    def load(self, path: Union[str, Path], default: Any = None) -> Any:
        """加载文件，不存在返回default"""
        if not self.backend.exists(path):
            return default
        return self.backend.read(path)
    
    def save(self, path: Union[str, Path], data: Any) -> None:
        """保存文件（自动创建目录）"""
        self.backend.write(path, data)

    def append(self, path: Union[str, Path], data: Any) -> None:
        """追加文件（无则自动创建）"""
        self.backend.append(path, data)
    
    def exists(self, path: Union[str, Path]) -> bool:
        """检查存在"""
        return self.backend.exists(path)


# 全局快捷函数
_io = FileIO()

def load(path: Union[str, Path], default: Any = None) -> Any:
    """全局加载函数"""
    return _io.load(path, default)

def save(path: Union[str, Path], data: Any) -> None:
    """全局保存函数"""
    _io.save(path, data)

def append(path: Union[str, Path], data: Any) -> None:
    """全局保存函数"""
    _io.append(path, data)

def exists(path: Union[str, Path]) -> bool:
    """全局检查函数"""
    return _io.exists(path)

