"""统一返回结构：所有对外接口都返回 {"ok", "data", "error"}。"""

from pydantic import BaseModel  # 导入 pydantic 基类，用于构造响应模型


class ErrorBody(BaseModel):  # 错误体模型
    """错误体：承载错误码与可读信息。
    入参：code - 字符串错误码；msg - 中文错误说明。
    出参：序列化后为 {"code": str, "msg": str}。
    失败时：pydantic 会在类型不符时抛出校验错误。
    """
    code: str  # 机器可读错误码
    msg: str  # 人类可读的中文错误信息


class ApiResponse(BaseModel):  # 统一响应模型
    """统一响应：所有接口的唯一返回结构。
    入参：ok - 是否成功；data - 业务数据（任意）；error - 错误体或 None。
    出参：序列化后为 {"ok": bool, "data": ..., "error": {...}}。
    失败时：pydantic 类型校验失败会抛出校验错误。
    """
    ok: bool  # 成功标志
    data: object = None  # 业务数据，失败时可为 None
    error: object = None  # 错误体，成功时为 None


def ok(data=None):
    """构造成功响应。
    入参：data - 要返回的业务数据，默认 None。
    出参：ApiResponse 实例，ok=True，error=None。
    失败时：不会失败。
    """
    return ApiResponse(ok=True, data=data, error=None)  # 返回成功结构


def fail(code, msg):
    """构造失败响应。
    入参：code - 错误码字符串；msg - 中文错误信息。
    出参：ApiResponse 实例，ok=False，data=None，error 为错误体。
    失败时：不会失败。
    """
    return ApiResponse(ok=False, data=None, error=ErrorBody(code=code, msg=msg))  # 返回失败结构
