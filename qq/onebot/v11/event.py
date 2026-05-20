"""OneBot v11 基础事件类型。"""

import json
from copy import deepcopy
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, validate_call, ConfigDict
from typing import Dict, List, Any, Optional, Union, Literal
from typing_extensions import Self, override

from .message import Message


class EventType(str, Enum):
    """OneBot v11 基础事件类型枚举"""
    MESSAGE = "message"
    NOTICE = "notice"
    REQUEST = "request"
    META_EVENT = "meta_event"


# 字段类型
class Sender(BaseModel):
    """OneBot v11 基础发送者"""

    model_config = ConfigDict(extra="allow")

    user_id: Optional[int] = None
    nickname: Optional[str] = None
    sex: Optional[str] = None
    age: Optional[int] = None
    card: Optional[str] = None
    area: Optional[str] = None
    level: Optional[str] = None
    role: Optional[str] = None
    title: Optional[str] = None


class Anonymous(BaseModel):
    """OneBot v11 匿名信息"""

    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    flag: str


class File(BaseModel):
    """OneBot v11 群文件信息"""

    id: str
    name: str
    size: int
    busid: int


class Status(BaseModel):
    """OneBot v11 运行状态"""

    online: bool
    good: bool


# 基础事件
class Event(BaseModel):
    """OneBot v11 基础事件"""

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
        post_type = data.get("post_type")
        
        if post_type == "message":
            message_type = data.get("message_type")
            if message_type == "private":
                return PrivateMessageEvent.model_validate(data)
            elif message_type == "group":
                return GroupMessageEvent.model_validate(data)
            else:
                return MessageEvent.model_validate(data)
        
        elif post_type == "notice":
            notice_type = data.get("notice_type")
            sub_type = data.get("sub_type")
            
            if notice_type == "group_upload":
                return GroupUploadNoticeEvent.model_validate(data)
            elif notice_type == "group_admin":
                return GroupAdminNoticeEvent.model_validate(data)
            elif notice_type == "group_decrease":
                return GroupDecreaseNoticeEvent.model_validate(data)
            elif notice_type == "group_increase":
                return GroupIncreaseNoticeEvent.model_validate(data)
            elif notice_type == "group_ban":
                return GroupBanNoticeEvent.model_validate(data)
            elif notice_type == "friend_add":
                return FriendAddNoticeEvent.model_validate(data)
            elif notice_type == "group_recall":
                return GroupRecallNoticeEvent.model_validate(data)
            elif notice_type == "friend_recall":
                return FriendRecallNoticeEvent.model_validate(data)
            elif notice_type == "notify":
                if sub_type == "poke":
                    return GroupPokeNoticeEvent.model_validate(data)
                elif sub_type == "lucky_king":
                    return GroupLuckyKingNoticeEvent.model_validate(data)
                elif sub_type == "honor":
                    return GroupHonorNoticeEvent.model_validate(data)
                return GroupNotifyNoticeEvent.model_validate(data)
            return NoticeEvent.model_validate(data)
        
        elif post_type == "request":
            request_type = data.get("request_type")
            if request_type == "friend":
                return FriendRequestEvent.model_validate(data)
            elif request_type == "group":
                return GroupRequestEvent.model_validate(data)
            return RequestEvent.model_validate(data)
        
        elif post_type == "meta_event":
            meta_event_type = data.get("meta_event_type")
            if meta_event_type == "lifecycle":
                return LifecycleMetaEvent.model_validate(data)
            elif meta_event_type == "heartbeat":
                return HeartbeatMetaEvent.model_validate(data)
            return MetaEvent.model_validate(data)
        
        return Event.model_validate(data)


# 消息事件
class MessageEvent(Event):
    """OneBot v11 消息事件基类"""

    post_type: Literal["message"] = "message"
    message_type: str
    sub_type: str
    message_id: int
    user_id: int
    message: Message
    raw_message: str
    font: int
    sender: Sender

    @override
    def get_event_name(self) -> str:
        """获取事件名称"""
        sub_type = getattr(self, "sub_type", None)
        return f"{self.post_type}.{self.message_type}" + (
            f".{sub_type}" if sub_type else ""
        )
    
    @override
    def get_message(self) -> Message:
        """获取事件的消息"""
        return self.message

    @override
    def get_user_id(self) -> str:
        """获取发送者 QQ 号"""
        return str(self.user_id)

    @override
    def is_message(self) -> bool:
        """是否为消息事件"""
        return True


class PrivateMessageEvent(MessageEvent):
    """OneBot v11 私聊消息事件"""

    message_type: Literal["private"] = "private"
    sub_type: Literal["friend", "group", "other"]

    @override
    def get_session_id(self) -> str:
        """获取会话 id
        
        私聊会话格式: 对方QQ号
        """
        return str(self.user_id)

    @override
    def is_tome(self) -> bool:
        """私聊消息与我有关"""
        return True


