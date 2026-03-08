"""
language_center - 纯函数版指代消解
最简实现，无类，无循环导入，直接可用
"""

# ============ 1. 数据定义（用字典，不用类） ============

def make_referent(name, ref_type, aliases=None, attrs=None):
    """创建一个指代对象（字典）"""
    return {
        "id": f"{ref_type}_{name}",
        "name": name,
        "type": ref_type,  # "person", "object", "location"
        "aliases": aliases or [],
        "attrs": attrs or {},
        "last_mentioned": 0
    }

def make_empty_box(surface, position, features=None):
    """创建一个空盒子（待消解指代）"""
    # 默认特征
    defaults = {
        "我": {"person": 1, "type": "person"},
        "你": {"person": 2, "type": "person"},
        "他": {"person": 3, "gender": "male", "type": "person"},
        "她": {"person": 3, "gender": "female", "type": "person"},
        "它": {"person": 3, "type": "object"},
        "这里": {"deixis": "near", "type": "location"},
        "那里": {"deixis": "far", "type": "location"},
        "这个": {"deixis": "near", "type": "object"},
        "那个": {"deixis": "far", "type": "object"},
    }
    
    return {
        "surface": surface,
        "position": position,
        "features": {**(defaults.get(surface, {})), **(features or {})},
        "candidates": [],      # [(referent, score), ...]
        "resolution": None,    # 最终消解结果
        "confidence": 0.0,
        "status": "empty"      # "empty", "filled", "guessed"
    }


# ============ 2. 语境管理（纯函数） ============

def create_context():
    """创建空语境"""
    return {
        "referents": {},       # id -> referent
        "mention_order": [],   # 按提及顺序排列的id
        "turn": 0
    }

def add_to_context(ctx, referent):
    """向语境添加指代对象"""
    ctx["referents"][referent["id"]] = referent
    ctx["mention_order"].append(referent["id"])
    return ctx

def mention(ctx, ref_id):
    """标记提及（提升可及性）"""
    if ref_id in ctx["referents"]:
        ctx["referents"][ref_id]["last_mentioned"] = ctx["turn"]
        # 移到末尾（最近）
        ctx["mention_order"].remove(ref_id)
        ctx["mention_order"].append(ref_id)
    return ctx

def next_turn(ctx):
    """进入下一轮"""
    ctx["turn"] += 1
    return ctx


# ============ 3. 匹配打分（纯函数） ============

def match_score(box, referent, current_turn):
    """计算空盒子与指代对象的匹配分数"""
    score = 0.0
    
    # 1. 名称匹配
    if box["surface"] in [referent["name"]] + referent["aliases"]:
        score += 1.0
    
    # 2. 类型匹配
    if box["features"].get("type") == referent["type"]:
        score += 0.3
    
    # 3. 可及性（最近提及）
    recency = 1.0 / (1 + (current_turn - referent["last_mentioned"]))
    score += recency * 0.2
    
    # 4. 特征匹配（性别、人称等）
    for key in ["gender", "person"]:
        if box["features"].get(key) and referent["attrs"].get(key):
            if box["features"][key] == referent["attrs"][key]:
                score += 0.1
    
    return min(score, 1.0)

def get_candidates(ctx, box, top_k=3):
    """为盒子获取候选指代"""
    candidates = []
    
    for ref_id in reversed(ctx["mention_order"]):  # 从最近开始
        ref = ctx["referents"][ref_id]
        s = match_score(box, ref, ctx["turn"])
        
        # 类型不兼容降权
        if box["features"].get("type") != ref["type"]:
            if not (box["features"].get("type") == "object" and ref["type"] == "person"):
                s *= 0.3
        
        if s > 0.1:
            candidates.append((ref, s))
    
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[:top_k]


# ============ 4. 消解流程（纯函数） ============

PRONOUNS = {"我", "你", "他", "她", "它", "我们", "你们", "他们", "她们", "它们",
            "这里", "那里", "这边", "那边", "这个", "那个", "这些", "那些"}

def find_boxes(sentence):
    """识别句子中的空盒子（简化版：直接找代词）"""
    boxes = []
    for i, char in enumerate(sentence):
        if char in PRONOUNS:
            boxes.append(make_empty_box(char, i))
    
    # 多字代词
    for pronoun in ["这里", "那里", "这个", "那个", "这些", "那些", "我们", "你们"]:
        pos = sentence.find(pronoun)
        if pos != -1:
            boxes.append(make_empty_box(pronoun, pos))
    
    # 去重排序
    seen = set()
    unique = []
    for b in sorted(boxes, key=lambda x: x["position"]):
        if b["surface"] not in seen:
            unique.append(b)
            seen.add(b["surface"])
    
    return unique

