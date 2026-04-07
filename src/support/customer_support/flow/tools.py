from typing import Optional, Any, Dict
from pydantic import BaseModel
from crewai.flow.flow import Flow, start, listen, router
from crewai import Agent, Task, Crew
from crewai import Agent, LLM
import os
import support.router.flows.agents as agents
import support.router.flows.tasks
from support.router.flows.agents import CustomAgents
from support.router.flows.tasks import CustomTasks

from pydantic import BaseModel, Field
from typing import Dict, Any

# --- 1. 定义状态模型 (State) ---
class SupportState(BaseModel):
    query: str = ""
    intent: str = ""
    slots: Dict[str, Any] = {}
    is_complete: bool = False
    response: str = ""

# --- 2. 定义意图与槽位的结构化输出模型 ---
class OrderStateOutput(BaseModel):
    order_id: str = Field(..., description="订单号")
    order_state: str = Field(..., description="订单状态")

class FitnessConsultingOutput(BaseModel):
    height: str = Field(..., description="身高")
    weight: str = Field(..., description="体重")
    fitness_suggestion: str = Field(..., description="健身建议")
