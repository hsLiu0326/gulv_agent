"""Windows 原生运行库引导（必须在任何第三方原生依赖导入之前调用）

本机 System32 的 VC++ 运行库过旧（14.00）：若 chromadb 的原生绑定在
fastapi/pydantic-core 等库之后才首次初始化，会因运行库不匹配直接崩溃
（access violation）。该模块做两件事：
1) 把项目自带的 14.44 版运行库目录（backend/vendor/win_runtime）加入 DLL 搜索路径；
2) 用 EphemeralClient 执行一次 chroma 写入+查询，提前初始化原生绑定。

在 app/main.py 的第一行调用；Linux/macOS 与运行库正常的机器上为无操作。
"""
import os
import sys


def ensure_windows_bootstrap():
    if sys.platform != "win32" or not hasattr(os, "add_dll_directory"):
        return
    dll_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "vendor", "win_runtime")
    )
    if not os.path.isdir(dll_dir):
        return
    try:
        os.add_dll_directory(dll_dir)
        import chromadb

        collection = chromadb.EphemeralClient().get_or_create_collection(
            name="warmup", metadata={"hnsw:space": "cosine"}
        )
        # 必须执行实际写入+查询，初始化 HNSW 段（仅 count 无效）
        collection.upsert(
            ids=["warmup"],
            embeddings=[[0.1, 0.2, 0.3]],
            documents=["warmup"],
        )
        collection.query(query_embeddings=[[0.1, 0.2, 0.3]], n_results=1)
    except Exception:
        pass
