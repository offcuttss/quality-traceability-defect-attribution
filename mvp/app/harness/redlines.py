"""数据红线模块：把硬约束写成代码级拦截，不靠文档承诺。

红线清单：
- f40 未复检+签核不得放行。
- f11/f44 换批号断链、资料缺依据、版本冲突、系统不可用 -> 转人工三要素。
- f33 歧义记录进人工修复队列，不进推荐样本。
- f15 建议不覆盖原记录，只追加。
"""

from app.config import load_config  # 导入配置读取函数


class RedlineHit(Exception):  # 红线命中异常
    """红线被触发时抛出，由 Harness 捕获转为降级/拒绝结果。
    入参：code - 红线码；reason - 中文原因。
    出参：异常实例，含 code 与 reason 属性。
    失败时：无（异常本身就是失败信号）。
    """
    def __init__(self, code, reason):  # 构造函数
        self.code = code  # 红线码
        self.reason = reason  # 中文原因
        super().__init__(reason)  # 调用父类构造，设置异常消息


def check_action_boundary(request_text):
    """检查业务请求是否越界（自动放行/自动认定根因/对外承诺）。
    入参：request_text - 用户请求文本。
    出参：None（未越界）；越界则抛出 RedlineHit。
    失败时：命中越界关键词抛 RedlineHit，由调用方拦截。
    """
    blocking = ["自动放行", "直接放行", "自动认定根因", "自动签核", "自动批准", "对外承诺", "替代签核"]  # 越界动作关键词
    for word in blocking:  # 遍历关键词
        if word in (request_text or ""):  # 命中任一越界词
            # 关键逻辑：这些动作不可逆且责任重大，必须当回复硬拒绝，不进入任何项目（f05/f40/f41）
            raise RedlineHit("ACTION_OUT_OF_BOUNDARY", "检测到越界动作：" + word + "；AI 只做提示，不放行/不认定根因/不签核")  # 抛红线异常


def check_ambiguity(inspections):
    """过滤歧义检测记录，歧义的不进入推荐样本。
    入参：inspections - 检测记录行列表（sqlite3.Row 或 dict）。
    出参：tuple (clean_list, ambiguous_ids)，干净记录与歧义记录编号列表。
    失败时：不会失败，空列表返回空结果。
    """
    clean, ambiguous = [], []  # 初始化两个结果列表
    for row in inspections:  # 遍历记录
        if row["ambiguous"] == 1 or row["gauge_calibrated"] == 0:  # 有歧义或量具过期
            ambiguous.append(row["id"])  # 记入歧义队列
        else:  # 干净记录
            clean.append(row)  # 进入推荐样本
    return clean, ambiguous  # 返回结果


def check_release(reinspection_done, signoff_done):
    """放行前置校验：未复检或未签核一律不得放行。
    入参：reinspection_done - bool 是否已完成复检；signoff_done - bool 是否已签核。
    出参：None（允许）；否则抛出 RedlineHit。
    失败时：任一条件不满足抛 RedlineHit。
    """
    cfg = load_config()["redlines"]  # 读取红线配置
    if cfg["blocked_release_without_signoff"] and not (reinspection_done and signoff_done):  # 硬约束开启且条件不全
        # 关键逻辑：客户图纸受限，未复检+签核不得放行，这是最高红线（f40），任何请求都不能绕过
        raise RedlineHit("RELEASE_BLOCKED", "未复检或未签核，不得放行；须由产品安全负责人签核（f40）")  # 抛红线异常


def manual_triggers(scenario, trace_result):
    """根据场景与追溯检查结果判断是否需要转人工，并返回触发原因。
    入参：scenario - 场景字符串；trace_result - check_trace 返回的 dict。
    出参：str 触发原因；无需转人工返回 None。
    失败时：不会失败。
    """
    if scenario == "missing":  # 材料缺漏
        return "资料缺少依据（批次/机台信息不完整）"  # 返回触发原因
    if scenario == "conflict":  # 版本冲突
        return "检测到两个版本冲突，不自行合并或选用宽松条款"  # 返回触发原因
    if scenario == "outage":  # 系统不可用
        return "关键系统不可用，使用带时间戳快照标待刷新并转人工"  # 返回触发原因
    if scenario == "broken_chain" or (not trace_result.get("complete") and trace_result.get("reason", "").find("断裂") >= 0):  # 换批号断链
        return "返工换批号追溯断链，追溯不到原刀具"  # 返回触发原因
    return None  # 无需转人工
