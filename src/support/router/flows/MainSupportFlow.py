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
from support.customer_support.flow.OrderStateProcessFlow_ import OrderStateProcessFlow
from support.customer_support.flow.FitnessConsultingProcessFlow import FitnessConsultingProcessFlow
from src.support.tools.tools import SupportState, IntentOutput  
import yaml  
from src.support.tools.FlowResponse import FlowResponse
from src.support.models.Question import Question
from src.support.models import constants
from src.support.api.config import llm
from src.support.api.tools import createFaultListFromFile
from src.support.models.FaultCase import FaultCase
from src.support.api.FaultSeekTools import generate_fault_case_from_faultlist_obj
from src.support.api.CommonIntent import CommonIntentCheck
from src.support.models.FaultList import FaultList
import json
#from langfuse.langchain import CallbackHandler

#逻辑 A（默认）：@listen 监听的是方法名。你应该监听 query_order_status。
#逻辑 B（手动路由）：如果你想根据返回值来触发，通常需要配合 @router。

# 定义每个意图的必填字段映射

# 在你的业务配置中定义
"""
BUSINESS_RULES = {
    "order_state": {
        "required": ["order_id"],
        "prompt": "为了查询订单，我需要您的订单号（8位数字）。"
    },
    "tech_support": {
        "required": ["device_type"],
        "prompt": "请问您使用的是哪款型号的设备？"
    },
    "transaction_count_query": {
        "required": ["org_name", "duration"],
        "prompt": "请提供机构名称和查询的时间范围（年，月等）。"
    }
}
"""

def build_chat_question_text(questionObj: Question) -> str:
    """
    根据 Question 实例生成提问文本。
    """
    if questionObj.type == "symptoms":
        return f"你还遇到过类似的现象吗：{questionObj.question}，回答 'Yes' 或 'No'。"
    # 可扩展其他类型
    return f"请回答关于问题：{questionObj.question}"


