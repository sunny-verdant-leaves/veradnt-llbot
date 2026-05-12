"""OneBot v11 基础消息段类型。"""

import re
import json
from copy import deepcopy
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, validate_call, ConfigDict
from collections.abc import Iterable
from typing import Dict, List, Any, Optional, Union
from typing_extensions import Self, override

from .utils import escape, unescape
from ..utils import ab2s


class MsgType(str, Enum):
    """OneBot v11 基础消息段类型枚举"""
    TEXT = "text"
    ANONYMOUS = "anonymous" # 已弃用
    AT = "at"
    CONTACT = "contact"
    DICE = "dice"
    FACE = "face"
    FORWARD = "forward"
    IMAGE = "image" # 已更迭
    # FILE = "file"
    # FLASH_FILE = "flash_file"
    JSON = "json"
    # KEYBOARD = "keyboard"
    LOCATION = "location" # 已弃用
    # MARKDOWN = "markdown"
    # MFACE = "mface"
    MUSIC = "music"
    NODE = "node"   # 已更迭
    POKE = "poke"   # 已更迭
    RECORD = "record"
    REPLY = "reply"
    RPS = "rps"
    SHAKE = "shake"
    SHARE = "share" # 已弃用
    VIDEO = "video" # 已更迭
    XML = "xml"


# 匹配 [CQ:type,key=value,key2=value2]
_CQ_PATTERN = re.compile(
    r"\[CQ:(?P<type>[a-zA-Z0-9-_.]+)"
    r"(?P<params>"
    r"(?:,[a-zA-Z0-9-_.]+=[^,\]]*)*"
    r"),?\]"
)


