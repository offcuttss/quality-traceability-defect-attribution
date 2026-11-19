# 质量追溯与缺陷归因 MVP

基于原 Node demo 的场景逻辑改造的可运行版本，技术栈锁定：Python 3.11+ / FastAPI / 自研 Harness / 本地知识图谱（networkx + SQLite）/ 两级权限（管理员 admin、用户 user）。

## 运行前提

- Python 3.11 或以上。
- 依赖：fastapi、uvicorn、PyYAML、networkx、pytest、httpx、pydantic（见 requirements.txt）。
- 本机无法直接联网装包时，配置代理后安装（示例见下方）。

## 安装依赖

```bash
pip install -r requirements.txt
# 若 pip 默认源不可用，显式指定代理与官方源：
# pip install --proxy "$HTTPS_PROXY" --index-url https://pypi.org/simple -r requirements.txt
```

## 启动服务

```bash
python mvp.py
# 服务：http://127.0.0.1:8000   接口文档：http://127.0.0.1:8000/docs
```

## 自测命令

```bash
python scripts/verify.py     # 端到端验证脚本，无需先启动服务，15 项检查
pytest -q tests/            # 单元测试，6 个用例
```

## 演示账号（来自 config.yaml，仅用于本地演练）

| 账号 | 口令 | 角色 | 权限 |
|---|---|---|---|
| admin | admin123 | 管理员 | 可看检测量值/校准/工艺版本/返工单，可签核放行，可查审计 |
| user | user123 | 用户 | 仅看追溯清单辅助字段，不可签核、不可看审计 |

## 接口示例

```bash
# 1) 登录取 token
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2) 追溯查询（把 <TOKEN> 换成上一步返回的 data.token）
curl -X POST http://127.0.0.1:8000/api/trace/query \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"batch_no":"B-260201","scenario":"normal"}'

# 3) 换批号断链场景（应返回 status=manual，并写入转人工三要素）
curl -X POST http://127.0.0.1:8000/api/trace/query \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"batch_no":"B-260203","scenario":"broken_chain"}'

# 4) 人工确认放行（未复检签核应被拒；齐全后才 released）
curl -X POST http://127.0.0.1:8000/api/confirm \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"batch_no":"B-260201","reinspection_done":true,"signoff_done":true}'
```

## 目录结构

```
quality-traceability-mvp/
├── config.yaml            # 全部配置（账号/口令/阈值/图谱路径/模型地址占位）
├── requirements.txt       # 依赖
├── mvp.py                 # 启动入口
├── app/
│   ├── main.py            # FastAPI 接口层
│   ├── config.py          # 配置加载
│   ├── schemas.py         # 统一返回结构
│   ├── db.py              # SQLite 建表 + 种子数据
│   ├── auth.py            # 两级权限与令牌
│   ├── kb/graph.py        # 知识图谱与断链判定
│   └── harness/
│       ├── redlines.py    # 数据红线拦截
│       ├── registry.py    # 工具注册
│       └── engine.py      # 编排引擎
├── tests/test_mvp.py      # 单元测试
├── scripts/verify.py      # 端到端验证脚本
└── data/                  # 运行时生成的 SQLite 与图谱文件
```

## 与原 demo 的对应关系

- runtime.js 的 runProjectDemo 场景编排 -> app/harness/engine.py 的 run_trace。
- demoScenarios 六场景 -> config.yaml 的 scenarios，新增 broken_chain。
- 种子合成样本 -> app/db.py 的 seed_data（螺纹件返工换批号断链）。
- 前端身份下拉（非鉴权）-> 服务端 token + 权限矩阵（真实鉴权）。

## 边界

AI 只做归因提示与风险标记，不认定根因、不放行、不替代签核；所有建议只追加审计，不覆盖原记录。LLM 默认关闭（enabled=false），无需 Ollama 即可运行；开启后地址与模型名从 config.yaml 读取。
