from typing import Optional, Any, Dict
from pydantic import BaseModel
import os


from pydantic import BaseModel, Field
from typing import Dict, Any

# --- 1. 定义“主流程”的状态模型 (self.state) ---
class SupportState(BaseModel):
    query: str = ""
    intent: str = ""
    slots: Dict[str, Any] = {}
    is_complete: bool = False
    response: str = ""

# --- 2. 定义“意图agent”的状态模型，包含：槽位的结构化输出模型 ---
class IntentOutput(BaseModel):
    intent: str = Field(..., description="意图分类标签")
    slots: Dict[str, Any] = Field(default_factory=dict, description="提取的实体信息")
    is_complete: bool = Field(..., description="关键槽位是否配齐")
    explanation: str = Field(..., description="简短的分类理由")

from langchain_openai import ChatOpenAI

def get_deepseek_llm(temperature=0.7):
    return ChatOpenAI(
        model="deepseek/deepseek-chat",
        base_url=os.getenv("OPENAI_API_BASE"),
        temperature=temperature
    )