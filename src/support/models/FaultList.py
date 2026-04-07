import json
from typing import List, Dict, Any, Optional
from src.support.models.Fault import Fault  # 假设你的 Fault 类定义在 Fault.py 文件中


class FaultList:
    """用于管理多个 Fault 对象的类"""

    def __init__(self, faults: Optional[List[Fault]] = None):
        self.faults: List[Fault] = faults if faults is not None else []

    # ========== 基础操作方法 ==========

    def add_fault(self, fault: Fault):
        """添加一个 Fault 对象"""
        if not isinstance(fault, Fault):
            raise TypeError("只能添加 Fault 类型的对象")
        self.faults.append(fault)

    def remove_fault(self, fault_id: str):
        """按 fault_id 删除 Fault 对象"""
        before = len(self.faults)
        self.faults = [f for f in self.faults if f.get_fault_id() != fault_id]
        after = len(self.faults)
        if before == after:
            raise ValueError(f"未找到 fault_id={fault_id} 的 Fault 对象。")

    def get_fault(self, fault_id: str) -> Optional[Fault]:
        """按 fault_id 获取 Fault 对象"""
        for f in self.faults:
            if f.get_fault_id() == fault_id:
                return f
        return None

    def list_fault_ids(self) -> List[str]:
        """返回所有 fault_id 列表"""
        return [f.get_fault_id() for f in self.faults]

    # ========== JSON 互转 ==========

    def to_json(self, indent: int = 2, ensure_ascii: bool = False) -> str:
        """将整个 FaultList 转换为 JSON 字符串"""
        fault_dicts = [f.to_dict() for f in self.faults]
        return json.dumps(fault_dicts, indent=indent, ensure_ascii=ensure_ascii)

    def to_dict(self) -> List[Dict[str, Any]]:
        """返回 Python 字典列表"""
        return [f.to_dict() for f in self.faults]

    @classmethod
    def from_json(cls, json_data: Any) -> "FaultList":
        """从 JSON（字符串或字典列表）创建 FaultList 对象"""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        if not isinstance(data, list):
            raise ValueError("FaultList JSON 数据必须是一个包含 Fault 字典的列表")

        faults = [Fault.from_json(f) for f in data]
        return cls(faults)

    # ========== 文件操作（可选） ==========

    @staticmethod
    def load_from_file(filepath: str) -> "FaultList":
        """从 JSON 文件加载 FaultList"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return FaultList.from_json(data)

    def save_to_file(self, filepath: str):
        """将 FaultList 保存为 JSON 文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def __len__(self):
        return len(self.faults)

    def __iter__(self):
        return iter(self.faults)

    def __repr__(self):
        return f"<FaultList size={len(self.faults)}>"

