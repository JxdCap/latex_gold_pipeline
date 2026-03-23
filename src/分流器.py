import argparse
import json
from pathlib import Path

try:
    from .导出表格 import 双格式写出
except ImportError:
    from 导出表格 import 双格式写出


def 读取_jsonl(输入路径: str | Path) -> list[dict]:
    结果 = []
    with Path(输入路径).open("r", encoding="utf-8") as 文件:
        for 行 in 文件:
            行 = 行.strip()
            if 行:
                结果.append(json.loads(行))
    return 结果


def 执行分流(记录列表: list[dict]) -> tuple[list[dict], list[dict]]:
    自动处理记录: list[dict] = []
    人工复核记录: list[dict] = []

    for 记录 in 记录列表:
        分桶结果 = 记录.get("分桶结果", "")
        是否待复核 = bool(记录.get("是否待复核", False))

        if 是否待复核 or 分桶结果 in {"疑难样本", "空白样本"}:
            分流结果 = "人工复核队列"
            分流依据 = "命中待复核或保守桶型"
        else:
            分流结果 = "自动处理队列"
            分流依据 = "样本可直接进入自动处理队列"

        新记录 = dict(记录)
        新记录["分流结果"] = 分流结果
        新记录["分流依据"] = 分流依据

        if 分流结果 == "人工复核队列":
            人工复核记录.append(新记录)
        else:
            自动处理记录.append(新记录)

    return 自动处理记录, 人工复核记录


def 导出分流结果(
    自动处理记录: list[dict],
    人工复核记录: list[dict],
    自动处理目录: str | Path,
    人工复核目录: str | Path,
) -> None:
    双格式写出(
        自动处理记录,
        Path(自动处理目录) / "自动处理样本.jsonl",
        Path(自动处理目录) / "自动处理样本.xlsx",
    )
    双格式写出(
        人工复核记录,
        Path(人工复核目录) / "人工复核样本.jsonl",
        Path(人工复核目录) / "人工复核样本.xlsx",
    )


def main() -> None:
    参数解析器 = argparse.ArgumentParser(description="执行保守分流。")
    参数解析器.add_argument("--输入文件", default="data/分桶结果/分桶样本.jsonl")
    参数解析器.add_argument("--自动处理目录", default="data/自动处理队列")
    参数解析器.add_argument("--人工复核目录", default="data/人工复核队列")
    参数 = 参数解析器.parse_args()

    记录列表 = 读取_jsonl(参数.输入文件)
    自动处理记录, 人工复核记录 = 执行分流(记录列表)
    导出分流结果(自动处理记录, 人工复核记录, 参数.自动处理目录, 参数.人工复核目录)


if __name__ == "__main__":
    main()