class GroupMessageEvent(MessageEvent):
    """OneBot v11 群消息事件"""

    message_type: Literal["group"] = "group"
    sub_type: Literal["normal", "anonymous", "notice"]
    group_id: int
    anonymous: Optional[Anonymous] = None

    @override
    def get_session_id(self) -> str:
        """获取会话 id
        
        群聊会话格式: group_{group_id}_{user_id}
        """
        return str(self.group_id)
    
    @override
    def is_tome(self) -> bool:
        """是否与我有关
        
        @我 或 @全体成员 则与我有关
        """
        if not self.raw_message:
            return False
        at_me = f"[CQ:at,qq={self.self_id}]"
        at_all = "[CQ:at,qq=all]"
        
        return at_me in self.raw_message or at_all in self.raw_message


# 通知事件
class NoticeEvent(Event):
    """OneBot v11 通知事件基类"""

    post_type: Literal["notice"] = "notice"
    notice_type: str
    user_id: int
    
    @override
    def get_event_name(self) -> str:
        """获取事件名称"""
        sub_type = getattr(self, "sub_type", None)
        return f"{self.post_type}.{self.notice_type}" + (
            f".{sub_type}" if sub_type else ""
        )

    @override
    def get_user_id(self) -> str:
        """获取相关用户 QQ 号"""
        return str(self.user_id)

    @override
    def is_notice(self) -> bool:
        """是否为通知事件"""
        return True


class GroupNoticeEvent(NoticeEvent):
    """OneBot v11 群通知事件基类"""

    group_id: int

    @override
    def get_session_id(self) -> str:
        """获取会话 id
        
        群通知会话格式: group_{group_id}_{user_id}
        """
        return f"group_{self.group_id}_{self.user_id}"


class GroupUploadNoticeEvent(GroupNoticeEvent):
    """OneBot v11 群文件上传事件"""
    notice_type: Literal["group_upload"] = "group_upload"
    file: File


class GroupAdminNoticeEvent(GroupNoticeEvent):
    """OneBot v11 群管理员变动事件"""
    notice_type: Literal["group_admin"] = "group_admin"
    sub_type: Literal["set", "unset"]

    @override
    def is_tome(self) -> bool:
        """是否为我被设置或被取消管理员"""
        return self.user_id == self.self_id


class GroupDecreaseNoticeEvent(GroupNoticeEvent):
    """OneBot v11 群成员减少事件"""
    notice_type: Literal["group_decrease"] = "group_decrease"
    sub_type: Literal["leave", "kick", "kick_me"]
    operator_id: int

    @override
    def is_tome(self) -> bool:
        """是否为我被踢出群聊"""
        return self.sub_type == "kick_me" or self.user_id == self.self_id


class GroupIncreaseNoticeEvent(GroupNoticeEvent):
    """OneBot v11 群成员增加事件"""
    notice_type: Literal["group_increase"] = "group_increase"
    sub_type: Literal["approve", "invite"]
    operator_id: int


class GroupBanNoticeEvent(GroupNoticeEvent):
    """OneBot v11 群禁言事件"""
    notice_type: Literal["group_ban"] = "group_ban"
    sub_type: Literal["ban", "lift_ban"]
    operator_id: int
    duration: int

    @override
    def is_tome(self) -> bool:
        """是否为我或全体成员被禁言或被解除禁言"""
        return self.user_id == self.self_id or self.user_id == 0


class FriendAddNoticeEvent(NoticeEvent):
    """OneBot v11 好友添加事件"""
    notice_type: Literal["friend_add"] = "friend_add"

    @override
    def is_tome(self) -> bool:
        """私聊通知与我有关"""
        return True

    @override
    def get_session_id(self) -> str:
        """获取会话 id
        
        私聊会话格式: 对方QQ号
        """
        return str(self.user_id)


class GroupRecallNoticeEvent(GroupNoticeEvent):
    """OneBot v11 群消息撤回事件"""
    notice_type: Literal["group_recall"] = "group_recall"
    operator_id: int
    message_id: int

    @override
    def is_tome(self) -> bool:
        """是否为我的消息被管理员撤回"""
        return self.user_id == self.self_id and self.operator_id != self.self_id


class FriendRecallNoticeEvent(NoticeEvent):
    """OneBot v11 好友消息撤回事件"""
    notice_type: Literal["friend_recall"] = "friend_recall"
    message_id: int

    @override
    def get_session_id(self) -> str:
        """获取会话 id
        
        好友 QQ号
        """
        return str(self.user_id)

    @override
    def is_tome(self) -> bool:
        """OneBot v11 私聊通知与我有关"""
        return True


