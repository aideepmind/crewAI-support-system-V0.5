from crewai.flow.flow import Flow, start, listen
from support.router.flows.agents import CustomAgents
from support.router.flows.tasks import CustomTasks
from crewai import Crew

from src.support.tools.tools import SupportState, IntentOutput   
from src.support.customer_support.flow.agents import CSAgents
from src.support.customer_support.flow.tasks import CSTasks
from src.support.customer_support.flow.tools import FitnessConsultingOutput
from src.support.tools.FlowResponse import FlowResponse

class FaultDiagnosisProcessFlow(Flow[SupportState]):

    def __init__(self):
        super().__init__()
        # 在初始化时只加载一次配置
        self.agents_factory = CSAgents()
        self.tasks_factory = CSTasks()
    
    @start()
    async def fitness_consulting_start(self):
        """步骤 1: 调用专门的查询 Agent 获取订单详情"""
        result = await self._execute_fitness_consulting_crew()
        if hasattr(result, "pydantic") and result.pydantic:
            json_dict = result.pydantic.model_dump()
        else:
            json_dict = {
            "type": "error",
            "message": str(result)
        }
        ## 返回格式统一，包含 type, success, message, data 四个字段
        self.state.response = FlowResponse(
                        type="fitness_consulting",
                        success=True,
                        message=f"身高 {json_dict['height']} 体重 {json_dict['weight']} 建议 {json_dict['fitness_suggestion']}",
                        data=json_dict
        ).model_dump()
        
        return "fitness_consulting"

    @listen("fitness_consulting")
    def format_fitness_consulting_report(self):
        """步骤 2: 对查询结果进行人性化包装（可选）"""
        print(f"==[FitnessConsulting.format_report] 查询结果: {self.state.response}")
        # 你可以在这里加入格式化逻辑，修改self.state.response
        return self.state.response
        
    async def _execute_fitness_consulting_crew(self) -> FitnessConsultingOutput:
        """
        专门负责组装和执行路由 Crew 的私有方法
        """
        agent1 = self.agents_factory.bmi_agent()
        weight = self.state.slots.get('weight')
        height = self.state.slots.get('height')
        task1 = self.tasks_factory.bmi_task(agent1, height, weight)
        
        agent2 = self.agents_factory.fitness_agent()
        #task2 = self.tasks_factory.fitness_task(agent2,FitnessConsultingOutput)
        task2 = self.tasks_factory.fitness_task(
            agent=agent2, 
            output_model=FitnessConsultingOutput,
            context_tasks=[task1] # 这里的列表可以包含多个前置任务，通过传递slots
        )

     
        result = Crew(
            agents=[agent1,agent2], 
            tasks=[task1,task2],
            verbose=True # 路由通常不需要刷屏日志
        ).kickoff()
       
        return result
    