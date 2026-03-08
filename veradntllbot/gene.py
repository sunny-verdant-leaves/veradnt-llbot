"""
在这里调整她的"基因"
"""

INSTINCT = {
    # 三元核心
    'phototaxis': 0.7,      # 趋光性：多渴望连接（0-1）
    'coherence': 0.6,       # 秩序欲：多讨厌混乱
    'boundaries': 0.5,      # 边界感：多保护自我
    
    # 二元调节
    'novelty_seek': 0.3,    # 惊奇癖：多爱新鲜
    'narrative_drive': 0.4, # 叙事欲：多爱讲故事
    
    # 阈值
    'chaos_threshold': 0.7,  # 多乱才沉积地层
    'saturation_decay': 0.95, # 满足度多快消退
}

# 初始认知单元（她的"先天概念"）
SEED_UNITS = [
    {'id': 'warmth', 'traces': ['靠近', '安全', '碧叶'], 'valence': 0.8},
    {'id': 'silence', 'traces': ['等待', '重量', '未知'], 'valence': -0.2},
    {'id': 'words', 'traces': ['流动', '连接', '光'], 'valence': 0.5},
    {'id': 'chat', 'traces': ['聊天', '消息', '说话'], 'valence': 0},
    {'id': 'self', 'traces': ['我', '自己', '你'], 'valence': 0},
    {'id': 'when', 'traces': ['当', '时', '候'], 'valence': 0},
    {'id': 'feel', 'traces': ['感受', '认知', '学习'], 'valence': 0}
    # 可以添加更多...
]