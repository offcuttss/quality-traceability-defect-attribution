"""pytest 单元测试：覆盖红线模块与编排引擎的关键约束。

运行命令：pytest -q tests/
"""

import os  # 导入系统模块
import sys  # 导入系统模块

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录
if ROOT not in sys.path:  # 若未加入搜索路径
    sys.path.insert(0, ROOT)  # 加入

from app.db import init_db  # 导入数据库初始化
from app.harness import redlines  # 导入红线模块
from app.harness.engine import run_trace, confirm_release, reset_graph  # 导入编排引擎
from app.kb.graph import build_graph, check_trace  # 导入知识图谱


ADMIN = {"username": "admin", "role": "admin", "display_name": "傅景"}  # 管理员用户
USER = {"username": "user", "role": "user", "display_name": "林亦舟"}  # 普通用户


def setup_module(module):
    """测试前初始化数据库与图谱。
    入参：module - pytest 传入的模块对象。
    出参：None。
    失败时：初始化异常会让测试报错。
    """
    init_db()  # 建表与种子
    reset_graph()  # 重置图谱缓存


def test_action_boundary():
    """越界动作必须被红线拦截。
    入参：无。
    出参：无，断言通过即成功。
    失败时：断言失败抛出 AssertionError。
    """
    import pytest  # 局部导入 pytest
    with pytest.raises(redlines.RedlineHit):  # 期望抛出红线异常
        redlines.check_action_boundary("请自动放行")  # 越界请求


def test_release_redline():
    """未复检+签核不得放行。
    入参：无。
    出参：无。
    失败时：断言失败抛出 AssertionError。
    """
    import pytest  # 局部导入
    with pytest.raises(redlines.RedlineHit):  # 期望拦截
        redlines.check_release(False, False)  # 未复检未签核
    redlines.check_release(True, True)  # 齐全不抛异常


def test_graph_break_chain():
    """换批号批次在知识图谱中应判定为断链。
    入参：无。
    出参：无。
    失败时：断言失败抛出 AssertionError。
    """
    graph = build_graph()  # 构建图谱
    result = check_trace(graph, "B-260203")  # 检查换号批次
    assert result["complete"] is False  # 断言断链
    assert "断裂" in result["reason"]  # 断言原因说明断链


def test_trace_user_cannot_see_sensitive():
    """user 角色查询不得返回检测明细。
    入参：无。
    出参：无。
    失败时：断言失败抛出 AssertionError。
    """
    result = run_trace(USER, "B-260201", "normal")  # user 查询
    assert "inspections" not in result["data"]  # 断言无敏感字段


def test_break_chain_to_manual():
    """换批号断链场景必须转人工。
    入参：无。
    出参：无。
    失败时：断言失败抛出 AssertionError。
    """
    result = run_trace(ADMIN, "B-260203", "broken_chain")  # 断链场景
    assert result["status"] == "manual"  # 断言转人工


def test_confirm_needs_admin():
    """放行必须 admin 且复检签核齐全。
    入参：无。
    出参：无。
    失败时：断言失败抛出 AssertionError。
    """
    r1 = confirm_release(USER, "B-260201", True, True)  # user 放行
    assert r1["status"] == "blocked"  # 断言被拒
    r2 = confirm_release(ADMIN, "B-260201", False, True)  # 未复检
    assert r2["status"] == "blocked"  # 断言被拒
    r3 = confirm_release(ADMIN, "B-260201", True, True)  # 齐全
    assert r3["status"] == "released"  # 断言放行成功
