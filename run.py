import uvicorn
import asyncio
import utils
import requests
import time
import random
import subprocess
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from qq.onebot.v11.event import Event, MessageEvent, GroupRecallNoticeEvent, FriendRecallNoticeEvent
from qq.onebot import V11Message as Message
from qq.onebot import V11MessageSegment as MessageSegment

today = datetime.now().strftime("%Y-%m-%d")
path = "d:/在/大量大型文件/Python/LLBot-CLI-win-x64-v7.11.4/llbot.exe"  # LLBot所在路径

async def worker(buffer: asyncio.Queue):
    repeat = Message()
    events = []
    msgs = []
    while True:
        
        # 从缓冲池里取出
        item: Event = await buffer.get()
        print(item)

        if item.is_message():
            # 获取新消息
            try:
                msg = item.get_message()
            except ValueError:
                utils.log_error("main", f"[worker] Event has no message!")
                continue

            # 处理新消息
            print(msg)
            repeat_tendency: float = 0.0    # 决定是否要复读，倾向越高，复读的可能性越大

            # 倾向计算
            if msg == repeat:
                utils.log_info("main", f"[worker] Have already repeated.")
                repeat_tendency = 0.0
            else:
                last_match = None
                for i in range(len(msgs)-1, -1, -1):
                    message: Message = msgs[i]
                    event: Event = events[i]

                    if message == msg:
                        if event.get_user_id() == item.get_user_id():
                            utils.log_info("main", f"[worker] Just somebody is stressing.")
                            repeat_tendency = 0.0
                            break
                        if last_match is None:
                            gap = len(msgs) - i     # 当前位置与最近的历史匹配
                        else:
                            gap = last_match - i    # 两个历史匹配之间
                        repeat_tendency += 1.0 / gap
                        last_match = i

            # 进行复读
            print(f"复读倾向为: {repeat_tendency}")
            if random.random() < repeat_tendency/2-0.2:
                repeat = msg
                segs = random.choices(
                    [
                        [seg.to_dict() for seg in msg], 
                        random.choices([
                                MessageSegment.text("[自动回复] 打断复读").to_dict(), 
                                MessageSegment.text("[自动回复] 打破复读").to_dict(), 
                                MessageSegment.text("[自动回复] 不许复读").to_dict(), 
                                MessageSegment.text("[自动回复] 禁止复读").to_dict(), 
                        ]), 
                        random.choices([
                                MessageSegment.text("[自动回复] ？").to_dict(), 
                                MessageSegment.text("[自动回复] ?").to_dict(), 
                                MessageSegment.text("[自动回复] 干什么").to_dict(), 
                                MessageSegment.text("[自动回复] 啊嘞").to_dict(), 
                                MessageSegment.text("[自动回复] 啊嘞嘞").to_dict(), 
                                MessageSegment.text("[自动回复] 笨蛋").to_dict(), 
                        ]), 
                    ], 
                    weights=[25*repeat_tendency, 5*repeat_tendency, 100-30*repeat_tendency]
                )[0]
                content = {"message": segs}

                session: str = item.get_session_id()
                if session.startswith("group_"):
                    content["group_id"] = session.split("_", 2)[1]    # ["group", "{group_id}", "{user_id}"]
                else:
                    content["user_id"] = session    # user_id

                utils.append(f"./logs/responses/{today}.log", [content])
                print(content)
                send([content])

            # 保留最近3条消息
            events.append(item)
            msgs.append(msg)
            while len(msgs) > 3:
                msgs.pop(0)
                events.pop(0)

        elif item.is_notice():
            if isinstance(item, FriendRecallNoticeEvent):
                message_id: int = item.message_id
            elif isinstance(item, GroupRecallNoticeEvent):
                message_id: int = item.message_id
            else:
                pass
        else:
            continue

@asynccontextmanager
async def lifespan(app: FastAPI):
    buffer = asyncio.Queue(maxsize=10)    # 缓冲池
    app.state.buffer = buffer             # 挂载
    asyncio.create_task(worker(buffer))
    utils.log_info("main", f"[lifespan] 缓冲池消费者已启动。")

    process = subprocess.Popen(
        [],
        creationflags=subprocess.CREATE_NEW_CONSOLE  # 新建独立窗口
    )
    utils.log_info("main", f"[lifespan] QQ已启动。")
    
    yield

    utils.log_info("main", f"[lifespan] 缓冲池消费者已启动。")

    process.terminate()
    process.wait()
    utils.log_info("main", f"[lifespan] QQ已关闭。")

app = FastAPI(lifespan=lifespan)

@app.post("/")
async def listener(request: Request):
    data = await request.json()  # 获取事件数据
    event: Event
    
    try:
        event = Event.from_dict(data)
    except Exception as e:
        utils.log_error("main", f"[listener] Event failed to transform!\n{e}")
    
    try:
        request.app.state.buffer.put_nowait(event)
    except asyncio.QueueFull:
        utils.log_warning("main", "[listener] Buffer has been full.")
    
    utils.append(f"./logs/data/{today}.log", data)
    
    return {}

def send(msgs: list, typing: Optional[float] = None):
    for msg in msgs:
        if not typing:
            typing = lenth_msg(msg)*0.3+lenth_msg(msg)/10*random.random()
        print(f"发送{str_msg(msg)}, 花费 {typing} 秒")
        utils.log_info("main", f"发送{str_msg(msg)}, 花费 {typing} 秒")
        time.sleep(typing)  # 模拟打字速度
        if "group_id" in msg:
            requests.post(
                "http://localhost:3235/send_group_msg",
                json=msg,
                timeout=5,
            )
        else:
            requests.post(
                "http://localhost:3235/send_private_msg",
                json=msg,
                timeout=5,
            )

def lenth_msg(msg: dict) -> int:
    lenth = 0
    if not "message" in msg:
        return -1
    for content in msg["message"]:
        if not "data" in content:
            utils.log_warning("main", "[lenth_msg] Cannot get content from message.")
            continue
        if not "text" in content["data"]:
            continue
        lenth += len(content["data"]["text"])
    return lenth

def str_msg(msg: dict) -> int:
    str_msg = "消息"
    if not "message" in msg:
        return str_msg
    for content in msg["message"]:
        if not "data" in content:
            utils.log_warning("main", "[lenth_msg] Cannot get content from message.")
            continue
        if not "text" in content["data"]:
            continue
        str_msg += f' “{content["data"]["text"]}” '
    if "group_id" in msg:
        str_msg += "到群聊"
        str_msg += f' {msg["group_id"]} '
    else:
        str_msg += "给联系人"
        str_msg += f' {msg["user_id"]} '
    return str_msg

if __name__ == "__main__":
    uvicorn.run(app, port=2350)