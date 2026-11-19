"""配置加载模块：从 config.yaml 读取全部配置，禁止在代码中写死任何参数。"""

import os  # 导入操作系统模块，用于路径拼接
import yaml  # 导入 yaml 库，用于解析配置文件


# 模块级缓存：配置只加载一次，避免重复读盘
_CONFIG = None  # 缓存的配置字典，初始为空


def load_config(path=None):
    """加载并返回配置字典。
    入参：path - config.yaml 路径，None 时取项目根目录下的 config.yaml。
    出参：dict 配置字典。
    失败时：文件不存在或 YAML 解析失败则抛出 FileNotFoundError / yaml.YAMLError。
    """
    global _CONFIG  # 声明使用模块级缓存变量
    if _CONFIG is not None:  # 若已缓存则直接返回
        return _CONFIG  # 返回缓存配置
    if path is None:  # 若未指定路径
        here = os.path.dirname(os.path.abspath(__file__))  # 取当前文件所在目录
        path = os.path.join(os.path.dirname(here), "config.yaml")  # 拼出项目根目录的 config.yaml
    with open(path, "r", encoding="utf-8") as fh:  # 以 UTF-8 打开配置文件
        _CONFIG = yaml.safe_load(fh)  # 解析 YAML 并写入缓存
    return _CONFIG  # 返回配置字典


def project_root():
    """返回项目根目录绝对路径。
    入参：无。
    出参：str 根目录路径。
    失败时：不会失败，纯路径计算。
    """
    here = os.path.dirname(os.path.abspath(__file__))  # 当前文件目录
    return os.path.dirname(here)  # 上一级即项目根目录


def data_path(relative):
    """把相对路径解析为项目根目录下的绝对路径。
    入参：relative - 相对于项目根目录的路径字符串。
    出参：str 绝对路径；若传入已是绝对路径则原样返回。
    失败时：不会失败，纯路径计算。
    """
    if os.path.isabs(relative):  # 若传入的是绝对路径
        return relative  # 直接返回
    return os.path.join(project_root(), relative)  # 否则拼到项目根目录
