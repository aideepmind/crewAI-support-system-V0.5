from src.support.models.LLMConfig import LLMConfig
from src.support.models.SessionManager import SessionManager
from src.support.api.CommonIntent import CommonIntentCheck
from src.support.models import constants
from src.support.models.DataSessionManager import DataSessionManager
from src.support.models.Question import Question
from src.support.api.config import llm
from typing import List, Dict, Any
from difflib import SequenceMatcher
from src.support.models.FaultList import FaultList


def ai_matching_input_to_options(input_text: str, options: List[str], model: int = 1) -> str:
    """
    将用户输入匹配到给定的选项列表中

    Args:
        input_text: 用户输入的字符串
        options: 多个字符串组成的数组，表示备选项
        model: 匹配模式，可选值：
               - 1: 使用大模型进行语义匹配（默认）
               - 0: 不使用大模型，使用字符串相似度算法

    Returns:
        返回和 input_text 语义最接近的那个字符串
        如果没有找到匹配的选项，返回空字符串 ""

    Example:
        >>> options = ["内存溢出", "CPU过高", "网络延迟"]

        # 使用大模型（推荐）
        >>> result = ai_matching_input_to_options("系统显示内存不足", options, 1)
        >>> print(result)  # "内存溢出"

        # 不使用大模型
        >>> result = ai_matching_input_to_options("系统显示内存不足", options, 0)
        >>> print(result)  # "内存溢出" 或 ""

        >>> result = ai_matching_input_to_options("硬盘坏了", options)
        >>> print(result)  # "" (空字符串)
    """
    if model == 1:
        return _match_with_llm(input_text, options)
    elif model == 0:
        return _match_without_llm(input_text, options)
    else:
        raise ValueError(f"不支持的 model 参数: {model}，请使用 1 (使用LLM) 或 0 (不使用LLM)")


def _match_with_llm(input_text: str, options: List[str]) -> str:
    """使用大模型进行语义匹配"""
    # 构建提示词
    options_str = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])

    prompt = f"""请分析用户输入的语义，并将其匹配到以下选项中语义最接近的一个：

可选选项：
{options_str}

用户输入：{input_text}

要求：
1. 只返回最匹配的选项原文，不要添加任何解释、编号或额外内容
2. 基于语义相似性进行匹配，而不仅仅是字面匹配
3. 如果没有找到语义匹配的选项，返回空字符串（什么都不输出）
4. 直接输出匹配到的选项字符串或空字符串

最匹配的选项："""

    # 调用大模型并获取结果
    response = llm.invoke(prompt)
    result = response.content.strip()

    # 验证返回的结果是否在选项中
    if result in options:
        return result
    else:
        # 没有匹配到任何选项，返回空字符串
        return ""


def _match_without_llm(input_text: str, options: List[str]) -> str:
    """不使用大模型，使用字符串相似度算法进行匹配"""
    if not options:
        return ""

    best_match = ""
    best_score = 0.0
    threshold = 0.35  # 相似度阈值

    for option in options:
        # 策略 1: 完全包含（最高优先级）
        if input_text in option or option in input_text:
            return option

        # 策略 2: 字符串相似度
        similarity = SequenceMatcher(None, input_text, option).ratio()

        # 策略 3: 关键词重叠
        input_words = set(input_text)
        option_words = set(option)
        overlap = len(input_words & option_words)
        union_len = len(input_words | option_words)
        keyword_score = overlap / union_len if union_len > 0 else 0

        # 策略 4: 关键词包含分数
        contain_score = overlap / len(input_words) if input_words else 0

        # 综合评分（取最高分）
        total_score = max(similarity, keyword_score, contain_score)

        if total_score > best_score:
            best_score = total_score
            best_match = option

    # 判断是否达到阈值
    if best_score >= threshold:
        return best_match
    else:
        return ""



