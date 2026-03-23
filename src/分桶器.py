import argparse
import json
import re
from pathlib import Path

import yaml

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


def 读取分桶规则(规则文件: str | Path = "configs/分桶规则.yaml") -> dict:
    with Path(规则文件).open("r", encoding="utf-8") as 文件:
        return yaml.safe_load(文件)


def 执行分桶(记录列表: list[dict], 规则: dict) -> list[dict]:
    桶名 = 规则["桶名"]
    LaTeX正则列表 = [re.compile(表达式) for 表达式 in 规则["LaTeX判定正则"]]
    结果 = []

    for 记录 in 记录列表:
        清洗后文本 = str(记录.get("清洗后文本", ""))
        轻预洗标记 = 记录.get("轻预洗标记", [])
        是否待复核 = bool(记录.get("是否待复核", False))

        if not 清洗后文本:
            分桶结果 = 桶名["空白样本"]
            分桶依据 = "清洗后文本为空"
        elif 是否待复核 or "命中疑难模式" in 轻预洗标记:
            分桶结果 = 桶名["疑难样本"]
            分桶依据 = "轻预洗阶段标记为待复核"
        elif any(正则.search(清洗后文本) for 正则 in LaTeX正则列表):
            分桶结果 = 桶名["LaTeX样本"]
            分桶依据 = "命中 LaTeX 特征"
        else:
            分桶结果 = 桶名["普通文本"]
            分桶依据 = "未命中疑难与 LaTeX 特征"

        新记录 = dict(记录)
        新记录["分桶结果"] = 分桶结果
        新记录["分桶依据"] = 分桶依据
        结果.append(新记录)

    return 结果


def 导出分桶结果(记录列表: list[dict], 输出目录: str | Path) -> None:
    目录 = Path(输出目录)
    双格式写出(
        记录列表,
        目录 / "分桶样本.jsonl",
        目录 / "分桶样本.xlsx",
    )


def main() -> None:
    参数解析器 = argparse.ArgumentParser(description="执行分桶。")
    参数解析器.add_argument("--输入文件", default="data/原始数据/轻预洗样本.jsonl")
    参数解析器.add_argument("--规则文件", default="configs/分桶规则.yaml")
    参数解析器.add_argument("--输出目录", default="data/分桶结果")
    参数 = 参数解析器.parse_args()

    记录列表 = 读取_jsonl(参数.输入文件)
    规则 = 读取分桶规则(参数.规则文件)
    结果 = 执行分桶(记录列表, 规则)
    导出分桶结果(结果, 参数.输出目录)


if __name__ == "__main__":
    main()
