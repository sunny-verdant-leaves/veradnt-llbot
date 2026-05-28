"""OneBot v11 基础数据。"""
__all__ = [
    "event",
    "MsgType",
    "Message",
    "MessageSegment"
]

from .event import *
from .message import MsgType as MsgType
from .message import Message as Message
from .message import MessageSegment as MessageSegment