if __name__ == "__main__":
    # 测试 AI 匹配函数
    print("=" * 60)
    print("测试 AI 语义匹配函数 (v3.0 - model: 1/0)")
    print("=" * 60)

    options = ["程序运行崩溃", "提示内存溢出", "程序运行失败"]

    # 测试用例 1: 使用 LLM 模式 (model=1)
    print("\n【测试用例 1】使用 LLM 模式 (model=1)")
    input1 = "提示内存溢出"
    result1 = ai_matching_input_to_options(input1, options, 1)
    print(f"输入: {input1}")
    print(f"模式: model=1 (使用 LLM)")
    print(f"匹配结果: '{result1}'")
    print("-" * 60)

    # 测试用例 2: 不使用 LLM 模式 (model=0)
    print("\n【测试用例 2】不使用 LLM 模式 (model=0)")
    input2 = "系统显示内存不足"
    result2 = ai_matching_input_to_options(input2, options, 0)
    print(f"输入: {input2}")
    print(f"模式: model=0 (不使用 LLM)")
    print(f"匹配结果: '{result2}'")
    print("-" * 60)

    # 测试用例 3: 默认模式 (model=1)
    print("\n【测试用例 3】默认模式（不指定 model 参数）")
    input3 = "应用闪退了"
    result3 = ai_matching_input_to_options(input3, options)
    print(f"输入: {input3}")
    print(f"模式: 默认 (model=1)")
    print(f"匹配结果: '{result3}'")
    print("-" * 60)

    # 测试用例 4: 无匹配情况对比
    print("\n【测试用例 4】无匹配情况对比")
    input4 = "硬盘坏了"
    result4_llm = ai_matching_input_to_options(input4, options, 1)
    result4_no_llm = ai_matching_input_to_options(input4, options, 0)
    print(f"输入: {input4}")
    print(f"model=1 结果: '{result4_llm}'")
    print(f"model=0 结果: '{result4_no_llm}'")
    print("-" * 60)

    # 测试用例 5: 无效 model 参数
    print("\n【测试用例 5】无效 model 参数")
    try:
        result5 = ai_matching_input_to_options("测试", options, 2)
        print(f"结果: '{result5}'")
    except ValueError as e:
        print(f"✅ 正确抛出异常: {e}")

    # 测试用例 6: 便捷使用示例
    print("\n【测试用例 6】便捷使用示例")
    print("result = ai_matching_input_to_options('系统内存不足', options, 1)")
    print("result = ai_matching_input_to_options('系统内存不足', options, 0)")
    print("result = ai_matching_input_to_options('系统内存不足', options)  # 默认 model=1")

    print("\n测试完成!")


# ===============================================================================
# 故障聚合函数
# ===============================================================================

def _summarize_causes_with_llm(causes: List[str], llm) -> str:
    """
    使用 LLM 总结多个故障原因，提取共同点和关键信息

    参数:
        causes: 多个故障原因描述列表
        llm: 大语言模型实例

    返回:
        总结后的故障原因描述
    """
    if not causes:
        return "未知原因"

    if len(causes) == 1:
        return causes[0]

    # 构建提示词
    causes_text = "\n".join([f"{i+1}. {cause}" for i, cause in enumerate(causes)])

    prompt = f"""请分析以下多个故障原因描述，提取它们的共同点和关键信息，生成一个简洁准确的总结性故障原因：

可能的故障原因：
{causes_text}

要求：
1. 如果这些原因描述的是同一类问题的不同方面，请提炼共同本质
2. 如果这些原因是不同的根本原因，请用分号分隔，逐一列出
3. 保持简洁专业，每个原因不超过30字
4. 只返回总结后的原因描述，不要添加任何解释或额外内容

总结性故障原因："""

    try:
        response = llm.invoke(prompt)
        result = response.content.strip()

        if result:
            return result
        else:
            # LLM 返回空，使用分号连接所有原因
            return "; ".join(causes)
    except Exception as e:
        print(f"  ⚠️  LLM 总结 cause 失败: {e}，使用原始原因")
        return "; ".join(causes)