# --- 3. 构建 Flow ---
class MainFlow(Flow[SupportState]):
    def __init__(self):
        super().__init__()
        # 在初始化时只加载一次配置
        self.agents_factory = CustomAgents()
        self.tasks_factory = CustomTasks()
        
        ## 加载业务规则字段配置的yaml
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "../config/businessrule.yaml")
        
        # 2. 初始化并加载规则
        self.business_rules = self._load_business_rules(config_path)

    @start()
    def get_user_query(self):
        # 实际应用中，这里可以从 API 或前端获取输入
        ##self.state.query = "我想查询我的订单状态，订单号是 9527"
        if not self.state.query:
            self.state.query = "默认查询"
        print(f"用户输入: {self.state.query}")

    ## 异步方式定义和执行意图判断，里面调用了await 方式运行的子流程
    @router(get_user_query)
    async def route_query(self):
        
        # 针对这种需要动态持续进行交互的意图识别，需要定义一个状态类来保存上下文信息
        # 1. 如果当前已经处于故障诊断中，且信息已完整，表示在处理过程中
        if self.state.intent == "fault_diagnosis"  and self.state.slots.get("symptom"):
            # 调用一个轻量级的判断：用户是在回答刚才的问题，还是想换个话题？
            print(f"+++++ in route_query 符合条件 diag and compete条件 +++++")
            print(f"+++++ 维持故障诊断业务交互，当前输入: {self.state.query} ---")
            
            ''''
            is_switching = await self._check_intent_switch()
            if not is_switching:
                # 维持意图，继续进入诊断逻辑
                print(f"--- 维持意图: {self.state.intent}，处理用户反馈 ---")
                return self.state.intent
            else:
                # 切换意图，进入新的意图识别流程
                print(f"--- 希望意图切换: {self.state.intent} -> unknown ---")
                
            '''
            return "fault_diagnosis"
       
        
            
        # 其他意图识别，只需要判断slots填充
        """
        利用专门的 Router Agent 进行意图识别和槽位提取
        """
        output = await self._execute_routing_crew()
        print(f"==after _execute_routing_crew === ")
        # 2. 状态更新（增量合并）
        
        # 1. 槽位更新
        if output.slots:
            self.state.slots.update(output.slots)
            # 如果某些情况update不生效，可以采用如下：先取出来，更新完再塞回去（触发 Pydantic 的 setter）
            #current_slots = self.state.slots.copy()
            #current_slots.update(output.slots)
            #self.state.slots = current_slots
            print(f"===route query slots 更新后: {self.state.slots}")
        self.state.is_complete = output.is_complete
        self.state.response = output.explanation
        
        # 3. 【关键】意图继承逻辑
        # 如果这一轮识别出了新意图，且不是 unknown，则更新
        if output.intent and output.intent not in ["unknown", "none", ""]:
            self.state.intent = output.intent
        
        print(f"==========槽位保持继承，同时意图更新后 start======= ")
        print(f"self.state.intent:{self.state.intent}")
        print(f"self.state.slots:{self.state.slots}")
        print(f"self.state.is_complete:{self.state.is_complete}")
        print(f"self.state.response:{self.state.response}")
        print(f"==========槽位保持继承，同时意图更新后 end ======= ")

        
        # 3. 【核心】基于 business_rules 的二次校验
        # 从配置中获取当前意图的校验规则
        rule = self.business_rules.get(self.state.intent, {})
        required_data = rule.get('required_slots', []) # 这里可能是 list 也可能是 dict

        # 统一处理：如果是字典，取 keys；如果是列表，直接用
        required_keys = required_data.keys() if isinstance(required_data, dict) else required_data

        # 检查所有必填槽位
        missing_slots = []
        for key in required_keys:
            # 确保 key 是字符串
            value = self.state.slots.get(key)
            if not value or str(value).strip() == "":
                missing_slots.append(key)

        # 4. 最终路由决策
        if missing_slots:
            # 如果有缺失，强制将状态设为不完整，并跳转追问
            self.state.is_complete = False
            print(f"==== 校验未通过: 意图 [{self.state.intent}] 缺少关键槽位 {missing_slots}，跳转到追问节点")
            return "incomplete_info"
        
        # 5. 校验通过
        self.state.is_complete = True
        print(f"==== 校验通过: 意图 [{self.state.intent}] 信息完整，进入业务流程")
        return self.state.intent

    ## 如果信息不完整，基于self.state 构建提示的具体内容，给前端返回
    @listen("incomplete_info")
    def handle_missing_data(self):
        """
        当信息不完整时，构造标准化的 FlowResponse 返回给前端
        """
        rule = self.business_rules.get(self.state.intent, {})
        required_map = rule.get('required_slots', {})
        
        # 兼容性处理：防止 YAML 缩进导致 required_map 变成 list
        if isinstance(required_map, list):
            # 如果是列表，将其转为简单的字典映射
            required_map = {slot: f"请补充您的【{slot}】信息。" for slot in required_map}
        
        # 逻辑：寻找第一个缺失的槽位
        selected_prompt = rule.get('missing_prompt', "您的请求缺少关键信息，请补充。")
        missing_fields = []

        for slot, prompt in required_map.items():
            if not self.state.slots.get(slot):
                selected_prompt = prompt # 找到具体的追问话术
                missing_fields.append(slot)
                break # 只要找到一个缺失就跳出，引导用户逐一补全
                
        # 同步更新 Flow 的内部状态??????????
        #self.state.response = selected_prompt
        #return self.state.response
        
        res_obj = FlowResponse(
          type="incomplete_info",
          success=False,
          message=selected_prompt,
          data={"missing": missing_fields}
        )
    
        # 使用优化后的方法，它会自动帮你 model_dump()
        self.state.set_response(res_obj)
        return res_obj
    
    @listen("fault_diagnosis")
    async def run_faultDiagnosisProcess(self):
        print(">>> 进入故障诊断子流程处理。")
        print(f"+++++故障针对槽位信息及用户输入信息self.state.slots:{self.state.slots}")
        print(f"++++++开始/继续 故障诊断逻辑。当前轨迹长度: {len(self.state.diagnose_trace)}")
        print(f"++++++intent:{self.state.intent}") 
        print(f"++++++slots:{self.state.slots}")
        print(f"++++++self.state.query:{self.state.query}")
        
        ##print(f"+++++故障针对槽位信息及用户输入信息self.state.new_traces:{self.state.new_traces}")
        if self.state.user_response:
            print(f"+++++故障针对槽位信息及用户输入信息self.state.user_response:{self.state.user_response}")
        ##self.state.slots["last_asked_question"]="之前的问题"
        
        
        ## 可以通过当前轨迹长度判断是否开始提问 len(self.state.diagnose_trace) 开始为0
        
        symptom = self.state.slots.get("symptom")
        ##user_ans = self.state.user_response 
        
        # 第一次处理,准备list和case
        if not self.state.slots.get("last_asked_question"):
            print(f">>> 当前诊断上下文: 现象=[{symptom}]")
            symptom_topic = llm.invoke(constants.GET_symptom_desc + self.state.query).content
            print("##故障现象核心主题是：", symptom_topic)
            json_filename = "/Users/liyansheng/github/agent-study/crewAI-support-system/src/tests/fault_list1.json"  # 文件名可修改为你当前文件的名称
            fault_list = createFaultListFromFile(json_filename)
            print("创建的fault_list是：", fault_list.to_json())
            if not fault_list:
                res_obj = FlowResponse(
                    type="fault_diagnosis_asking",
                    success=True,
                    message= f"没有找到历史问题信息库,请联系IT检查系统。",
                    data={"is_final": True}
                )
                self.state.set_response(res_obj)
                self.state.clear_session(keep_response=True)
                return self.state.response

            ## 查询历史记录，如果存在，则直接返回，否则，调用故障分析程序，返回结果，根据返回结果，决定给客户的返回信息
            list1_json = fault_list.to_json()
            print(list1_json)
        
        
            ## case1:FaultCase = generate_fault_case_from_faultlist("/Users/liyansheng/github/langgraph/testp/tests/fault_list1.json", symptom_topic)
            symptom_topic ="程序运行崩溃"

            case1:FaultCase = generate_fault_case_from_faultlist_obj(fault_list, symptom_topic)
            ##？？？？？？======需要增加如果不能创建faultCase，也就是没有备选的fault怎么办
            if not case1:
                res_obj = FlowResponse (
                    type="fault_diagnosis_asking",
                    success=True,
                    message=f"历史记录中无该故障现象相关的记录：{symptom_topic}，因此系统无法进行故障分析。",
                    data={"is_final": True}
                )
                self.state.set_response(res_obj)
                self.state.clear_session(keep_response=True)
                return self.state.response
            
            case1_json = case1.to_json()
            print("###创建的faultcase成功是：", case1_json)                    
            ## 把faultcase 和 symptom_topic update session   
            self.state.slots["Fault_case"]=json.loads(case1_json)
            self.state.slots["Fault_list"]=json.loads(list1_json)
            self.state.slots["Intent_failure_times_value"]=0   
            curq:Question = Question("symptoms", symptom_topic, "yes")
            case1.next_question.clear()
            #把当前问题放到next下，为后面处理做准备
            case1.next_question.append(curq.to_dict())
            #curq:Question = case1.get_next_question_obj()
            
        ## 如果不是第一次提问，从state中获得list和case，而不是创建新的信息
        else:
            ## session中有faultcase信息，继续执行分析处理
            print ("====调用faultcase处理程序进行处理======")
            case1:FaultCase = FaultCase.from_json(self.state.slots.get( "Fault_case"))
            ## 准备答案
            user_input= self.state.query
            curq:Question = case1.get_next_question_obj()
            if curq.type == "symptoms" :
                result = CommonIntentCheck.evaluate(
                    llm, "", user_input, "",constants.Symptom_answer_check,
                    ismock=False
            )
            if result.target == "no" or result.target == "yes":
                ##把客户回答放入faultcase 的nextquestion中
                #nextq:Question = case1.get_next_question_obj()
                curq.answer = result.target  ## 结果放入
                #case1.next_question[0] = nextq.to_dict()
                        
                ##进行计算，计算完next question会自动更新
                fault_list= FaultList.from_json(self.state.slots.get("Fault_list"))
                   
        ## 无伦是第一次，还是后续处理，都统一处理
        ##取出faultcase中的 next question 问题对象,也就是当前客户输入答案对应的问题。
        #curq:Question = case1.get_next_question_obj()
        ## 判断问题类型是否为“symptoms”，如果是这种类型，那么用户的回答只能是“Yes” 或者“No”
        ## 意图判断客户回答是不是“Yes”
        ## 把question放入next中后进行计算============
        
        # 第一次放入faultcase作为下一问题，以后计算引擎自动产生next question，这样做，是为了faultcase中的compute统一一种计算算法                      
        ## 调用故障分析程序，返回结果，根据返回结果，决定给客户的返回信息  
        ##case1.compute("symptoms","提示内存溢出","yes",fault_list)
        case1.compute(fault_list)
        #把faultcase放入session
        #data_manager.set_data(user_id, "Fault_case", case1.to_json())
        self.state.slots["Fault_case"]=json.loads(case1.to_json())
        ## 判断flag是否结束
        flag = case1.judgementStop()
        print("=======faultcase is:", case1.to_json())
    
        ## 如果是stop
        if flag:
            print(f"===================judgementStop true======")
            print(case1.getResultStr())
            ##responseStr = case1.getResultStr()
            res_obj = FlowResponse(
                type="fault_diagnosis_asking",
                success=True,
                message=case1.getFullResultStr(fault_list),
                data={"is_final": True}
            )
            self.state.set_response(res_obj)
            self.state.clear_session(keep_response=True)
            return self.state.response
        
        nextq = case1.get_next_question_obj()
        print("@@@@@@ ===next question is:", nextq.to_json())
        print("@@@@@@ ===chat display is:", build_chat_question_text(nextq))
        self.state.slots["last_asked_question"] = json.loads(nextq.to_json())  
        res_obj = FlowResponse(
                type="fault_diagnosis_asking",
                success=True,
                message= build_chat_question_text(nextq),
                data={"is_final": False}
            )
        self.state.set_response(res_obj)
        #self.state.clear_session(keep_response=True)
        return self.state.response
          
    @listen("fitness_consulting")
    async def run_fitnessConsultingProcess(self):
        print(">>> 进入健身咨询子流程")
        # 实例化子 Flow 并同步状态
        sub_flow = FitnessConsultingProcessFlow()
        await sub_flow.kickoff_async(inputs=self.state.model_dump())
        sub_result = sub_flow.state.response
        print(f">>>>>fitnessConsulting子流程返回给主流程的信息: {sub_flow.state.response}")
        
        if isinstance(sub_result, dict) and "type" in sub_result:
            # 已经是标准格式
            self.state.response = sub_result
        else:
            # 兜底包装（防止未来子流程乱返回）
            self.state.response = {
                    "type": "fitness_consulting",
                    "success": True,
                    "message": "结果以返回",
                    "data": None
            }
        # 将自流程状态更新到主流程状态
        # self.state.response = sub_flow.state.response
        print(f">>>>>子流程返回给主流程的信息: {self.state.response}")
        ## 清除状态，避免子流程状态污染主流程
        self.state.clear_session(keep_response=True)
        return self.state.response
        ""
        # ====== 安全校验 ======
    
        
    ## 监听 order_state 意图，进入订单状态查询子流程
    @listen("order_state")
    async def run_orderStateProcess(self):
        print(">>> 进入物流子流程")
        # 实例化子 Flow 并同步状态
        sub_flow = OrderStateProcessFlow()
        await sub_flow.kickoff_async(inputs=self.state.model_dump())
        sub_result = sub_flow.state.response
        # ====== 安全校验 ======
        
        if isinstance(sub_result, dict) and "type" in sub_result:
            # 已经是标准格式
            self.state.response = sub_result
        else:
            # 兜底包装（防止未来子流程乱返回）
            self.state.response = {
                    "type": "order_state",
                    "success": True,
                    "message": str(sub_result),
                    "data": None
            }
        # 将自流程状态更新到主流程状态
        # self.state.response = sub_flow.state.response
        print(f">>>>>子流程返回给主流程的信息: {self.state.response}")
        
        ## 清除状态，避免子流程状态污染主流程
        self.state.clear_session(keep_response=True)
        return self.state.response
        """
        res_obj = FlowResponse(
            type="order_state",
            success=True,
            message=str(sub_result), # 确保是字符串
            data={
                "order_id": self.state.slots.get("order_id"),
                "order_state": self.state.slots.get("order_state")  # 如果有更详细的 JSON 数据可以放这里
            }
        )

        # 4. 使用你定义的优化方法更新状态
        # 这会自动处理对象到字典的转换（即调用你定义的 set_response）
        self.state.set_response(res_obj)
        print(f">>>>> 子流程处理完毕，已统一格式并存入 state")
        # 5. 必须 return，这样 flow.kickoff 才能拿到这个结果
        return res_obj
        """
        
        

    @listen("tech_support")
    def handle_tech(self):
        print(f"激活技术支持逻辑，设备类型: {self.state.slots.get('device_type')}")
        # return TechCrew().kickoff(inputs=self.state.slots)
        #self.state.response = "已为您联系技术工程师。"
        self.state.response = {
            "type": "tech_support",
            "success": True,
            "message": "已为您联系技术工程师。",
            "data": None
        }

    @listen("unknown")
    def handle_unknown(self):
        print("无法识别的意图")
        self.state.response = {
            "type": "unknown",
            "success": False,
            "message": "抱歉，我不太明白您的意思，请尝试重新输入。",
            "data": None
        }
        
    @listen("transaction_count_query")
    def handle_transaction_count_query(self):
        print(">>> 进入交易量查询子流程")
        # 这里可以将 self.state.slots 传递给 TransactionCountQueryFlow
        # return TransactionCountQueryFlow().kickoff(inputs=self.state.slots)
        self.state.response = {
            "type": "transaction_count_query",
            "success": True,
            "message": f"机构 {self.state.slots.get('org_name')} 最近 {self.state.slots.get('duration')} 的交易数量为 12345 笔。",
            "data": None
        }
    
    def _load_business_rules(self, path):
        """
        私有方法：安全加载 YAML 配置文件
        """
        if not os.path.exists(path):
            print(f"警告: 配置文件 {path} 未找到，将使用空规则。")
            return {}
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
                print(f"成功加载业务规则: {list(rules.keys())}")
                return rules or {}
        except Exception as e:
            print(f"读取业务规则失败: {e}")
            return {}
    

    ## 支持异步
    ## 执行route 子crew，实现意图识别，槽为提取，完整性检查等功能
    async def _execute_routing_crew(self) -> IntentOutput:
        """
        专门负责组装和执行路由 Crew 的私有方法
        """
        #langfuse_handler = CallbackHandler()
        
        last_q = self.state.slots.get("last_asked_question", "无")
        r_agent = self.agents_factory.router_agent()
        routing_task = self.tasks_factory.routing_task(
            r_agent,
            self.state.query,
            ## 为了多轮输入参数，将当前状态中的 slots 传递给意图识别任务
            self.state.intent,
            self.state.slots,
            last_q,
            IntentOutput
        )
        result = Crew(
            agents=[r_agent], 
            tasks=[routing_task],
            verbose=False, # 路由通常不需要刷屏日志
            #callbacks=[langfuse_handler]
        ).kickoff()
        return result.pydantic

# --- 4. 运行 ---
if __name__ == "__main__":
    # 模拟从 Web 前端传来的数据
    user_input_from_web = "我想查询我的订单状态，订单号是 9527"
    flow = MainFlow()
    flow.kickoff(inputs={"query": user_input_from_web})
    
    
    
    print(f"最终回复: {flow.state.response}")