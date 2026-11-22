"""ctb 帮助系统。

用法:
    >>> from ctb import ctbhelp
    >>> ctbhelp()             # 库总览
    >>> ctbhelp("balance")    # balance 详细帮助
    >>> ctbhelp("mass")       # mass 详细帮助
"""

import sys

from . import __version__

__all__ = ["ctbhelp"]


_LINE = "=" * 72
_DASH = "-" * 72


# ==================== 总览 ====================

def _build_overview() -> str:
    return f"""{_LINE}
  ctb —— 化学工具箱核心库  v{__version__}
{_LINE}

可用函数:
    balance(equation)          化学方程式配平（支持离子方程式）
    mass(name, mode=1)         相对原子质量 / 相对分子质量计算
    parse_formula(formula)     化学式解析，返回元素计数字典
    ctbhelp(name=None)         查看帮助（就是本函数）

用法:
    from ctb import balance, mass, parse_formula, ctbhelp

    balance("H2+O2=H2O")             # '2H2+O2=2H2O'
    mass("H2O")                       # 18.015
    mass("H2O", 2)                    # 18.0
    parse_formula("Ca(OH)2")          # {{'Ca': 1, 'O': 2, 'H': 2}}
    ctbhelp("balance")                # 查看 balance 的详细帮助

    # 在终端直接运行:
    #   python -c "from ctb import ctbhelp; ctbhelp()"
    #   python -c "from ctb import ctbhelp; ctbhelp('mass')"

文档与源码:
    https://github.com/123IOPjklbnm/Chemistry-Toolbox
"""


# ==================== 各函数详细帮助 ====================

def _build_balance_help() -> str:
    return f"""{_LINE}
  balance(equation: str) -> str
{_LINE}

配平化学方程式。

参数:
    equation (str):
        方程式字符串。反应箭头支持 ``=``、``->``、``→``。
        化合物之间用 ``+`` 分隔。
        离子用 ``^数字+`` / ``^数字-`` 表示（如 ``H^1+``、``CO3^2-``）。
        化学式支持 ``()`` / ``[]`` 括号，可嵌套。

返回:
    str —— 配平后的方程式字符串（不含空格）。

异常:
    ValueError —— 格式错误或无法配平。

示例:
    >>> balance("H2+O2=H2O")
    '2H2+O2=2H2O'

    >>> balance("Fe2O3+CO=Fe+CO2")
    'Fe2O3+3CO=2Fe+3CO2'

    >>> balance("Cu+AgNO3=Cu(NO3)2+Ag")
    'Cu+2AgNO3=Cu(NO3)2+2Ag'

    >>> balance("H^1++OH^1-=H2O")
    'H^1++OH^1-=H2O'

    >>> balance("CO3^2-+H^1+=HCO3^1-")
    'CO3^2-+H^1+=HCO3^1-'
"""


def _build_mass_help() -> str:
    return f"""{_LINE}
  mass(name: str, mode: int = 1) -> float
{_LINE}

计算相对原子质量（单元素）或相对分子质量（化合物）。

参数:
    name (str):
        元素符号或化学式，如 ``"H"``、``"C"``、``"Ag"``、
        ``"CO2"``、``"Fe2(SO4)3"``、``"Ca(OH)2"``。
    mode (int):
        输出模式，默认 1。
        - 1 —— 精确值（IUPAC 推荐相对原子质量）
        - 2 —— 近似值（四舍五入到整数，氯除外，氯固定为 35.5）

返回:
    float —— 相对原子质量 / 相对分子质量（保留 4 位小数）。

异常:
    ValueError —— mode 不是 1 或 2，或化学式无效。
    KeyError   —— 化学式中含未知元素。

示例:
    >>> mass("H")
    1.008
    >>> mass("H", 1)
    1.008
    >>> mass("H", 2)
    1.0
    >>> mass("CO2")
    44.009
    >>> mass("CO2", 2)
    44.0
    >>> mass("NaCl")
    58.44
    >>> mass("NaCl", 2)
    58.5
    >>> mass("Fe2(SO4)3")
    399.858
    >>> mass("Fe2(SO4)3", 2)
    400.0
"""


def _build_parse_formula_help() -> str:
    return f"""{_LINE}
  parse_formula(formula: str) -> dict
{_LINE}

解析化学式，返回元素计数字典。

参数:
    formula (str):
        化学式字符串。支持括号 ``()`` / ``[]``，可嵌套。

返回:
    dict —— 形如 ``{{元素: 个数}}`` 的字典。

示例:
    >>> parse_formula("H2O")
    {{'H': 2, 'O': 1}}

    >>> parse_formula("Ca(OH)2")
    {{'Ca': 1, 'O': 2, 'H': 2}}

    >>> parse_formula("K4[Fe(CN)6]")
    {{'K': 4, 'Fe': 1, 'C': 6, 'N': 6}}
"""


def _build_ctbhelp_help() -> str:
    return f"""{_LINE}
  ctbhelp(name: str = None, file=None) -> None
{_LINE}

显示 ctb 帮助信息。

参数:
    name (str):
        要查看的函数名，大小写不敏感。
        支持: ``"balance"``、``"mass"``、``"parse_formula"``、``"ctbhelp"``。
        传入 None（默认）则显示库总览。
    file (TextIO):
        输出流，默认 ``sys.stdout``。
        可传入 ``io.StringIO()`` 用于捕获输出（测试用）。

示例:
    >>> ctbhelp()                # 库总览
    >>> ctbhelp("balance")       # balance 详细帮助
    >>> ctbhelp("mass")          # mass 详细帮助
    >>> ctbhelp("BaLance")       # 大小写不敏感

    # 在终端中:
    #   python -c "from ctb import ctbhelp; ctbhelp()"
    #   python -c "from ctb import ctbhelp; ctbhelp('mass')"
"""


# ==================== 名称 -> 构建器 ====================

_HELP_BUILDERS = {
    "balance": _build_balance_help,
    "mass": _build_mass_help,
    "parse_formula": _build_parse_formula_help,
    "ctbhelp": _build_ctbhelp_help,
}

_FUNCTION_NAMES = sorted(_HELP_BUILDERS.keys())


# ==================== 公开 API ====================

def ctbhelp(name: str = None, file=None) -> None:
    """
    显示 ctb 帮助信息。

    参数:
        name: 要查看的函数名；None 显示库总览。大小写不敏感。
        file: 输出流，默认 sys.stdout。

    示例:
        >>> ctbhelp()
        >>> ctbhelp("balance")
        >>> ctbhelp("mass")
    """
    out = file if file is not None else sys.stdout

    # 总览
    if name is None:
        print(_build_overview(), file=out)
        return

    # 非法类型
    if not isinstance(name, str):
        print(
            f"ctbhelp: 参数 name 必须是字符串或 None，收到 {type(name).__name__!r}。",
            file=out,
        )
        print(f"可用: {', '.join(_FUNCTION_NAMES)}", file=out)
        return

    key = name.strip().lower()

    if key in _HELP_BUILDERS:
        print(_HELP_BUILDERS[key](), file=out)
        return

    # 未找到
    print(f"ctbhelp: 未找到名为 {name!r} 的函数或主题。", file=out)
    print(f"可用: {', '.join(_FUNCTION_NAMES)}", file=out)
    print(f"输入 ctbhelp() 查看总览。", file=out)