def generate_fault_list(
    fault_records: List[Dict[str, Any]],
    llm,
    test: bool = False,
    use_llm: bool = False
) -> str:
    """
    根据故障记录列表，基于 AI 语义匹配聚合生成 fault_list JSON

    参数:
        fault_records: 故障记录列表，格式参考 tests/testdata-1.json
        llm: 大语言模型实例
        test: 是否输出到临时文件
        use_llm: 是否使用 LLM 进行语义匹配和 cause 总结（默认 False，使用字符串匹配）

    返回:
        JSON 字符串，格式参考 tests/fault_list1.json

    处理规则:
        1. 根据 "fault" 字段进行语义聚合
        2. cause 字段处理：
           - 如果只有一个 cause，直接使用
           - 如果有多个不同的 cause：
             * use_llm=True: 使用 LLM 智能总结
             * use_llm=False: 用分号连接所有 cause
        3. 如果没有 prior，生成随机值 (0.1-0.9) 并添加注释
        4. 聚合 symptom、test、check，添加随机 likelihoods (0.1-0.9) 并注释
        5. 如果 test=True，输出到文件 generate_fault_list_file_<时间戳>.json
    """
    import random
    import json
    from datetime import datetime

    print(f"\n{'='*80}")
    print(f"故障聚合程序 - 生成 fault_list")
    print(f"{'='*80}")
    print(f"输入记录数: {len(fault_records)}")
    print(f"语义匹配模式: {'LLM (model=1)' if use_llm else '字符串匹配 (model=0)'}")

    # 1. 语义聚合：根据 fault 字段进行分组
    print(f"\n【步骤1】语义聚合 - 根据 fault 字段分组...")

    # 提取所有唯一的 fault 描述
    unique_faults = {}
    fault_to_group = {}  # 原始记录 -> 聚合组映射

    for idx, record in enumerate(fault_records):
        fault_desc = record.get('fault', '')
        if not fault_desc:
            print(f"  警告: 记录 {idx} 没有 fault 字段，跳过")
            continue

        # 检查是否已有语义相似的 fault 组
        matched_group = None
        for group_key, group_info in unique_faults.items():
            # 使用 AI 或字符串匹配判断是否相似
            similarity = ai_matching_input_to_options(
                fault_desc,
                [group_key],
                model=1 if use_llm else 0
            )
            if similarity:  # 匹配成功
                matched_group = group_key
                break

        if matched_group:
            # 添加到现有组
            unique_faults[matched_group]['records'].append(record)
            fault_to_group[idx] = matched_group
            print(f"  记录 {idx}: '{fault_desc}' -> 聚合到组 '{matched_group}'")
        else:
            # 创建新组
            unique_faults[fault_desc] = {
                'records': [record],
                'aggregated_name': fault_desc
            }
            fault_to_group[idx] = fault_desc
            print(f"  记录 {idx}: '{fault_desc}' -> 创建新组")

    print(f"\n聚合结果: {len(unique_faults)} 个故障组")

    # 2. 生成 fault_list JSON
    print(f"\n【步骤2】生成 fault_list JSON...")

    fault_list_output = []

    for group_idx, (group_key, group_info) in enumerate(unique_faults.items(), 1):
        print(f"\n--- 处理故障组 {group_idx}/{len(unique_faults)}: {group_key} ---")

        # 生成 fault_id
        fault_id = f"f{group_idx:03d}"

        # 聚合所有记录的数据
        all_records = group_info['records']

        # 提取并聚合症状
        all_symptoms = set()
        for record in all_records:
            symptom = record.get('symptom', '')
            if symptom:
                all_symptoms.add(symptom)

        # 提取并聚合测试方法
        all_tests = []
        for record in all_records:
            tests = record.get('test', [])
            if tests:
                all_tests.extend(tests)

        # 提取并聚合检查项
        all_checks = []
        for record in all_records:
            checks = record.get('check', [])
            if checks:
                all_checks.extend(checks)

        # 获取原因（支持多个原因的 LLM 总结）
        all_causes = list({record.get('cause', '') for record in all_records if record.get('cause')})

        if len(all_causes) > 1:
            # 有多个不同的原因
            if use_llm:
                # 使用 LLM 总结
                print(f"  📝 发现 {len(all_causes)} 个不同原因，使用 LLM 总结...")
                cause = _summarize_causes_with_llm(all_causes, llm)
                print(f"  ✅ LLM 总结: {cause}")
            else:
                # 不使用 LLM，用分号连接
                cause = "; ".join(all_causes)
                print(f"  ⚠️  发现 {len(all_causes)} 个不同原因: {cause}")
        elif len(all_causes) == 1:
            # 只有一个原因
            cause = all_causes[0]
        else:
            # 没有原因
            cause = '未知原因'

        # 获取修复方案
        all_remedies = []
        for record in all_records:
            remedies = record.get('remedy', [])
            if remedies:
                all_remedies.extend(remedies)

        # 获取安全注意事项
        all_safety = []
        for record in all_records:
            safety = record.get('safety', [])
            if safety:
                all_safety.extend(safety)

        # 获取 RequestNo（使用第一个记录）
        request_no = all_records[0].get('RequestNo', f'SR-202500{group_idx:03d}')

        # 生成先验概率（如果没有）
        prior = all_records[0].get('prior')
        if prior is None:
            prior = round(random.uniform(0.1, 0.9), 2)
            prior_comment = f"// TODO: 自动生成值 {prior}，需要专家确认"
            print(f"  ⚠️  prior: {prior} {prior_comment}")
        else:
            prior_comment = ""

        # 生成症状列表（带随机 likelihoods）
        symptoms_with_likelihoods = []
        for symptom in all_symptoms:
            likelihood = round(random.uniform(0.1, 0.9), 2)
            symptoms_with_likelihoods.append({
                "name": symptom,
                "likelihoods": likelihood
            })
            print(f"  ⚠️  symptom '{symptom}': likelihoods={likelihood} // TODO: 自动生成")

        # 生成测试方法列表（带随机 likelihoods）
        tests_with_likelihoods = []
        for test_item in all_tests:
            likelihood = round(random.uniform(0.1, 0.9), 2)
            tests_with_likelihoods.append({
                **test_item,
                "likelihoods": likelihood
            })
            print(f"  ⚠️  test: {test_item.get('method', '')}: likelihoods={likelihood} // TODO: 自动生成")

        # 生成检查项列表（带随机 likelihoods）
        checks_with_likelihoods = []
        for check_item in all_checks:
            likelihood = round(random.uniform(0.1, 0.9), 2)
            checks_with_likelihoods.append({
                **check_item,
                "likelihoods": likelihood
            })
            print(f"  ⚠️  check: {check_item.get('question', '')}: likelihoods={likelihood} // TODO: 自动生成")

        # 构建 fault 记录
        fault_record = {
            "fault_id": fault_id,
            "prior": prior,
            "fault": group_key,
            "symptoms": symptoms_with_likelihoods,
            "test": tests_with_likelihoods,
            "check": checks_with_likelihoods,
            "cause": cause,
            "remedy": all_remedies if all_remedies else [{"step": "待补充"}],
            "safety": all_safety if all_safety else ["注意安全操作"],
            "posterior": 0.0,  # 初始后验概率为 0
            "RequestNo": request_no
        }

        fault_list_output.append(fault_record)
        print(f"  ✅ 生成故障记录: {fault_id} - {group_key}")

    # 3. 转换为 JSON 字符串
    json_str = json.dumps(fault_list_output, ensure_ascii=False, indent=2)

    # 4. 如果 test=1，输出到文件
    if test:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"generate_fault_list_file_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_str)
        print(f"\n{'='*80}")
        print(f"✅ 结果已输出到文件: {output_file}")

    print(f"{'='*80}")
    print(f"聚合完成！生成了 {len(fault_list_output)} 个故障记录")

    return json_str



def createFaultListFromFile(filename: str) -> "FaultList":
    # 1️⃣ 从文件加载
    fault_list = FaultList.load_from_file(filename)
    print("✅ 成功加载 FaultList 对象：")
    return fault_list