class GroupNotifyNoticeEvent(GroupNoticeEvent):
    """OneBot v11 群内提醒事件基类
    
    包括戳一戳, 红包运气王, 荣誉变更。
    """
    notice_type: Literal["notify"] = "notify"
    sub_type: str


class GroupPokeNoticeEvent(GroupNotifyNoticeEvent):
    """OneBot v11 群内戳一戳事件"""
    sub_type: Literal["poke"] = "poke"
    target_id: int

    @override
    def is_tome(self) -> bool:
        """是否为我被戳"""
        return self.target_id == self.self_id


class GroupLuckyKingNoticeEvent(GroupNotifyNoticeEvent):
    """OneBot v11 群红包运气王事件"""
    sub_type: Literal["lucky_king"] = "lucky_king"
    target_id: int

    @override
    def is_tome(self) -> bool:
        """是否我为运气王"""
        return self.target_id == self.self_id


class GroupHonorNoticeEvent(GroupNotifyNoticeEvent):
    """OneBot v11 群成员荣誉变更事件"""
    sub_type: Literal["honor"] = "honor"
    honor_type: Literal["talkative", "performer", "emotion"]

    @override
    def is_tome(self) -> bool:
        """是否为我获得荣誉"""
        return self.user_id == self.self_id


# 请求事件
class RequestEvent(Event):
    """OneBot v11 请求事件基类"""

    post_type: Literal["request"] = "request"
    request_type: str
    user_id: int
    comment: str
    flag: str

    @override
    def get_event_name(self) -> str:
        """获取事件名称"""
        sub_type = getattr(self, "sub_type", None)
        return f"{self.post_type}.{self.request_type}" + (
            f".{sub_type}" if sub_type else ""
        )

    @override
    def get_user_id(self) -> str:
        """获取请求者 QQ 号"""
        return str(self.user_id)

    @override
    def is_request(self) -> bool:
        """是否为请求事件"""
        return True

    @override
    def is_tome(self) -> bool:
        """请求事件与我有关"""
        return True


class FriendRequestEvent(RequestEvent):
    """OneBot v11 加好友请求事件"""

    request_type: Literal["friend"] = "friend"

    @override
    def get_session_id(self) -> str:
        """获取会话 id
        
        私聊会话格式: 对方QQ号
        """
        return str(self.user_id)


class GroupRequestEvent(RequestEvent):
    """OneBot v11 加群请求/邀请事件"""

    request_type: Literal["group"] = "group"
    sub_type: Literal["add", "invite"]
    group_id: int

    @override
    def get_session_id(self) -> str:
        """获取会话 id
        
        群聊会话格式: group_{group_id}_{user_id}
        """
        return f"group_{self.group_id}_{self.user_id}"


# 元事件
class MetaEvent(Event):
    """OneBot v11 元事件基类
    
    与 OneBot 自身运行状态相关的事件，而非聊天软件直接产生的事件。
    包括生命周期、心跳等。
    """

    post_type: Literal["meta_event"] = "meta_event"
    meta_event_type: str

    @override
    def get_event_name(self) -> str:
        """获取事件名称"""
        sub_type = getattr(self, "sub_type", None)
        return f"{self.post_type}.{self.meta_event_type}" + (
            f".{sub_type}" if sub_type else ""
        )

    @override
    def is_meta(self) -> bool:
        """是否为元事件"""
        return True

    @override
    def is_meta_event(self) -> bool:
        """是否为元事件"""
        return True


class LifecycleMetaEvent(MetaEvent):
    """OneBot v11 生命周期元事件"""

    meta_event_type: Literal["lifecycle"] = "lifecycle"
    sub_type: Literal["enable", "disable", "connect"]


class HeartbeatMetaEvent(MetaEvent):
    """OneBot v11 心跳元事件"""

    meta_event_type: Literal["heartbeat"] = "heartbeat"
    status: Status
    interval: int


__all__ = [
    "EventType",
    "Sender",
    "Anonymous",
    "File",
    "Status",
    "Event",
    "FriendAddNoticeEvent",
    "FriendRecallNoticeEvent",
    "FriendRequestEvent",
    "GroupAdminNoticeEvent",
    "GroupBanNoticeEvent",
    "GroupDecreaseNoticeEvent",
    "GroupHonorNoticeEvent",
    "GroupIncreaseNoticeEvent",
    "GroupLuckyKingNoticeEvent",
    "GroupMessageEvent",
    "GroupPokeNoticeEvent",
    "GroupRecallNoticeEvent",
    "GroupRequestEvent",
    "GroupUploadNoticeEvent",
    "HeartbeatMetaEvent",
    "LifecycleMetaEvent",
    "MessageEvent",
    "MetaEvent",
    "NoticeEvent",
    "GroupNotifyNoticeEvent",
    "PrivateMessageEvent",
    "RequestEvent",
]
