"""
故障诊断工具模块

提供从 fault_list 生成 FaultCase 的功能
支持基于AI的语义匹配
"""

import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from src.support.models.FaultCase import FaultCase
from src.support.models.FaultList import FaultList
from src.support.api.config import llm
from src.support.api.tools import ai_matching_input_to_options


# 辅助类：症状匹配结果

class SymptomMatchResult(BaseModel):
    """
    用于结构化输出，承载症状匹配结果
    """
    is_relevant: bool = Field(
        description="输入的症状是否与该故障相关。True表示相关，False表示不相关"
    )
    confidence: float = Field(
        description="匹配置信度，范围0.0到1.0。值越高表示越相关"
    )
    matched_symptoms: List[str] = Field(
        description="故障症状列表中，与输入症状语义匹配的症状名称列表"
    )
    reason: str = Field(
        description="匹配或不匹配的原因说明"
    )


def check_symptom_match_with_llm(
    llm,
    input_symptoms: str,
    fault_id: str,
    fault_name: str,
    fault_symptoms: List[str]
) -> SymptomMatchResult:
    """
    使用 LLM 进行语义匹配，判断输入症状是否与故障相关

    参数:
        llm: LangChain LLM 实例
        input_symptoms: 用户输入的症状描述
        fault_id: 故障ID
        fault_name: 故障名称
        fault_symptoms: 故障的症状列表

    返回:
        SymptomMatchResult 对象
    """
    structured_llm = llm.with_structured_output(SymptomMatchResult)

    fault_symptoms_str = "\n".join([f"- {s}" for s in fault_symptoms])

    prompt = f"""
你是一个故障诊断专家。请分析用户输入的症状是否与某个故障相关。

用户输入的症状：
{input_symptoms}

故障信息：
- 故障ID: {fault_id}
- 故障名称: {fault_name}
- 该故障的典型症状：
{fault_symptoms_str}

请判断：
1. 用户输入的症状是否与该故障相关？（is_relevant）
2. 如果相关，置信度是多少？（confidence: 0.0-1.0）
3. 该故障的症状列表中，哪些症状与用户输入语义匹配？（matched_symptoms）
4. 请说明匹配或不匹配的原因

注意：
- 支持部分匹配，不必完全匹配
- 语义相似即可，不需要完全相同的文字
- 即使只有部分症状匹配，也应该认为是相关的
"""
    print(f"\n[AI匹配] 正在分析故障 {fault_id} ({fault_name})...")
    result = structured_llm.invoke(prompt)

    print(f"[AI匹配] 结果: {'✅ 相关' if result.is_relevant else '❌ 不相关'} "
          f"(置信度: {result.confidence:.2f})")
    if result.matched_symptoms:
        print(f"[AI匹配] 匹配的症状: {', '.join(result.matched_symptoms)}")
    print(f"[AI匹配] 原因: {result.reason}")

    return result

# 主要函数：根据故障列表和症状生成 FaultCase

