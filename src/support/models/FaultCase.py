import json
import math
from typing import Any, Dict, List, Optional
from src.support.models.FaultList import FaultList
from src.support.models.Question import Question

from src.support.api.CommonIntent import CommonIntentCheck
from src.support.models import constants
from src.support.models.LLMConfig import LLMConfig

from src.support.api.config import llm
from src.support.api.tools import ai_matching_input_to_options


class FaultCase:
    ENTROPY_THRESHOLD = 0.1
    """故障诊断案例类，用于管理单个案例的全部数据及JSON互转"""

    def __init__(self,
                 case_id: str,
                 device: Dict[str, Any],
                 env: Dict[str, Any],
                 symptom_text: str,
                 symptoms_all: List[str],
                 symptoms_share: List[str],
                 candidates: List[Dict[str, Any]],
                 asked: List[Dict[str, Any]],
                 next_question: List[Dict[str, Any]],
                 stop: bool = False):
        self.case_id = case_id
        self.device = device
        self.env = env
        self.symptom_text = symptom_text
        self.symptoms_all = symptoms_all
        self.symptoms_share = symptoms_share
        self.candidates = candidates
        self.asked = asked
        self.next_question = next_question
        self.stop = stop

    # ========== 基础读写方法 ==========
    @classmethod
    def create_empty(cls, case_id: str) -> "FaultCase":
        """只通过 case_id 创建一个空的 FaultCase 对象"""
        return cls(
            case_id=case_id,
            device={"brand": "", "series": "", "fw": ""},
            env={"voltage": 0, "phase": 0, "ambient_temp": 0},
            symptom_text="",
            symptoms_all=[],
            symptoms_share=[],
            candidates=[],
            asked=[],
            next_question=[],
            stop=False
        )

    def get_field(self, field: str) -> Any:
        """按字段名读取"""
        return getattr(self, field, None)

    def set_field(self, field: str, value: Any):
        """按字段名写入"""
        if hasattr(self, field):
            setattr(self, field, value)
        else:
            raise AttributeError(f"字段 '{field}' 不存在。")

    # ========== JSON互转方法 ==========

    @classmethod
    def from_json(cls, json_data: Any) -> "FaultCase":
        """从 JSON（字符串或字典）创建 FaultCase 对象"""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        return cls(**data)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "FaultCase":
        """从 JSON 文件加载 FaultCase 对象"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_json(data)

    def to_json(self, indent: int = 2, ensure_ascii: bool = False) -> str:
        """将对象转换为 JSON 字符串"""
        return json.dumps(self.__dict__, indent=indent, ensure_ascii=ensure_ascii)
    
    def save_to_file(self, filepath: str):
        """将对象保存为 JSON 文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.__dict__, f, indent=2, ensure_ascii=False)

    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为 Python 字典"""
        return self.__dict__

    # ========== 数据操作示例方法 ==========

    def add_asked(self, q_type: str, question: str, answer: str):
        """新增一条已提问记录"""
        new_id = len(self.asked) + 1
        self.asked.append({"id": new_id, "type": q_type, "quesion": question, "answer": answer})

    def update_candidate(self, fault_id: str, posterior: Optional[float] = None, prior: Optional[float] = None):
        """更新候选故障的概率"""
        for cand in self.candidates:
            if cand["fault_id"] == fault_id:
                if posterior is not None:
                    cand["posterior"] = posterior
                if prior is not None:
                    cand["prior"] = prior
                return
        raise ValueError(f"未找到 fault_id={fault_id} 的候选项。")

    def next_to_asked(self):
        """将下一问题移动到已问列表（模拟提问完成）"""
        if not self.next_question:
            return
        nq = self.next_question.pop(0)
        self.add_asked(nq["type"], nq["quesion"], nq.get("answer", "未回答"))
        
    def next_to_asked1(self):
        """将下一问题移动到已问列表"""
        if not self.next_question:
            return
        nq_dict = self.next_question.pop(0)
        nq = Question.from_dict(nq_dict)
        self.add_asked(nq.type, nq.question, nq.answer or "未回答")
        

    def __repr__(self):
        return f"<FaultCase {self.case_id}, stop={self.stop}, candidates={len(self.candidates)}>"

    # 设置设备信息
    def set_device(self, brand, series, fw):
        self.device = {"brand": brand, "series": series, "fw": fw}

    # 设置环境信息
    def set_env(self, voltage, phase, ambient_temp):
        self.env = {"voltage": voltage, "phase": phase, "ambient_temp": ambient_temp}


    # 添加候选故障
    def add_candidate(self, fault_id, fault, prior, posterior):
        self.candidates.append({
            "fault_id": fault_id,
            "fault": fault,
            "prior": prior,
            "posterior": posterior
        })

    # 添加提问记录
    def add_asked(self, q_type, question, answer):
        new_id = len(self.asked) + 1
        self.asked.append({
            "id": new_id,
            "type": q_type,
            "quesion": question,
            "answer": answer
        })

    # 设置下一问题
    #def set_next_question(self, q_type, question, answer):
    #    self.next_question = [{"type": q_type, "quesion": question, "answer": answer}]
        
    def set_next_question(self, q_type, question, answer):
        q = Question(q_type, question, answer)
        self.next_question = [q.to_dict()]

    
    def set_symptoms(self, symptom_text: str, all_list: list, share_list: list):
        """设置症状信息"""
        self.symptom_text = symptom_text
        self.symptoms_all = all_list
        self.symptoms_share = share_list
    
    
    ##打印结果
    def printResult(self):
        candidates_list = self.candidates
        print("--- 逐条打印候选故障信息 ---")
        for index, record in enumerate(candidates_list):
            print(f"记录 {index + 1}:")
            # 打印字典的所有键值对
            for key, value in record.items():
                print(f"  - {key}: {value}")
        print("-" * 30)

    ## 返回各个fault后验概率结果的字符串，用于给前端
    def getResultStr(self) -> str:
        candidates_list = self.candidates
        formatted_records = [
            f"ID: {item['fault_id']}, 故障: {item['fault']}, 概率: {item.get('posterior', 'N/A')}"
            for item in candidates_list
        ]
        # 使用换行符 '\n' 将所有记录连接成一个单一字符串
        candidates_str_custom = "\n".join(formatted_records)
        #print("--- 自定义格式的字符串变量 ---")
        #print(candidates_str_custom)
        return candidates_str_custom

    ## 返回各个fault后验概率和根本原因的字符串，用于给前端
    def getFullResultStr(self, faultlist: FaultList, format: str = "text") -> str:
        """
        返回包含 fault_id、后验概率和根本原因的格式化字符串

        参数:
            faultlist: FaultList 对象，用于获取故障的详细信息
            format: 返回格式，可选值：
                - "text": 纯文本格式（默认）
                - "json": JSON字符串格式
                - "html": HTML有序列表格式
                - "dict": Python字典格式（用于API返回）

        返回:
            根据format参数返回不同格式的结果
        """
        import json

        # 1. 收集所有候选故障的信息
        fault_info_list = []

        for cand in self.candidates:
            fault_id = cand['fault_id']
            posterior = cand.get('posterior', 0.0)

            # 从 faultlist 中获取对应的 fault 对象
            fault_obj = faultlist.get_fault(fault_id)

            if fault_obj:
                cause = fault_obj.get_cause()
            else:
                cause = "未找到故障原因"

            fault_info_list.append({
                'fault_id': fault_id,
                'fault': cand['fault'],
                'posterior': posterior,
                'posterior_percent': f"{posterior*100:.2f}%",
                'cause': cause
            })

        # 2. 按 posterior 从大到小排序
        fault_info_list.sort(key=lambda x: x['posterior'], reverse=True)

        # 3. 根据format参数返回不同格式
        if format == "json":
            # JSON字符串格式
            return json.dumps(fault_info_list, ensure_ascii=False, indent=2)

        elif format == "html":
            # HTML有序列表格式
            html_items = []
            for index, item in enumerate(fault_info_list, 1):
                html_items.append(
                    f'<li>ID: {item["fault_id"]} | 故障: {item["fault"]} | '
                    f'概率: {item["posterior"]:.6f} ({item["posterior_percent"]}) | '
                    f'根因: {item["cause"]}</li>'
                )
            return f'<ol>\n' + '\n'.join(html_items) + '\n</ol>'

        elif format == "dict":
            # 返回字典对象（用于API）
            return {
                'success': True,
                'data': fault_info_list,
                'total': len(fault_info_list)
            }

        else:  # format == "text" (默认)
            # 纯文本格式（编号列表）
            formatted_records = []
            for index, item in enumerate(fault_info_list, 1):
                formatted_records.append(
                    f"{index}. ID: {item['fault_id']} | 故障: {item['fault']} | "
                    f"概率: {item['posterior']:.6f} ({item['posterior_percent']}) | "
                    f"根因: {item['cause']}"
                )
            return "\n".join(formatted_records)


    #计算“不确定性熵”
    def compute_entropy(self) -> float:
        """根据 candidates 中 posterior 计算不确定性熵"""
        entropy = 0.0

        for c in self.candidates:
            p = c.get("posterior", 0)
            if p > 0:                  # 避免 log(0)
                entropy += - p * math.log(p, 2)
        return entropy
    
    ## 判断“不确定性熵”是否满足小于等于ENTROPY_THRESHOLD，结果满足，不再继续提问  
    def judgementStop(self) -> bool:
        ##entropy = self.compute_entropy()
        ##return entropy <= self.ENTROPY_THRESHOLD
        return self.stop

    # 基于自己case数据，问题类型，问题，答案，进行概率计算，计算结果更新自己
    # 三种问题类型：
    # 类型1:symptoms 提问方式为：是否有该如下现象发生：{symptom}
    # 用户回答的正确答案默认就是“yes”或者 语义识别就是“有该现象”.
    # 注意：第一次调用compute时由于当前客户输入的现象默认就是肯定答案“yes”，因此就不需要再提问了。后续需要提问。
    # 因此第一次，调用compute前需要通过 faultcase的append 函数讲客户输入的“症状” 放入next question
    ## case1.next_question.append(q1.to_dict())
    # 这之后就可以使用compute 进行概率计算了。
    # 类型2:test，正确答案根据fault中定义进行语义识别
    # 类型3:check，正确答案根据fault中定义“yes”，“no”
    # 第一次调用时，由于当前输入的故障现象，也就是“symptom_topic” 默认的答案就是yes，进行概率计算，同时
    # 计算完成后，产生 next_question，用于返回后提问。
    # qtype：问题类型
    # quesiton：问题内容
    # answer：问题答案 （通过语义分析进行和fault中的答案匹配）
    # 计算时把fault candidates 中每个fault的“后验概率”（如果存在，第一次计算不存在）赋值给“先验概率”
    # 然后基于next 进行计算

    # 计算后验概率，并更新当前 FaultCase 状态，将next_question中的问题移动到asked中，然后
    # 基于candidates选择下一个symptom放入next_question
    
    def compute_test(self, flist: FaultList):
        return
    
    def compute_check(self, flist: FaultList):
        return
    
    def getNextQuestion(self) -> Question:
        if not self.next_question:
            return None
        nq_dict = self.next_question.pop(0)
        nq = Question.from_dict(nq_dict)
        return nq

    def compute(self, flist: FaultList):
        # ========== 0. 从 next_question 取出当前的问题 ==========
        #if not self.next_question:
        #    print("[compute] next_question 为空，无法计算。")
        #    self.stop = True
        #    return


        # 只取第一个问题，默认情况也只有一个
        #nq_dict = self.next_question.pop(0)
        #nq = Question.from_dict(nq_dict)
        
        nq = self.getNextQuestion()
        if nq == None:
            print("[compute] next_question 为空，无法计算。")
            self.stop = True
            return
        
        qtype = nq.type
        question = nq.question
        answer = nq.answer
        
        ## ？？？？？？处理 test 和 check 类型的问题，未实现？？？？？？？？
        if qtype == "test":
            self.compute_test(flist)
            return
        
        if qtype == "check":
            self.compute_check(flist)
            return
        
        # ========== 1. 以下处理 symptoms 类型（保持原逻辑）==========
        
        # 判断answer是否为no或No
        is_no = answer.lower() == "no"
        if is_no:  ## 如果答案是 no，直接跳过，不进行贝叶斯计算
            
            print(f"[compute] 用户回答 no，跳过贝叶斯计算。")
            
            matched_symptom = ai_matching_input_to_options(question, self.symptoms_share, 1)
            self.add_asked(qtype, matched_symptom, answer)

            # 重新选择下一个 symptom
            next_symptom = None
            for s in self.symptoms_share:
                if not any(a["quesion"] == s for a in self.asked):
                    next_symptom = s
                    break
            if next_symptom:
                self.set_next_question("symptoms", next_symptom, "")
                print(f"[compute] 下一问题: {next_symptom}")
            else:
                self.next_question = []
                self.stop = True
                print("[compute] 没有更多症状可提问，结束诊断。")
            return

        # 回答是yes，继续进行计算
        print(f"[compute] 当前问题: type={qtype}, question={question}, answer={answer}")

       

        # 通过大模型进行语意匹配，需要优化，传一个数组给大模型，一次调用，返回那个匹配的结果
        # 在 symptoms_share 中查找是否存在该 symptom
        # matched_symptom = None
        '''
        for s in self.symptoms_share:
            # 判断相似度
            result1 = CommonIntentCheck.evaluate(
                llm, s, question, None,constants.Similarity_check_desc,
                    ismock=False
                )
            if result1.target == "yes":
                matched_symptom = s
                break
         '''
        ## 使用 ai_matching_input_to_options 进行匹配,大模型调用
        ## 传入 question，和 symptoms_share 列表,返回匹配的 symptom，用列表中的那个
        matched_symptom = ai_matching_input_to_options(question, self.symptoms_share, 1)
        if matched_symptom == '' or matched_symptom is None:
            print(f"[compute] 未找到匹配症状: {question} -> 结束诊断")
            self.stop = True
            return

        print(f"[compute] 找到 symptom: {matched_symptom}，开始计算后验概率。")

        # ========== 2. 根据 symptom 更新 candidates ==========
        total_posterior = 0.0

        for cand in self.candidates:
            fault_id = cand["fault_id"]

            # 2.1 获取 fault object
            fault_obj = flist.get_fault(fault_id)
            if not fault_obj:
                print(f"[compute] 未找到 fault_id={fault_id}")
                continue
            
            ## 计算前把posterior值赋给prior
            posterior = cand.get("posterior", 0.0)

            if posterior == 0:
                # 第一次计算，使用原始 prior
                prior = cand.get("prior", 0.0)
                print(f"[compute] fault={fault_id}, 第一次计算，使用原始 prior={prior}")
            else:
                # 后续计算，将上次的 posterior 作为新的 prior
                prior = posterior
                cand["prior"] = prior  # 更新 prior
                print(f"[compute] fault={fault_id}, 使用上次 posterior 作为 prior={prior}")

            # 2.2 找到对应 symptom 的 likelihood
            likelihood = None
            for sym in fault_obj.get_symptoms():
                if sym.get("name") == matched_symptom:
                    likelihood = sym.get("likelihoods", 0.0)
                    break

            if likelihood is None:
                likelihood = 0.01
                print(f"[compute] fault={fault_id} 未定义该 symptom 的似然值，使用默认 0.01")

            # 2.3 计算 posterior
            posterior = prior * likelihood
            cand["posterior"] = posterior
            total_posterior += posterior

            print(f"[compute] 贝叶斯更新: {fault_id}")
            print(f"[compute]   prior={prior:.6f} × likelihood={likelihood:.4f} = posterior={posterior:.6f}")

        # 2.4 归一化
        print(f"\n[compute] ========== 归一化后验概率 ==========")
        print(f"[compute] 概率总和: {total_posterior:.6f}")
        if total_posterior > 0:
            for cand in self.candidates:
                old_posterior = cand["posterior"]
                cand["posterior"] /= total_posterior
                print(f"[compute] {cand['fault_id']} ({cand['fault']}):")
                print(f"[compute]   {old_posterior:.6f} / {total_posterior:.6f} = {cand['posterior']:.6f} ({cand['posterior']*100:.2f}%)")
        else:
            print("[compute] 后验概率为 0，无法归一化。")
        print(f"[compute] =======================================")

        # ========== 3. 更新 asked ==========
        self.add_asked(qtype, matched_symptom, answer)

        # ========== 4. 选择下一个 symptom ==========
        next_symptom = None
        
        # 从 symptoms_share 删除刚处理过的 matched_symptom， 从剩余的中选择下一个未提问的 symptom
        # self.symptoms_share.__delitem__(self.symptoms_share.index(matched_symptom))
        
        for s in self.symptoms_share:
            if not any(a["quesion"] == s for a in self.asked):
                next_symptom = s
                break

        if next_symptom:
            self.set_next_question("symptoms", next_symptom, "")
            print(f"[compute] 下一问题: {next_symptom}")
        else:
            self.next_question = []
            self.stop = True
            print("[compute] 没有更多症状可提问，结束诊断。")
        return




    def updateToNext():
        return 

    def get_next_question_obj(self) -> Optional[Question]:
        """
        将 next_question 中的第一条记录转换成 Question 对象返回。
        若 next_question 为空，则返回 None。
        """
        if not self.next_question:
            return None
        
        # next_question 是一个 [{"type": "...", "quesion": "...", "answer": "..."}]
        nq_dict = self.next_question[0]

        # Question.from_dict() 是你已有的工具方法
        return Question.from_dict(nq_dict)


'''
    def compute1(self, qtype: str, question: str, answer: str, flist: FaultList):
        """
        根据输入问题和答案计算后验概率，并更新当前 FaultCase 状态。
        qtype: "symptoms" / "test" / "check"
        question: 当前问题（例如症状名）
        answer: 用户回答（yes/no 等）
        flist: 故障列表对象，用于查找 Fault 信息
        """

        ## 只传入“问题答案”，没有问题和类型
        if not qtype and not question:
            for n in self.next_question:
              type = n["type"]
              question = n["question"]
              answer = n["answer"]
              ## 判断传入的答案和标准“答案”是否一致
              if type == "symptom" :
                    result = CommonIntentCheck.evaluate(
                llm, q, user_input, history,constants.Fault_check_desc,
                ismock=False
            )
                   
        
        return
'''

        


