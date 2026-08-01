"""Windows 运行库准备脚本

本机 System32 的 VC++ 运行库过旧（vcruntime140/msvcp140 等为 14.00 版），
导致 onnxruntime / chromadb 等原生库加载失败。本脚本从本机 Ollama 安装目录
复制一份 14.44 版运行库到 backend/vendor/win_runtime，应用启动时通过
os.add_dll_directory 将其加入 DLL 搜索路径（仅 Windows、仅本项目，不改系统）。

用法：python scripts/setup_win_runtime.py
"""
import os
import shutil
import sys


OLLAMA_LIB_CANDIDATES = [
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\lib\ollama\cuda_v12"),
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\lib\ollama\vulkan"),
]
RUNTIME_FILES = (
    "concrt140.dll",
    "msvcp140.dll",
    "msvcp140_1.dll",
    "msvcp140_2.dll",
    "msvcp140_atomic_wait.dll",
    "msvcp140_codecvt_ids.dll",
    "vcruntime140.dll",
    "vcruntime140_1.dll",
    "vcruntime140_threads.dll",
)


def main():
    src = next((d for d in OLLAMA_LIB_CANDIDATES if os.path.isdir(d)), None)
    if src is None:
        print("未找到 Ollama 运行库目录，请先安装 Ollama 或手动安装 VC++ 运行库")
        sys.exit(1)

    dest = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "vendor", "win_runtime")
    )
    os.makedirs(dest, exist_ok=True)
    copied = 0
    for name in RUNTIME_FILES:
        path = os.path.join(src, name)
        if os.path.exists(path):
            shutil.copy2(path, os.path.join(dest, name))
            copied += 1
    print(f"已复制 {copied} 个运行库文件到 {dest}")
    print("请确认 app/services/knowledge_base.py 顶部的 DLL 路径与此目录一致。")


if __name__ == "__main__":
    main()
