"""ctb —— 化学工具箱核心库。

用法:
    >>> from ctb import balance, mass, parse_formula, ctbhelp
    >>> balance("H2+O2=H2O")
    '2H2+O2=2H2O'
    >>> mass("H2O")
    18.015
    >>> mass("H2O", 2)
    18.0
    >>> ctbhelp()          # 查看帮助
"""

__version__ = "0.3.0"

from ._balance import balance
from ._formula import parse_formula
from ._mass import mass
from ._help import ctbhelp

__all__ = ["balance", "mass", "parse_formula", "ctbhelp"]