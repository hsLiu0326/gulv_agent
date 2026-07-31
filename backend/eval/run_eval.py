"""AI 能力评测脚本：体检报告解析 + 知识库检索

用法（在 backend 目录下执行）：
    python eval/run_eval.py                      # 使用默认配置的 embedding 提供方
    python eval/run_eval.py --provider hash      # 强制哈希向量（完全离线）
    python eval/run_eval.py --provider ollama    # 使用 Ollama 语义向量

用途：修改提示词 / 知识库 / 解析规则后跑一遍，确认没有回归。
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.health_report_parser import HealthReportParser
from app.services.knowledge_base import KnowledgeBase


CASES_DIR = Path(__file__).parent / "cases"


def load_cases(name: str):
    with open(CASES_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def eval_report_parse(cases) -> tuple:
    """体检报告解析评测（正则部分，完全离线确定性）"""
    parser = HealthReportParser()
    ok = total = 0
    for case in cases:
        result = parser._regex_parse(case["content"])
        expected = case["expected"]
        match = all(result.get(k) == v for k, v in expected.items())
        total += 1
        if match:
            ok += 1
        else:
            print(f"  [FAIL] {case['name']}: got {result}")
    return ok, total


def eval_kb_search(cases, provider: str) -> tuple:
    """知识库检索评测：期望分类出现在 top3"""
    kb = KnowledgeBase(provider=provider)
    ok = total = 0
    for case in cases:
        results = kb.search(case["query"], n_results=3)
        categories = [r["metadata"]["category"] for r in results]
        if case["expected_category"] in categories:
            ok += 1
        else:
            print(f"  [FAIL] {case['query']} -> {categories}")
        total += 1
    return ok, total


def main():
    parser = argparse.ArgumentParser(description="AI 能力评测")
    parser.add_argument(
        "--provider",
        default=None,
        choices=["hash", "ollama"],
        help="知识库 embedding 提供方，默认使用配置",
    )
    args = parser.parse_args()

    print("=== 体检报告解析评测（离线正则）===")
    ok, total = eval_report_parse(load_cases("report_parse_cases.json"))
    print(f"解析通过率: {ok}/{total}")

    print(f"\n=== 知识库检索评测（provider={args.provider or 'config'}）===")
    ok, total = eval_kb_search(load_cases("kb_retrieval_cases.json"), args.provider)
    print(f"检索通过率: {ok}/{total}")


if __name__ == "__main__":
    main()
