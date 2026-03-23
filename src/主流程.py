import argparse
from pathlib import Path

import yaml

try:
    from .分桶器 import 读取_jsonl as 读取分桶输入_jsonl
    from .分桶器 import 读取分桶规则, 导出分桶结果, 执行分桶
    from .导入器 import 导出导入结果, 读取输入表格
    from .分流器 import 导出分流结果, 执行分流
    from .轻预洗 import 读取_jsonl as 读取轻预洗输入_jsonl
    from .轻预洗 import 读取轻预洗规则, 导出轻预洗结果, 执行轻预洗
except ImportError:
    from 分桶器 import 读取_jsonl as 读取分桶输入_jsonl
    from 分桶器 import 读取分桶规则, 导出分桶结果, 执行分桶
    from 导入器 import 导出导入结果, 读取输入表格
    from 分流器 import 导出分流结果, 执行分流
    from 轻预洗 import 读取_jsonl as 读取轻预洗输入_jsonl
    from 轻预洗 import 读取轻预洗规则, 导出轻预洗结果, 执行轻预洗


def 读取全局规则(规则文件: str | Path = "configs/全局规则.yaml") -> dict:
    with Path(规则文件).open("r", encoding="utf-8") as 文件:
        return yaml.safe_load(文件)


def 运行第一阶段(全局规则文件: str | Path = "configs/全局规则.yaml", 样本条数: int | None = None) -> dict:
    全局规则 = 读取全局规则(全局规则文件)
    if not 全局规则["运行约束"]["仅支持小样本"]:
        raise ValueError("当前版本只支持小样本模式。")

    实际样本条数 = 样本条数 or int(全局规则["默认样本条数"])
    if 实际样本条数 <= 0:
        raise ValueError("样本条数必须大于 0。")

    输入文件 = 全局规则["输入文件"]
    原始目录 = 全局规则["输出目录"]["原始数据"]
    分桶目录 = 全局规则["输出目录"]["分桶结果"]
    自动处理目录 = 全局规则["输出目录"]["自动处理队列"]
    人工复核目录 = 全局规则["输出目录"]["人工复核队列"]
    原始样本jsonl = Path(原始目录) / 全局规则["阶段输出文件名"]["导入"]["jsonl"]
    轻预洗样本jsonl = Path(原始目录) / 全局规则["阶段输出文件名"]["轻预洗"]["jsonl"]
    分桶样本jsonl = Path(分桶目录) / 全局规则["阶段输出文件名"]["分桶"]["jsonl"]

    原始记录 = 读取输入表格(输入文件, 实际样本条数)
    导出导入结果(原始记录, 原始目录)

    导入后记录 = 读取轻预洗输入_jsonl(原始样本jsonl)
    轻预洗规则 = 读取轻预洗规则()
    轻预洗记录 = 执行轻预洗(导入后记录, 轻预洗规则)
    导出轻预洗结果(轻预洗记录, 原始目录)

    轻预洗后记录 = 读取分桶输入_jsonl(轻预洗样本jsonl)
    分桶规则 = 读取分桶规则()
    分桶记录 = 执行分桶(轻预洗后记录, 分桶规则)
    导出分桶结果(分桶记录, 分桶目录)

    分桶后记录 = 读取分桶输入_jsonl(分桶样本jsonl)
    自动处理记录, 人工复核记录 = 执行分流(分桶后记录)
    导出分流结果(自动处理记录, 人工复核记录, 自动处理目录, 人工复核目录)

    return {
        "导入条数": len(原始记录),
        "轻预洗条数": len(轻预洗记录),
        "分桶条数": len(分桶记录),
        "自动处理条数": len(自动处理记录),
        "人工复核条数": len(人工复核记录),
        "输出目录": {
            "原始数据": 原始目录,
            "分桶结果": 分桶目录,
            "自动处理队列": 自动处理目录,
            "人工复核队列": 人工复核目录,
        },
    }


def main() -> None:
    参数解析器 = argparse.ArgumentParser(description="运行第一阶段小样本流程。")
    参数解析器.add_argument("--全局规则文件", default="configs/全局规则.yaml")
    参数解析器.add_argument("--样本条数", type=int, default=None)
    参数 = 参数解析器.parse_args()

    结果 = 运行第一阶段(参数.全局规则文件, 参数.样本条数)
    for 键, 值 in 结果.items():
        print(f"{键}={值}")


if __name__ == "__main__":
    main()
