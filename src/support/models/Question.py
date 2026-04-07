import json

class Question:
    def __init__(self, q_type: str, question: str, answer: str = ""):
        self.type = q_type
        self.question = question
        self.answer = answer

    def to_dict(self) -> dict:
        """转换为 FaultCase 可使用的字典格式"""
        return {
            "type": self.type,
            "quesion": self.question,   # 注意：FaultCase 中字段名写作 'quesion'
            "answer": self.answer
        }
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


    @classmethod
    def from_dict(cls, data: dict):
        """从 FaultCase 的 dict 还原成 Question 对象"""
        return cls(
            q_type=data.get("type", ""),
            question=data.get("quesion", ""),
            answer=data.get("answer", "")
        )

    def __repr__(self):
        return f"<Question type={self.type}, question={self.question}, answer={self.answer}>"
