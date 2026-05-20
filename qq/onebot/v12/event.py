"""OneBot v12 基础事件类型。"""

import json
from copy import deepcopy
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, validate_call, ConfigDict
from typing import Dict, List, Any, Optional, Union, Literal
from typing_extensions import Self, override

from .message import Message


class EventType(str, Enum):
    """OneBot v12 基础事件类型枚举"""
    pass


# 基础事件
class Event(BaseModel):
    """OneBot v12 基础事件"""

    model_config = ConfigDict(extra="allow")

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
        """获取会话 id
        
        会话 id 用于区分不同的聊天上下文，通常的格式如下：
        - 私聊: 对方的QQ号
        - 群聊: group_{group_id}_{user_id}
        """
        raise ValueError("Event has no context!")

    def is_message(self) -> bool:
        """是否为消息事件"""
        return self.post_type == "message"
    
    def is_notice(self) -> bool:
        """是否为通知事件"""
        return self.post_type == "notice"
    
    def is_request(self) -> bool:
        """是否为请求事件"""
        return self.post_type == "request"
    
    def is_meta(self) -> bool:
        """是否为元事件"""
        return self.post_type == "meta_event"
    
    def is_meta_event(self) -> bool:
        """是否为元事件"""
        return self.post_type == "meta_event"
    
    def is_tome(self) -> bool:
        """是否与我有关"""
        return False
    
    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """从原始 JSON 字典自动分发到正确的子类。
        
        这是构造事件的主要入口，HTTP 上报的数据直接丢进来即可。
        根据 post_type 和子类型字段自动路由到对应的事件子类。
        """
        pass


__all__ = [
    "EventType",
    "Event"
]
