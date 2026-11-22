# Chemistry-Toolbox (CTB)

一款开源的化学方程式自动配平与化学计算桌面工具，同时提供可独立安装的 Python 配平库 `ctb`。

![软件主界面](https://raw.github.com/123IOPjklbnm/Chemistry-Toolbox/main/images/screenshot-main.png)

## 简介

Chemistry-Toolbox（化学工具箱 v5.0）面向化学学习与实验计算场景，提供方程式配平、摩尔质量、浓度换算、产率计算、经验式确定等功能。

项目同时维护一个发布于 PyPI 的轻量配平库 `ctb`，可以直接在 Python 代码中调用。此外，项目为 Windows XP 提供了独立的兼容特别版。

## 功能特性

- **方程式配平**：支持常规方程式与离子方程式；离子电荷用 `^n+` / `^n-` 表示（如 `Fe^3+`）；支持 `=`、`->`、`→` 作为箭头；支持嵌套括号。
- **化学计算**：摩尔质量、元素质量分数、浓度计算与稀释、质量分数换算、产率、比例求解、经验式确定。
- **元素周期表**：内置完整元素数据，包含电子排布与电负性。
- **中文编程环境**：内置中文关键字的条件、循环、函数定义，适合教学演示。
- **插件扩展**：`plugins/` 目录下的 `.py` 文件可在启动时自动加载。
- **CTB 表格**：内置表格工具，支持公式与图表（依赖 openpyxl）。

## 下载与安装

### 桌面应用（Windows）

前往 [Releases 页面](https://github.com/123IOPjklbnm/Chemistry-Toolbox/releases) 下载最新版本 `v5.0` 的可执行文件（EXE）。

### Windows XP 兼容特别版

XP 用户请在 Releases 页面查找标记为 **XP 特别版** 的附件。该版本复用相同的配平与计算核心，针对 XP 环境做了适配。

### PyPI 配平库 `ctb`

库版本为 `0.3.0`，安装方式：

```bash
pip install ctb
```

使用示例：

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

**输入格式约定**：`^n+` 表示 n 个正电荷，`^n-` 表示 n 个负电荷；`=`、`->`、`→` 均为合法反应箭头。格式错误或无法配平时抛出 `ValueError`。

## 从源码运行

如果你想直接运行源码或进行二次开发：

```bash
git clone https://github.com/123IOPjklbnm/Chemistry-Toolbox.git
cd Chemistry-Toolbox
pip install -r requirements.txt
python 5.0.py
```

主要依赖：
- Python 3.x
- `numpy`（用于配平方程组的线性代数求解）
- `openpyxl`（可选，用于 CTB 表格与 Excel 导出）
- `xlrd`（可选，用于读取旧版 Excel 文件）

## 反馈与贡献

- 提交 Bug 或功能建议：[GitHub Issues](https://github.com/123IOPjklbnm/Chemistry-Toolbox/issues)
- 欢迎提交 Pull Request。

## 许可证

本项目基于 MIT License 开源，`ctb` 库同样使用 MIT License。
