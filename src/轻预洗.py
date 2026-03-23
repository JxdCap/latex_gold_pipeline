import argparse
import json
import re
from pathlib import Path

import yaml

try:
    from .导出表格 import 双格式写出
except ImportError:
    from 导出表格 import 双格式写出

行内空白正则 = re.compile(r"[ \t]+")
连续空行正则 = re.compile(r"\n{3,}")


def 读取_jsonl(输入路径: str | Path) -> list[dict]:
    结果 = []
    with Path(输入路径).open("r", encoding="utf-8") as 文件:
        for 行 in 文件:
            行 = 行.strip()
            if 行:
                结果.append(json.loads(行))
    return 结果


def 读取轻预洗规则(规则文件: str | Path = "configs/轻预洗规则.yaml") -> dict:
    with Path(规则文件).open("r", encoding="utf-8") as 文件:
        return yaml.safe_load(文件)


def 执行轻预洗(记录列表: list[dict], 规则: dict) -> list[dict]:
    标记配置 = 规则["输出标记"]
    疑难模式 = tuple(规则["疑难模式"])
    结果 = []

    for 记录 in 记录列表:
        原文本 = str(记录.get("原文本", ""))
        清洗后文本 = 原文本.replace("\r\n", "\n").replace("\r", "\n")
        清洗后文本 = "\n".join(行内空白正则.sub(" ", 行).strip() for 行 in 清洗后文本.split("\n"))
        清洗后文本 = 连续空行正则.sub("\n\n", 清洗后文本).strip()

        轻预洗标记: list[str] = []
        if not 清洗后文本:
            轻预洗标记.append(标记配置["空文本"])
        if 原文本 != 清洗后文本:
            轻预洗标记.append(标记配置["空白规范化"])
        if any(模式 in 原文本 for 模式 in 疑难模式):
            轻预洗标记.append(标记配置["命中疑难模式"])

        新记录 = dict(记录)
        新记录["清洗后文本"] = 清洗后文本
        新记录["轻预洗标记"] = 轻预洗标记
        新记录["是否待复核"] = (
            标记配置["空文本"] in 轻预洗标记 or 标记配置["命中疑难模式"] in 轻预洗标记
        )
        结果.append(新记录)

    return 结果


def 导出轻预洗结果(记录列表: list[dict], 输出目录: str | Path) -> None:
    目录 = Path(输出目录)
    双格式写出(
        记录列表,
        目录 / "轻预洗样本.jsonl",
        目录 / "轻预洗样本.xlsx",
    )


def main() -> None:
    参数解析器 = argparse.ArgumentParser(description="执行轻预洗。")
    参数解析器.add_argument("--输入文件", default="data/原始数据/原始样本.jsonl")
    参数解析器.add_argument("--规则文件", default="configs/轻预洗规则.yaml")
    参数解析器.add_argument("--输出目录", default="data/原始数据")
    参数 = 参数解析器.parse_args()

    记录列表 = 读取_jsonl(参数.输入文件)
    规则 = 读取轻预洗规则(参数.规则文件)
    结果 = 执行轻预洗(记录列表, 规则)
    导出轻预洗结果(结果, 参数.输出目录)


if __name__ == "__main__":
    main()
