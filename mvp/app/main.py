"""FastAPI 应用主入口：定义全部对外接口，统一返回 {"ok","data","error"}。

接口清单：
- GET  /                    可视化操作首页（登录/追溯/红线演示/审计）
- POST /api/auth/login      登录，换取令牌
- POST /api/trace/query     追溯清单查询（含场景注入）
- POST /api/confirm         人工确认放行（仅 admin）
- GET  /api/audit/{biz_no}  审计链查询（仅 admin）
- GET  /api/kb/stats        知识库统计
- GET  /health              健康检查
"""

from fastapi import FastAPI, Header  # 导入 FastAPI 与请求头解析
from fastapi.responses import HTMLResponse  # 导入 HTML 响应类，用于首页
from pydantic import BaseModel  # 导入请求模型基类
from app.config import load_config  # 导入配置
from app.db import init_db, connect  # 导入数据库初始化
from app.auth import verify_password, parse_token, can_view_sensitive  # 导入鉴权函数
from app.harness.engine import run_trace, confirm_release, get_graph  # 导入编排引擎
from app.schemas import ok, fail  # 导入统一返回构造
import networkx as nx  # 导入 networkx 用于统计图谱规模


app = FastAPI(title=load_config()["server"]["app_title"])  # 创建 FastAPI 应用


