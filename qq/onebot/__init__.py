"""OneBot 基础数据模块。"""

__version__ = "0.1.0"
__all__ = [
    "V11Event", "V12Event",
    "V11EventType", "V12EventType",
    "V11Message", "V12Message",
    "V11MsgType", "V12MsgType",
    "V11MessageSegment", "V12MessageSegment",
]
from .v11 import event as V11Event  # module
from .v12 import event as V12Event  # module
from .v11 import EventType as V11EventType
from .v12 import EventType as V12EventType
from .v11 import Message as V11Message
from .v12 import Message as V12Message
from .v11 import MsgType as V11MsgType
from .v12 import MsgType as V12MsgType
from .v11 import MessageSegment as V11MessageSegment
from .v12 import MessageSegment as V12MessageSegment

