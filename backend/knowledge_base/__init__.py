from .default_data import NUTRITION_KNOWLEDGE


def init_knowledge_base():
    try:
        from app.services.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        collection = kb.get_or_create_collection()
        
        if collection.count() == 0:
            kb.add_documents(NUTRITION_KNOWLEDGE)
            print("知识库初始化完成，已添加", len(NUTRITION_KNOWLEDGE), "条营养知识")
        else:
            print("知识库已存在数据，跳过初始化")
    except Exception as e:
        print("知识库初始化失败:", str(e))
        print("应用将继续运行，但知识库功能可能受限")