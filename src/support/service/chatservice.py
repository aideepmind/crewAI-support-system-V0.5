from fastapi import FastAPI, HTTPException # type: ignore
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import datetime
import json, traceback
from src.support.tools.ReqMessage import ReqMessage
from src.support.router.flows.MainSupportFlow import MainFlow

class chatRequest(BaseModel):
    user_id: str
    message: str
    
# 创建 FastAPI 应用表示是个API service
app = FastAPI()

# IMPORTANT: 生产环境中，SECRET_KEY 必须是一个长、随机且保密的字符串。
#app.add_middleware(SessionMiddleware, secret_key="your-long-secret-key-here", session_cookie="user_history_id")

# 添加 CORS 中间件,目的是为了解决跨域问题，由于使用的是本地启动的html，因为跨域问题，没有权限调用server
## 上的http服务，因此使用如下定义，设置可以跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或者指定 ["http://localhost:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 辅助函数，用于向调试列表添加信息
def add_debug(debug_list: List[Dict[str, Any]], key: str, value: Any):
    """
    向调试信息列表中添加一个键值对。
    
    :param debug_list: 存储调试信息的列表。
    :param key: 调试信息的键。
    :param value: 调试信息的值。
    """
    debug_list.append({"key": key, "value": value})
     
def add_debug_info(userid:str, debug_info=None):
    add_debug(debug_info, "symptom_topic", "testing")
 

# 存储所有活跃用户的流程实例
# key: user_id (str), value: MainFlow instance
active_flows: dict[str, MainFlow] = {}
  
# 一个简单的测试接口
@app.post("/chat")
async def testchat1(chatRequest: chatRequest):
    # 1. 初始化调试信息列表
    debug_info = []
    responseStr = ''
    try:
        reqmes=ReqMessage(chatRequest.user_id,chatRequest.message)
        reqmes.print()
        q = "有什么可以帮助的"
        user_input = chatRequest.message
        user_id = chatRequest.user_id
        print (f"user id is {user_id}, user input is {user_input}")
        
        # 如果该用户已有 flow 实例，则复用，否则新建
        if user_id not in active_flows:
            active_flows[user_id] = MainFlow()
            print(f"为用户 {user_id} 创建了新的 Flow 实例")
        flow = active_flows[user_id]
        
        flow.state.query = user_input
        result = await flow.kickoff_async(
            inputs={"query": user_input}
        )
        print(f"<<<< main程序最终获得的result返回结果: {result}")
        print(f"<<<< main程序最终获得的flow.state.response返回结果: {flow.state.response}")
        print(f"<<<< type(flow.state.response): {type(flow.state.response)}")
        print(f"<<<< type(result): {type(result)}")
        responseStr = str(flow.state.response)
        print(f"<<<< result 内容: {result}")
        
        # 1. 检查 result 是否是我们定义的 FlowResponse 对象
        if result and hasattr(result, 'message'):
            print (f"!!!! result 是一个 FlowResponse 对象，message: {result.message}")
            response_text = result.message
            # 如果你想把整个结构传给前端
            return {
                "response": result, 
                ##"debug": debug_info
                "debug":flow.state.response
            }
        
        # 2. 保底逻辑：如果 result 为空，再看 state
        # response_text = result if flow.state.response else "抱歉，我没有理解您的意思。"
        if flow.state.response and hasattr(flow.state.response, 'data'): 
             data_content = flow.state.response.data 
             print(f"==== data content: {data_content}")
             #add_debug_info(user_id, data_content)
        else:
            data_content = None
            
        return {"response":flow.state.response, "debug":flow.state.response }
     
    
    except Exception as e:
        print("ERROR:",e)
        traceback.print_exc()
        add_debug(debug_info, "error", str(e))
        add_debug(debug_info, "end_time", datetime.datetime.now().isoformat())
        # 如果需要，可以将 debug_info 记录到日志系统，并返回一个干净的错误
        raise HTTPException(status_code=500, detail=str(e))
