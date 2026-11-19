"""数据库模块：SQLite 建表、会话管理与合成种子数据。

表结构对应数据红线：
- audit_log：审计六字段（f45），每次建议都必须落一行。
- manual_queue：转人工三要素（f44），NOT NULL 强制。
- reworks：原批号关联（f11），换批号断链即在此体现。
"""

import os  # 导入系统模块，用于建目录
import sqlite3  # 导入 SQLite 驱动
from app.config import load_config, data_path  # 导入配置读取与路径解析函数


def connect():
    """建立并返回 SQLite 连接（每行写操作后由调用方提交）。
    入参：无，路径从 config.yaml 读取。
    出参：sqlite3.Connection 连接对象，已设置 row_factory 便于按列名取值。
    失败时：数据库文件不可写会抛出 sqlite3.OperationalError。
    """
    cfg = load_config()  # 读取配置
    db_file = data_path(cfg["database"]["path"])  # 解析数据库绝对路径
    os.makedirs(os.path.dirname(db_file), exist_ok=True)  # 确保 data 目录存在
    conn = sqlite3.connect(db_file)  # 建立连接
    conn.row_factory = sqlite3.Row  # 设置按列名访问
    return conn  # 返回连接


def init_db():
    """初始化全部业务表（幂等，重复执行不报错）。
    入参：无。
    出参：None，副作用是建表并写入种子数据。
    失败时：SQL 执行异常原样抛出。
    """
    conn = connect()  # 获取连接
    cur = conn.cursor()  # 获取游标
    # 批次表：original_batch_no 为空表示原始批次，非空表示由该批次返工换号而来
    cur.execute("""CREATE TABLE IF NOT EXISTS batches (
        batch_no TEXT PRIMARY KEY,           -- 批次编号（业务编号）
        original_batch_no TEXT,              -- 原批号：返工换批号后指向来源批次
        part_type TEXT,                      -- 零件类型（两类试点零件）
        machine_id TEXT,                     -- 机台编号
        tool_id TEXT,                        -- 刀具编号
        data_version TEXT,                   -- 资料版本号
        data_time TEXT                       -- 数据时点（快照时间）
    )""")
    # 检测记录表：ambiguous=1 的记录进人工修复队列，不进推荐样本（f33）
    cur.execute("""CREATE TABLE IF NOT EXISTS inspections (
        id TEXT PRIMARY KEY,                 -- 检测记录编号
        batch_no TEXT,                       -- 所属批次
        gauge_id TEXT,                       -- 量具编号
        value_text TEXT,                     -- 检测量值摘要
        unit TEXT,                           -- 测量单位（单位混用是已知问题）
        tolerance_version TEXT,              -- 公差版本（版本混用是已知问题）
        gauge_calibrated INTEGER,            -- 量具校准是否有效：1 有效 0 过期
        ambiguous INTEGER DEFAULT 0,         -- 是否有歧义：1 需人工修复
        event_time TEXT                      -- 事件时间
    )""")
    # 返工单表：体现原批号->新批号的换号关系
    cur.execute("""CREATE TABLE IF NOT EXISTS reworks (
        id TEXT PRIMARY KEY,                 -- 返工单编号
        original_batch_no TEXT,              -- 返工前原批号
        new_batch_no TEXT,                   -- 返工后新批号
        reason TEXT,                         -- 返工原因
        tool_id TEXT                         -- 涉及刀具
    )""")
    # 审计表：六字段完整留痕（f45）
    cur.execute("""CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT, -- 自增主键
        biz_no TEXT,                         -- 业务编号
        data_version TEXT,                   -- 资料版本
        fact_refs TEXT,                      -- 事实引用（JSON 字符串）
        suggestion TEXT,                     -- 建议结果
        human_changes TEXT,                  -- 人工改动
        signer TEXT,                         -- 签核人
        created_at TEXT                      -- 留痕时间
    )""")
    # 转人工队列表：三要素 NOT NULL 强制（f44）
    cur.execute("""CREATE TABLE IF NOT EXISTS manual_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT, -- 自增主键
        biz_no TEXT,                         -- 业务编号
        trigger_reason TEXT NOT NULL,        -- 触发原因（必填）
        handler TEXT NOT NULL,               -- 接手人（必填）
        confirmed_at TEXT NOT NULL,          -- 确认时间（必填）
        status TEXT DEFAULT 'PENDING'        -- 处理状态
    )""")
    seed_data(cur)  # 写入合成种子数据
    conn.commit()  # 提交建表与种子数据
    conn.close()  # 关闭连接


