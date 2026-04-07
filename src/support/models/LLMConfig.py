import os
##from langchain_community.chat_models import ChatOllama
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatTongyi
from langchain.chat_models import init_chat_model  # DeepSeek

class LLMConfig:
    """
    大模型全局配置类，支持 Ollama / Qwen / DeepSeek / ChatGPT
    自动从环境变量加载 API Key 和 Base URL
    """

    _config = {
        "provider": None,       # ollama, qwen, deepseek, chatgpt
        "model_name": None,
        "temperature": 0.7,
        "api_key": None,
        "api_base": None
    }

    _llm_instance = None

    ENV_KEY_MAP = {
        "chatgpt": "OPENAI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "qwen": "DASHSCOPE_API_KEY",
        "ollama": None  # Ollama 本地部署，一般不需要 key
    }

    ENV_BASE_MAP = {
        "chatgpt": "OPENAI_API_BASE",
        "deepseek": "DEEPSEEK_API_BASE",
        "qwen": "DASHSCOPE_API_BASE",
        "ollama": "OLLAMA_API_BASE"
    }

    def __init__(self, provider=None, model_name=None, temperature=0.7, api_key=None, api_base=None):
        if provider:
            self.set("provider", provider)
        if model_name:
            self.set("model_name", model_name)
        if temperature is not None:
            self.set("temperature", temperature)

        # 如果没传 api_key，尝试从环境变量读取
        if api_key:
            self.set("api_key", api_key)
        else:
            env_key = self.ENV_KEY_MAP.get(provider)
            if env_key:
                self.set("api_key", os.environ.get(env_key))

        # 如果没传 api_base，尝试从环境变量读取
        if api_base:
            self.set("api_base", api_base)
        else:
            env_base = self.ENV_BASE_MAP.get(provider)
            if env_base:
                self.set("api_base", os.environ.get(env_base))

    @classmethod
    def set(cls, key, value):
        cls._config[key] = value

    @classmethod
    def get(cls, key, default=None):
        return cls._config.get(key, default)

    @classmethod
    def all(cls):
        return cls._config

    @classmethod
    def build_llm(cls):
        """
        根据 provider 构建不同的大模型实例
        """
        provider = cls.get("provider")
        model_name = cls.get("model_name")
        temperature = cls.get("temperature", 0.7)
        api_key = cls.get("api_key")
        api_base = cls.get("api_base")

        if provider == "ollama":
            cls._llm_instance = ChatOllama(
                model=model_name,
                temperature=temperature,
                base_url=api_base
            )

        elif provider == "qwen":
            cls._llm_instance = ChatTongyi(
                model_name=model_name,
                temperature=temperature,
                ##openai_api_base=api_base,
                openai_api_key=api_key
            )

        elif provider == "deepseek":
            cls._llm_instance = init_chat_model(
                model_name,
                model_provider="deepseek",
                api_key=api_key,
                base_url=api_base
            )

        elif provider == "chatgpt":
            cls._llm_instance = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                api_key=api_key,
                base_url=api_base
            )

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        return cls._llm_instance

    @classmethod
    def llm(cls):
        """获取大模型实例"""
        if cls._llm_instance is None:
            return cls.build_llm()
        return cls._llm_instance

if __name__ == "__main__":
    ## 测试 LLMConfig 

    config = LLMConfig(provider="deepseek", model_name="deepseek-chat")
    llm = LLMConfig.llm()
    print(llm.invoke("你好 DeepSeek!"))

    '''
    config = LLMConfig(provider="ollama",api_base="http://192.168.1.13:11434", model_name="gpt-oss:20b")
    llm = LLMConfig.llm()
    print(llm.invoke("你好 ollama!"))
    '''
    '''
    config = LLMConfig(provider="qwen", model_name="qwen-max")
    llm = LLMConfig.llm()
    print(llm.invoke("你好 qwen!"))
    '''

