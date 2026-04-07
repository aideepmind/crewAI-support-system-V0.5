
# 全局 LLM 配置
LLM_PROVIDER = "qwen"
LLM_MODEL = "qwen-max"
#LLM_TEMPERATURE = 0.7

# 初始化 LLM 实例
from src.support.models.LLMConfig import LLMConfig

_config = LLMConfig(
    provider=LLM_PROVIDER, 
    model_name=LLM_MODEL,
    #temperature=LLM_TEMPERATURE
)
llm = _config.llm()
