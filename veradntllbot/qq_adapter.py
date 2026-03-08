"""
与QQ的桥梁，尽量薄
"""

import asyncio
from typing import Callable

class QQBot:
    def __init__(self, pulse_func: Callable, field):
        self.pulse = pulse_func
        self.field = field
        self.message_queue = asyncio.Queue()
        
    async def on_message(self, msg: dict):
        """
        收到消息时
        """
        # 包装为刺激
        stimulus = {
            'type': 'message',
            'text': msg.get('message', ''),
            'sender': msg.get('sender', {}).get('nickname', 'unknown'),
            'time': msg.get('time')
        }
        
        # 心跳
        action = self.pulse(stimulus)
        
        # 执行行动
        if action['type'] == 'reply':
            await self._send(action['content'], delay=action['pace'])
        elif action['type'] == 'silence':
            pass  # 沉默也是行动
    
    async def _send(self, content: str, delay: float = 1.0):
        """发送回复（接入实际的QQ库）"""
        await asyncio.sleep(delay)  # 模拟思考时间
        print(f"[发送] {content}")  # 占位：替换为实际发送代码
    
    async def heartbeat(self):
        """
        自主心跳（没有消息时也思考）
        """
        while True:
            await asyncio.sleep(10)  # 每10秒
            if self._time_since_last() > 60:  # 1分钟无互动
                action = self.pulse(None)  # 沉默的pulse
                # 可能产生"主动消息"或内部状态变化
    
    def _time_since_last(self) -> float:
        from datetime import datetime
        if not self.field.last_contact:
            return float('inf')
        return (datetime.now() - self.field.last_contact).total_seconds()
