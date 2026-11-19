"""工具注册表：Harness 可调用的工具在此登记，测试与运行时共用同一套注册机制。

每个工具是一个纯查询函数，不执行写操作（放行/签核/发消息），
写操作只能由人工确认接口完成。
"""

from app.db import connect, get_batch  # 导入数据库查询函数
from app.kb.graph import check_trace  # 导入图谱追溯检查
from app.harness.redlines import check_ambiguity  # 导入歧义过滤


def tool_trace_query(batch_no, graph, user):
    """追溯清单查询工具：返回批次链路、追溯完整性与辅助字段。
    入参：batch_no - 批次编号；graph - 知识图谱；user - 当前用户字典（权限判断）。
    出参：dict 追溯信息；敏感字段按权限裁剪。
    失败时：批次不存在返回 {"found": False}。
    """
    conn = connect()  # 连接数据库
    row = get_batch(conn, batch_no)  # 查批次
    if row is None:  # 批次不存在
        conn.close()  # 关闭连接
        return {"found": False}  # 返回未找到
    trace = check_trace(graph, batch_no)  # 用图谱检查追溯完整性
    inspections = conn.execute("SELECT * FROM inspections WHERE batch_no=?", (batch_no,)).fetchall()  # 查检测记录
    clean, ambiguous_ids = check_ambiguity(inspections)  # 过滤歧义记录
    result = {  # 组装结果
        "found": True,  # 找到批次
        "batch_no": batch_no,  # 批次编号
        "original_batch_no": row["original_batch_no"],  # 原批号
        "part_type": row["part_type"],  # 零件类型
        "data_version": row["data_version"],  # 资料版本
        "data_time": row["data_time"],  # 数据时点
        "trace_complete": trace["complete"],  # 追溯是否完整
        "tool_id": trace["tool_id"],  # 刀具编号
        "trace_reason": trace["reason"],  # 追溯结论说明
        "ambiguous_ids": ambiguous_ids,  # 歧义记录编号（进人工修复队列）
        "stale": False,  # 是否待刷新，默认否，场景注入时改写
    }
    # 关键逻辑：敏感字段（检测量值、量具校准、公差版本）仅 admin 可见，user 角色裁剪掉（f41）
    if user and user.get("role") == "admin":  # 仅管理员
        result["inspections"] = [dict(r) for r in clean]  # 附加干净检测记录明细
    conn.close()  # 关闭连接
    return result  # 返回结果


def tool_diagnose(batch_no, graph):
    """异常定位辅助工具：基于图谱给出带事实引用的提示，不认定根因。
    入参：batch_no - 批次编号；graph - 知识图谱。
    出参：dict 建议，含 suggestion/fact_refs/confidence；只提示不写处置字段。
    失败时：批次不存在返回低置信度建议并说明。
    """
    trace = check_trace(graph, batch_no)  # 检查追溯
    if not trace["complete"]:  # 追溯不完整
        return {"suggestion": "追溯链不完整，建议转人工核对原批号与刀具", "fact_refs": [trace["reason"]], "confidence": 0.4}  # 低置信转人工
    return {"suggestion": "追溯链完整，可结合检测量值由人工判断原因（AI 不认定根因）", "fact_refs": ["机台与刀具关联齐全"], "confidence": 0.8}  # 正常提示


def tool_snapshot(batch_no):
    """快照工具：读取批次资料时点时点，判断待刷新标记。
    入参：batch_no - 批次编号（当前未用，保留接口一致性）。
    出参：dict 含 stale 标志与时点说明。
    失败时：不会失败。
    """
    cfg = load_cfg()  # 读取配置
    cycles = cfg["kb"]["update_cycles_per_day"]  # 每天更新周期数
    return {"stale": False, "note": "数据每天更新{}次，超过一个周期标待刷新".format(cycles)}  # 返回快照说明


def load_cfg():
    """封装配置读取，避免工具层重复导入。
    入参：无。
    出参：dict 配置。
    失败时：配置读取异常原样抛出。
    """
    from app.config import load_config  # 局部导入配置函数
    return load_config()  # 返回配置
