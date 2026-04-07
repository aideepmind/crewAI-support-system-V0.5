import json
from typing import Any, Dict, List, Optional

# 假设 prior 和 posterior 应该是 float 类型
class Fault:
    """表示单个故障（Fault）的类"""

    def __init__(
        self,
        fault_id: str,
        fault: str,
        symptoms: List[Dict[str, Any]],
        test: List[Dict[str, Any]],
        check: List[Dict[str, Any]],
        cause: str,
        remedy: List[Dict[str, Any]],
        safety: List[str],
        RequestNo: str,
        # 1. 新增的两个属性作为必需参数
        prior: float,
        posterior: float
    ):
        self.fault_id = fault_id
        self.fault = fault
        self.symptoms = symptoms
        self.test = test
        self.check = check
        self.cause = cause
        self.remedy = remedy
        self.safety = safety
        self.RequestNo = RequestNo
        # 2. 初始化新属性
        self.prior = prior
        self.posterior = posterior

    # ========== 通用属性操作方法 ==========

    def get_field(self, field: str) -> Any:
        """按字段名读取属性"""
        return getattr(self, field, None)

    def set_field(self, field: str, value: Any):
        """按字段名写入属性"""
        if hasattr(self, field):
            setattr(self, field, value)
        else:
            raise AttributeError(f"字段 '{field}' 不存在。")

    # ========== 专用 set/get 方法（便于调用） ==========

    def set_fault_id(self, fault_id: str):
        self.fault_id = fault_id

    def get_fault_id(self) -> str:
        return self.fault_id

    def set_fault(self, fault: str):
        self.fault = fault

    def get_fault(self) -> str:
        return self.fault

    def set_symptoms(self, symptoms: List[Dict[str, Any]]):
        self.symptoms = symptoms

    def get_symptoms(self) -> List[Dict[str, Any]]:
        return self.symptoms

    def set_test(self, test: List[Dict[str, Any]]):
        self.test = test

    def get_test(self) -> List[Dict[str, Any]]:
        return self.test

    def set_check(self, check: List[Dict[str, Any]]):
        self.check = check

    def get_check(self) -> List[Dict[str, Any]]:
        return self.check

    def set_cause(self, cause: str):
        self.cause = cause

    def get_cause(self) -> str:
        return self.cause

    def set_remedy(self, remedy: List[Dict[str, Any]]):
        self.remedy = remedy

    def get_remedy(self) -> List[Dict[str, Any]]:
        return self.remedy

    def set_safety(self, safety: List[str]):
        self.safety = safety

    def get_safety(self) -> List[str]:
        return self.safety

    def set_RequestNo(self, RequestNo: str):
        self.RequestNo = RequestNo

    def get_RequestNo(self) -> str:
        return self.RequestNo

    # ========== 新增 prior 和 posterior 的 set/get 方法 ==========
    def set_prior(self, prior: float):
        self.prior = prior

    def get_prior(self) -> float:
        return self.prior

    def set_posterior(self, posterior: float):
        self.posterior = posterior

    def get_posterior(self) -> float:
        return self.posterior

    # ========== JSON 互转 ==========

    @classmethod
    def from_json(cls, json_data: Any) -> "Fault":
        """从 JSON（字符串或字典）创建 Fault 对象"""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        # __init__ 要求所有参数都必须在 data 中提供
        return cls(**data)

    def to_json(self, indent: int = 2, ensure_ascii: bool = False) -> str:
        """将对象转换为 JSON 字符串"""
        # __dict__ 会自动包含所有实例属性，包括新添加的 prior 和 posterior
        return json.dumps(self.__dict__, indent=indent, ensure_ascii=ensure_ascii)

    def to_dict(self) -> Dict[str, Any]:
        """转换为 Python 字典"""
        # __dict__ 会自动包含所有实例属性，包括新添加的 prior 和 posterior
        return self.__dict__

    @staticmethod
    def load_from_file(filepath: str) -> "Fault":
        """从 JSON 文件加载 Fault 对象"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Fault.from_json(data)

    def save_to_file(self, filepath: str):
        """将对象保存为 JSON 文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def __repr__(self):
        return f"<Fault {self.fault_id}: {self.fault}>"