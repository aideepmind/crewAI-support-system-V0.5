from src.support.router.flows.MainSupportFlow import MainFlow
if __name__ == "__main__":
    # 模拟从 Web 前端传来的数据
    #user_input_from_web = "我想查询我的订单状态，订单号是 9527"
    #user_input_from_web = "我有一个订单 号码是44444，现在怎样了？"
    #user_input_from_web = "我有一个订单，现在怎样了？"
    #user_input_from_web = "我们的一笔业务的状态如何，单号56666"
    #user_input_from_web = "查询业务的状态，56666"
    #user_input_from_web = "查询业务，11111111"
    #user_input_from_web = "查询订单，48585"
    user_input_from_web = "帮我进行订单查询"
    
 
    flow = MainFlow()
    result = flow.kickoff(inputs={"query": user_input_from_web})
    
    print(f"<<<< flow.state.response结果: {flow.state.response}")
    print(f"..... result 返回结果: {flow.state.response}")
    
    
    