def resolve_box(ctx, box):
    """消解单个盒子"""
    candidates = get_candidates(ctx, box)
    box["candidates"] = candidates
    
    if candidates:
        best_ref, best_score = candidates[0]
        
        if best_score > 0.7:
            box["resolution"] = best_ref
            box["confidence"] = best_score
            box["status"] = "filled"
            mention(ctx, best_ref["id"])
        elif best_score > 0.3:
            box["resolution"] = best_ref
            box["confidence"] = best_score
            box["status"] = "filled"  # 但低置信
            mention(ctx, best_ref["id"])
        else:
            # 默认规则
            _apply_default(ctx, box)
    else:
        _apply_default(ctx, box)
    
    return box

def _apply_default(ctx, box):
    """应用默认消解"""
    surface = box["surface"]
    
    if surface in ["我", "我们"]:
        box["resolution"] = make_referent("说话者", "person")
        box["confidence"] = 0.3
        box["status"] = "guessed"
    elif surface in ["你", "你们"]:
        box["resolution"] = make_referent("听话者", "person")
        box["confidence"] = 0.3
        box["status"] = "guessed"
    else:
        box["status"] = "empty"

def resolve_sentence(ctx, sentence):
    """完整消解流程"""
    next_turn(ctx)
    boxes = find_boxes(sentence)
    
    for box in boxes:
        resolve_box(ctx, box)
    
    return boxes


# ============ 5. 理解报告（纯函数） ============

def make_report(sentence, boxes):
    """生成理解报告"""
    total = len(boxes)
    filled = sum(1 for b in boxes if b["status"] == "filled")
    guessed = sum(1 for b in boxes if b["status"] == "guessed")
    empty = sum(1 for b in boxes if b["status"] == "empty")
    
    avg_conf = sum(b["confidence"] for b in boxes) / total if total else 1.0
    
    level = "清晰" if avg_conf > 0.7 else "基本理解" if avg_conf > 0.4 else "模糊" if avg_conf > 0.2 else "困惑"
    
    return {
        "sentence": sentence,
        "level": level,
        "confidence": round(avg_conf, 2),
        "stats": {"total": total, "filled": filled, "guessed": guessed, "empty": empty},
        "boxes": [
            {
                "surface": b["surface"],
                "resolved_to": b["resolution"]["name"] if b["resolution"] else None,
                "confidence": round(b["confidence"], 2),
                "status": b["status"]
            }
            for b in boxes
        ]
    }


# ============ 6. 简单回应生成（纯函数） ============

def generate_response(report):
    """基于理解报告生成简单回应"""
    level = report["level"]
    boxes = report["boxes"]
    
    if level == "困惑":
        # 询问未消解的
        unknown = [b["surface"] for b in boxes if b["resolved_to"] is None]
        if unknown:
            return f"我不太明白「{'」「'.join(unknown)}」指什么？"
        return "我不太明白你的意思。"
    
    if level == "模糊":
        # 确认理解
        resolutions = [f"「{b['surface']}」是{b['resolved_to']}" for b in boxes if b["resolved_to"]]
        if resolutions:
            return "你是说" + "，".join(resolutions) + "对吗？"
        return "我理解对了吗？"
    
    # 清晰
    return "我明白了。"


# ============ 7. 完整使用示例 ============

def demo():
    """演示"""
    print("=" * 40)
    print("Language Center - 纯函数版演示")
    print("=" * 40)
    
    # 1. 创建语境
    ctx = create_context()
    
    # 2. 添加已知指代（模拟对话历史）
    add_to_context(ctx, make_referent("小李", "person", ["他"], {"gender": "male"}))
    add_to_context(ctx, make_referent("碧叶", "person", ["你"], {"gender": "female"}))
    add_to_context(ctx, make_referent("手机", "object", ["它"], {"movable": True}))
    add_to_context(ctx, make_referent("书桌", "location", ["那里"], {}))
    
    print(f"\n初始语境: {list(ctx['referents'].keys())}")
    
    # 3. 处理句子
    sentence = "我把它放在那里了"
    print(f"\n输入: {sentence}")
    
    boxes = resolve_sentence(ctx, sentence)
    
    print("\n消解结果:")
    for b in boxes:
        if b["resolution"]:
            icon = "✓" if b["confidence"] > 0.6 else "?"
            print(f"  {icon} 「{b['surface']}」→ {b['resolution']['name']} ({b['confidence']:.2f})")
        else:
            print(f"  ✗ 「{b['surface']}」→ 未消解")
    
    # 4. 理解报告
    report = make_report(sentence, boxes)
    print(f"\n理解程度: {report['level']} (置信度: {report['confidence']})")
    
    # 5. 生成回应
    response = generate_response(report)
    print(f"\n回应: {response}")
    
    # 6. 第二轮（测试可及性更新）
    print("\n" + "-" * 40)
    sentence2 = "他看到了"
    print(f"输入: {sentence2}")
    
    boxes2 = resolve_sentence(ctx, sentence2)
    print("消解结果:")
    for b in boxes2:
        if b["resolution"]:
            print(f"  「{b['surface']}」→ {b['resolution']['name']} ({b['confidence']:.2f})")
    
    report2 = make_report(sentence2, boxes2)
    print(f"\n回应: {generate_response(report2)}")


if __name__ == "__main__":
    demo()