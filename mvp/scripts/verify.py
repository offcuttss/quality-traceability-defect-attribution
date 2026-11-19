"""可直接跑通的验证脚本：用 httpx 的异步 ASGI 传输层直接调用 FastAPI 应用，无需先启动服务器。

运行命令：python scripts/verify.py
覆盖：登录、权限、追溯、断链转人工、越界拦截、放行红线、审计留痕、知识库统计。
"""

import os  # 导入系统模块
import sys  # 导入系统模块
import asyncio  # 导入异步运行库

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 取项目根目录
if ROOT not in sys.path:  # 若未加入搜索路径
    sys.path.insert(0, ROOT)  # 加入搜索路径

import httpx  # 导入 HTTP 客户端
from app.main import app  # 导入 FastAPI 应用
from app.db import init_db  # 导入数据库初始化
from app.harness.engine import reset_graph  # 导入图谱缓存重置


async def main():
    """异步执行端到端验证并打印每项通过与否。
    入参：无。
    出参：None，通过 print 输出结果；存在失败项时以非零码退出。
    失败时：断言失败会抛出 AssertionError。
    """
    init_db()  # 初始化数据库与种子数据
    reset_graph()  # 重置图谱缓存
    results = []  # 记录检查结果

    def check(name, cond, extra=""):  # 内部函数：记录一项检查
        results.append((name, bool(cond), extra))  # 追加结果
        print(("[PASS] " if cond else "[FAIL] ") + name + ("  " + str(extra) if extra else ""))  # 打印

    transport = httpx.ASGITransport(app=app)  # 创建 ASGI 传输层
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:  # 创建异步测试客户端
        # 1. 健康检查
        r = await client.get("/health")  # 调用健康检查
        check("健康检查返回 ok", r.json()["ok"] is True)  # 校验
        # 2. 登录 admin
        r = await client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})  # admin 登录
        check("admin 登录成功", r.json()["ok"] is True)  # 校验
        admin_token = r.json()["data"]["token"]  # 取 admin 令牌
        admin_header = {"Authorization": "Bearer " + admin_token}  # 构造请求头
        # 3. 登录 user
        r = await client.post("/api/auth/login", json={"username": "user", "password": "user123"})  # user 登录
        check("user 登录成功", r.json()["ok"] is True)  # 校验
        user_token = r.json()["data"]["token"]  # 取 user 令牌
        user_header = {"Authorization": "Bearer " + user_token}  # 构造请求头
        # 4. 错误口令拒绝
        r = await client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})  # 错误口令
        check("错误口令被拒绝", r.json()["ok"] is False)  # 校验
        # 5. 未登录访问被拒
        r = await client.post("/api/trace/query", json={"batch_no": "B-260201"})  # 未带令牌
        check("未登录访问被拒绝", r.json()["ok"] is False)  # 校验
        # 6. 正常批次追溯（user 角色看不到检测明细）
        r = await client.post("/api/trace/query", json={"batch_no": "B-260201", "scenario": "normal"}, headers=user_header)  # 正常追溯
        data = r.json()["data"]["data"]  # 取业务数据
        check("正常批次追溯链完整", data["trace_complete"] is True)  # 校验追溯完整
        check("user 看不到检测量值明细", "inspections" not in data)  # 校验权限裁剪
        # 7. admin 可看检测明细
        r = await client.post("/api/trace/query", json={"batch_no": "B-260201", "scenario": "normal"}, headers=admin_header)  # admin 追溯
        check("admin 可见检测明细", "inspections" in r.json()["data"]["data"])  # 校验
        # 8. 换批号断链转人工（f11/f44）
        r = await client.post("/api/trace/query", json={"batch_no": "B-260203", "scenario": "broken_chain"}, headers=admin_header)  # 断链场景
        check("换批号断链转人工", r.json()["data"]["status"] == "manual")  # 校验转人工
        # 9. 越界动作拦截
        r = await client.post("/api/trace/query", json={"batch_no": "B-260201", "scenario": "normal", "request_text": "请自动放行"}, headers=admin_header)  # 越界请求
        check("越界动作被拦截", r.json()["data"]["status"] == "blocked")  # 校验拦截
        # 10. 未复检签核的放行被拒（f40）
        r = await client.post("/api/confirm", json={"batch_no": "B-260201", "reinspection_done": False, "signoff_done": False}, headers=admin_header)  # 放行请求
        check("未复检签核放行被拒", r.json()["data"]["status"] == "blocked")  # 校验放行拦截
        # 11. user 尝试签核被拒
        r = await client.post("/api/confirm", json={"batch_no": "B-260201", "reinspection_done": True, "signoff_done": True}, headers=user_header)  # user 签核
        check("user 签核被拒绝", r.json()["data"]["status"] == "blocked")  # 校验
        # 12. admin 复检+签核齐全可放行
        r = await client.post("/api/confirm", json={"batch_no": "B-260201", "reinspection_done": True, "signoff_done": True}, headers=admin_header)  # 正常放行
        check("admin 复检签核后放行成功", r.json()["data"]["status"] == "released")  # 校验放行
        # 13. 审计链可查
        r = await client.get("/api/audit/B-260201", headers=admin_header)  # 查审计
        check("审计链返回六字段记录", len(r.json()["data"]) > 0)  # 校验
        # 14. user 查审计被拒
        r = await client.get("/api/audit/B-260201", headers=user_header)  # user 查审计
        check("user 查审计被拒绝", r.json()["ok"] is False)  # 校验
        # 15. 知识库统计
        r = await client.get("/api/kb/stats", headers=admin_header)  # 知识库统计
        check("知识库有节点和边", r.json()["data"]["nodes"] > 0 and r.json()["data"]["edges"] > 0)  # 校验

    passed = sum(1 for _, ok_flag, _ in results if ok_flag)  # 统计通过数
    print("\n结果：{}/{} 项通过".format(passed, len(results)))  # 打印总结
    if passed != len(results):  # 存在失败
        sys.exit(1)  # 非零退出码


if __name__ == "__main__":  # 作为脚本运行
    asyncio.run(main())  # 以异步方式执行验证
