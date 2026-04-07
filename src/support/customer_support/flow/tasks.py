# To know more about the Task class, visit: https://docs.crewai.com/concepts/tasks
from crewai import Task
from textwrap import dedent
import yaml
import os
from typing import Literal


class CSTasks:
    
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), '../config', 'tasks.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def order_state_task(self, agent, query, output_model):
        return Task(
            config=self.config['order_state_task'],
            agent=agent,
            description=self.config['order_state_task']['description'].format(order_id=query),
            output_pydantic=output_model,
            verbose=True
        )
    
    def bmi_task(self, agent, var1, var2):
        return Task(
            config=self.config['bmi_task'],
            description=self.config['bmi_task']['description'].format(height=var1, weight=var2),
            output_file="bmi_report.txt",
            agent=agent,
        )

    def fitness_task(self, agent, context_tasks:list, output_model):
        """
        通过 context_tasks 参数，将 bmi_task 的输出作为背景信息传给健身任务
        """
        return Task(
            config=self.config['fitness_task'],
            agent=agent,
            description=self.config['fitness_task']['description'],
            # 声明上下文依赖
            context=context_tasks,
            output_file="fitness_plan.md",
            output_pydantic=output_model,
            verbose=True
        )

 