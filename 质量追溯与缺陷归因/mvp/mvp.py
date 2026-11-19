"""MVP 启动入口：运行本文件即可启动 FastAPI 服务。

启动命令：python mvp.py
服务地址：http://127.0.0.1:8000 ，接口文档：http://127.0.0.1:8000/docs
所有参数来自 config.yaml，本文件不写死端口/地址/密钥。
"""

import os  # 导入系统模块，用于修正工作目录
import sys  # 导入系统模块，用于设置模块搜索路径

# 关键逻辑：把项目根目录加入模块搜索路径，保证从任意目录启动都能 import app
ROOT = os.path.dirname(os.path.abspath(__file__))  # 取本文件所在目录（项目根目录）
if ROOT not in sys.path:  # 若未加入搜索路径
    sys.path.insert(0, ROOT)  # 插入到最前，优先使用本项目代码

import uvicorn  # 导入 ASGI 服务器
from app.config import load_config  # 导入配置读取函数
from app.main import app  # 导入 FastAPI 应用实例


if __name__ == "__main__":  # 仅作为脚本运行时启动服务
    cfg = load_config()["server"]  # 读取 server 配置段（本地开发回退使用）
    # 部署沙箱通过 PORT 环境变量注入对外端口，本地开发回退到 config.yaml 的 port
    port = int(os.environ.get("PORT", cfg.get("port", 8000)))
    # 沙箱要求绑定 0.0.0.0 才能经反向代理对外访问，HOST 环境变量可覆盖
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)  # 按环境/配置启动服务
