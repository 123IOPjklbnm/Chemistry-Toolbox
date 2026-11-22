"""化学方程式配平核心。"""

import re
from fractions import Fraction
from math import gcd
from typing import List, Optional, Tuple

import numpy as np

from ._formula import parse_formula

__all__ = ["balance"]


# 电荷后缀：^数字+ 或 ^数字-
_CHARGE_RE = re.compile(r"\^(\d+)([+-])$")
# 判断 current 是否以 ^数字 结尾（用来区分电荷里的 + 和分隔符 +）
_TAIL_DIGITS_RE = re.compile(r"\^\d+$")


# ==================== 解析辅助 ====================

def _parse_charge(compound: str) -> Tuple[str, int]:
    """
    解析化合物字符串，返回 (化学式, 电荷)。

    例：
        "H^1+"    -> ("H", +1)
        "CO3^2-"  -> ("CO3", -2)
        "H2O"     -> ("H2O", 0)
    """
    m = _CHARGE_RE.search(compound)
    if m:
        num = int(m.group(1))
        sign = m.group(2)
        charge = num if sign == "+" else -num
        formula = compound[: m.start()]
    else:
        charge = 0
        formula = compound
    return formula, charge


def _split_side(side: str) -> List[str]:
    """
    按 + 拆分一侧的化合物，但不拆开电荷里的 +。

    例： "H^1++OH^1-" -> ["H^1+", "OH^1-"]
    """
    compounds: List[str] = []
    current = ""
    for c in side:
        if c == "+":
            # 如果 current 以 ^数字 结尾，这个 + 是电荷
            if _TAIL_DIGITS_RE.search(current):
                current += c
            else:
                if current:
                    compounds.append(current)
                current = ""
        else:
            current += c
    if current:
        compounds.append(current)
    return compounds


def _format_compound(formula: str, coeff: int, charge: int) -> str:
    """按原格式输出化合物（含系数和电荷）。"""
    out = ""
    if coeff > 1:
        out += str(coeff)
    out += formula
    if charge > 0:
        out += f"^{charge}+"
    elif charge < 0:
        out += f"^{abs(charge)}-"
    return out


# ==================== 零空间 -> 整数解 ====================

def _nullspace_to_integers(v: np.ndarray, max_denominator: int = 1000) -> Optional[List[int]]:
    """
    把零空间向量转成最小正整数向量。
    失败（无法全正 / 无法整数化）返回 None。
    """
    v = np.asarray(v, dtype=float)
    v = np.where(np.abs(v) < 1e-8, 0.0, v)

    if np.all(v == 0):
        return None

    # 让大部分分量为正
    if np.sum(v < 0) > np.sum(v > 0):
        v = -v

    # 除以最小非零绝对值，让最小分量变成 ±1
    nonzero = np.abs(v[v != 0])
    if len(nonzero) == 0:
        return None
    v = v / nonzero.min()

    # 用分数精确还原各分量之间的整数比
    fractions = [Fraction(float(x)).limit_denominator(max_denominator) for x in v]

    # 通分
    lcm_val = 1
    for f in fractions:
        lcm_val = lcm_val * f.denominator // gcd(lcm_val, f.denominator)

    ints = [int(f * lcm_val) for f in fractions]

    # 除以最大公约数
    g = 0
    for x in ints:
        g = gcd(g, abs(x))
    if g > 1:
        ints = [x // g for x in ints]

    # 必须全为正
    if any(x <= 0 for x in ints):
        return None

    return ints


def _find_coefficients(A: np.ndarray) -> Optional[List[int]]:
    """
    求 A·x = 0 的最小正整数解。
    化学方程式的零空间通常是一维的。
    """
    try:
        _, s, Vt = np.linalg.svd(A)
    except np.linalg.LinAlgError:
        return None

    if len(s) == 0:
        return None

    # 判断秩
    tol = 1e-10 * max(A.shape) * s[0]
    rank = int(np.sum(s > tol))

    nullspace = Vt[rank:]
    if nullspace.shape[0] == 0:
        return None

    # 一维零空间（最常见）
    if nullspace.shape[0] == 1:
        return _nullspace_to_integers(nullspace[0])

    # 高维零空间：逐个基向量尝试
    for i in range(nullspace.shape[0]):
        result = _nullspace_to_integers(nullspace[i])
        if result is not None:
            return result
    return None


# ==================== 公开 API ====================

def balance(equation: str) -> str:
    """
    配平化学方程式。

    参数:
        equation: 方程式字符串，支持 = / -> / →

    返回:
        配平后的方程式字符串

    异常:
        ValueError: 格式错误或无法配平

    示例:
        >>> balance("H2+O2=H2O")
        '2H2+O2=2H2O'
        >>> balance("Fe2O3+CO=Fe+CO2")
        'Fe2O3+3CO=2Fe+3CO2'
        >>> balance("H^1++OH^1-=H2O")
        'H^1++OH^1-=H2O'
        >>> balance("CO3^2-+H^1+=HCO3^1-")
        'CO3^2-+H^1+=HCO3^1-'
    """
    # 1. 规范化
    equation = equation.replace(" ", "")
    equation = equation.replace("->", "=").replace("→", "=")

    if "=" not in equation:
        raise ValueError("方程式必须包含等号(=)或箭头(->)")

    parts = equation.split("=")
    if len(parts) != 2:
        raise ValueError("方程式必须恰好包含一个等号")

    left, right = parts

    # 2. 拆分成 (化学式, 电荷) 列表
    left_compounds = [_parse_charge(c) for c in _split_side(left)]
    right_compounds = [_parse_charge(c) for c in _split_side(right)]

    if not left_compounds or not right_compounds:
        raise ValueError("方程式两边都必须有化合物")

    # 3. 解析每个化学式，收集所有元素
    left_counts = [parse_formula(f) for f, _ in left_compounds]
    right_counts = [parse_formula(f) for f, _ in right_compounds]

    all_elements = set()
    for c in left_counts + right_counts:
        all_elements.update(c.keys())
    elements = sorted(all_elements)

    n_left = len(left_compounds)
    n_right = len(right_compounds)

    # 4. 构造矩阵 A：每行一个守恒条件，每列一个化合物
    #    左：+；右：-（移到等式一边）
    rows = []
    for elem in elements:
        row = []
        for c in left_counts:
            row.append(c.get(elem, 0))
        for c in right_counts:
            row.append(-c.get(elem, 0))
        rows.append(row)

    # 电荷守恒行（如果有离子）
    charge_row = [ch for _, ch in left_compounds] + [-ch for _, ch in right_compounds]
    if any(c != 0 for c in charge_row):
        rows.append(charge_row)

    A = np.array(rows, dtype=float)

    # 5. 求整数系数
    coeffs = _find_coefficients(A)
    if coeffs is None:
        raise ValueError("无法配平该方程式，请检查输入")

    # 6. 格式化输出（不加空格，与示例一致）
    left_parts = [
        _format_compound(f, coeffs[i], ch)
        for i, (f, ch) in enumerate(left_compounds)
    ]
    right_parts = [
        _format_compound(f, coeffs[n_left + i], ch)
        for i, (f, ch) in enumerate(right_compounds)
    ]

    return "+".join(left_parts) + "=" + "+".join(right_parts)