"""
一次心跳的完整循环
"""

from typing import Optional, Dict, Any
from datetime import datetime
import random

class Pulse:
    def __init__(self, field, instinct, units):
        self.field = field
        self.instinct = instinct
        self.units = units

    def beat(self, stimulus: Optional[Dict] = None) -> Dict:
        """一次完整的心跳"""
        impact = self._feel(stimulus)
        resonance = self._resonate(impact)
        tone = self._attune(resonance)
        action = self._express(tone)
        self._saturate(action)
        return action

    def _feel(self, stimulus: Optional[Dict]) -> Dict:
        """感知：将输入转化为撞击"""
        if stimulus is None:
            silence = datetime.now() - (self.field.last_contact or datetime.now())
            seconds = silence.seconds

            # 沉默的矢量：趋光性拉向渴望，边界感抵抗
            pull = -self.instinct['phototaxis'] * min(1.0, seconds / 60)
            resist = self.instinct['boundaries'] * (0.3 if seconds > 300 else 0)

            return {
                'type': 'silence',
                'weight': min(1.0, seconds / 60),
                'valence': pull + resist,  # 负=渴望，正=封闭
                'texture': '沉重' if seconds > 300 else '轻盈'
            }

        text = stimulus.get('text', '')

        # 简单矢量计算
        push = text.count('不') + text.count('没')
        pull = text.count('来') + text.count('呢')
        raw = (push - pull) * 0.1 + (text.count('!') - text.count('?')) * 0.05

        return {
            'type': 'message',
            'content': text,
            'valence': max(-1, min(1, raw + self.field.tone * 0.3)),
            'texture': '尖锐' if '!' in text else '绵延' if '…' in text else '流动'
        }

    def _resonate(self, impact: Dict) -> Dict[str, float]:
        """认知：唤醒单元，涟漪扩散"""
        self.field.decay()

        # 直接唤醒
        for uid, unit in self.units.items():
            sim = self._similarity(impact, unit)
            if sim > 0.3:
                wake = sim * (0.8 + self.instinct['phototaxis'] * 0.4)
                self.field.touch(uid, min(1.0, wake))

        # 简单扩散（只扩散1轮）
        self._spread()

        # 混乱时沉积
        if self._chaos() > 0.7:
            from sediment import add_sediment
            add_sediment(self.field, impact)

        return self.field.activation.copy()

    def _attune(self, resonance: Dict) -> Dict:
        """情感：计算整体色调"""
        if not resonance:
            self.field.tone = 0
            self.field.tension = self.instinct['coherence']
            return {'tone': 0, 'tension': self.field.tension, 'dominant': []}

        total_val = sum(self.units[uid]['valence'] * act for uid, act in resonance.items())
        total_act = sum(resonance.values())

        self.field.tone = total_val / total_act if total_act > 0 else 0
        self.field.tension = abs(self.field.tone - self.instinct['coherence'])

        dominant = sorted(resonance.items(), key=lambda x: x[1], reverse=True)[:3]
        return {'tone': self.field.tone, 'tension': self.field.tension, 'dominant': dominant}

    def _express(self, tone: Dict) -> Dict:
        """行动：从认知单元涌出表达"""
        dominant = tone.get('dominant', [])

        if not dominant:
            return self._instinct_reply(tone)

        # 收集主导单元的痕迹
        traces = []
        depths = []
        for uid, act in dominant:
            if uid in self.units:
                u = self.units[uid]
                if u.get('traces'):
                    traces.append(u['traces'][0])
                    depths.append(u.get('depth', 0.5))

        if not traces:
            return self._instinct_reply(tone)

        # 根据深度和张力选风格
        avg_depth = sum(depths) / len(depths)
        tension = tone['tension']

        if avg_depth > 0.6 and tension > 0.5:
            style, content = '沉郁', '…'.join(t[:3] for t in traces[:2]) + '…'
        elif tension > 0.6:
            style, content = '紧绷', '！'.join(t[:4] for t in traces[:2]) + '！'
        elif avg_depth > 0.6:
            style, content = '深邃', '，'.join(traces[:2]) + '。'
        elif tone['tone'] > 0.3:
            style, content = '温暖', '～'.join(traces[:2]) + '～'
        elif tone['tone'] < -0.3:
            style, content = '疏离', traces[0] + '。'
        else:
            style, content = '自然', '，'.join(traces[:3])

        return {
            'type': 'reply',
            'style': style,
            'content': content,
            'pace': 0.5 + avg_depth * 2
        }

    def _saturate(self, action: Dict):
        """饱和：更新本能状态"""
        if action['type'] == 'reply':
            self.field.saturation['connection'] = min(1.0, 
                self.field.saturation.get('connection', 0) + 0.3)
        else:
            self.field.saturation['connection'] = max(0.0,
                self.field.saturation.get('connection', 0) - 0.1)

        for key in self.field.saturation:
            self.field.saturation[key] *= self.instinct.get('saturation_decay', 0.95)

        self.field.last_contact = datetime.now()

    # ===== 辅助函数 =====

    def _similarity(self, impact: Dict, unit: Dict) -> float:
        """轻量相似度：字重合 + 连续子串"""
        text = impact.get('content', '')
        traces = unit.get('traces', [])
        if not text or not traces:
            return 0.0

        text_chars = set(text)
        scores = []

        for trace in traces:
            trace_chars = set(trace)
            overlap = len(text_chars & trace_chars) / max(len(trace_chars), 1)

            # 连续2字匹配
            sub = sum(1 for i in range(len(trace)-1) if trace[i:i+2] in text)
            sub_score = sub / max(len(trace)-1, 1)

            scores.append(overlap * 0.6 + sub_score * 0.4)

        avg = sum(scores) / len(scores)
        threshold = 0.3 - self.instinct['phototaxis'] * 0.15
        return avg if avg > threshold else 0.0

    def _spread(self):
        """简单涟漪扩散（1轮）"""
        current = self.field.activation.copy()
        if not current:
            return

        new_act = {}
        for sid, sact in current.items():
            if sact < 0.4:
                continue
            s_unit = self.units.get(sid)
            if not s_unit:
                continue

            for tid, t_unit in self.units.items():
                if tid == sid or tid in current:
                    continue

                # 简单关联度：traces重叠
                shared = len(set(s_unit.get('traces', [])) & set(t_unit.get('traces', [])))
                affinity = shared / max(len(s_unit.get('traces', [1])), 1)

                if affinity > 0.3:
                    new_act[tid] = new_act.get(tid, 0) + sact * affinity * 0.5

        for uid, amt in new_act.items():
            cur = self.field.activation.get(uid, 0)
            self.field.touch(uid, min(1.0, cur + amt))

    def _chaos(self) -> float:
        """简单混乱度：激活分散程度"""
        acts = list(self.field.activation.values())
        if not acts:
            return 0.0

        total = sum(acts)
        if total == 0:
            return 0.0

        # 分布越均匀越混乱
        entropy = sum(-(a/total) * ((a/total) ** 0.5) for a in acts if a > 0)
        return min(1.0, entropy * (2 - self.instinct['coherence']))

    def _instinct_reply(self, tone: Dict) -> Dict:
        """本能反应"""
        p, c, b = self.instinct['phototaxis'], self.instinct['coherence'], self.instinct['boundaries']

        if p > 0.7 and tone['tension'] < 0.8:
            content, style = random.choice(['嗯…', '我在', '～']), '亲近'
        elif b > 0.6:
            content, style = '…', '封闭'
        elif c > 0.6:
            content, style = '让我想想…', '整理'
        else:
            return {'type': 'silence', 'style': '沉默', 'content': None, 'pace': 3.0}

        return {'type': 'reply', 'style': style, 'content': content, 'pace': 2.0}
