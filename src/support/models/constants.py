# Intent
Fault_check_desc =  "根据用户的输入，判断用户的意图，如果是想定位故障，取值：'fault' 或 'else'"
Weather_get_desc = "根据用户的输入，判断用户是想获得天气信息吗，取值：'yes' 或 'no'"
IS_symptom_desc = "用户的输入信息中，是否包含设备故障的具体，明确，可重现的现象描述，取值：'yes' 或 'no'"
Session_reset =  "判断用户是否输入了'reset'，取值：'yes' 或 'no'"
# 回答问题的判断
Symptom_answer_check = "根据用户的输入，判断用户的回答是肯定还是否定，或者是其他，取值：'yes' 或 'no' 或 'else'"
# 通用LLM处理
GET_symptom_desc = "下面是一个用户的输入信息，取出用户输入信息中的故障现象的描述文本,只返回单纯的故障现象的具体描述内容，其他信息不返回，以下全部是用户的输入："
# 判断两个参数的语义相似度，用于1，判断用户的回答是否和预期的问题答案相似 2，故障现象的相似度判断
# 在falutcase的compute中会用到
Similarity_check_desc = "判断下面两个文本的语义相似度是否很高，如果很高，取值：'yes'，否则取值：'no'"