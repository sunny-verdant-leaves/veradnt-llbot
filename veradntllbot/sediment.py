"""
历史不是存储，是压缩的质感
"""

from datetime import datetime
from typing import Dict, List, Optional, Callable

# 存储接口（碧叶替换这两个）
SAVE_MEMORY: Callable[[str, Dict], None] = lambda name, data: None
LOAD_MEMORY: Callable[[str], Optional[Dict]] = lambda name: None


def add_sediment(field, trigger, units):
    """
    当场发生质变，沉积一层
    传入units用于获取完整单元快照
    """
    # 提取主导单元完整快照（id + 当时状态）
    dominant = []
    if field.activation:
        top = sorted(field.activation.items(), key=lambda x: x[1], reverse=True)[:3]
        for uid, act in top:
            if uid in units:
                u = units[uid]
                dominant.append({
                    'id': uid,
                    'act': round(act, 2),
                    'valence': u.get('valence', 0),
                    'depth': u.get('depth', 0.5),
                    'traces': u.get('traces', [])[:3]  # 只存前3个traces
                })
    
    sediment = {
        'time': datetime.now().isoformat()[:19],
        'trigger': {
            'type': trigger.get('type'),
            'texture': trigger.get('texture'),
            'valence': round(trigger.get('valence', 0), 2)
        },
        'field_state': {
            'tone': round(field.tone, 2),
            'tension': round(field.tension, 2),
            'dominant': dominant
        },
        'narrative': _compress_to_words(field, trigger)
    }
    
    field.sediments.append(sediment)
    
    # 只保留最近15层
    if len(field.sediments) > 15:
        field.sediments = field.sediments[-15:]
        _persist_sediments(field)


def _compress_to_words(field, trigger) -> List[str]:
    """压缩成关键词"""
    words = []
    
    if trigger.get('texture'):
        words.append(trigger['texture'])
    
    if field.tone > 0.3:
        words.append('明亮')
    elif field.tone < -0.3:
        words.append('沉重')
    
    if field.tension > 0.6:
        words.append('紧绷')
    elif field.tension < 0.3:
        words.append('松弛')
    
    # 用当时的dominant ids
    if field.activation:
        top = sorted(field.activation.items(), key=lambda x: x[1], reverse=True)[:2]
        words.extend([uid[:4] for uid, _ in top])
    
    return words[:5]


def excavate(field, depth: int = 1) -> Optional[Dict]:
    """挖掘历史"""
    if not field.sediments or depth > len(field.sediments):
        return None
    return field.sediments[-depth]


def recall_by_texture(field, texture: str) -> Optional[Dict]:
    """按质地回忆"""
    for sed in reversed(field.sediments):
        if sed.get('trigger', {}).get('texture') == texture:
            return sed
    return None


def _persist_sediments(field):
    """持久化存储"""
    try:
        SAVE_MEMORY('./memory/sediments', {
            'count': len(field.sediments),
            'latest': field.sediments[-15:]
        })
    except:
        pass


def load_sediments(field):
    """加载历史"""
    try:
        data = LOAD_MEMORY('./memory/sediments')
        if data and 'latest' in data:
            field.sediments = data['latest']
    except:
        pass