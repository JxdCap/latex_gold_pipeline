import unittest

from src.分流器 import 执行分流


class 分流测试(unittest.TestCase):
    def test_疑难与空白进入人工复核(self):
        记录列表 = [
            {"编号": "样本000001", "分桶结果": "LaTeX样本", "是否待复核": False},
            {"编号": "样本000002", "分桶结果": "普通文本", "是否待复核": False},
            {"编号": "样本000003", "分桶结果": "疑难样本", "是否待复核": True},
            {"编号": "样本000004", "分桶结果": "空白样本", "是否待复核": True},
        ]

        自动处理记录, 人工复核记录 = 执行分流(记录列表)

        self.assertEqual(["样本000001", "样本000002"], [记录["编号"] for 记录 in 自动处理记录])
        self.assertEqual(["样本000003", "样本000004"], [记录["编号"] for 记录 in 人工复核记录])
        self.assertEqual("自动处理队列", 自动处理记录[0]["分流结果"])
        self.assertEqual("人工复核队列", 人工复核记录[0]["分流结果"])


if __name__ == "__main__":
    unittest.main()
