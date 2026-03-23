import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from openpyxl import Workbook


def 确保目录(path: str | Path) -> Path:
    路径 = Path(path)
    路径.parent.mkdir(parents=True, exist_ok=True)
    return 路径


def 写出_jsonl(记录列表: Iterable[Mapping], 输出路径: str | Path) -> Path:
    路径 = 确保目录(输出路径)
    with 路径.open("w", encoding="utf-8") as 文件:
        for 记录 in 记录列表:
            文件.write(json.dumps(记录, ensure_ascii=False) + "\n")
    return 路径


def 写出_xlsx(记录列表: Sequence[Mapping], 输出路径: str | Path) -> Path:
    路径 = 确保目录(输出路径)
    工作簿 = Workbook()
    工作表 = 工作簿.active
    工作表.title = "Sheet1"

    if 记录列表:
        表头 = list(记录列表[0].keys())
        工作表.append(表头)
        for 记录 in 记录列表:
            工作表.append([_标准化单元格(记录.get(列名)) for 列名 in 表头])
    else:
        工作表.append(["空结果"])

    工作簿.save(路径)
    return 路径


def 双格式写出(记录列表: Sequence[Mapping], jsonl路径: str | Path, xlsx路径: str | Path) -> None:
    写出_jsonl(记录列表, jsonl路径)
    写出_xlsx(记录列表, xlsx路径)


def _标准化单元格(值):
    if isinstance(值, list):
        return json.dumps(值, ensure_ascii=False)
    if isinstance(值, bool):
        return "true" if 值 else "false"
    return 值