def generate_fault_case_from_faultlist(
    faultlist_path: str,
    symptom: str
) -> FaultCase:
    """
    根据故障列表文件和症状描述生成 FaultCase 对象

    参数:
        faultlist_path: fault_list JSON 文件路径
        symptom: 用户输入的症状描述字符串（单个症状）

    返回:
        FaultCase 对象

    规则:
        1. 分析 fault_list.json 文件，找出所有的 symptoms 和候选 faults
        2. 根据输入的 symptom 字符串，通过AI找出语意匹配的 faults（只要有一个症状匹配即可）
        3. 生成一个 FaultCase 对象，包含所有匹配的 faults
        4. symptoms_all: 所有匹配故障的所有症状（去重）
        5. symptoms_share: 所有匹配故障的共有症状（交集）
        6. candidates: 匹配的故障列表（按 prior 降序排列）
        7. 格式参考 tests/fault_case0.json 文件
    """
    from datetime import datetime

    # 设置默认设备与环境信息
    device = {"brand": "", "series": "", "fw": ""}
    env = {"voltage": 0, "phase": 0, "ambient_temp": 0}

    print(f"\n{'='*80}")
    print(f"从 fault_list 生成 FaultCase (AI语义匹配版)")
    print(f"{'='*80}")
    print(f"输入症状: {symptom}")
    print(f"Fault List 文件: {faultlist_path}")

    # 1. 加载 fault_list JSON 文件
    with open(faultlist_path, 'r', encoding='utf-8') as f:
        fault_list_data = json.load(f)

    print(f"\n成功加载 {len(fault_list_data)} 个故障定义")

    # 2. 遍历所有故障，使用AI进行症状匹配
    matched_faults = []  # 存储匹配的故障及其匹配症状
    all_symptoms_set = set()  # 所有匹配故障的所有症状

    for fault in fault_list_data:
        fault_id = fault['fault_id']
        fault_name = fault['fault']
        prior = fault.get('prior', 0.0)
        symptoms_list = fault.get('symptoms', [])

        # 提取该故障的所有症状名称
        symptom_names = [s['name'] for s in symptoms_list]

        print(f"\n检查故障 {fault_id} ({fault_name})...")
        print(f"  症状列表: {', '.join(symptom_names)}")

        # 使用AI匹配：检查输入的symptom是否与该故障的任何一个症状匹配
        matched_symptom = ai_matching_input_to_options(
            input_text=symptom,
            options=symptom_names,
            model=1
        )

        if matched_symptom:  # 如果找到了匹配的症状
            print(f"  ✅ 匹配成功: '{symptom}' → '{matched_symptom}'")

            # 记录匹配的故障及其所有症状
            matched_faults.append({
                'fault_id': fault_id,
                'fault': fault_name,
                'prior': prior,
                'all_symptoms': symptom_names,
                'matched_symptom': matched_symptom
            })

            # 收集所有症状到 all_symptoms_set
            all_symptoms_set.update(symptom_names)
        else:
            print(f"  ❌ 未匹配")

    # 3. 按 prior 降序排序
    matched_faults.sort(key=lambda x: x['prior'], reverse=True)

    # 4. 计算共享症状（所有匹配故障的症状交集）
    if matched_faults:
        # 从第一个故障的症状开始
        shared_symptoms = set(matched_faults[0]['all_symptoms'])

        # 与其他故障的症状求交集
        for fault in matched_faults[1:]:
            shared_symptoms.intersection_update(fault['all_symptoms'])

        symptoms_share = list(shared_symptoms)
    else:
        symptoms_share = []

    # 5. 生成 FaultCase 对象
    case_id = datetime.now().strftime("%Y-%m-%d-%H%M%S")

    fault_case = FaultCase(
        case_id=case_id,
        device=device,
        env=env,
        symptom_text=symptom,
        symptoms_all=list(all_symptoms_set),
        symptoms_share=symptoms_share,
        candidates=[],
        asked=[],
        next_question=[],
        stop=False
    )

    # 6. 填充候选项
    for fault in matched_faults:
        fault_case.candidates.append({
            "fault_id": fault['fault_id'],
            "fault": fault['fault'],
            "prior": fault['prior']
        })

    # 7. 输出结果摘要
    print(f"\n{'='*80}")
    print(f"匹配结果:")
    print(f"{'='*80}")
    print(f"匹配的故障数: {len(matched_faults)}")
    print(f"所有症状数: {len(all_symptoms_set)}")
    print(f"共享症状数: {len(symptoms_share)}")
    print(f"共享症状: {symptoms_share}")

    print(f"\n匹配的故障列表（按 prior 降序）:")
    for i, fault in enumerate(matched_faults, 1):
        print(f"  {i}. {fault['fault']} (ID: {fault['fault_id']}, prior={fault['prior']})")
        print(f"     匹配的症状: {fault['matched_symptom']}")

    print(f"\n{'='*80}")
    print(f"生成的 FaultCase:")
    print(f"{'='*80}")

    return fault_case


