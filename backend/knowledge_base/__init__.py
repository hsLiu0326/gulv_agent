from .default_data import NUTRITION_KNOWLEDGE


def init_knowledge_base():
    try:
        from app.services.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        count = kb.count()
        if count == 0:
            kb.add_documents(NUTRITION_KNOWLEDGE)
            print("知识库初始化完成，已添加", len(NUTRITION_KNOWLEDGE), "条营养知识")
        elif count != len(NUTRITION_KNOWLEDGE):
            # 种子数据已更新：重建集合（该集合由种子数据生成，可安全重建）
            print(
                f"检测到种子数据更新（当前 {count} 条，期望 {len(NUTRITION_KNOWLEDGE)} 条），重建知识库..."
            )
            kb.reset(NUTRITION_KNOWLEDGE)
            print("知识库重建完成，已添加", len(NUTRITION_KNOWLEDGE), "条营养知识")
        else:
            print("知识库已存在数据，跳过初始化")
        # 补齐向量缓存（首次使用 Ollama 或切换提供方后自动迁移）
        kb.ensure_embeddings()
    except Exception as e:
        print("知识库初始化失败:", str(e))
        print("应用将继续运行，但知识库功能可能受限")
