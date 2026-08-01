"""营养知识库服务

架构（三层）：
1. 向量化：Ollama qwen-emb 语义向量为主，jieba 哈希向量离线兜底（EMBEDDING_PROVIDER）
2. 存储检索：ChromaDB 向量库（VECTOR_STORE=chroma）做 ANN 粗排；
   不可用时自动降级为纯 Python JSON 内存检索（VECTOR_STORE=json / 异常降级）
3. 重排：自研混合打分（余弦相似度 + 词频重叠），对候选做精排
"""
import hashlib
import json
import math
import os
import re
import sys
import urllib.request
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import jieba

from app.core.config import settings


EMBED_DIM = 512  # hash 向量维度（Ollama 向量维度由模型决定，qwen-emb 为 1024）
DATA_FILE = "nutrition_knowledge.json"

# Qwen3-Embedding 官方要求 query 与文档使用不同的指令前缀
QUERY_PREFIX = (
    "Instruct: Given a web search query, retrieve relevant passages "
    "that answer the query\nQuery: "
)
DOC_PREFIX = "Represent this sentence for searching relevant passages: "


def _ensure_windows_runtime():
    """Windows 下将项目自带 VC++ 运行库目录加入 DLL 搜索路径。

    本机 System32 运行库过旧（14.00）会导致 onnxruntime/chromadb 原生库加载失败，
    该函数在 import chromadb 之前调用；其他平台直接跳过。
    """
    if sys.platform != "win32" or not hasattr(os, "add_dll_directory"):
        return
    dll_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "vendor", "win_runtime")
    )
    if os.path.isdir(dll_dir):
        try:
            os.add_dll_directory(dll_dir)
        except Exception:
            pass


def _tokenize(text: str) -> List[str]:
    """将文本切成 ASCII 词 + jieba 中文词 + 中文二元组，用于本地向量化"""
    text = text.lower()
    words = re.findall(r"[a-z0-9]+", text)
    seg_words = [
        w.strip()
        for w in jieba.cut(text, cut_all=False)
        if w.strip() and len(w.strip()) <= 6
    ]
    hanzi = re.findall(r"[\u4e00-\u9fff]", text)
    bigrams = [hanzi[i] + hanzi[i + 1] for i in range(len(hanzi) - 1)]
    return words + seg_words + bigrams


