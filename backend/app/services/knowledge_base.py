"""营养知识库服务"""​
import chromadb​
        collection = self.get_or_create_collection()​
        ​
        ids = [str(i) for i in range(len(documents))]​
        texts = [doc["content"] for doc in documents]​
        metadatas = [{"source": doc.get("source", ""), "category": doc.get("category", "")} for doc in documents]​
        ​
        # 生成嵌入向量​
        embeddings = self.embeddings.embed_documents(texts)​
        ​
        collection.add(​
            ids=ids,​
            embeddings=embeddings,​
            documents=texts,​
            metadatas=metadatas​
        )​
    ​
    def search(self, query: str, n_results: int = 5) -> List[Dict]:​
        """搜索知识库"""​
        collection = self.get_or_create_collection()​
        ​
        # 生成查询嵌入​
        query_embedding = self.embeddings.embed_query(query)​
        ​
        results = collection.query(​
            query_embeddings=[query_embedding],​
            n_results=n_results​
        )​
        ​
        documents = []​
        if results["documents"]:​
            for i, doc in enumerate(results["documents"][0]):​
                documents.append({​
                    "content": doc,​
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},​
                    "distance": results["distances"][0][i] if results["distances"] else None​
                })​
        ​
        return documents