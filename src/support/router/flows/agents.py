from decouple import config
from crewai import Agent
from textwrap import dedent
## from langchain.llms import OpenAI, Ollama
from langchain_openai import ChatOpenAI
import os
from crewai import Agent, LLM
import yaml
from src.support.tools.tools import  get_deepseek_llm

class CustomAgents:
    def __init__(self):        
        self.DeepSeek = get_deepseek_llm()
        
        # 加载配置文件
        config_path = os.path.join(os.path.dirname(__file__), '../config', 'agents.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
     ## 从yaml文件获取agent配置
    def router_agent(self):
        return Agent(
            config=self.config['router_agent'], 
            llm=self.DeepSeek,
            verbose=True
        )
    ##  未实现
    ##  安全检查 Agent，专门负责对输出结果进行安全审查，确保不包含敏感信息或违规内容  
    def security_check_agent(self):
        return Agent(
            config=self.config['security_check_agent'], 
            llm=self.DeepSeek,
            verbose=True
        )
    ## 未实现
    ## 隐私检查 Agent，专门负责对输出结果进行隐私审查，确保不泄露用户隐私信息
    def privacy_check_agent(self):
        return Agent(
            config=self.config['privacy_check_agent'], 
            llm=self.DeepSeek,
            verbose=True
        )  


    def router_agent_bk(self):
        return Agent(
            role="意图路由专家",
            goal=dedent(f"""准确识别用户意图并提取订单号或设备类型等信息"""),
            backstory=dedent(f"""你负责解析用户需求。如果是订单查询，必须提取 order_id；如果是技术支持，提取 device_type。"""),
            allow_delegation=False,
            verbose=True,
            #llm=LLM(model="deepseek/deepseek-chat",base_url=os.getenv("OPENAI_API_BASE")),
            llm=self.DeepSeek
        )

   

