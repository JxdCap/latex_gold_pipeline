import json
import unittest
from pathlib import Path

from src.分桶器 import 执行分桶, 读取分桶规则


class 分桶测试(unittest.TestCase):
    def test_回归样例分桶结果稳定(self):
        样例路径 = Path("tests/回归样例.jsonl")
        with 样例路径.open("r", encoding="utf-8") as 文件:
            记录列表 = [json.loads(行) for 行 in 文件 if 行.strip()]

        分桶规则 = 读取分桶规则("configs/分桶规则.yaml")
        分桶后记录 = 执行分桶(记录列表, 分桶规则)

        self.assertEqual("普通文本", 分桶后记录[0]["分桶结果"])
        self.assertEqual("LaTeX样本", 分桶后记录[1]["分桶结果"])
        self.assertEqual("疑难样本", 分桶后记录[2]["分桶结果"])
        self.assertEqual("空白样本", 分桶后记录[3]["分桶结果"])
        self.assertEqual("轻预洗阶段标记为待复核", 分桶后记录[2]["分桶依据"])


if __name__ == "__main__":
    unittest.main()
