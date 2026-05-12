"""OneBot 辅助函数。"""

import json
from enum import Enum
from typing import Dict, List, Any, Optional, Union

def b2s(b: Optional[bool]) -> Optional[str]:
    """转换布尔值为字符串。"""
    return b if b is None else str(b).lower()

def ab2s(b: Optional[Any]) -> Optional[str]:
    """转换指定类型的布尔值为"0"|"1"值。"""
    if b is None:
        return b
    elif b in {1, "1", "yes", "true", "True", True}:
        return "1"
    else:
        return "0"

def f2s(file: str) -> str:
    return file
