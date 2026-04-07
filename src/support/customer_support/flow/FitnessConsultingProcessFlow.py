from crewai.flow.flow import Flow, start, listen
from crewai import Crew

from src.support.tools.tools import SupportState
from src.support.customer_support.flow.agents import CSAgents
from src.support.customer_support.flow.tasks import CSTasks
from src.support.tools.FlowResponse import FlowResponse


class FitnessConsultingProcessFlow(Flow[SupportState]):
    def __init__(self):
        super().__init__()
        # 在初始化时只加载一次配置
        self.agents_factory = CSAgents()
        self.tasks_factory = CSTasks()

    @start()
    async def fitness_consulting_start(self):
        """步骤 1: 调用专门的查询 Agent 获取订单详情"""
        result = await self._execute_fitness_consulting_crew()

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
                match = re.search(r'\{[\s\S]*?"height"[\s\S]*?\}', raw_str)
                if match:
                    try:
                        json_dict = json.loads(match.group(0))
                    except json.JSONDecodeError:
                        json_dict = {
                            "height": "unknown",
                            "weight": "unknown",
                            "fitness_suggestion": raw_str[:200],
                        }

        height = json_dict.get("height", self.state.slots.get("height", "unknown"))
        weight = json_dict.get("weight", self.state.slots.get("weight", "unknown"))
        suggestion = json_dict.get("fitness_suggestion", "暂无建议")

        self.state.response = FlowResponse(
            type="fitness_consulting",
            success=True,
            message=f"身高 {height} 体重 {weight} 建议 {suggestion}",
            data=json_dict,
        ).model_dump()

        return "fitness_consulting"

    @listen("fitness_consulting")
    def format_fitness_consulting_report(self):
        """步骤 2: 对查询结果进行人性化包装（可选）"""
        print(f"==[FitnessConsulting.format_report] 查询结果: {self.state.response}")
        # 你可以在这里加入格式化逻辑，修改self.state.response
        return self.state.response

    async def _execute_fitness_consulting_crew(self):
        """
        专门负责组装和执行路由 Crew 的私有方法
        """
        agent1 = self.agents_factory.bmi_agent()
        weight = self.state.slots.get("weight")
        height = self.state.slots.get("height")
        task1 = self.tasks_factory.bmi_task(agent1, height, weight)

        agent2 = self.agents_factory.fitness_agent()
        task2 = self.tasks_factory.fitness_task(agent=agent2, context_tasks=[task1])

        result = Crew(
            agents=[agent1, agent2], tasks=[task1, task2], verbose=True
        ).kickoff()

        return result
