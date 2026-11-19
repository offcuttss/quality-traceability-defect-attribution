"""权限模块：管理员(admin)/用户(user)两级权限，基于 config.yaml 的静态账号。

数据红线 f41：只有授权岗位可查看检测量值、校准证书、工艺版本、返工单。
- admin：可查看全部字段，可执行签核/确认。
- user：仅可查看追溯清单辅助字段（批次、零件、数据时点），不可查看量值/证书/工艺版本/返工单，不可签核。
禁止借用账号：每次请求都必须带 token，服务端校验，不信任前端身份下拉。
"""

import hmac  # 导入 hmac，用于安全比较口令
import hashlib  # 导入哈希模块
import json  # 导入 json，用于令牌载荷序列化
import base64  # 导入 base64，用于令牌编码
import time  # 导入时间模块，用于令牌过期校验
from app.config import load_config  # 导入配置读取函数


def find_user(username):
    """按用户名在配置中查找账号。
    入参：username - 用户名字符串。
    出参：dict 用户配置（含 role/password/display_name）或 None。
    失败时：不会失败，找不到返回 None。
    """
    for u in load_config()["auth"]["users"]:  # 遍历配置中的账号列表
        if u["username"] == username:  # 找到匹配用户名
            return u  # 返回该账号配置
    return None  # 未找到返回空


def verify_password(username, password):
    """校验用户名与口令是否匹配。
    入参：username - 用户名；password - 明文口令。
    出参：dict 用户信息（不含口令）或 None（校验失败）。
    失败时：口令错误或用户不存在返回 None，不抛异常。
    """
    user = find_user(username)  # 查账号
    if user is None:  # 账号不存在
        return None  # 返回失败
    # 关键逻辑：用 constant-time 比较避免时序侧信道；demo 口令来自配置，生产应改为哈希+企业身份
    if not hmac.compare_digest(str(user["password"]), str(password)):  # 安全比较口令
        return None  # 口令不符返回失败
    return {"username": username, "role": user["role"], "display_name": user["display_name"]}  # 返回脱敏用户


def make_token(user):
    """签发一个简易令牌（demo 用 HMAC 签名，生产应换 JWT/会话）。
    入参：user - 含 username/role/display_name 的字典。
    出参：str 令牌字符串。
    失败时：不会失败，纯计算。
    """
    cfg = load_config()["auth"]  # 读取鉴权配置
    payload = {  # 构造令牌载荷
        "u": user["username"],  # 用户名
        "r": user["role"],  # 角色
        "n": user["display_name"],  # 显示名
        "exp": int(time.time()) + int(cfg["token_ttl_seconds"]),  # 过期时间戳
    }
    body = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")  # 载荷 base64 编码
    secret = str(cfg["token_secret"]).encode("utf-8")  # 取签名密钥
    sig = hmac.new(secret, body.encode("ascii"), hashlib.sha256).hexdigest()  # 计算 HMAC 签名
    return body + "." + sig  # 返回 载荷.签名 格式令牌


def parse_token(token):
    """解析并校验令牌签名与有效期。
    入参：token - 令牌字符串。
    出参：dict 用户信息（含 username/role/display_name）或 None（无效/过期）。
    失败时：签名不符、过期、格式错误均返回 None，不抛异常。
    """
    if not token or "." not in token:  # 令牌为空或格式不对
        return None  # 返回无效
    body, sig = token.rsplit(".", 1)  # 拆分载荷与签名
    secret = str(load_config()["auth"]["token_secret"]).encode("utf-8")  # 取密钥
    expected = hmac.new(secret, body.encode("ascii"), hashlib.sha256).hexdigest()  # 重算签名
    # 关键逻辑：签名不一致说明令牌被篡改，直接拒绝，防止伪造 admin 角色越权
    if not hmac.compare_digest(expected, sig):  # 安全比较签名
        return None  # 签名无效返回空
    try:  # 尝试解码载荷
        payload = json.loads(base64.urlsafe_b64decode(body.encode("ascii")))  # 解码 JSON
    except Exception:  # 解码失败
        return None  # 返回无效
    if int(payload.get("exp", 0)) < int(time.time()):  # 检查是否过期
        return None  # 过期返回无效
    return {"username": payload["u"], "role": payload["r"], "display_name": payload["n"]}  # 返回用户


def can_view_sensitive(user):
    """判断用户是否可查看敏感字段（量值/证书/工艺版本/返工单）。
    入参：user - 含 role 的用户字典。
    出参：bool，admin 为 True。
    失败时：user 为空或缺少 role 返回 False（默认拒绝，最小权限）。
    """
    # 关键逻辑：默认拒绝，只有明确是 admin 才放行，避免新增角色时误开放敏感数据
    return bool(user and user.get("role") == "admin")  # 仅管理员可见敏感字段


def can_signoff(user):
    """判断用户是否可执行签核/人工确认。
    入参：user - 含 role 的用户字典。
    出参：bool，admin 为 True。
    失败时：user 为空返回 False（默认拒绝）。
    """
    # 关键逻辑：签核是高风险动作，硬编码仅 admin，用户角色永远不能签核（f40/f41）
    return bool(user and user.get("role") == "admin")  # 仅管理员可签核
