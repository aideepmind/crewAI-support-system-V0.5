from crewai.flow.flow import Flow, start, listen
from crewai import Crew

from src.support.tools.tools import SupportState
from src.support.customer_support.flow.agents import CSAgents
from src.support.customer_support.flow.tasks import CSTasks
from src.support.tools.FlowResponse import FlowResponse


class OrderStateProcessFlow(Flow[SupportState]):
    def __init__(self):
        super().__init__()
        # 在初始化时只加载一次配置
        self.agents_factory = CSAgents()
        self.tasks_factory = CSTasks()

    @start()
    async def query_order_state(self):
        """步骤 1: 调用专门的查询 Agent 获取订单详情"""
        result = await self._execute_order_state_crew()

        raw_str = str(result)
        json_dict = {}

        if hasattr(result, "pydantic") and result.pydantic:
            json_dict = result.pydantic.model_dump()
        elif hasattr(result, "json_dict") and result.json_dict:
            json_dict = result.json_dict
        else:
            import json
            import re

            try:
                json_dict = json.loads(raw_str)
            except json.JSONDecodeError:
                match = re.search(r'\{[\s\S]*?"order_id"[\s\S]*?\}', raw_str)
                if match:
                    try:
                        json_dict = json.loads(match.group(0))
                    except json.JSONDecodeError:
                        json_dict = {
                            "order_id": "unknown",
                            "order_state": "unknown",
                            "message": raw_str[:200],
                        }

        order_id = json_dict.get(
            "order_id", self.state.slots.get("order_id", "unknown")
        )
        order_state = json_dict.get("order_state", "unknown")

        self.state.response = FlowResponse(
            type="order_state",
            success=True,
            message=f"订单 {order_id} 当前状态为 {order_state}",
            data=json_dict,
        ).model_dump()

        return "query_completed"

    @listen("query_order_state")
    def format_order_state_report(self):
        """步骤 2: 对查询结果进行人性化包装（可选）"""
        print(
            f"==[OrderStateProcessFlow.format_order_state_report] 查询结果: {self.state.response}"
        )
        # 你可以在这里加入格式化逻辑，修改self.state.response
        return self.state.response

    async def _execute_order_state_crew(self):
        """
        专门负责组装和执行路由 Crew 的私有方法
        """
        agent1 = self.agents_factory.order_state_agent()
        order_id = self.state.slots.get("order_id")
        task1 = self.tasks_factory.order_state_task(agent1, order_id)
        result = Crew(agents=[agent1], tasks=[task1], verbose=True).kickoff()

        return result
