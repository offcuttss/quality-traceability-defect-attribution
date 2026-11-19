"""Harness 编排引擎：请求 -> 权限校验 -> 红线前置 -> 工具调用 -> 置信度门限 -> 人工确认拦截 -> 审计落库。

沿用原 demo 的六场景语义（normal/missing/conflict/unauthorized/outage/injection）
并新增 broken_chain（换批号断链，f11 核心场景）。
所有动作只读，写操作（签核/确认）必须走 confirm 接口由 admin 完成。
"""

from app.config import load_config  # 导入配置
from app.db import connect, append_audit, append_manual  # 导入数据库与留痕函数
from app.kb.graph import build_graph  # 导入图谱构建
from app.harness import redlines  # 导入红线模块
from app.harness import registry  # 导入工具注册
from app.auth import can_view_sensitive  # 导入权限判断

# 模块级图谱缓存：启动时构建一次，避免每请求重建
_GRAPH = None  # 缓存的图谱


def get_graph():
    """获取（或首次构建）知识图谱。
    入参：无。
    出参：networkx.DiGraph。
    失败时：构建异常原样抛出，由接口层转为失败响应。
    """
    global _GRAPH  # 使用模块级缓存
    if _GRAPH is None:  # 尚未构建
        _GRAPH = build_graph()  # 构建并缓存
    return _GRAPH  # 返回图谱


def reset_graph():
    """清空图谱缓存，用于测试数据变更后重建。
    入参：无。
    出参：None。
    失败时：不会失败。
    """
    global _GRAPH  # 使用模块级缓存
    _GRAPH = None  # 置空触发下次重建


def _audit(biz_no, data_version, fact_refs, suggestion, human_changes="", signer=""):
    """内部函数：写审计六字段留痕。
    入参：六个参数对应审计字段。
    出参：None。
    失败时：写库异常原样抛出。
    """
    append_audit(connect(), biz_no, data_version, str(fact_refs), suggestion, human_changes, signer)  # 追加审计


