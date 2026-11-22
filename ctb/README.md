\# ctb



化学工具箱核心库。目前提供：



\- \*\*`balance(equation)`\*\* — 化学方程式配平（支持离子）

\- \*\*`mass(name, mode=1)`\*\* — 相对原子 / 分子质量计算

\- \*\*`parse\_formula(formula)`\*\* — 化学式解析

\- \*\*`ctbhelp(name=None)`\*\* — 终端帮助系统



\## 安装



```bash

pip install ctb

```



\## 快速开始



```python

from ctb import balance, mass, parse\_formula, ctbhelp



\# 配平

balance("H2+O2=H2O")                 # '2H2+O2=2H2O'

balance("Fe2O3+CO=Fe+CO2")           # 'Fe2O3+3CO=2Fe+3CO2'

balance("H^1++OH^1-=H2O")            # 'H^1++OH^1-=H2O'



\# 质量计算

mass("H")                            # 1.008

mass("CO2")                          # 44.009

mass("CO2", 2)                       # 44.0

mass("NaCl", 2)                      # 58.5   ← 氯按 35.5



\# 化学式解析

parse\_formula("Ca(OH)2")             # {'Ca': 1, 'O': 2, 'H': 2}



\# 帮助

ctbhelp()                            # 库总览

ctbhelp("balance")                   # balance 详细帮助

```



\## 终端帮助系统



在终端运行：



```bash

python -c "from ctb import ctbhelp; ctbhelp()"

python -c "from ctb import ctbhelp; ctbhelp('mass')"

```



或在交互环境：



```python

>>> from ctb import ctbhelp

>>> ctbhelp()

>>> ctbhelp("balance")

>>> ctbhelp("mass")

```



\## API



\### `balance(equation: str) -> str`



配平化学方程式，返回配平后的字符串。失败抛 `ValueError`。



\*\*输入格式\*\*



| 符号 | 含义 |

|------|------|

| `=` / `->` / `→` | 反应箭头 |

| `+` | 分隔化合物 |

| `^n+` | 带 n 个正电荷（如 `H^1+`、`Fe^3+`） |

| `^n-` | 带 n 个负电荷（如 `CO3^2-`） |

| `()` / `\[]` | 支持括号，可嵌套 |

| 大小写 | 严格区分，`Co`（钴）≠ `CO`（一氧化碳） |



\### `mass(name: str, mode: int = 1) -> float`



计算相对原子 / 分子质量（float，保留 4 位小数）。



\- `mode=1`（默认）：精确值（IUPAC 推荐）

\- `mode=2`：近似值（四舍五入到整数，\*\*Cl 固定为 35.5\*\*）



失败抛 `ValueError`（无效化学式 / 非法 mode）或 `KeyError`（未知元素）。



\### `parse\_formula(formula: str) -> dict`



解析化学式，返回 `{元素: 个数}` 字典。



```python

>>> parse\_formula("H2O")

{'H': 2, 'O': 1}

>>> parse\_formula("Ca(OH)2")

{'Ca': 1, 'O': 2, 'H': 2}

```



\### `ctbhelp(name: str = None, file=None) -> None`



在终端打印帮助信息。



\- `name=None`：显示库总览

\- `name="balance"` / `"mass"` / `"parse\_formula"` / `"ctbhelp"`：显示对应函数详细帮助

\- `file`：输出流，默认 `sys.stdout`（可传 `io.StringIO` 用于测试）



\## 更新日志



\### v0.3.0

\- 新增 `ctbhelp(name=None)` 帮助系统

\- 修正 `test\_mass.py` 中 `Ca(OH)2` 期望值（74.093 → 74.092）



\### v0.2.0

\- 新增 `mass(name, mode=1)` 函数

\- 相对原子质量改用 IUPAC 精确值



\### v0.1.0

\- 首个版本，提供 `balance(equation)`



\## 许可证



MIT © 2026 123IOPjklbnm

