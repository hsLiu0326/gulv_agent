"""营养知识库服务 — 本地向量检索

向量化提供方（EMBEDDING_PROVIDER）：
- ollama：调用本地 Ollama 的 embedding 模型（默认 qwen-emb，1024 维），
  语义检索质量最好；服务不可用时自动回退到 hash 向量，不会中断功能。
- hash：纯 Python 哈希向量（jieba 分词 + n-gram 哈希），无任何模型依赖。

文档向量一次性算好后持久化到 JSON（CHROMA_PERSIST_DIR），
检索时只需对 query 实时向量化。
"""
import hashlib
import json
import math
import os
import re
import urllib.request
from collections import Counter
from typing import Dict, List, Optional

import jieba

from app.core.config import settings


EMBED_DIM = 512  # hash 向量维度（ollama 向量维度由模型决定，qwen-emb 为 1024）
DATA_FILE = "nutrition_knowledge.json"

# Qwen3-Embedding 官方要求 query 与文档使用不同的指令前缀
QUERY_PREFIX = (
    "Instruct: Given a web search query, retrieve relevant passages "
    "that answer the query\nQuery: "
)
DOC_PREFIX = "Represent this sentence for searching relevant passages: "


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
    """营养知识库管理类"""

    def __init__(
        self,
        persist_dir: str = None,
        provider: str = None,
        ollama_base_url: str = None,
        ollama_model: str = None,
    ):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        self.data_path = os.path.join(self.persist_dir, DATA_FILE)
        self.provider = (provider or settings.EMBEDDING_PROVIDER or "hash").lower()
        self.ollama_base_url = (ollama_base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.ollama_model = ollama_model or settings.OLLAMA_EMBED_MODEL

    # ---------- 持久化 ----------

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
        """以内容哈希去重，追加写入，并补齐向量缓存"""
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

    def _embed_query(self, query: str) -> tuple:
        """返回 (query 向量, 使用的提供方)。ollama 失败时回退 hash"""
        if self.provider == "ollama":
            result = self._ollama_embed([QUERY_PREFIX + query])
            if result:
                return result[0], "ollama"
        return embed_text(query), "hash"

    # ---------- 检索 ----------

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """混合检索：向量余弦相似度 + 查询词重叠度"""
        documents = self._load()
        if not documents:
            return []

        query_vec, provider = self._embed_query(query)
        # 语义向量质量高，语义权重更大；哈希兜底时更依赖关键词重叠
        if provider == "ollama":
            vec_weight, overlap_weight = 0.75, 0.25
        else:
            vec_weight, overlap_weight = 0.55, 0.45

        query_counter = Counter(_tokenize(query))
        query_total = sum(query_counter.values()) or 1
        scored = []
        for doc in documents:
            content = doc["content"]
            if provider == "ollama" and doc.get("embedding"):
                doc_vec = doc["embedding"]
            else:
                doc_vec = embed_text(content)
            vec_score = _cosine_similarity(query_vec, doc_vec)
            doc_counter = Counter(_tokenize(content))
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
