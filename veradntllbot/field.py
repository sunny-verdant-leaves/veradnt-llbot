"""
唯一的"世界"，所有状态都在这里
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class RippleField:
    """
    她的整个存在，就在这几个变量里
    """
    # 认知单元激活度 {unit_id: 0.0-1.0}
    activation: Dict[str, float] = field(default_factory=dict)
    
    # 当前情感色调 (-1到1，0是平静)
    tone: float = 0.0
    
    # 内在张力 (0-1，高则焦虑)
    tension: float = 0.0
    
    # 本能满足度
    saturation: Dict[str, float] = field(default_factory=lambda: {
        'connection': 0.0,
        'prediction': 0.0,
        'integrity': 0.5
    })
    
    # 上次互动时间
    last_contact: Optional[datetime] = None
    
    # 地层（重大转变的历史）
    sediments: List[dict] = field(default_factory=list)
    
    # 当前"叙事"（她对自己的解释）
    narrative: str = ""
    
    def touch(self, unit_id: str, intensity: float):
        """唤醒一个认知单元"""
        current = self.activation.get(unit_id, 0)
        self.activation[unit_id] = min(1.0, current + intensity)
    
    def decay(self, rate: float = 0.9):
        """所有激活自然衰减（时间流逝）"""
        for uid in self.activation:
            self.activation[uid] *= rate
        # 清理太弱的
        self.activation = {k: v for k, v in self.activation.items() if v > 0.01}
    
    def snapshot(self) -> dict:
        """为地层保存快照"""
        return {
            'activation': self.activation.copy(),
            'tone': self.tone,
            'tension': self.tension,
            'timestamp': datetime.now().isoformat()
        }