"""营养知识库服务"""
import chromadb
from typing import List, Dict
from app.core.config import settings
from langchain_openai import OpenAIEmbeddings


class KnowledgeBase:
    """营养知识库管理类"""

    def __init__(self):
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL
        )
        self.collection_name = "nutrition_knowledge"

    def get_or_create_collection(self):
        """获取或创建集合"""
        return self.client.get_or_create_collection(name=self.collection_name)

    def add_documents(self, documents: List[Dict]):
        """添加文档到知识库"""
        collection = self.get_or_create_collection()

        ids = [str(i) for i in range(len(documents))]
        texts = [doc["content"] for doc in documents]
        metadatas = [{"source": doc.get("source", ""), "category": doc.get("category", "")} for doc in documents]

        # 生成嵌入向量
        embeddings = self.embeddings.embed_documents(texts)

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """搜索知识库"""
        collection = self.get_or_create_collection()

        # 生成查询嵌入
        query_embedding = self.embeddings.embed_query(query)

        results = collection.query(
            query_embeddings=[query_embedding],
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