@dataclass
class MessageSegment():
    """OneBot v11 消息段"""

    type_: str
    data: Dict[str, Any]

    @override
    def __str__(self) -> str:
        if self.type == "text":
            return escape(self.data.get("text", ""), escape_comma=False)

        params = ",".join(
            f"{k}={escape(str(v))}" for k, v in self.data.items() if v is not None
        )
        return f"[CQ:{self.type}{',' if params else ''}{params}]"

    def to_dict(self) -> Dict[str, Any]:
        """转换成字典"""
        return {"type": self.type_, "data": self.data}
    
    def to_json(self) -> str:
        """转换成 json 字符串"""
        return json.dumps({"type": self.type_, "data": self.data}, ensure_ascii=False)

    def is_text(self) -> bool:
        """是否是文本"""
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
    def anonymous(cls, ignore: Union[str, bool, None] = None) -> Self:
        """匿名消息

        Args:
            ignore: 无法匿名时是否继续发送 (仅发), 可为 "0"|"1"
        """
        data = {}
        if ignore is not None:
            data["ignore"] = ab2s(ignore)
        return cls("anonymous", data)

    @classmethod
    @validate_call
    def at(cls, qq: Union[str, int]) -> Self:
        """@某人

        Args:
            qq: @的QQ号, "all"表示@全体成员
        """
        return cls("at", {"qq": str(qq)})
    
    @classmethod
    @validate_call
    def contact(cls, type_: str, id_: Union[str, int]) -> Self:
        """推荐联系人

        Args:
            type_: 联系人类型, 可为 "qq"(好友)|"group"(群聊)
            id_: QQ号|群号
        """
        return cls("contact", {"type": type_, "id": str(id_)})

    @classmethod
    @validate_call
    def contact_group(cls, group_id: Union[str, int]) -> Self:
        """推荐群聊 - 群名片

        Args:
            group_id: 群号
        """
        return cls("contact", {"type": "group", "id": str(group_id)})

    @classmethod
    @validate_call
    def contact_user(cls, user_id: Union[str, int]) -> Self:
        """推荐好友 - 好友名片

        Args:
            user_id: QQ号
        """
        return cls("contact", {"type": "qq", "id": str(user_id)})
    
    @classmethod
    def dice(cls) -> Self:
        """掷骰子魔法表情"""
        return cls("dice", {})

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
    def forward(cls, id_: Union[str, int]) -> Self:
        """合并转发 (仅收)

        Args:
            id_: 合并转发 ID
        """
        return cls("forward", {"id": id_})

    @classmethod
    @validate_call
    def node(cls, id_: Union[str, int]) -> Self:
        """合并转发指定节点

        Args:
            id_: 消息 ID (仅发), 不支持自己构造, 需从其他消息获取
        """
        return cls("forward", {"id": id_})

    @classmethod
    def node_custom(
        cls, 
        content: Union[str, List["MessageSegment"]], 
        user_id: Union[str, int, None] = None, 
        nickname: Union[str, None] = None
    ) -> Self:
        """合并转发自定义节点

        Args:
            content: 消息内容, 可为文本内容、CQ码消息或消息段列表
            user_id: 用户 ID, 自行构造后发送会被自动转换成由自己发送
            nickname: 昵称
        """
        if isinstance(content, List):
            data = {"content": deepcopy(content)}
        else:
            data = {"content": content}
        
        if user_id is not None:
            data["user_id"] = str(user_id)
        if nickname is not None:
            data["nickname"] = nickname
        return cls("forward", data)

    @classmethod
    @validate_call
    def image(
        cls, 
        file: str, 
        type_: Union[str, None] = None, 
        subType: Union[str, int, None] = None, 
        url: Union[str, None] = None, 
        cache: Union[str, bool, None] = None, 
        proxy: Union[str, bool, None] = None, 
        timeout: Union[str, int, None] = None, 
        **kwargs
    ) -> Self:
        """图片

        Args:
            file: 图片文件名, 路径, URL 或 Base64 编码
            type_: 图片显示类型, 可为 "flash"(闪照), 无则表示普通图片
            subType: 图片子类型, 可为 "0"(图片)|"1"(动画表情)
            url: 图片 URL (仅收)
            
            cache: 是否使用缓存 (仅URL发), 可为 "0"|"1", 无则表示是
            proxy: 是否通过代理下载 (仅URL发), 可为 "0"|"1", 无则表示是
            timeout: 下载超时秒数 (仅URL发), 无则表示不超时

            **kwargs: 自定义附加参数
        """
        data = {"file": file}
        data.update(**kwargs)
        if type_ is not None:
            data["type"] = type_
        if url is not None:
            data["url"] = url
        if subType is not None:
            data["subType"] = str(subType)
        if cache is not None:
            data["cache"] = ab2s(cache)
        if proxy is not None:
            data["proxy"] = ab2s(proxy)
        if timeout is not None:
            data["timeout"] = str(timeout)
        return cls("image", data)

    @classmethod
    @validate_call
    def json(cls, data: Union[str, Dict[str, Any]]) -> Self:
        """JSON 消息

        Args:
            data: JSON 内容
        """
        if isinstance(data, Dict[str, Any]):
            data = json.dumps(data)
        return cls("json", {"data": data})

    @classmethod
    @validate_call
    def location(
        cls,
        latitude: Union[str, float],
        longitude: Union[str, float],
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> Self:
        """位置分享

        Args:
            latitude: 纬度
            longitude: 经度
            title: 标题
            content: 内容描述
        """
        data = {
            "lat": str(latitude),
            "lon": str(longitude)
        }
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content
        return cls("location", data)

    @classmethod
    @validate_call
    def music(cls, type_: str, id_: Union[str, int]) -> Self:
        """音乐指定分享 (仅发)

        Args:
            type_: 音乐类型, 可为 "qq"|"163"(网易云)|"xm"(虾米)
            id_: 歌曲 ID
        """
        return cls("music", {"type": type_, "id": str(id_)})

    @classmethod
    @validate_call
    def music_custom(
        cls, 
        url: str,
        audio: str,
        title: str,
        content: Optional[str] = None,
        img_url: Optional[str] = None
    ) -> Self:
        """音乐自定义分享 (仅发)

        Args:
            type_: 音乐类型, 仅为"custom"
            url: 点击后跳转目标 URL
            audio: 音乐 URL
            title: 标题
            content: 内容描述
            img_url: 图片 URL
        """
        data = {
            "type": "custom",
            "url": url,
            "audio": audio,
            "title": title
        }
        if content is not None:
            data["content"] = content
        if img_url is not None:
            data["img_url"] = img_url
        return cls("music", data)

    @classmethod
    @validate_call
    def poke(cls, type_: str, id_: str, name: Union[str, None] = None) -> Self:
        """戳一戳

        Args:
            type_: 戳一戳类型
            id_: 戳一戳类型 ID
            name: 表情名 (仅收)
        """
        data = {
            "type": type_, 
            "id": id_
        }
        if name is not None:
            data["name"] = name
        return cls("poke", data)

    @classmethod
    @validate_call
    def record(
        cls,
        file: str,
        magic: Union[str, bool, None] = None,
        url: Union[str, None] = None,
        cache: Union[str, bool, None] = None, 
        proxy: Union[str, bool, None] = None, 
        timeout: Union[str, int, None] = None, 
        **kwargs
    ) -> Self:
        """语音

        Args:
            file: 语音文件名, 路径, URL 或 Base64 编码
            magic: 是否变声, 可为 "0"|"1", 无则表示否
            url: 图片 URL (仅收)
            
            cache: 是否使用缓存 (仅URL发), 可为 "0"|"1", 无则表示是
            proxy: 是否通过代理下载 (仅URL发), 可为 "0"|"1", 无则表示是
            timeout: 下载超时秒数 (仅URL发), 无则表示不超时

            **kwargs: 自定义附加参数
        """
        data = {"file": file}
        data.update(**kwargs)
        if magic is not None:
            data["magic"] = ab2s(magic)
        if url is not None:
            data["url"] = url
        if cache is not None:
            data["cache"] = ab2s(cache)
        if proxy is not None:
            data["proxy"] = ab2s(proxy)
        if timeout is not None:
            data["timeout"] = str(timeout)
        return cls("record", data)

    @classmethod
    @validate_call
    def reply(cls, id_: Union[str, int]) ->  Self:
        """回复

        Args:
            id_: 回复时引用的消息 ID
        """
        return cls("reply", {"id": str(id_)})

    @classmethod
    def rps(cls) -> Self:
        """猜拳魔法表情"""
        return cls("rps", {})

    @classmethod
    def shake(cls) -> Self:
        """窗口抖动(另一种戳一戳)"""
        return cls("shake", {})

    @classmethod
    @validate_call
    def share(
        cls,
        url: str = "",
        title: str = "",
        content: Optional[str] = None,
        image: Optional[str] = None,
    ) -> Self:
        """链接分享

        Args:
            url: 链接 URL
            title: 标题
            content: 内容描述
            image: 图片 URL
        """
        data = {
            "url": url, 
            "title": title
        }
        if content is not None:
            data["content"] = content
        if image is not None:
            data["image"] = image
        return cls("share", data)

    @classmethod
    @validate_call
    def video(
        cls, 
        file: str, 
        url: Union[str, None] = None, 
        cache: Union[str, bool, None] = None, 
        proxy: Union[str, bool, None] = None, 
        timeout: Union[str, int, None] = None, 
        **kwargs
    ) -> Self:
        """短视频

        Args:
            file: 视频文件名, 路径, URL 或 Base64 编码
            url: 视频 URL (仅收)
            
            cache: 是否使用缓存 (仅URL发), 可为 "0"|"1", 无则表示是
            proxy: 是否通过代理下载 (仅URL发), 可为 "0"|"1", 无则表示是
            timeout: 下载超时秒数 (仅URL发), 无则表示不超时

            **kwargs: 自定义附加参数
        """
        data = {"file": file}
        data.update(**kwargs)
        if url != None:
            data["url"] = url
        if cache is not None:
            data["cache"] = ab2s(cache)
        if proxy is not None:
            data["proxy"] = ab2s(proxy)
        if timeout != None:
            data["timeout"] = str(timeout)
        return cls("video", data)

    @classmethod
    @validate_call
    def xml(cls, data: str) -> Self:
        """XML 消息

        Args:
            data: XML 内容
        """
        return cls("xml", {"data": data})


class Message(List[MessageSegment]):
    """OneBot v11 消息数组(列表)"""

    @override
    def __init__(self, message: Union[str, MessageSegment, List[MessageSegment], None] = None):
        super().__init__()
        if message is None:
            return
        elif isinstance(message, str):
            self.extend(MessageSegment.text(message))
        elif isinstance(message, MessageSegment):
            self.append(message)
        elif isinstance(message, Iterable):
            self.extend(message)
        else:
            self.extend(MessageSegment.text(message))

    @override
    def __add__(
        self, other: Union[str, MessageSegment, List[MessageSegment]]
    ) -> Self:
        result = self.copy()
        result += other
        return result
    
    @override
    def __radd__(
        self, other: Union[str, MessageSegment, List[MessageSegment]]
    ) -> Self:
        result = self.__class__(other)
        return result + self

    @override
    def __iadd__(
        self, other: Union[str, MessageSegment, List[MessageSegment]]
    ) -> Self:
        if isinstance(other, str):
            self.extend(MessageSegment.text(other))
        elif isinstance(other, MessageSegment):
            self.append(other)
        elif isinstance(other, Iterable):
            self.extend(other)
        else:
            raise TypeError(f"Unsupported type {type(other)!r}")
        return super().__iadd__(other)
    