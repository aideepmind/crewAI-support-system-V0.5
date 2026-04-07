from crewai.flow.flow import Flow, start, listen
from support.router.flows.agents import CustomAgents
from support.router.flows.tasks import CustomTasks
from crewai import Crew

from src.support.tools.tools import SupportState, IntentOutput   
from src.support.customer_support.flow.agents import CSAgents
from src.support.customer_support.flow.tasks import CSTasks
from src.support.customer_support.flow.tools import OrderStateOutput
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
        #retval = result.pydantic
        #print(f"===[OrderStateProcessFlow.start] 查询结果: {result}")
        #data_obj = result.pydantic
        #json_dict = data_obj.model_dump()
        #print(f"===[OrderStateProcessFlow.start] 查询结果json_dict: {json_dict}")
        ## 直接将整个查询结果存入状态，供后续步骤使用，后续进行和主流程同步
        #self.state.response = json_dict
        if hasattr(result, "pydantic") and result.pydantic:
            json_dict = result.pydantic.model_dump()
        else:
            json_dict = {
            "type": "error",
            "message": str(result)
        }
        ## 返回格式统一，包含 type, success, message, data 四个字段
        self.state.response = FlowResponse(
                        type="order_state",
                        success=True,
                        message=f"订单 {json_dict['order_id']} 当前状态为 {json_dict['order_state']}",
                        data=json_dict
        ).model_dump()
        
        return "query_completed"

    @listen("query_order_state")
    def format_order_state_report(self):
        """步骤 2: 对查询结果进行人性化包装（可选）"""
        print(f"==[OrderStateProcessFlow.format_order_state_report] 查询结果: {self.state.response}")
        # 你可以在这里加入格式化逻辑，修改self.state.response
        return self.state.response
        
    async def _execute_order_state_crew(self) -> OrderStateOutput:
        """
        专门负责组装和执行路由 Crew 的私有方法
        """
        agent1 = self.agents_factory.order_state_agent() 
        order_id = self.state.slots.get('order_id')
        task1 = self.tasks_factory.order_state_task(agent1, order_id, OrderStateOutput)
        result = Crew(
            agents=[agent1], 
            tasks=[task1],
            verbose=True # 路由通常不需要刷屏日志
        ).kickoff()
       
        return result
    