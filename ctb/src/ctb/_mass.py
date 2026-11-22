"""相对原子质量 / 相对分子质量计算。"""

from ._formula import parse_formula

__all__ = ["mass", "ATOMIC_MASSES"]


# ==================== 精确相对原子质量（IUPAC 推荐值）====================
ATOMIC_MASSES = {
    'H': 1.008,   'He': 4.0026, 'Li': 6.94,   'Be': 9.0122,
    'B': 10.81,   'C': 12.011,  'N': 14.007,  'O': 15.999,
    'F': 18.998,  'Ne': 20.180, 'Na': 22.990, 'Mg': 24.305,
    'Al': 26.982, 'Si': 28.085, 'P': 30.974,  'S': 32.06,
    'Cl': 35.45,  'Ar': 39.948, 'K': 39.098,  'Ca': 40.078,
    'Sc': 44.956, 'Ti': 47.867, 'V': 50.942,  'Cr': 51.996,
    'Mn': 54.938, 'Fe': 55.845, 'Co': 58.933, 'Ni': 58.693,
    'Cu': 63.546, 'Zn': 65.38,  'Ga': 69.723, 'Ge': 72.630,
    'As': 74.922, 'Se': 78.971, 'Br': 79.904, 'Kr': 83.798,
    'Rb': 85.468, 'Sr': 87.62,  'Y':  88.906, 'Zr': 91.224,
    'Nb': 92.906, 'Mo': 95.95,  'Tc': 98.0,   'Ru': 101.07,
    'Rh': 102.91, 'Pd': 106.42, 'Ag': 107.87, 'Cd': 112.41,
    'In': 114.82, 'Sn': 118.71, 'Sb': 121.76, 'Te': 127.60,
    'I':  126.90, 'Xe': 131.29, 'Cs': 132.91, 'Ba': 137.33,
    'La': 138.91, 'Ce': 140.12, 'Pr': 140.91, 'Nd': 144.24,
    'Pm': 145.0,  'Sm': 150.36, 'Eu': 151.96, 'Gd': 157.25,
    'Tb': 158.93, 'Dy': 162.50, 'Ho': 164.93, 'Er': 167.26,
    'Tm': 168.93, 'Yb': 173.05, 'Lu': 174.97, 'Hf': 178.49,
    'Ta': 180.95, 'W':  183.84, 'Re': 186.21, 'Os': 190.23,
    'Ir': 192.22, 'Pt': 195.08, 'Au': 196.97, 'Hg': 200.59,
    'Tl': 204.38, 'Pb': 207.2,  'Bi': 208.98, 'Po': 209.0,
    'At': 210.0,  'Rn': 222.0,  'Fr': 223.0,  'Ra': 226.0,
    'Ac': 227.0,  'Th': 232.04, 'Pa': 231.04, 'U':  238.03,
    'Np': 237.0,  'Pu': 244.0,  'Am': 243.0,  'Cm': 247.0,
    'Bk': 247.0,  'Cf': 251.0,  'Es': 252.0,  'Fm': 257.0,
    'Md': 258.0,  'No': 259.0,  'Lr': 262.0,  'Rf': 267.0,
    'Db': 268.0,  'Sg': 269.0,  'Bh': 270.0,  'Hs': 269.0,
    'Mt': 278.0,  'Ds': 281.0,  'Rg': 282.0,  'Cn': 285.0,
    'Nh': 286.0,  'Fl': 289.0,  'Mc': 290.0,  'Lv': 293.0,
    'Ts': 294.0,  'Og': 294.0,
}


# ==================== 近似相对原子质量表 ====================
def _build_approx_table() -> dict:
    """
    近似质量规则：
      - 所有元素：精确值四舍五入到整数
      - 氯 (Cl)：固定为 35.5（教材惯例）
    """
    table = {}
    for sym, m in ATOMIC_MASSES.items():
        if sym == 'Cl':
            table[sym] = 35.5
        else:
            table[sym] = float(round(m))
    return table


_APPROX_MASSES = _build_approx_table()


# ==================== 公开 API ====================
def mass(name: str, mode: int = 1) -> float:
    """
    计算元素的相对原子质量或化合物的相对分子质量。

    参数:
        name: 元素符号或化学式，如 "H", "C", "Ag", "CO2", "Fe2(SO4)3", "Ca(OH)2"
        mode: 输出模式
              1（默认）- 完整（精确）相对原子质量 / 相对分子质量
              2         - 近似相对原子质量 / 相对分子质量
                          （所有元素四舍五入到整数，氯除外，氯为 35.5）

    返回:
        相对原子质量 / 相对分子质量 (float)

    异常:
        ValueError: mode 不是 1 或 2，或化学式无效
        KeyError:   化学式中含未知元素

    示例:
        >>> mass("H")
        1.008
        >>> mass("H", 2)
        1.0
        >>> mass("CO2")
        44.009
        >>> mass("CO2", 2)
        44.0
        >>> mass("Fe2(SO4)3")
        399.858
        >>> mass("Fe2(SO4)3", 2)
        400.0
        >>> mass("Cl", 2)
        35.5
        >>> mass("Ag")
        107.87
    """
    if mode not in (1, 2):
        raise ValueError(f"mode 必须是 1 或 2，收到 {mode!r}")

    if not isinstance(name, str) or not name:
        raise ValueError("name 必须是非空字符串")

    counts = parse_formula(name)
    if not counts:
        raise ValueError(f"无效的化学式: {name!r}")

    table = ATOMIC_MASSES if mode == 1 else _APPROX_MASSES

    total = 0.0
    for element, count in counts.items():
        if element not in table:
            raise KeyError(f"未知元素: {element}")
        total += table[element] * count

    # 抹掉浮点累加误差（如 18.014999999999997 -> 18.015）
    return round(total, 4)