"""OneBot v11 基础事件类型。"""

import json
from copy import deepcopy
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, validate_call, ConfigDict
from typing import Dict, List, Any, Optional, Union
from typing_extensions import override

from .message import Message


class EventType(str, Enum):
    """OneBot v11 基础事件类型枚举"""
    MESSAGE = "message"
    NOTICE = "notice"
    REQUEST = "request"
    META_EVENT = "meta_event"


@da
class Event():
    """OneBot v11 基础事件"""

    time: int
    self_id: int
    post_type: str

    def __str__(self) -> str:
        return f"[{self.get_event_name()}]: {self.get_event_description()}"
    
    def get_type(self) -> str:
        """获取事件类型"""
        return self.post_type

    def get_event_name(self) -> str:
        """获取事件名称(类型)"""
        return self.post_type

    def get_event_description(self) -> str:
        """获取事件内容(json格式)"""
        return json.dumps(self.model_dump(), ensure_ascii=False)

    def get_message(self) -> Message:
        """获取事件的消息"""
        raise ValueError("Event has no message!")

    def get_user_id(self) -> str:
        """获取事件主体 id"""
        raise ValueError("Event has no context!")

    def get_session_id(self) -> str:
        """获取会话 id。
        
        通常是用户 id、群组 id 组合。
        """
        raise ValueError("Event has no context!")

    def is_message(self) -> bool:
        """是否为消息事件"""
        return self.post_type == "message"
    
    def is_notice(self) -> bool:
        """是否为通知事件"""
        return self.post_type == "notice"
    
    def is_notice(self) -> bool:
        """是否为请求事件"""
        return self.post_type == "request"
    
    def is_notice(self) -> bool:
        """是否为元事件"""
        return self.post_type == "meta_event"
    
    def is_tome(self) -> bool:
        """是否与我有关"""
        return False
