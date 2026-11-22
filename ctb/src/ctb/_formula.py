"""化学式解析工具。"""

from collections import defaultdict

__all__ = ["parse_formula"]


def parse_formula(formula: str) -> dict:
    """
    解析化学式，返回元素计数字典。

    支持：
      - 简单化学式：H2O, CO2, Fe2O3
      - 带括号：Ca(OH)2, Al2(SO4)3
      - 嵌套括号：K4[Fe(CN)6]

    示例:
        >>> parse_formula("H2O")
        {'H': 2, 'O': 1}
        >>> parse_formula("Ca(OH)2")
        {'Ca': 1, 'O': 2, 'H': 2}
    """
    counts: dict = defaultdict(int)

    def parse_part(part: str, multiplier: int = 1) -> None:
        i, n = 0, len(part)
        while i < n:
            c = part[i]
            if c.isupper():
                # 元素符号：大写 + 可选小写
                element = c
                i += 1
                if i < n and part[i].islower():
                    element += part[i]
                    i += 1
                # 数字
                num = ""
                while i < n and part[i].isdigit():
                    num += part[i]
                    i += 1
                count = int(num) if num else 1
                counts[element] += count * multiplier
            elif c in "([":
                # 括号：找到匹配的右括号
                start = i
                depth = 1
                i += 1
                while i < n and depth > 0:
                    if part[i] in "([":
                        depth += 1
                    elif part[i] in ")]":
                        depth -= 1
                    i += 1
                inner = part[start + 1 : i - 1]
                num = ""
                while i < n and part[i].isdigit():
                    num += part[i]
                    i += 1
                bracket_mult = int(num) if num else 1
                parse_part(inner, multiplier * bracket_mult)
            else:
                i += 1

    parse_part(formula)
    return dict(counts)