def generate_fault_case_from_faultlist_obj(
    faultlist: FaultList,
    symptom: str
) -> FaultCase:
    """
    基于 FaultList 对象生成 FaultCase 对象

    参数:
        faultlist: FaultList 对象（已加载的故障列表）
        symptom: 用户输入的症状描述字符串（单个症状）

    返回:
        FaultCase 对象

    规则:
        1. 分析 faultlist 对象中的 faults，每个 fault 下有多个 symptoms
        2. 如果 fault 中有一个 symptom 的 name 字段与输入语义匹配，则认为该 fault 匹配
        3. 匹配的 fault 作为候选包含在 candidates 列表中
        4. 所有匹配 fault 的所有症状包含在 symptoms_all 列表中
        5. 所有匹配 fault 的共有症状（交集）包含在 symptoms_share 列表中
        6. stop 字段默认为 False
    """
    from datetime import datetime

    # 设置默认设备与环境信息
    device = {"brand": "", "series": "", "fw": ""}
    env = {"voltage": 0, "phase": 0, "ambient_temp": 0}

    print(f"\n{'='*80}")
    print(f"从 FaultList 对象生成 FaultCase (AI语义匹配版)")
    print(f"{'='*80}")
    print(f"输入症状: {symptom}")
    print(f"FaultList 对象: {faultlist}")

    # 1. 遍历 FaultList 对象中的所有故障
    matched_faults = []  # 存储匹配的故障及其匹配症状
    all_symptoms_set = set()  # 所有匹配故障的所有症状

    for fault_obj in faultlist.faults:
        fault_id = fault_obj.get_fault_id()
        fault_name = fault_obj.get_fault()
        prior = fault_obj.get_prior()
        symptoms_list = fault_obj.get_symptoms()

        # 提取该故障的所有症状名称
        symptom_names = [s['name'] for s in symptoms_list]

        print(f"\n检查故障 {fault_id} ({fault_name})...")
        print(f"  症状列表: {', '.join(symptom_names)}")

        # 使用AI匹配：检查输入的symptom是否与该故障的任何一个症状匹配
        matched_symptom = ai_matching_input_to_options(
            input_text=symptom,
            options=symptom_names,
            model=1
        )

        if matched_symptom:  # 如果找到了匹配的症状
            print(f"  ✅ 匹配成功: '{symptom}' → '{matched_symptom}'")

            # 记录匹配的故障及其所有症状
            matched_faults.append({
                'fault_id': fault_id,
                'fault': fault_name,
                'prior': prior,
                'all_symptoms': symptom_names,
                'matched_symptom': matched_symptom
            })

            # 收集所有症状到 all_symptoms_set
            all_symptoms_set.update(symptom_names)
        else:
            print(f"  ❌ 未匹配")

    # 2. 按 prior 降序排序
    matched_faults.sort(key=lambda x: x['prior'], reverse=True)

    # 3. 计算共享症状（所有匹配故障的症状交集）
    if matched_faults:
        # 从第一个故障的症状开始
        shared_symptoms = set(matched_faults[0]['all_symptoms'])

        # 与其他故障的症状求交集
        for fault in matched_faults[1:]:
            shared_symptoms.intersection_update(fault['all_symptoms'])

        symptoms_share = list(shared_symptoms)
    else:
        symptoms_share = []

    # 4. 生成 FaultCase 对象
    case_id = datetime.now().strftime("%Y-%m-%d-%H%M%S")

    fault_case = FaultCase(
        case_id=case_id,
        device=device,
        env=env,
        symptom_text=symptom,
        symptoms_all=list(all_symptoms_set),
        symptoms_share=symptoms_share,
        candidates=[],
        asked=[],
        next_question=[],
        stop=False
    )

    # 5. 填充候选项
    for fault in matched_faults:
        fault_case.candidates.append({
            "fault_id": fault['fault_id'],
            "fault": fault['fault'],
            "prior": fault['prior']
        })

    # 6. 输出结果摘要
    print(f"\n{'='*80}")
    print(f"匹配结果:")
    print(f"{'='*80}")
    print(f"匹配的故障数: {len(matched_faults)}")
    print(f"所有症状数: {len(all_symptoms_set)}")
    print(f"共享症状数: {len(symptoms_share)}")
    print(f"共享症状: {symptoms_share}")

    print(f"\n匹配的故障列表（按 prior 降序）:")
    for i, fault in enumerate(matched_faults, 1):
        print(f"  {i}. {fault['fault']} (ID: {fault['fault_id']}, prior={fault['prior']})")
        print(f"     匹配的症状: {fault['matched_symptom']}")

    print(f"\n{'='*80}")
    print(f"生成的 FaultCase:")
    print(f"{'='*80}")

    return fault_case


def save_fault_case_to_file(fault_case: FaultCase, output_path: str):
    """
    将 FaultCase 对象保存到 JSON 文件

    参数:
        fault_case: FaultCase 对象
        output_path: 输出文件路径
    """
    fault_case.save_to_file(output_path)
    print(f"✅ FaultCase 已保存到: {output_path}")


def display_fault_case_json(fault_case: FaultCase):
    """
    以 JSON 格式显示 FaultCase 对象

    参数:
        fault_case: FaultCase 对象
    """
    print(f"\n{'='*80}")
    print(f"FaultCase JSON 输出:")
    print(f"{'='*80}")
    json_str = fault_case.to_json(indent=2, ensure_ascii=False)
    print(json_str)
    print(f"{'='*80}\n")

