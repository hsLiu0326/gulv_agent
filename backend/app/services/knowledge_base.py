"""营养知识库服务"""
import chromadb
from typing import List, Dict
from app.core.config import settings


class KnowledgeBase:
    """营养知识库管理类"""

    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection_name = "nutrition_knowledge"

    def get_or_create_collection(self):
        """获取或创建集合"""
        try:
            collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            return collection
        except Exception as e:
            print(f"创建集合失败: {e}")
            try:
                collections = self.client.list_collections()
                if collections:
                    return self.client.get_collection(self.collection_name)
            except Exception:
                pass
            return None

    def add_documents(self, documents: List[Dict]):
        """添加文档到知识库"""
        collection = self.get_or_create_collection()
        if not collection:
            print("无法获取集合，跳过添加文档")
            return

        ids = [str(i) for i in range(len(documents))]
        texts = [doc["content"] for doc in documents]
        metadatas = [{"source": doc.get("source", ""), "category": doc.get("category", "")} for doc in documents]

        try:
            collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            print(f"成功添加 {len(documents)} 条文档")
        except Exception as e:
            print(f"添加文档失败: {e}")

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """搜索知识库"""
        collection = self.get_or_create_collection()
        if not collection:
            return []

        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )

            documents = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None
                    })

            return documents
        except Exception as e:
            print(f"搜索失败: {e}")
            return []