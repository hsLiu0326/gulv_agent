import math

from app.services.knowledge_base import KnowledgeBase, embed_text


DOCS = [
    {
        "content": "高血压饮食注意事项：控制盐分摄入有助于降低血压，建议每日盐摄入量不超过5克。",
        "source": "中国高血压防治指南",
        "category": "血压管理",
    },
    {
        "content": "血糖管理饮食指南：低糖饮食有助于控制血糖水平，选择低GI食物如燕麦、糙米。",
        "source": "中国糖尿病医学营养治疗指南",
        "category": "血糖管理",
    },
    {
        "content": "运动补水原则：运动前2小时补水400-600毫升，运动后按体重丢失量补充。",
        "source": "运动营养学",
        "category": "运动营养",
    },
]


def test_embed_text_deterministic_and_normalized():
    v1 = embed_text("高血压 少吃盐")
    v2 = embed_text("高血压 少吃盐")
    assert v1 == v2
    assert len(v1) == 512
    assert abs(math.sqrt(sum(x * x for x in v1)) - 1.0) < 1e-6


def test_add_documents_dedup(tmp_path):
    kb = KnowledgeBase(persist_dir=str(tmp_path), provider="hash", vector_store="json")
    kb.add_documents(DOCS)
    assert kb.count() == 3
    kb.add_documents(DOCS)  # 重复添加应去重
    assert kb.count() == 3


def test_reset(tmp_path):
    kb = KnowledgeBase(persist_dir=str(tmp_path), provider="hash", vector_store="json")
    kb.add_documents(DOCS)
    kb.reset(DOCS[:1])
    assert kb.count() == 1


def test_search_hash_top1(tmp_path):
    kb = KnowledgeBase(persist_dir=str(tmp_path), provider="hash", vector_store="json")
    kb.add_documents(DOCS)
    results = kb.search("高血压 少吃盐", n_results=3)
    assert results[0]["metadata"]["category"] == "血压管理"
    assert results[0]["content"].startswith("高血压饮食注意事项")