def embed_text(text: str, dim: int = EMBED_DIM) -> List[float]:
    """确定性哈希向量：无需任何外部模型/网络，离线兜底 embedding"""
    vec = [0.0] * dim
    for token in _tokenize(text):
        digest = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        sign = 1.0 if (digest >> 8) & 1 else -1.0
        vec[digest % dim] += sign
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class KnowledgeBase:
    """营养知识库管理类（支持 chroma / json 两种存储后端）"""

    def __init__(
        self,
        persist_dir: str = None,
        provider: str = None,
        vector_store: str = None,
        ollama_base_url: str = None,
        ollama_model: str = None,
    ):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        self.data_path = os.path.join(self.persist_dir, DATA_FILE)
        self.provider = (provider or settings.EMBEDDING_PROVIDER or "hash").lower()
        self.vector_store = (vector_store or settings.VECTOR_STORE or "json").lower()
        self.ollama_base_url = (ollama_base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.ollama_model = ollama_model or settings.OLLAMA_EMBED_MODEL
        self._client = None
        self._collection = None

    # ---------- 持久化（JSON 为数据源） ----------

    def _load(self) -> List[Dict]:
        if not os.path.exists(self.data_path):
            return []
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"读取知识库数据失败: {e}")
            return []

    def _save(self, documents: List[Dict]):
        os.makedirs(self.persist_dir, exist_ok=True)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)

    def count(self) -> int:
        """当前文档数"""
        return len(self._load())

    # ---------- 文档写入 ----------

    def add_documents(self, documents: List[Dict]):
        """以内容哈希去重，追加写入，并同步向量库"""
        existing = self._load()
        existing_ids = {doc["id"] for doc in existing}
        added = 0
        for doc in documents:
            doc_id = hashlib.md5(doc["content"].encode("utf-8")).hexdigest()[:16]
            if doc_id not in existing_ids:
                existing.append(
                    {
                        "id": doc_id,
                        "content": doc["content"],
                        "source": doc.get("source", ""),
                        "category": doc.get("category", ""),
                    }
                )
                existing_ids.add(doc_id)
                added += 1
        self._save(existing)
        print(
            f"成功写入 {len(documents)} 条文档"
            f"（新增 {added} 条，当前共 {len(existing)} 条）"
        )
        self.ensure_embeddings()
        self.sync_chroma()

    def reset(self, documents: List[Dict]):
        """清空并重建（种子数据更新时使用）"""
        self._save([])
        self.add_documents(documents)

    def ensure_embeddings(self):
        """为缺少向量缓存的文档补齐 embedding（切换提供方后自动迁移）"""
        if self.provider != "ollama":
            return
        documents = self._load()
        missing = [d for d in documents if not d.get("embedding")]
        if not missing:
            return
        embeddings = self._ollama_embed([DOC_PREFIX + d["content"] for d in missing])
        if not embeddings:
            print("[知识库] Ollama 不可用，本次跳过向量缓存（检索时自动回退哈希向量）")
            return
        for doc, vec in zip(missing, embeddings):
            doc["embedding"] = vec
        self._save(documents)
        print(f"[知识库] 已缓存 {len(missing)} 条文档的 Ollama embedding")

    # ---------- ChromaDB 向量库 ----------

    def _get_collection(self):
        """惰性创建 Chroma 集合；不可用时返回 None（自动降级 JSON）"""
        if self.vector_store != "chroma":
            return None
        if self._collection is not None:
            return self._collection
        try:
            _ensure_windows_runtime()
            import chromadb

            self._client = chromadb.PersistentClient(path=self.persist_dir)
            self._collection = self._client.get_or_create_collection(
                name="nutrition_knowledge",
                metadata={"hnsw:space": "cosine"},
            )
            return self._collection
        except Exception as e:
            print(f"[知识库] ChromaDB 不可用，降级 JSON 检索: {e}")
            return None

    def sync_chroma(self):
        """把 JSON 数据源同步进 ChromaDB（向量由 Ollama 计算）"""
        collection = self._get_collection()
        if collection is None or self.provider != "ollama":
            return
        documents = self._load()
        if not documents:
            return
        embeddings = self._ollama_embed([DOC_PREFIX + d["content"] for d in documents])
        if not embeddings:
            print("[知识库] Ollama 不可用，跳过 Chroma 同步")
            return
        try:
            if collection.count() != len(documents):
                # 数量不一致：重建集合（chroma 1.5.x 不支持 delete(where={}) 清空）
                if self._client is not None:
                    try:
                        self._client.delete_collection(collection.name)
                    except Exception:
                        pass
                self._collection = None
                collection = self._get_collection()
                if collection is None:
                    return
            collection.upsert(
                ids=[d["id"] for d in documents],
                embeddings=embeddings,
                documents=[d["content"] for d in documents],
                metadatas=[
                    {"source": d.get("source", ""), "category": d.get("category", "")}
                    for d in documents
                ],
            )
            print(f"[知识库] 已同步 {len(documents)} 条文档到 ChromaDB")
        except Exception as e:
            print(f"[知识库] Chroma 同步失败: {e}")

    # ---------- 向量化 ----------

    def _ollama_embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        """调用 Ollama /api/embed，失败返回 None"""
        try:
            payload = json.dumps(
                {"model": self.ollama_model, "input": texts}
            ).encode("utf-8")
            req = urllib.request.Request(
                self.ollama_base_url + "/api/embed",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            embeddings = data.get("embeddings")
            return embeddings if embeddings else None
        except Exception as e:
            print(f"[知识库] Ollama embedding 调用失败，回退本地哈希向量: {e}")
            return None

    def _embed_query(self, query: str) -> Tuple[List[float], str]:
        """返回 (query 向量, 使用的提供方)。ollama 失败时回退 hash"""
        if self.provider == "ollama":
            result = self._ollama_embed([QUERY_PREFIX + query])
            if result:
                return result[0], "ollama"
        return embed_text(query), "hash"

    # ---------- 检索 ----------

    def _chroma_candidates(
        self, query: str, n_candidates: int
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[List[float]]]:
        """Chroma 向量粗排：返回候选文档列表与查询向量；不可用返回 (None, None)"""
        collection = self._get_collection()
        if collection is None or self.provider != "ollama":
            return None, None
        query_vec, provider = self._embed_query(query)
        if provider != "ollama":
            return None, None
        try:
            result = collection.query(
                query_embeddings=[query_vec],
                n_results=n_candidates,
                include=["documents", "metadatas"],
            )
            docs = (result.get("documents") or [[]])[0]
            metas = (result.get("metadatas") or [[]])[0]
            return [
                {"content": d, "metadata": m or {}}
                for d, m in zip(docs, metas)
            ], query_vec
        except Exception as e:
            print(f"[知识库] Chroma 查询失败，降级 JSON 检索: {e}")
            return None, None

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """混合检索：向量粗排（Chroma/内存） + 自研重排（余弦 + 词频重叠）"""
        documents = self._load()
        if not documents:
            return []

        query_counter = Counter(_tokenize(query))
        query_total = sum(query_counter.values()) or 1

        # 1) Chroma 向量粗排（仅 Ollama 提供方可用）
        candidates, query_vec = self._chroma_candidates(
            query, max(n_results * 4, 20)
        )
        if candidates is not None:
            provider = "ollama"
            vec_weight, overlap_weight = 0.75, 0.25
            by_content = {d["content"]: d for d in documents}
            scored = []
            for cand in candidates:
                doc = by_content.get(cand["content"])
                if not doc or not doc.get("embedding"):
                    continue
                vec_score = _cosine_similarity(query_vec, doc["embedding"])
                doc_counter = Counter(_tokenize(doc["content"]))
                overlap = (
                    sum(min(query_counter[t], doc_counter[t]) for t in query_counter)
                    / query_total
                )
                score = vec_weight * vec_score + overlap_weight * overlap
                scored.append((score, doc))
        else:
            # 2) 降级路径：内存检索（Ollama 缓存向量 / 哈希向量）
            query_vec, provider = self._embed_query(query)
            if provider == "ollama":
                vec_weight, overlap_weight = 0.75, 0.25
            else:
                vec_weight, overlap_weight = 0.55, 0.45
            scored = []
            for doc in documents:
                if provider == "ollama" and doc.get("embedding"):
                    doc_vec = doc["embedding"]
                else:
                    doc_vec = embed_text(doc["content"])
                vec_score = _cosine_similarity(query_vec, doc_vec)
                doc_counter = Counter(_tokenize(doc["content"]))
                overlap = (
                    sum(min(query_counter[t], doc_counter[t]) for t in query_counter)
                    / query_total
                )
                score = vec_weight * vec_score + overlap_weight * overlap
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "content": doc["content"],
                "metadata": {
                    "source": doc.get("source", ""),
                    "category": doc.get("category", ""),
                },
                "distance": round(1.0 - score, 6),  # cosine distance，兼容原返回结构
            }
            for score, doc in scored[:n_results]
        ]
