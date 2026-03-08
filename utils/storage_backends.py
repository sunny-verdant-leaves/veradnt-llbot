# 存储后端接口和实现（与业务完全无关）

from abc import ABC, abstractmethod
from pathlib import Path
import json
import pickle
from typing import Any, Union


class StorageBackend(ABC):
    """存储后端接口 - 任何存储方式只需实现这三个方法"""
    
    @abstractmethod
    def read(self, path: Union[str, Path]) -> Any:
        """从路径读取数据"""
        pass
    
    @abstractmethod
    def write(self, path: Union[str, Path], data: Any) -> None:
        """写入数据到路径"""
        pass
    
    @abstractmethod
    def append(self, path: Union[str, Path], data: Any) -> None:
        """追加数据到路径"""
        pass

    @abstractmethod
    def exists(self, path: Union[str, Path]) -> bool:
        """检查路径是否存在"""
        pass


class JSONBackend(StorageBackend):
    """JSON 存储 - 适合字典、列表等基础数据"""
    
    def read(self, path: Union[str, Path]) -> Any:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def write(self, path: Union[str, Path], data: Any) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def append(self, path: Union[str, Path], data: Any) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def exists(self, path: Union[str, Path]) -> bool:
        return Path(path).exists()


class PickleBackend(StorageBackend):
    """Pickle 二进制存储 - 适合任意 Python 对象"""
    
    def read(self, path: Union[str, Path]) -> Any:
        with open(path, 'rb') as f:
            return pickle.load(f)
    
    def write(self, path: Union[str, Path], data: Any) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    def append(self, path: Union[str, Path], data: Any) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'ab') as f:
            pickle.dump(data, f)
    
    def exists(self, path: Union[str, Path]) -> bool:
        return Path(path).exists()


class TextBackend(StorageBackend):
    """纯文本存储 - 适合字符串"""
    
    def read(self, path: Union[str, Path]) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write(self, path: Union[str, Path], data: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
    
    def append(self, path: Union[str, Path], data: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(data)
    
    def exists(self, path: Union[str, Path]) -> bool:
        return Path(path).exists()