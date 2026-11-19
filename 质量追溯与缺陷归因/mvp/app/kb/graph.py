"""知识库模块：本地知识图谱（networkx 内存图 + GraphML 持久化）。

图谱节点：批次、零件、机台、刀具、量具。
图谱边：produced_on(批次->机台)、used_tool(批次->刀具)、part_of(批次->零件)、
        measured_by(批次->量具)、reworked_from(新批号->原批号)。
核心推断：换批号后若机台/刀具缺失，或 reworked_from 边断裂，则判定追溯断链（f11）。
"""

import os  # 导入系统模块，用于判断文件存在
import networkx as nx  # 导入 networkx 构建知识图谱
from app.config import load_config, data_path  # 导入配置与路径解析
from app.db import connect  # 导入数据库连接函数


def build_graph():
    """从 SQLite 业务数据构建知识图谱并持久化。
    入参：无，数据来自数据库与 config.yaml。
    出参：networkx.DiGraph 有向图。
    失败时：数据库读取或写文件失败会抛出异常。
    """
    graph = nx.DiGraph()  # 创建有向图
    conn = connect()  # 连接数据库
    rows = conn.execute("SELECT * FROM batches").fetchall()  # 读取全部批次
    for row in rows:  # 遍历批次
        graph.add_node("batch:" + row["batch_no"], type="批次", version=row["data_version"], time=row["data_time"])  # 加批次节点
        graph.add_node("part:" + row["part_type"], type="零件")  # 加零件节点
        graph.add_edge("batch:" + row["batch_no"], "part:" + row["part_type"], rel="part_of")  # 批次属于零件
        if row["machine_id"]:  # 机台非空才建边，缺失即断链的信号
            graph.add_node("machine:" + row["machine_id"], type="机台")  # 加机台节点
            graph.add_edge("batch:" + row["batch_no"], "machine:" + row["machine_id"], rel="produced_on")  # 批次生产于机台
        if row["tool_id"]:  # 刀具非空才建边
            graph.add_node("tool:" + row["tool_id"], type="刀具")  # 加刀具节点
            graph.add_edge("batch:" + row["batch_no"], "tool:" + row["tool_id"], rel="used_tool")  # 批次 used_tool
        if row["original_batch_no"]:  # 有原批号说明是返工换号批次
            graph.add_node("batch:" + row["original_batch_no"], type="批次")  # 确保原批次节点存在
            graph.add_edge("batch:" + row["batch_no"], "batch:" + row["original_batch_no"], rel="reworked_from")  # 换号指向原批
    inspection_rows = conn.execute("SELECT * FROM inspections").fetchall()  # 读取检测记录
    for row in inspection_rows:  # 遍历检测记录
        graph.add_node("gauge:" + row["gauge_id"], type="量具", calibrated=row["gauge_calibrated"])  # 加量具节点
        graph.add_edge("batch:" + row["batch_no"], "gauge:" + row["gauge_id"], rel="measured_by")  # 批次被量具测量
    conn.close()  # 关闭连接
    save_graph(graph)  # 持久化图谱
    return graph  # 返回图谱


def save_graph(graph):
    """把知识图谱写入 GraphML 文件。
    入参：graph - networkx 图。
    出参：None。
    失败时：写文件失败抛出异常。
    """
    path = data_path(load_config()["kb"]["graph_path"])  # 解析图谱文件绝对路径
    os.makedirs(os.path.dirname(path), exist_ok=True)  # 确保目录存在
    nx.write_graphml(graph, path, encoding="utf-8")  # 写 GraphML


def check_trace(graph, batch_no):
    """检查某批次的追溯完整性，返回是否断链及可追溯到的刀具。
    入参：graph - 知识图谱；batch_no - 批次编号。
    出参：dict {complete: bool, tool_id: str|None, reason: str, neighbors: list}。
    失败时：批次不存在返回 complete=False 并说明原因，不抛异常。
    """
    node = "batch:" + batch_no  # 拼节点 ID
    if not graph.has_node(node):  # 批次不在图谱中
        return {"complete": False, "tool_id": None, "reason": "批次不在知识库中", "neighbors": []}  # 返回断链
    machine_edges = [e for e in graph.out_edges(node, data=True) if e[2].get("rel") == "produced_on"]  # 找机台边
    tool_nodes = [v for u, v, d in graph.out_edges(node, data=True) if d.get("rel") == "used_tool"]  # 找刀具节点
    rework_edges = [v for u, v, d in graph.out_edges(node, data=True) if d.get("rel") == "reworked_from"]  # 找换号关联边
    neighbors = [v for u, v in graph.out_edges(node)]  # 全部出边邻居
    # 关键逻辑：换批号批次若没有机台边或没有刀具节点，视为追溯断链，必须转人工（f11/f44）
    if rework_edges and (not machine_edges or not tool_nodes):  # 换号且机台/刀具缺失
        return {"complete": False, "tool_id": None, "reason": "返工换批号后机台或刀具信息缺失，追溯链断裂", "neighbors": neighbors}  # 返回断链
    tool_id = tool_nodes[0].split(":", 1)[1] if tool_nodes else None  # 取刀具编号
    return {"complete": bool(machine_edges and tool_nodes), "tool_id": tool_id, "reason": "追溯链完整" if tool_nodes else "未找到刀具关联", "neighbors": neighbors}  # 返回追溯结果
