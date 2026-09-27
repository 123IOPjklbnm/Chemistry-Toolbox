# Chemistry-Toolbox
## 简介
Chemistry-Toolbox是一个化学工具，主要用于化学方程式的配平，以及一些计算
使用说明见软件的帮助和关于
## 插件开发
### 目录结构
```
chemistry-toolbox/
├── 其他文件
├── Chemistry_Toolbox_3.1.py
└── plugins/
    ├── example_plugin.py
    └── your_plugin.py    ← 你的插件
```
### 最小插件示例
创建 plugins/my_plugin.py
```python
import tkinter

class Plugin:
    def __init__(self, app):
        self.app = app                # 主程序实例
        self.name = "我的插件"         # 插件名称

    def get_menu_name(self):
        return self.name

    def run(self):
        self.app.clear_content()
        tkinter.Label(
            self.app.content_frame,
            text="Hello from plugin!",
            font=self.app.title_font
        ).pack(pady=20)
```
### 可调用的主程序资源
|资源	| 说明|
|---|---|
|app.content_frame	|内容显示区 Frame|
|app.clear_content()	|清空内容区|
|app.update_status(msg)	|更新状态栏文本|
|app.title_font / app.default_font	|预定义字体|
|app.ChemicalFormulaParser	|化学式解析器（calculate_molar_mass、parse_formula 等）|
|app.AtomicMass	|原子量数据|
|app.ValenceData	|化合价数据|
|app.EquationBalancer	|配平引擎（balance(equation)）|
|app.ExtendedPeriodicTable	|周期表数据|
## 免责声明
本软件中所有数据均由 AI 收集整理，不保证完全准确。

本软件的数据由 AI 添加，部分功能由 AI 开发，不保证任何数据及功能计算结果的绝对准确，也不保证结论正确。

由本软件造成的任何问题，本软件开发者不承担任何责任。

「实验演示模块」为测试功能，不稳定，请谨慎使用。

使用协议：如果您开始使用本软件，即视为已同意上述说明。若不同意，请立即停止使用。
## 感谢所有测试和反馈的用户！
