"""OneBot v12 基础消息段类型。"""

import re
import json
from copy import deepcopy
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, validate_call, ConfigDict, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from collections.abc import Iterable
from typing import Dict, List, Any, Optional, Union, Literal
from typing_extensions import Self, override

from ..utils import ab2s


class MsgType(str, Enum):
    """OneBot v12 基础消息段类型枚举"""
    TEXT = "text"
    AT = "at"
    IMAGE = "image"
    FACE = "face"
    FILE = "file"
    LOCATION = "location"
    MUSIC = "music"
    RECORD = "record"
    VIDEO = "video"


@dataclass
class MessageSegment():
    """OneBot v12 消息段"""

    type_: str
    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """转换成字典"""
        return {"type": self.type_, "data": self.data}
    
    def to_json(self) -> str:
        """转换成 json 字符串"""
        return json.dumps({"type": self.type_, "data": self.data}, ensure_ascii=False)

    def is_text(self) -> bool:
        return self.type == "text"
    
    @classmethod
    @validate_call
    def text(cls, text: str) -> Self:
        """文本

        Args:
            text: 文本内容
        """
        return cls("text", {"text": text})

    @classmethod
    @validate_call
    def at(cls) -> Self:
        """@某人

        Args:
        """
        pass
    
    @classmethod
    @validate_call
    def face(cls, id_: Union[str, int]) -> Self:
        """QQ表情

        Args:
            id_: QQ表情 ID
        """
        return cls("face", {"id": id_})
    
    @classmethod
    @validate_call
    def image(cls, **kwargs) -> Self:
        """图片

        Args:
            **kwargs: 自定义附加参数
        """
        data = {}
        data.update(**kwargs)
        return cls("image", data)

    @classmethod
    @validate_call
    def location(cls, **kwargs) -> Self:
        """位置分享

        Args:
            **kwargs: 自定义附加参数
        """
        data = {}
        data.update(**kwargs)
        return cls("location", data)

    @classmethod
    @validate_call
    def music(cls, **kwargs) -> Self:
        """音乐分享

        Args:
            **kwargs: 自定义附加参数
        """
        data = {}
        data.update(**kwargs)
        return cls("music", data)

    @classmethod
    @validate_call
    def record(cls, **kwargs) -> Self:
        """语音

        Args:
            **kwargs: 自定义附加参数
        """
        data = {}
        data.update(**kwargs)
        return cls("record", data)

    @classmethod
    @validate_call
    def video(cls, **kwargs) -> Self:
        """短视频

        Args:
            **kwargs: 自定义附加参数
        """
        data = {}
        data.update(**kwargs)
        return cls("video", data)


class Message(List[MessageSegment]):
    """OneBot v12 消息数组(列表)"""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, 
        source_type: Any, 
        handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.list_schema(handler.generate_schema(MessageSegment))

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return handler(core_schema)

    @override
    def __init__(
        self, 
        message: Union[str, MessageSegment, List[MessageSegment], None] = None
    ):
        super().__init__()
        if message is None:
            return
        elif isinstance(message, str):
            self.append(MessageSegment.text(message))
        elif isinstance(message, MessageSegment):
            self.append(message)
        elif isinstance(message, Iterable):
            self.extend(message)
        else:
            self.append(MessageSegment.text(message))

    @override
    def __add__(
        self, other: Union[str, MessageSegment, List[MessageSegment]]
    ) -> Self:
        result = deepcopy(self)
        result += other
        return result

    @override
    def __radd__(
        self, other: Union[str, MessageSegment, List[MessageSegment]]
    ) -> Self:
        result = deepcopy(self)
        return result + self

    @override
    def __iadd__(
        self, other: Union[str, MessageSegment, List[MessageSegment]]
    ) -> Self:
        if isinstance(other, str):
            self.append(Message._construct(other))
        elif isinstance(other, MessageSegment):
            self.append(other)
        elif isinstance(other, Iterable):
            self.extend(other)
        else:
            raise TypeError(f"Unsupported type {type(other)!r}")
        return self

    @staticmethod
    def _construct(msg: str) -> List[MessageSegment]:
        MessageSegment.text(msg)
    