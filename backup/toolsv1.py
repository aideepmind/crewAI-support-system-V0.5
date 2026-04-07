from typing import Optional, Any, Dict
from pydantic import BaseModel
import os
import sys
from typing import Union, Dict, Any

from pydantic import BaseModel, Field
from typing import Dict, Any
from src.support.tools.FlowResponse import FlowResponse

# --- 1. 定义“主流程”的状态模型 (self.state) ---
class SupportState(BaseModel):
    query: str = ""
    intent: str = ""
    is_complete: bool = False
    slots: Dict[str, Any] = {}
    
    # 核心优化：定义 response 可以接收多种类型，但我们可以通过方法统一它
    response: Any = None

    def set_response(self, resp: Union[str, Dict[str, Any], FlowResponse]):
        """
        专用方法：自动将各种格式转换为标准字典/JSON 兼容格式
        """
        if isinstance(resp, str):
            # 如果是纯字符串，包装成简单的成功格式
            self.response = {
                "type": self.intent or "general",
                "success": True,
                "message": resp,
                "data": None
            }
        elif hasattr(resp, "model_dump"):
            # 如果是 FlowResponse 对象，自动转为字典
            self.response = resp.model_dump()
        else:
            # 已经是字典或其他格式
            self.response = resp
    
    ## 执行完后，可以调用此方法，将意图和槽位重置
    def clear_session(self, keep_response: bool = True):
        """
        一键清除意图历史和槽位历史。
        :param keep_response: 是否保留当前的 response 内容。
                              通常设为 True，因为流程结束时我们需要把 response 返回给前端。
        """
        print(f"--- [状态重置] 正在清除意图: {self.intent} 和 槽位: {list(self.slots.keys())} ---")  # 打印重置前的状态信息
        
        # 1. 重置核心业务字段
        self.intent = ""
        self.slots = {}
        self.is_complete = False
        
        # 2. 根据需要重置响应
        if not keep_response:
            self.response = None
            
        # 3. query 通常保留，代表用户最后一次输入，
        # 如果需要彻底开启全新会话，也可以设为 ""
        self.query = ""      
            

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