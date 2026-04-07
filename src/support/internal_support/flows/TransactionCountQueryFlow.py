from crewai.flow.flow import Flow, start, listen
from support.router.flows.agents import CustomAgents
from support.router.flows.tasks import CustomTasks
from crewai import Crew

from src.support.tools import SupportState, IntentOutput   

class TransactionCountQueryFlow(Flow[SupportState]):

    @start()
    def query_transaction(self):
        """步骤 1: 调用专门的查询交易数量"""
        org_name = self.state.slots.get('org_name')
        duration = self.state.slots.get('duration')
        print(f"[TransactionCountQueryFlow] 正在为机构 {org_name} 查询最近 {duration} 的交易数量...")

        ''''
        # 初始化业务 Agent 和 Task
        agents = CustomAgents()
        tasks = CustomTasks()
        
        # 假设你在 agents.yaml 中定义了 logistics_agent
        logistics_agent = agents.logistics_agent() 
        
        # 假设你在 tasks.yaml 中定义了 query_task
        query_task = tasks.query_task(logistics_agent, order_id)

        # 执行物流查询 Crew
        result = Crew(
            agents=[logistics_agent],
            tasks=[query_task],
            verbose=True
        ).kickoff()
        '''

        # 将查询到的详细结果存入状态
        #self.state.response = str(result)
        return "query_transaction_completed"

    @listen("query_transaction")
    def format_query_transaction_report(self):
        """步骤 2: 对查询结果进行人性化包装（可选）"""
        print("[TransactionCountQueryFlow] 正在优化查询报告...")
        # 你可以在这里加入格式化逻辑，或者直接返回
        self.state.response = f"机构 {self.state.slots.get('org_name')} 最近 {self.state.slots.get('duration')} 的交易数量为 12345 笔。"