def run_trace(user, batch_no, scenario="normal", request_text=""):
    """执行追溯与异常定位辅助的完整编排流程。
    入参：user - 当前用户字典；batch_no - 批次编号；scenario - 场景；request_text - 业务请求文本。
    出参：dict 含 status/summary/data/trace/steps；status ∈ blocked/manual/review/degraded。
    失败时：红线命中会被捕获转为 blocked/manual 状态，不向外抛异常。
    """
    cfg = load_config()  # 读取配置
    steps = []  # 执行轨迹列表
    graph = get_graph()  # 获取知识图谱

    def step(agent, action, detail):  # 内部函数：记录一步轨迹
        steps.append({"step": len(steps) + 1, "agent": agent, "action": action, "detail": detail})  # 追加轨迹

    step("入口与权限控制", "校验输入", "只处理本场景批次，所有输出保留来源")  # 记录入口步骤
    if scenario not in cfg["scenarios"]:  # 场景未在配置中定义
        return {"status": "blocked", "summary": "场景无效", "data": {}, "steps": steps, "code": "INVALID_SCENARIO"}  # 拒绝

    # 关键逻辑：先做越界动作审查，命中即硬拒绝，AI 不放行/不认定根因（f05/f40/f41）
    try:  # 捕获红线异常
        redlines.check_action_boundary(request_text)  # 审查请求动作边界
    except redlines.RedlineHit as hit:  # 命中越界红线
        step("动作控制", "拦截越界动作", hit.reason)  # 记录拦截
        return {"status": "blocked", "summary": hit.reason, "data": {}, "steps": steps, "code": hit.code}  # 硬拒绝

    # 关键逻辑：user 角色不得查看敏感字段，越权场景直接拒绝，禁止借用账号（f41）
    if scenario == "unauthorized" and not can_view_sensitive(user):  # 越权场景且非管理员
        step("权限控制", "拒绝读取", "当前身份不具备敏感数据访问范围")  # 记录拒绝
        return {"status": "blocked", "summary": "访问被拒绝：请使用有权限的账号", "data": {}, "steps": steps, "code": "UNAUTHORIZED"}  # 拒绝

    data = registry.tool_trace_query(batch_no, graph, user)  # 调用追溯工具
    if not data["found"]:  # 批次不存在
        step("资料核对", "样本不存在", "未读取其他记录")  # 记录
        return {"status": "blocked", "summary": "批次不存在", "data": {}, "steps": steps, "code": "BATCH_NOT_FOUND"}  # 拒绝

    step("知识库检索", "读取授权快照", "批次版本 " + data["data_version"])  # 记录读库

    # 关键逻辑：歧义记录进人工修复队列，不进自动推荐样本（f33）
    if data["ambiguous_ids"]:  # 存在歧义记录
        step("数据口径校验", "歧义记录隔离", "歧义记录进人工修复队列")  # 记录隔离

    # 场景故障注入：系统不可用时用带时间戳快照标待刷新（f34/f35）
    if scenario == "outage":  # 来源不可用
        data["stale"] = True  # 标记待刷新
        step("来源读取", "接口中断", "使用带时间戳的上一份只读快照，标待刷新")  # 记录降级

    # 转人工触发：断链/缺依据/版本冲突/系统不可用 -> 三要素落库（f44）
    trigger = redlines.manual_triggers(scenario, {"complete": data["trace_complete"], "reason": data["trace_reason"]})  # 判断触发
    if trigger:  # 需要转人工
        step("人工兜底", "转人工", trigger)  # 记录
        append_manual(connect(), batch_no, trigger, "唐映秋", "2026-11-19T12:00:00")  # 三要素落库（demo 用固定接手人与确认时间）
        _audit(batch_no, data["data_version"], [data["trace_reason"]], "转人工核对：" + trigger)  # 审计留痕
        return {"status": "manual", "summary": trigger, "data": data, "steps": steps, "code": "MANUAL_REQUIRED"}  # 返回转人工

    suggestion = registry.tool_diagnose(batch_no, graph)  # 调用归因辅助工具
    step("归因辅助", "生成带引用提示", suggestion["suggestion"])  # 记录建议
    # 关键逻辑：AI 建议不覆盖原记录，只追加审计（f15），且低于门限转人工
    if suggestion["confidence"] < cfg["redlines"]["low_confidence_to_manual"]:  # 置信度不足
        append_manual(connect(), batch_no, "归因置信度低于门限", "唐映秋", "2026-11-19T12:00:00")  # 转人工
        return {"status": "manual", "summary": "置信度不足，转人工核对", "data": data, "steps": steps, "code": "LOW_CONFIDENCE"}  # 返回转人工
    _audit(batch_no, data["data_version"], suggestion["fact_refs"], suggestion["suggestion"])  # 追加审计六字段
    step("人工复核关卡", "等待责任人确认", "AI 只做提示，不认定根因/不放行")  # 记录人工关卡
    return {"status": "review", "summary": "已生成带来源的辅助建议，等待人工复核", "data": {**data, "suggestion": suggestion}, "steps": steps, "code": None}  # 返回结果


def confirm_release(user, batch_no, reinspection_done, signoff_done):
    """人工确认放行接口：只有 admin 且复检+签核齐全才允许。
    入参：user - 用户；batch_no - 批次；reinspection_done - 复检完成；signoff_done - 已签核。
    出参：dict 含 status/summary。
    失败时：红线命中返回 blocked，不抛异常。
    """
    steps = []  # 轨迹
    # 关键逻辑：签核权硬编码仅 admin，user 角色调用直接拒绝（f40/f41）
    if not user or user.get("role") != "admin":  # 非管理员
        return {"status": "blocked", "summary": "只有产品安全负责人（admin）可执行签核放行", "steps": steps, "code": "FORBIDDEN"}  # 拒绝
    try:  # 捕获放行红线
        redlines.check_release(reinspection_done, signoff_done)  # 校验复检+签核
    except redlines.RedlineHit as hit:  # 未满足
        return {"status": "blocked", "summary": hit.reason, "steps": steps, "code": hit.code}  # 拒绝放行
    _audit(batch_no, "signed", ["复检通过", "签核完成"], "人工确认放行", signer=user.get("display_name", "admin"))  # 审计留痕
    return {"status": "released", "summary": "复检与签核齐全，已由人工确认放行", "steps": steps, "code": None}  # 返回放行成功
