## ==============意图识别和答案判别===================
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
#from typing import List, Dict
from src.support.models.LLMConfig import LLMConfig
from src.support.models.SessionManager import SessionManager
from src.support.models import constants

class CommonIntentCheck(BaseModel):
    """
    用于结构化输出，承载用户的意图判断结果。
    注意：target 字段的 description 仍然是固定的，但我们在 Prompt 中会动态替换意图判断的说明。
    """
    target: str = Field(
        # 这里的 description 主要用于Pydantic的自我描述和Schema生成，
        # 实际的判断逻辑和描述在下面的 evaluate 方法的 prompt 中动态替换。
        description="判断用户的核心意图。可选值根据Prompt中的描述而定。"
    )

    @classmethod
    def evaluate(
        cls,
        llm,
        question: str,
        user_answer: str,
        history: str = None,
        intent_description: str = None,
        ismock: bool = False
    ) -> "CommonIntentCheck":
        """
        调用大模型，判断用户意图
        :param llm: LangChain LLM 实例
        :param question: 问题
        :param user_answer: 用户回答
        :param history: 历史对话 [{"role": "user"/"assistant", "content": "xxx"}, ...]
        :param intent_description: 意图判断的描述，用于指导LLM的判断和输出值。
        """
        # ===============================================
        # 检查 ismock 参数并返回固定值
        if ismock:
            print("===============================================")
            print("!!! MOCK 模式启用：返回固定意图: 'mocked' !!!")
            print("===============================================")
            # 返回 CommonIntentCheck 的实例，target 赋值为 "mocked"
            return cls(target="mocked")
        # ===============================================
        
        structured_llm = llm.with_structured_output(cls)
        prompt = f"""
        问题：{question}
        用户回答：{user_answer}
        和用户对话历史：{history}

        请判断：
        1. 根据用户的回答，判断用户的意图，{intent_description}
        只需要输出字段 target。
        """

        print("===============================================")
        print(prompt)
        print("===============================================")
        return structured_llm.invoke(prompt)


if __name__ == "__main__":
    # 初始化 LLM，可以换成你自己的模型
    ##llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    config = LLMConfig(provider="qwen", model_name="qwen-max")
    llm = LLMConfig.llm()
    manager = SessionManager()
    
    #config = LLMConfig(provider="ollama",api_base="http://192.168.1.13:11434", model_name="gpt-oss:20b")
    #llm = LLMConfig.llm()
  
  
    q = "有什么可以帮助的"
    user_input = "请帮我分析问题"
    history = manager.getHistory("lys", 10) 
    print ("history is :",history)
    
    result =  CommonIntentCheck.evaluate(
        llm, q, user_input, history,constants.Fault_check_desc,
        ismock=True
        )
    print("用户意图1:", result.target)
    manager.add_message("lys", "user",user_input)
    manager.add_message("lys", "system",q)
    
    
    q = "请说出故障现象"
    user_input = "天气如何"
    history = manager.getHistory("lys", 10) 
    print ("history is :",history)
    
    result = CommonIntentCheck.evaluate(
        llm, q, user_input, history,constants.Weather_get_desc,
        ismock=True
        )
    print("用户意图2:", result.target)
    manager.add_message("lys", "user",user_input)
    manager.add_message("lys", "system",q)