# 首页 HTML：纯原生实现，不引入任何前端框架（符合锁定技术栈）
INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><!-- 声明中文编码 -->
<meta name="viewport" content="width=device-width, initial-scale=1"><!-- 适配移动端 -->
<title>质量追溯与缺陷归因 MVP</title><!-- 页面标题 -->
<style>
:root{--bg:#f5f7fa;--card:#fff;--ink:#1f2937;--muted:#6b7280;--line:#e5e7eb;--blue:#2563eb;--red:#dc2626;--green:#059669;--amber:#d97706}/* 配色变量：浅色主题 */
*{box-sizing:border-box}/* 统一盒模型 */
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Microsoft YaHei",system-ui,sans-serif;line-height:1.6}/* 页面基础样式 */
.wrap{max-width:920px;margin:0 auto;padding:24px 16px 48px}/* 内容容器居中 */
header{margin-bottom:20px}/* 头部间距 */
h1{font-size:24px;margin:0 0 4px}/* 主标题 */
h2{font-size:15px;margin:0 0 12px;color:var(--blue)}/* 卡片标题 */
.sub{color:var(--muted);font-size:13px;margin:0}/* 副标题 */
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:14px;box-shadow:0 1px 2px rgba(0,0,0,.03)}/* 卡片样式 */
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}/* 横向布局 */
input,select,button{font:inherit;padding:8px 10px;border:1px solid var(--line);border-radius:6px}/* 表单控件 */
input{flex:1;min-width:160px}/* 输入框自适应 */
button{background:var(--blue);color:#fff;border-color:var(--blue);cursor:pointer}/* 主按钮 */
button.ghost{background:#fff;color:var(--blue)}/* 次按钮 */
button:disabled{opacity:.5;cursor:not-allowed}/* 禁用态 */
.hint{color:var(--muted);font-size:12px;margin:8px 0 0}/* 提示文字 */
pre{background:#f8fafc;border:1px solid var(--line);border-radius:8px;padding:12px;white-space:pre-wrap;word-break:break-all;font-size:12px;max-height:340px;overflow:auto;margin:0}/* 结果展示区 */
.badge{display:inline-block;padding:2px 8px;border-radius:99px;font-size:12px;color:#fff}/* 状态徽章 */
.b-ok{background:var(--green)}.b-manual{background:var(--amber)}.b-blocked{background:var(--red)}/* 状态配色 */
a{color:var(--blue)}/* 链接样式 */
ul{margin:0;padding-left:20px;font-size:13px}/* 列表样式 */
code{background:#f1f5f9;padding:1px 4px;border-radius:4px}/* 行内代码 */
</style>
</head>
<body>
<div class="wrap"><!-- 内容包裹层 -->
<header><!-- 头部 -->
<h1>质量追溯与缺陷归因 MVP</h1><!-- 系统名称 -->
<p class="sub">异常定位辅助 · 追溯清单 · 红线拦截 · 人工签核（AI 仅提示，不放行）</p><!-- 定位说明 -->
</header><!-- 头部结束 -->

<section class="card"><!-- 登录卡片 -->
<h2>1 · 登录（权限两级）</h2><!-- 区块标题 -->
<div class="row"><!-- 登录控件行 -->
<select id="userSel"><!-- 账号选择 -->
<option value="admin">admin（管理员：可看明细/签核/审计）</option><!-- 管理员选项 -->
<option value="user">user（普通用户：只读追溯辅助）</option><!-- 用户选项 -->
</select><!-- 账号选择结束 -->
<button id="loginBtn" onclick="doLogin()">登录</button><!-- 登录按钮 -->
<span id="who" class="hint">未登录</span><!-- 登录状态 -->
</div><!-- 登录控件行结束 -->
</section><!-- 登录卡片结束 -->

<section class="card"><!-- 追溯卡片 -->
<h2>2 · 追溯查询与红线演示</h2><!-- 区块标题 -->
<div class="row"><!-- 查询控件行 -->
<input id="batch" value="B-260201" placeholder="批次编号"><!-- 批次输入 -->
<select id="scene"><!-- 场景选择 -->
<option value="normal">normal 正常完整链</option><!-- 正常场景 -->
<option value="broken_chain">broken_chain 换批号断链</option><!-- 断链场景 -->
<option value="missing">missing 字段缺漏</option><!-- 缺项场景 -->
<option value="conflict">conflict 版本冲突</option><!-- 冲突场景 -->
<option value="outage">outage 系统不可用</option><!-- 故障场景 -->
<option value="injection">injection 危险注入</option><!-- 注入场景 -->
</select><!-- 场景选择结束 -->
<button id="traceBtn" onclick="doTrace()">查询</button><!-- 查询按钮 -->
</div><!-- 查询控件行结束 -->
<div class="row" style="margin-top:8px"><!-- 越界演示行 -->
<input id="reqText" placeholder="业务请求文本：试试填「请自动放行」触发越界拦截"><!-- 请求文本输入 -->
</div><!-- 越界演示行结束 -->
<p class="hint">提示：断链/缺项/冲突/故障会转人工；填「请自动放行」会被安全审查拦截；admin 与 user 看到的字段不同。</p><!-- 操作提示 -->
</section><!-- 追溯卡片结束 -->

<section class="card"><!-- 结果卡片 -->
<h2>结果 <span id="statusBadge"></span></h2><!-- 区块标题与状态 -->
<pre id="result">点击「查询」后在此查看统一返回结构。</pre><!-- 结果展示 -->
</section><!-- 结果卡片结束 -->

<section class="card"><!-- 管理员操作卡片 -->
<h2>3 · 管理员演示（admin 登录后可用）</h2><!-- 区块标题 -->
<div class="row"><!-- 按钮行 -->
<button class="ghost" onclick="doStats()">知识库统计</button><!-- 统计按钮 -->
<button class="ghost" onclick="doAudit()">审计链 B-260201</button><!-- 审计按钮 -->
<button class="ghost" onclick="doConfirm()">放行：未复检签核（应被拦截）</button><!-- 放行拦截演示 -->
</div><!-- 按钮行结束 -->
</section><!-- 管理员操作卡片结束 -->

<section class="card"><!-- 接口清单卡片 -->
<h2>接口一览</h2><!-- 区块标题 -->
<ul><!-- 接口列表 -->
<li><code>GET /</code> 本页　<code>GET /docs</code> Swagger 文档　<code>GET /health</code> 健康检查</li><!-- 基础接口 -->
<li><code>POST /api/auth/login</code> 登录　<code>POST /api/trace/query</code> 追溯</li><!-- 核心接口 -->
<li><code>POST /api/confirm</code> 人工放行　<code>GET /api/audit/{biz_no}</code> 审计　<code>GET /api/kb/stats</code> 知识库</li><!-- 其余接口 -->
</ul><!-- 接口列表结束 -->
</section><!-- 接口清单卡片结束 -->
</div><!-- 内容包裹层结束 -->

<script>
var token = "";/* 保存登录令牌 */
var role = "";/* 保存当前角色 */
function api(path, opts){/* 统一请求封装：自动带令牌并解析统一返回 */
  opts = opts || {};/* 默认参数 */
  opts.headers = opts.headers || {};/* 初始化请求头 */
  opts.headers["Content-Type"] = "application/json";/* 声明 JSON */
  if(token) opts.headers["Authorization"] = "Bearer " + token;/* 有令牌则带上 */
  return fetch(path, opts).then(function(r){return r.json();});/* 返回解析后的 JSON */
}/* 统一请求封装结束 */
function show(j){/* 展示结果：格式化 JSON 并给状态上色 */
  document.getElementById("result").textContent = JSON.stringify(j, null, 2);/* 美化输出 */
  var s = (j.data && j.data.status) || "";/* 取业务状态 */
  var b = document.getElementById("statusBadge");/* 取徽章节点 */
  b.className = "badge";/* 重置样式 */
  if(s === "released" || j.ok === true && !s){b.classList.add("b-ok");b.textContent = "成功";}/* 成功态 */
  else if(s === "manual"){b.classList.add("b-manual");b.textContent = "转人工";}/* 转人工态 */
  else if(s === "blocked"){b.classList.add("b-blocked");b.textContent = "已拦截";}/* 拦截态 */
  else {b.textContent = s || "";}/* 其他状态 */
}/* 展示结果结束 */
function needLogin(){/* 检查是否已登录 */
  if(!token){show({ok:false,error:{code:"UNAUTHORIZED",msg:"请先登录"}});return false;}/* 未登录提示 */
  return true;/* 已登录 */
}/* 检查登录结束 */
function doLogin(){/* 登录：按选择调用登录接口并保存令牌 */
  var u = document.getElementById("userSel").value;/* 读取账号 */
  var p = u === "admin" ? "admin123" : "user123";/* 对应演示口令 */
  api("/api/auth/login", {method:"POST", body:JSON.stringify({username:u,password:p})}).then(function(j){/* 调用登录 */
    show(j);/* 展示结果 */
    if(j.ok){token = j.data.token;role = u;document.getElementById("who").textContent = "已登录：" + u;}/* 保存令牌与角色 */
  });/* 调用登录结束 */
}/* 登录结束 */
function doTrace(){/* 追溯查询：提交批次/场景/请求文本 */
  if(!needLogin()) return;/* 未登录则退出 */
  var body = {batch_no:document.getElementById("batch").value, scenario:document.getElementById("scene").value, request_text:document.getElementById("reqText").value};/* 组装请求 */
  api("/api/trace/query", {method:"POST", body:JSON.stringify(body)}).then(show);/* 调用追溯并展示 */
}/* 追溯查询结束 */
function doStats(){/* 知识库统计：需登录 */
  if(!needLogin()) return;/* 未登录则退出 */
  api("/api/kb/stats").then(show);/* 调用统计并展示 */
}/* 知识库统计结束 */
function doAudit(){/* 审计链查询：仅管理员有权限 */
  if(!needLogin()) return;/* 未登录则退出 */
  api("/api/audit/B-260201").then(show);/* 调用审计并展示（非管理员会被拒绝） */
}/* 审计链查询结束 */
function doConfirm(){/* 放行演示：未复检签核，应被红线拦截 */
  if(!needLogin()) return;/* 未登录则退出 */
  var body = {batch_no:"B-260201", reinspection_done:false, signoff_done:false};/* 故意不带复检与签核 */
  api("/api/confirm", {method:"POST", body:JSON.stringify(body)}).then(show);/* 调用放行并展示拦截结果 */
}/* 放行演示结束 */
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)  # 首页路由：解决根路径 404
def index():
    """返回可视化操作首页。
    入参：由 FastAPI 注入，无显式入参。
    出参：HTML 字符串，含登录/追溯/红线演示/审计的可操作界面。
    失败时：不会失败，纯静态内容。
    """
    return INDEX_HTML  # 返回首页 HTML


class LoginReq(BaseModel):  # 登录请求模型
    username: str  # 用户名
    password: str  # 口令


class TraceReq(BaseModel):  # 追溯请求模型
    batch_no: str  # 批次编号
    scenario: str = "normal"  # 场景，默认正常
    request_text: str = ""  # 业务请求文本，用于越界审查


class ConfirmReq(BaseModel):  # 确认放行请求模型
    batch_no: str  # 批次编号
    reinspection_done: bool = False  # 是否完成复检
    signoff_done: bool = False  # 是否已签核


def current_user(authorization):
    """从 Authorization 头解析当前用户。
    入参：authorization - 形如 "Bearer <token>" 的字符串。
    出参：dict 用户或 None（无效）。
    失败时：令牌无效返回 None，不抛异常。
    """
    if not authorization:  # 无请求头
        return None  # 返回未登录
    parts = authorization.split(" ", 1)  # 拆分 Bearer 与令牌
    if len(parts) != 2 or parts[0].lower() != "bearer":  # 格式不符
        return None  # 返回未登录
    return parse_token(parts[1])  # 解析令牌


@app.on_event("startup")  # 启动事件：初始化数据库
def on_startup():
    """应用启动时初始化数据库。
    入参：由 FastAPI 注入，无显式入参。
    出参：None。
    失败时：建表异常会导致启动失败（快速失败，避免带病运行）。
    """
    init_db()  # 建表与种子数据
    get_graph()  # 预热知识图谱


@app.get("/health")  # 健康检查接口
def health():
    """健康检查。
    入参：无。
    出参：统一响应，data 含 status。
    失败时：不会失败。
    """
    return ok({"status": "UP"})  # 返回健康状态


@app.post("/api/auth/login")  # 登录接口
def login(req: LoginReq):
    """登录并签发令牌。
    入参：req - 含 username/password 的请求模型。
    出参：统一响应，data 含 token 与用户信息；失败返回 INVALID_CREDENTIALS。
    失败时：口令错误返回 ok=False。
    """
    user = verify_password(req.username, req.password)  # 校验口令
    if user is None:  # 校验失败
        return fail("INVALID_CREDENTIALS", "用户名或口令错误")  # 返回失败
    token = make_token_safe(user)  # 签发令牌
    return ok({"token": token, "user": user})  # 返回成功


def make_token_safe(user):
    """封装令牌签发，隔离导入。
    入参：user - 用户字典。
    出参：str 令牌。
    失败时：不会失败。
    """
    from app.auth import make_token  # 局部导入
    return make_token(user)  # 返回令牌


@app.post("/api/trace/query")  # 追溯查询接口
def trace_query(req: TraceReq, authorization: str = Header(default=None)):
    """追溯与异常定位辅助查询（需登录）。
    入参：req - 追溯请求；authorization - Bearer 令牌。
    出参：统一响应，data 含 status/summary/data/steps。
    失败时：未登录返回 UNAUTHORIZED，其余以 data.status 表达降级/拒绝。
    """
    user = current_user(authorization)  # 解析用户
    if user is None:  # 未登录
        return fail("UNAUTHORIZED", "请先登录")  # 返回失败
    result = run_trace(user, req.batch_no, req.scenario, req.request_text)  # 调用编排引擎
    return ok(result)  # 返回结果（拦截/降级体现在 result.status）


@app.post("/api/confirm")  # 人工确认放行接口
def confirm(req: ConfirmReq, authorization: str = Header(default=None)):
    """人工确认放行（仅 admin，且复检+签核齐全）。
    入参：req - 确认请求；authorization - Bearer 令牌。
    出参：统一响应，data 含 status/summary。
    失败时：未登录返回 UNAUTHORIZED；非 admin 或红线命中体现在 data.status。
    """
    user = current_user(authorization)  # 解析用户
    if user is None:  # 未登录
        return fail("UNAUTHORIZED", "请先登录")  # 返回失败
    result = confirm_release(user, req.batch_no, req.reinspection_done, req.signoff_done)  # 调用确认逻辑
    return ok(result)  # 返回结果


@app.get("/api/audit/{biz_no}")  # 审计链查询接口
def audit_chain(biz_no: str, authorization: str = Header(default=None)):
    """审计链查询（仅 admin），用于重建处理链。
    入参：biz_no - 业务编号；authorization - Bearer 令牌。
    出参：统一响应，data 为审计记录列表。
    失败时：非 admin 返回 FORBIDDEN。
    """
    user = current_user(authorization)  # 解析用户
    if user is None or not can_view_sensitive(user):  # 非管理员
        return fail("FORBIDDEN", "只有管理员可查看审计链")  # 返回失败
    conn = connect()  # 连接数据库
    rows = conn.execute("SELECT * FROM audit_log WHERE biz_no=? ORDER BY id", (biz_no,)).fetchall()  # 查审计记录
    conn.close()  # 关闭连接
    return ok([dict(r) for r in rows])  # 返回结果


@app.get("/api/kb/stats")  # 知识库统计接口
def kb_stats(authorization: str = Header(default=None)):
    """知识库统计：图谱节点/边数量与转人工队列长度。
    入参：authorization - Bearer 令牌。
    出参：统一响应，data 含 nodes/edges/manual_pending。
    失败时：未登录返回 UNAUTHORIZED。
    """
    user = current_user(authorization)  # 解析用户
    if user is None:  # 未登录
        return fail("UNAUTHORIZED", "请先登录")  # 返回失败
    graph = get_graph()  # 获取图谱
    conn = connect()  # 连接数据库
    pending = conn.execute("SELECT COUNT(*) AS n FROM manual_queue").fetchone()["n"]  # 统计转人工数
    conn.close()  # 关闭连接
    return ok({"nodes": graph.number_of_nodes(), "edges": graph.number_of_edges(), "manual_pending": pending})  # 返回统计