def seed_data(cur):
    """写入合成种子数据，模拟星衡精密两类试点零件与换批号断链场景。
    入参：cur - sqlite3 游标对象。
    出参：None，副作用是插入样本行（用 INSERT OR IGNORE 保证幂等）。
    失败时：SQL 异常原样抛出。
    """
    # 原始批次 B-260201：螺纹零件，机台 M-01，刀具 T-07，数据版本 v3
    cur.execute("INSERT OR IGNORE INTO batches VALUES (?,?,?,?,?,?,?)",
                ("B-260201", None, "螺纹件", "M-01", "T-07", "v3", "2026-11-19T09:00:00"))
    # 返工后换号批次 B-260203：由 B-260201 换号而来，但机台/刀具信息缺失 -> 断链
    cur.execute("INSERT OR IGNORE INTO batches VALUES (?,?,?,?,?,?,?)",
                ("B-260203", "B-260201", "螺纹件", None, None, "v4", "2026-11-19T11:00:00"))
    # 正常批次 B-260202：轴类零件，信息齐全，用于对正常场景
    cur.execute("INSERT OR IGNORE INTO batches VALUES (?,?,?,?,?,?,?)",
                ("B-260202", None, "轴类件", "M-02", "T-11", "v3", "2026-11-19T10:00:00"))
    # 合格检测记录：单位 mm，公差 v3，量具已校准，无歧义
    cur.execute("INSERT OR IGNORE INTO inspections VALUES (?,?,?,?,?,?,?,?,?)",
                ("I-001", "B-260201", "G-01", "螺纹中径 8.01", "mm", "v3", 1, 0, "2026-11-19T09:05:00"))
    # 歧义检测记录：单位混用 cm、量具过期、有歧义 -> 进人工修复队列
    cur.execute("INSERT OR IGNORE INTO inspections VALUES (?,?,?,?,?,?,?,?,?)",
                ("I-002", "B-260203", "G-02", "螺纹中径 0.81", "cm", "v4", 0, 1, "2026-11-19T11:05:00"))
    # 返工单：B-260201 换号为 B-260203，涉及原刀具 T-07（用于验证断链可追溯）
    cur.execute("INSERT OR IGNORE INTO reworks VALUES (?,?,?,?,?)",
                ("R-001", "B-260201", "B-260203", "螺纹中径超差返工", "T-07"))


def get_batch(conn, batch_no):
    """按批次编号查询批次记录。
    入参：conn - 数据库连接；batch_no - 批次编号字符串。
    出参：sqlite3.Row 或 None（不存在时）。
    失败时：SQL 异常原样抛出。
    """
    return conn.execute("SELECT * FROM batches WHERE batch_no=?", (batch_no,)).fetchone()  # 返回查询结果


def append_audit(conn, biz_no, data_version, fact_refs, suggestion, human_changes, signer):
    """追加一条审计留痕（只追加不覆盖，保证处理链可重建）。
    入参：conn - 连接；后六个参数对应审计六字段。
    出参：None。
    失败时：SQL 异常原样抛出，由调用方转为失败响应。
    """
    from datetime import datetime  # 局部导入时间模块
    now = datetime.now().isoformat(timespec="seconds")  # 生成留痕时间
    conn.execute("""INSERT INTO audit_log
        (biz_no,data_version,fact_refs,suggestion,human_changes,signer,created_at)
        VALUES (?,?,?,?,?,?,?)""",
        (biz_no, data_version, fact_refs, suggestion, human_changes, signer, now))  # 写入六字段+时间
    conn.commit()  # 提交事务


def append_manual(conn, biz_no, trigger_reason, handler, confirmed_at):
    """追加一条转人工记录（三要素缺一不可）。
    入参：conn - 连接；biz_no - 业务编号；trigger_reason - 触发原因；handler - 接手人；confirmed_at - 确认时间。
    出参：None。
    失败时：任一要素为空会触发 NOT NULL 约束，抛 sqlite3.IntegrityError。
    """
    conn.execute("""INSERT INTO manual_queue
        (biz_no,trigger_reason,handler,confirmed_at) VALUES (?,?,?,?)""",
        (biz_no, trigger_reason, handler, confirmed_at))  # 写入三要素
    conn.commit()  # 提交事务
