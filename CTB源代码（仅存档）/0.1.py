import tkinter as tk
from tkinter import messagebox, scrolledtext
import re
from fractions import Fraction
from collections import defaultdict

# ==================== 配平引擎 ====================
def balance_equation(equation):
    """
    配平化学方程式
    输入格式: "H2+O2=H2O" 或 "H2 + O2 -> H2O"
    返回配平后的方程式字符串
    """
    try:
        # 清理输入
        equation = equation.replace(" ", "").replace("->", "=").replace("→", "=")
        if "=" not in equation:
            return "错误：方程式必须包含等号(=)或箭头(->)"
        
        left, right = equation.split("=")
        
        # 解析化合物
        def parse_compounds(s):
            # 按 + 分割，处理可能的空字符串
            return [c for c in re.split(r'\+', s) if c]
        
        left_compounds = parse_compounds(left)
        right_compounds = parse_compounds(right)
        
        if not left_compounds or not right_compounds:
            return "错误：方程式两边都必须有化合物"
        
        # 提取元素和计数
        def get_element_counts(formula):
            # 解析化学式，返回元素到原子数的映射
            counts = defaultdict(int)
            i = 0
            n = len(formula)
            while i < n:
                if formula[i].isupper():
                    element = formula[i]
                    i += 1
                    if i < n and formula[i].islower():
                        element += formula[i]
                        i += 1
                    # 读取数字
                    num = ""
                    while i < n and formula[i].isdigit():
                        num += formula[i]
                        i += 1
                    counts[element] += int(num) if num else 1
                else:
                    # 不应该出现，但跳过
                    i += 1
            return counts
        
        # 收集所有元素
        all_elements = set()
        left_comp_counts = []
        for comp in left_compounds:
            counts = get_element_counts(comp)
            left_comp_counts.append(counts)
            all_elements.update(counts.keys())
        
        right_comp_counts = []
        for comp in right_compounds:
            counts = get_element_counts(comp)
            right_comp_counts.append(counts)
            all_elements.update(counts.keys())
        
        elements = sorted(all_elements)
        n_left = len(left_compounds)
        n_right = len(right_compounds)
        n_total = n_left + n_right
        
        # 构建线性方程组: 对于每个元素，左边原子数 = 右边原子数
        # 未知数: 系数 x1...xn_left (左边), y1...yn_right (右边)
        # 方程: sum(x_i * left_count[element][i]) = sum(y_j * right_count[element][j])
        # 设 y1 = 1 (固定一个系数)
        # 方程组变为: sum(x_i * left_count) - sum(y_j * right_count) = 0
        
        # 简化：使用整数线性规划的思想，从较小的系数开始尝试
        # 这里使用分数矩阵求解，然后转换为整数
        
        # 构建矩阵 A * coeff = 0, 其中 coeff = [x1...xn_left, y1...yn_right]
        # 每个元素一个方程
        import numpy as np
        
        A = []
        for elem in elements:
            row = []
            for comp in left_comp_counts:
                row.append(comp.get(elem, 0))
            for comp in right_comp_counts:
                row.append(-comp.get(elem, 0))
            A.append(row)
        
        A = np.array(A, dtype=float)
        
        # 添加约束: 所有系数 > 0
        # 通过枚举 y1 从1到某个上限来求解
        max_try = 20
        for y1 in range(1, max_try + 1):
            # 固定 y1 = y1, 将方程移到右边
            # 重新构建方程组: 未知数为 x1..xn_left, y2..yn_right
            # 方程: sum(x_i * left_count) - sum_{j>=2}(y_j * right_count) = y1 * right_count[0]
            b = []
            for elem in elements:
                b.append(y1 * right_comp_counts[0].get(elem, 0))
            
            # 构建系数矩阵
            n_unknowns = n_left + n_right - 1
            M = []
            for elem_idx, elem in enumerate(elements):
                row = []
                # 左边系数
                for comp in left_comp_counts:
                    row.append(comp.get(elem, 0))
                # 右边系数（除第一个）
                for comp in right_comp_counts[1:]:
                    row.append(-comp.get(elem, 0))
                M.append(row)
            
            M = np.array(M, dtype=float)
            b = np.array(b, dtype=float)
            
            try:
                # 求解最小二乘解（如果方程数多于未知数）
                if M.shape[0] > M.shape[1]:
                    # 超定方程，用最小二乘
                    solution, residuals, rank, s = np.linalg.lstsq(M, b, rcond=None)
                    # 检查是否近似满足
                    if np.allclose(M @ solution, b, atol=1e-6):
                        coeffs = list(solution)
                        # 插入 y1
                        coeffs.insert(n_left, y1)
                        # 检查所有系数 > 0 且接近整数
                        int_coeffs = []
                        valid = True
                        for c in coeffs:
                            if c < 0.01:
                                valid = False
                                break
                            # 四舍五入到最近整数，检查误差
                            ic = round(c)
                            if abs(ic - c) > 1e-5:
                                valid = False
                                break
                            int_coeffs.append(ic)
                        if valid:
                            # 化简系数（除以最大公约数）
                            from math import gcd
                            g = int_coeffs[0]
                            for c in int_coeffs[1:]:
                                g = gcd(g, c)
                            if g > 1:
                                int_coeffs = [c // g for c in int_coeffs]
                            # 格式化输出
                            left_part = "+".join(f"{c if c>1 else ''}{comp}" for c, comp in zip(int_coeffs[:n_left], left_compounds))
                            right_part = "+".join(f"{c if c>1 else ''}{comp}" for c, comp in zip(int_coeffs[n_left:], right_compounds))
                            return f"{left_part} = {right_part}"
                else:
                    # 方阵或欠定，求解线性方程组
                    solution = np.linalg.lstsq(M, b, rcond=None)[0]
                    coeffs = list(solution)
                    coeffs.insert(n_left, y1)
                    int_coeffs = []
                    valid = True
                    for c in coeffs:
                        if c < 0.01:
                            valid = False
                            break
                        ic = round(c)
                        if abs(ic - c) > 1e-5:
                            valid = False
                            break
                        int_coeffs.append(ic)
                    if valid:
                        from math import gcd
                        g = int_coeffs[0]
                        for c in int_coeffs[1:]:
                            g = gcd(g, c)
                        if g > 1:
                            int_coeffs = [c // g for c in int_coeffs]
                        left_part = "+".join(f"{c if c>1 else ''}{comp}" for c, comp in zip(int_coeffs[:n_left], left_compounds))
                        right_part = "+".join(f"{c if c>1 else ''}{comp}" for c, comp in zip(int_coeffs[n_left:], right_compounds))
                        return f"{left_part} = {right_part}"
            except np.linalg.LinAlgError:
                continue
        
        return "错误：无法配平该方程式，请检查输入或尝试更简单的方程式"
    
    except Exception as e:
        return f"配平失败: {str(e)}"

# ==================== 元素周期表数据 ====================
elements_data = {
    "H": {"name": "氢", "atomic": 1, "mass": 1.008, "group": 1, "period": 1, "config": "1s¹", "desc": "最轻的元素，宇宙中含量最丰富"},
    "He": {"name": "氦", "atomic": 2, "mass": 4.0026, "group": 18, "period": 1, "config": "1s²", "desc": "稀有气体，沸点最低"},
    "Li": {"name": "锂", "atomic": 3, "mass": 6.94, "group": 1, "period": 2, "config": "[He] 2s¹", "desc": "最轻的金属，用于电池"},
    "Be": {"name": "铍", "atomic": 4, "mass": 9.0122, "group": 2, "period": 2, "config": "[He] 2s²", "desc": "轻金属，有毒"},
    "B": {"name": "硼", "atomic": 5, "mass": 10.81, "group": 13, "period": 2, "config": "[He] 2s² 2p¹", "desc": "类金属，用于半导体"},
    "C": {"name": "碳", "atomic": 6, "mass": 12.011, "group": 14, "period": 2, "config": "[He] 2s² 2p²", "desc": "生命的基础，有机化合物骨架"},
    "N": {"name": "氮", "atomic": 7, "mass": 14.007, "group": 15, "period": 2, "config": "[He] 2s² 2p³", "desc": "大气主要成分"},
    "O": {"name": "氧", "atomic": 8, "mass": 15.999, "group": 16, "period": 2, "config": "[He] 2s² 2p⁴", "desc": "支持燃烧，生命必需"},
    "F": {"name": "氟", "atomic": 9, "mass": 18.998, "group": 17, "period": 2, "config": "[He] 2s² 2p⁵", "desc": "最活泼的非金属"},
    "Ne": {"name": "氖", "atomic": 10, "mass": 20.18, "group": 18, "period": 2, "config": "[He] 2s² 2p⁶", "desc": "稀有气体，用于霓虹灯"},
    # 添加更多常见元素...
    "Na": {"name": "钠", "atomic": 11, "mass": 22.99, "group": 1, "period": 3, "config": "[Ne] 3s¹", "desc": "碱金属，活泼"},
    "Mg": {"name": "镁", "atomic": 12, "mass": 24.305, "group": 2, "period": 3, "config": "[Ne] 3s²", "desc": "轻金属，合金"},
    "Al": {"name": "铝", "atomic": 13, "mass": 26.982, "group": 13, "period": 3, "config": "[Ne] 3s² 3p¹", "desc": "地壳中含量最丰富的金属"},
    "Si": {"name": "硅", "atomic": 14, "mass": 28.086, "group": 14, "period": 3, "config": "[Ne] 3s² 3p²", "desc": "半导体材料"},
    "P": {"name": "磷", "atomic": 15, "mass": 30.974, "group": 15, "period": 3, "config": "[Ne] 3s² 3p³", "desc": "白磷易燃"},
    "S": {"name": "硫", "atomic": 16, "mass": 32.06, "group": 16, "period": 3, "config": "[Ne] 3s² 3p⁴", "desc": "黄色固体"},
    "Cl": {"name": "氯", "atomic": 17, "mass": 35.45, "group": 17, "period": 3, "config": "[Ne] 3s² 3p⁵", "desc": "黄绿色气体，消毒"},
    "Ar": {"name": "氩", "atomic": 18, "mass": 39.95, "group": 18, "period": 3, "config": "[Ne] 3s² 3p⁶", "desc": "稀有气体"},
    "K": {"name": "钾", "atomic": 19, "mass": 39.098, "group": 1, "period": 4, "config": "[Ar] 4s¹", "desc": "活泼金属"},
    "Ca": {"name": "钙", "atomic": 20, "mass": 40.078, "group": 2, "period": 4, "config": "[Ar] 4s²", "desc": "骨骼主要成分"},
    "Fe": {"name": "铁", "atomic": 26, "mass": 55.845, "group": 8, "period": 4, "config": "[Ar] 3d⁶ 4s²", "desc": "最常用的金属"},
    "Cu": {"name": "铜", "atomic": 29, "mass": 63.546, "group": 11, "period": 4, "config": "[Ar] 3d¹⁰ 4s¹", "desc": "导电性好"},
    "Zn": {"name": "锌", "atomic": 30, "mass": 65.38, "group": 12, "period": 4, "config": "[Ar] 3d¹⁰ 4s²", "desc": "防腐镀层"},
    "Ag": {"name": "银", "atomic": 47, "mass": 107.87, "group": 11, "period": 5, "config": "[Kr] 4d¹⁰ 5s¹", "desc": "贵金属，导电性最佳"},
    "Au": {"name": "金", "atomic": 79, "mass": 196.97, "group": 11, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s¹", "desc": "延展性好，不氧化"},
}

# ==================== 主应用程序 ====================
class ChemistryToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title("化学工具箱 v0.1")
        self.root.geometry("900x600")
        
        # 顶部按钮框架
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.btn_balance = tk.Button(self.button_frame, text="配平", width=12, command=self.show_balance)
        self.btn_balance.pack(side=tk.LEFT, padx=5)
        
        self.btn_periodic = tk.Button(self.button_frame, text="元素周期表", width=12, command=self.show_periodic)
        self.btn_periodic.pack(side=tk.LEFT, padx=5)
        
        self.btn_about = tk.Button(self.button_frame, text="关于", width=12, command=self.show_about)
        self.btn_about.pack(side=tk.LEFT, padx=5)
        
        self.btn_help = tk.Button(self.button_frame, text="帮助", width=12, command=self.show_help)
        self.btn_help.pack(side=tk.LEFT, padx=5)
        
        # 内容区域框架
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 默认显示配平界面
        self.show_balance()
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    # ==================== 配平界面 ====================
    def show_balance(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="化学方程式配平", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.content_frame, text="输入格式示例: H2+O2=H2O 或 Fe + O2 -> Fe2O3").pack()
        
        self.equation_entry = tk.Entry(self.content_frame, width=50, font=("Arial", 12))
        self.equation_entry.pack(pady=10)
        self.equation_entry.bind('<Return>', lambda e: self.do_balance())
        
        self.balance_btn = tk.Button(self.content_frame, text="确定", command=self.do_balance, width=15)
        self.balance_btn.pack(pady=5)
        
        self.result_text = scrolledtext.ScrolledText(self.content_frame, height=10, width=70, font=("Arial", 12))
        self.result_text.pack(pady=10, fill=tk.BOTH, expand=True)
    
    def do_balance(self):
        equation = self.equation_entry.get().strip()
        if not equation:
            messagebox.showwarning("警告", "请输入化学方程式")
            return
        
        result = balance_equation(equation)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"输入: {equation}\n\n配平结果:\n{result}")
    
    # ==================== 元素周期表界面 ====================
    def show_periodic(self):
        self.clear_content()
        
        # 创建一个可滚动的画布来放置周期表
        canvas = tk.Canvas(self.content_frame)
        scrollbar = tk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 定义周期表布局（简化版，只显示有数据的元素）
        # 周期1
        row1 = [("H", 1), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("He", 18)]
        # 周期2
        row2 = [("Li", 1), ("Be", 2), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("B", 13), ("C", 14), ("N", 15), ("O", 16), ("F", 17), ("Ne", 18)]
        # 周期3
        row3 = [("Na", 1), ("Mg", 2), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("",), ("Al", 13), ("Si", 14), ("P", 15), ("S", 16), ("Cl", 17), ("Ar", 18)]
        # 周期4 (部分)
        row4 = [("K", 1), ("Ca", 2), ("Sc", 3), ("Ti", 4), ("V", 5), ("Cr", 6), ("Mn", 7), ("Fe", 8), ("Co", 9), ("Ni", 10), ("Cu", 11), ("Zn", 12), ("Ga", 13), ("Ge", 14), ("As", 15), ("Se", 16), ("Br", 17), ("Kr", 18)]
        # 周期5 (部分)
        row5 = [("Rb", 1), ("Sr", 2), ("Y", 3), ("Zr", 4), ("Nb", 5), ("Mo", 6), ("Tc", 7), ("Ru", 8), ("Rh", 9), ("Pd", 10), ("Ag", 11), ("Cd", 12), ("In", 13), ("Sn", 14), ("Sb", 15), ("Te", 16), ("I", 17), ("Xe", 18)]
        # 周期6 (部分)
        row6 = [("Cs", 1), ("Ba", 2), ("La", 3), ("Hf", 4), ("Ta", 5), ("W", 6), ("Re", 7), ("Os", 8), ("Ir", 9), ("Pt", 10), ("Au", 11), ("Hg", 12), ("Tl", 13), ("Pb", 14), ("Bi", 15), ("Po", 16), ("At", 17), ("Rn", 18)]
        
        rows = [row1, row2, row3, row4, row5, row6]
        
        # 创建单元格
        for r, row in enumerate(rows):
            for c, (symbol, group) in enumerate(row):
                if symbol == "":
                    continue
                if symbol in elements_data:
                    data = elements_data[symbol]
                    color = "lightblue"
                    # 按族着色
                    if data["group"] == 1:
                        color = "lightcoral"
                    elif data["group"] == 2:
                        color = "lightgreen"
                    elif 13 <= data["group"] <= 18:
                        color = "lightyellow"
                    elif data["group"] in [3,4,5,6,7,8,9,10,11,12]:
                        color = "lightgray"
                    
                    btn = tk.Button(scrollable_frame, text=f"{symbol}\n{data['atomic']}", width=5, height=2,
                                   bg=color, command=lambda s=symbol: self.show_element_info(s))
                    btn.grid(row=r, column=c, padx=1, pady=1)
        
        # 添加镧系和锕系简单说明
        tk.Label(scrollable_frame, text="注：完整周期表包含更多元素，当前版本仅展示常见元素").grid(row=len(rows), column=0, columnspan=18, pady=10)
    
    def show_element_info(self, symbol):
        data = elements_data.get(symbol)
        if data:
            info = f"元素符号: {symbol}\n"
            info += f"名称: {data['name']}\n"
            info += f"原子序数: {data['atomic']}\n"
            info += f"原子量: {data['mass']}\n"
            info += f"族: {data['group']}\n"
            info += f"周期: {data['period']}\n"
            info += f"电子排布: {data['config']}\n"
            info += f"简介: {data['desc']}\n"
            messagebox.showinfo(f"元素信息 - {symbol}", info)
        else:
            messagebox.showinfo("元素信息", f"未找到 {symbol} 的详细信息，将在后续版本添加。")
    
    # ==================== 关于界面 ====================
    def show_about(self):
        self.clear_content()
        
        about_text = """化学工具箱 (Chemistry Toolbox)
版本: 0.1
更新日期: 2025年3月26日

这是一个用于化学学习和计算的工具集。

主要功能:
• 化学方程式配平
• 元素周期表查询
• 后续将添加更多化学计算功能

开发者: 化学爱好者
开源协议: MIT License

感谢使用本软件！
"""
        text_widget = scrolledtext.ScrolledText(self.content_frame, wrap=tk.WORD, font=("Arial", 12))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, about_text)
        text_widget.config(state=tk.DISABLED)
    
    # ==================== 帮助界面 ====================
    def show_help(self):
        self.clear_content()
        
        help_text = """化学工具箱 v0.1 使用帮助

1. 配平功能
   - 在输入框中输入未配平的化学方程式
   - 支持格式: H2+O2=H2O 或 Fe + O2 -> Fe2O3
   - 支持使用等号(=)或箭头(->)分隔反应物和生成物
   - 点击"确定"按钮或按回车键进行配平
   - 程序会自动计算系数并显示配平结果

2. 元素周期表
   - 点击周期表中的元素按钮
   - 会弹出窗口显示该元素的详细信息
   - 包括: 名称、原子序数、原子量、族、周期、电子排布等

3. 关于
   - 显示软件版本信息和更新日期
   - 介绍软件的主要功能

4. 帮助
   - 您正在查看的就是帮助内容

更新日志 v0.1 (2025-03-26):
   - 初始版本发布
   - 实现基础方程式配平功能
   - 添加部分元素周期表（包含常见元素）
   - 提供关于和帮助界面

注意事项:
   - 配平功能目前支持常见无机方程式
   - 不支持带电荷的离子方程式
   - 有机方程式配平可能不完善
   - 元素周期表数据将持续扩充

如有问题或建议，欢迎反馈！
"""
        text_widget = scrolledtext.ScrolledText(self.content_frame, wrap=tk.WORD, font=("Arial", 12))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

# ==================== 程序入口 ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = ChemistryToolbox(root)
    root.mainloop()