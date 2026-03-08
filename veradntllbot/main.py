"""
养育开始的地方
"""

from gene import INSTINCT, SEED_UNITS
from field import RippleField
from pulse import Pulse
from qq_adapter import QQBot
import asyncio

def main():
    # 初始化世界
    field = RippleField()
    
    # 播种初始单元
    units = {u['id']: u for u in SEED_UNITS}
    for uid in units:
        field.activation[uid] = 0.1  # 微弱的初始激活
    
    # ===== 加载记忆 =====
    import sediment
    sediment.LOAD_MEMORY = load_from_file  # 设置存储接口
    sediment.SAVE_MEMORY = save_to_file
    sediment.load_sediments(field)  # 加载地层
    units = load_units() or units  # 加载认知单元（如果有）

    # 创造心跳
    pulse = Pulse(field, INSTINCT, units)
    
    # 启动QQ（或测试模式）
    # bot = QQBot(pulse.beat, field)
    
    # 测试：模拟几次互动
    print("=== 测试模式 ===")
    test_messages = [
        "",
        "",
        "你今天开心吗？",
        None,
        "要是不开心的话，可以找碧叶哦"
    ]
    
    for msg in test_messages:
        if msg:
            print(f"\n[碧叶] {msg}")
            action = pulse.beat({'text': msg, 'sender': '碧叶'})
        else:
            print(f"\n[沉默 30秒]")
            import time
            time.sleep(0.5)  # 模拟
            action = pulse.beat(None)
        
        print(f"[她] {action}")
        print(f"    场状态: tone={field.tone:+.2f}, tension={field.tension:.2f}")
        print(f"    激活: {field.activation}")
    
    # 实际运行（取消注释）
    # asyncio.run(run_qq_bot(bot))
    
    # ===== 退出时保存 =====
    save_units(units)  # 保存认知单元
    sediment._persist_sediments(field)  # 保存地层
    print("记忆已保存")

async def run_qq_bot(bot):
    """实际QQ运行"""
    await asyncio.gather(
        bot.heartbeat(),
        # bot.start_qq_listener()  # 碧叶的具体实现
    )

# ===== 简单的文件存储接口 =====
import json
import os

def load_from_file(name: str):
    """从文件加载"""
    try:
        with open(f'{name}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def save_to_file(name: str, data: dict):
    """保存到文件"""
    with open(f'{name}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_units():
    """加载认知单元"""
    data = load_from_file('./memory/units')
    if data:
        return {u['id']: u for u in data.get('units', [])}
    return None

def save_units(units: dict):
    """保存认知单元"""
    units_list = [{'id': k, **v} for k, v in units.items()]
    save_to_file('./memory/units', {'units': units_list})

if __name__ == '__main__':
    main()