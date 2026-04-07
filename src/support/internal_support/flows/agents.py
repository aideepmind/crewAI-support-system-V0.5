from decouple import config
from crewai import Agent
from textwrap import dedent
## from langchain.llms import OpenAI, Ollama
from langchain_openai import ChatOpenAI
import os
from crewai import Agent, LLM
import yaml
from src.support.tools.tools import SupportState, IntentOutput, get_deepseek_llm


class ISAgents:
    def __init__(self):        
        self.DeepSeek = get_deepseek_llm()
        
        # 加载配置文件
        config_path = os.path.join(os.path.dirname(__file__), '../config', 'agents.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
