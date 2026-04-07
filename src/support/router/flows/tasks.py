# To know more about the Task class, visit: https://docs.crewai.com/concepts/tasks
from crewai import Task
from textwrap import dedent
import yaml
import os
from typing import Literal
from pydantic import BaseModel
from crewai.flow.flow import Flow, start, listen, router


class CustomTasks:
    
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), '../config', 'tasks.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    ## 从yaml文件获取任务配置
    def routing_task(self,agent, query,current_intent, current_slots,last_asked_question, output_model):
        return Task(
            config=self.config['routing_task'],
            agent=agent,
            ## 你应该把 slots 通过 description 注入到 Prompt 中，让 Agent 看到它。
            description=self.config['routing_task']['description'].format(
                query=query,
                current_intent=current_intent,
                current_slots=current_slots,
                last_asked_question=last_asked_question,
            ),
            output_pydantic=output_model,
            verbose=True
        )
        
    ## 未实现
    ## 安全检查任务，每个crew流程最后一步都要调用，确保输出符合安全要求
    def security_check_task(self, agent, output_model):
        return Task(
            config=self.config['security_check_task'],
            agent=agent,
            description=self.config['security_check_task']['description'],
            output_pydantic=output_model,
            verbose=True
        )
    ## 未实现    
    ## 隐私安全检查任务，专门检查输出中是否包含敏感信息
    def privacy_check_task(self, agent, output_model):
        return Task(
            config=self.config['privacy_check_task'],
            agent=agent,
            description=self.config['privacy_check_task']['description'],
            output_pydantic=output_model,
            verbose=True
        )
    
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission!"
  
 