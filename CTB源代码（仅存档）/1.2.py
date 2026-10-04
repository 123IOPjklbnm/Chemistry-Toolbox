import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import re
from collections import defaultdict
import numpy as np
from math import gcd, log10, floor
import datetime
import random

# ==================== 化合价数据 ====================
class ValenceData:
    """化合价数据库"""
    
    element_valences = {
        'H': [1, -1], 'Li': [1], 'Na': [1], 'K': [1], 'Rb': [1], 'Cs': [1], 'Fr': [1],
        'Be': [2], 'Mg': [2], 'Ca': [2], 'Sr': [2], 'Ba': [2], 'Ra': [2],
        'B': [3], 'Al': [3], 'Ga': [3], 'In': [3], 'Tl': [1, 3],
        'C': [4, 2, -4], 'Si': [4], 'Ge': [4, 2], 'Sn': [2, 4], 'Pb': [2, 4],
        'N': [5, 3, 1, 2, 4, -3], 'P': [5, 3, -3], 'As': [5, 3, -3], 
        'Sb': [5, 3], 'Bi': [3, 5],
        'O': [-2, -1], 'S': [6, 4, 2, -2], 'Se': [6, 4, -2], 'Te': [6, 4, -2], 'Po': [4, 2],
        'F': [-1], 'Cl': [7, 5, 3, 1, -1], 'Br': [7, 5, 3, 1, -1], 'I': [7, 5, 3, 1, -1], 'At': [-1],
        'He': [0], 'Ne': [0], 'Ar': [0], 'Kr': [0], 'Xe': [0], 'Rn': [0],
        'Sc': [3], 'Ti': [4, 3], 'V': [5, 4, 3, 2], 'Cr': [6, 3, 2], 
        'Mn': [7, 6, 4, 3, 2], 'Fe': [3, 2], 'Co': [3, 2], 'Ni': [2, 3],
        'Cu': [2, 1], 'Zn': [2], 'Ag': [1], 'Au': [3, 1], 'Hg': [2, 1],
        'Cd': [2], 'Pt': [4, 2], 'Pd': [2, 4], 'Ir': [4, 3], 'Os': [4, 3],
        'Rh': [3], 'Ru': [3], 'Nb': [5], 'Mo': [6, 5, 4, 3], 'Tc': [7],
        'Re': [7, 6, 4], 'W': [6], 'Ta': [5], 'Zr': [4], 'Hf': [4],
        'La': [3], 'Ce': [3, 4], 'Pr': [3], 'Nd': [3], 'Pm': [3], 'Sm': [3, 2],
        'Eu': [3, 2], 'Gd': [3], 'Tb': [3, 4], 'Dy': [3], 'Ho': [3], 'Er': [3],
        'Tm': [3], 'Yb': [3, 2], 'Lu': [3], 'Ac': [3], 'Th': [4], 'Pa': [5, 4],
        'U': [6, 5, 4, 3], 'Np': [6, 5, 4], 'Pu': [6, 5, 4, 3], 'Am': [6, 5, 4, 3],
        'Cm': [3], 'Bk': [3, 4], 'Cf': [3], 'Es': [3], 'Fm': [3], 'Md': [3],
        'No': [3], 'Lr': [3],
    }
    
    radical_valences = {
        'OH': -1, 'NO3': -1, 'NO2': -1, 'SO4': -2, 'SO3': -2, 'CO3': -2,
        'PO4': -3, 'NH4': 1, 'ClO4': -1, 'ClO3': -1, 'ClO2': -1, 'ClO': -1,
        'MnO4': -1, 'CrO4': -2, 'Cr2O7': -2, 'C2O4': -2, 'CH3COO': -1,
    }
    
    @classmethod
    def get_valence(cls, element, compound_context=None):
        if element in cls.element_valences:
            return cls.element_valences[element]
        return [0]

# ==================== 相对原子质量数据 ====================
class AtomicMass:
    atomic_masses = {
        'H': 1, 'He': 4, 'Li': 7, 'Be': 9, 'B': 11, 'C': 12, 'N': 14, 'O': 16, 'F': 19, 'Ne': 20,
        'Na': 23, 'Mg': 24, 'Al': 27, 'Si': 28, 'P': 31, 'S': 32, 'Cl': 35.5, 'Ar': 40,
        'K': 39, 'Ca': 40, 'Sc': 45, 'Ti': 48, 'V': 51, 'Cr': 52, 'Mn': 55, 'Fe': 56,
        'Co': 59, 'Ni': 59, 'Cu': 64, 'Zn': 65, 'Ga': 70, 'Ge': 73, 'As': 75, 'Se': 79,
        'Br': 80, 'Kr': 84, 'Rb': 85, 'Sr': 88, 'Y': 89, 'Zr': 91, 'Nb': 93, 'Mo': 96,
        'Tc': 98, 'Ru': 101, 'Rh': 103, 'Pd': 106, 'Ag': 108, 'Cd': 112, 'In': 115, 'Sn': 119,
        'Sb': 122, 'Te': 128, 'I': 127, 'Xe': 131, 'Cs': 133, 'Ba': 137, 'La': 139, 'Ce': 140,
        'Pr': 141, 'Nd': 144, 'Pm': 145, 'Sm': 150, 'Eu': 152, 'Gd': 157, 'Tb': 159, 'Dy': 163,
        'Ho': 165, 'Er': 167, 'Tm': 169, 'Yb': 173, 'Lu': 175, 'Hf': 179, 'Ta': 181, 'W': 184,
        'Re': 186, 'Os': 190, 'Ir': 192, 'Pt': 195, 'Au': 197, 'Hg': 201, 'Tl': 204, 'Pb': 207,
        'Bi': 209, 'Po': 209, 'At': 210, 'Rn': 222, 'Fr': 223, 'Ra': 226, 'Ac': 227, 'Th': 232,
        'Pa': 231, 'U': 238, 'Np': 237, 'Pu': 244, 'Am': 243, 'Cm': 247, 'Bk': 247, 'Cf': 251,
        'Es': 252, 'Fm': 257, 'Md': 258, 'No': 259, 'Lr': 262, 'Rf': 267, 'Db': 268, 'Sg': 269,
        'Bh': 270, 'Hs': 269, 'Mt': 278, 'Ds': 281, 'Rg': 282, 'Cn': 285, 'Nh': 286, 'Fl': 289,
        'Mc': 290, 'Lv': 293, 'Ts': 294, 'Og': 294,
    }
    
    @classmethod
    def get_mass(cls, element):
        return cls.atomic_masses.get(element, 0)

# ==================== 化学式解析器 ====================
class ChemicalFormulaParser:
    @staticmethod
    def parse_formula(formula):
        counts = defaultdict(int)
        
        def parse_simple(formula_part, multiplier=1):
            i = 0
            n = len(formula_part)
            while i < n:
                if formula_part[i].isupper():
                    element = formula_part[i]
                    i += 1
                    if i < n and formula_part[i].islower():
                        element += formula_part[i]
                        i += 1
                    
                    num = ""
                    while i < n and formula_part[i].isdigit():
                        num += formula_part[i]
                        i += 1
                    count = int(num) if num else 1
                    counts[element] += count * multiplier
                elif formula_part[i] in '([':
                    bracket_start = i
                    bracket_count = 1
                    i += 1
                    while i < n and bracket_count > 0:
                        if formula_part[i] in '([':
                            bracket_count += 1
                        elif formula_part[i] in ')]':
                            bracket_count -= 1
                        i += 1
                    
                    bracket_content = formula_part[bracket_start+1:i-1]
                    num = ""
                    while i < n and formula_part[i].isdigit():
                        num += formula_part[i]
                        i += 1
                    bracket_multiplier = int(num) if num else 1
                    parse_simple(bracket_content, multiplier * bracket_multiplier)
                else:
                    i += 1
        
        parse_simple(formula)
        return dict(counts)
    
    @staticmethod
    def calculate_molar_mass(formula):
        try:
            counts = ChemicalFormulaParser.parse_formula(formula)
            if not counts:
                return 0, "错误：无效的化学式"
            
            total_mass = 0
            details = []
            for element, count in sorted(counts.items()):
                mass = AtomicMass.get_mass(element)
                if mass == 0:
                    return 0, f"错误：未知元素 {element}"
                contribution = mass * count
                total_mass += contribution
                if count == 1:
                    details.append(f"{element}({mass})")
                else:
                    details.append(f"{element}{count}({mass}×{count})")
            return total_mass, " + ".join(details) + f" = {total_mass}"
        except Exception as e:
            return 0, f"计算错误：{str(e)}"

# ==================== 配平引擎 ====================
class EquationBalancer:
    @staticmethod
    def parse_compound_with_charge(compound):
        charge_pattern = r'(\*+)$'
        charge_match = re.search(charge_pattern, compound)
        if charge_match:
            stars = charge_match.group(1)
            charge = -len(stars) if stars.startswith('*') else len(stars)
            formula = compound[:charge_match.start()]
        else:
            charge = 0
            formula = compound
        return formula, charge
    
    @staticmethod
    def balance(equation):
        try:
            equation = equation.replace(" ", "").replace("->", "=").replace("→", "=")
            if "=" not in equation:
                return "错误：方程式必须包含等号(=)或箭头(->)", {}
            
            left, right = equation.split("=")
            
            def parse_side(side):
                compounds = []
                for comp in side.split('+'):
                    if comp:
                        formula, charge = EquationBalancer.parse_compound_with_charge(comp)
                        compounds.append((formula, charge))
                return compounds
            
            left_compounds = parse_side(left)
            right_compounds = parse_side(right)
            
            if not left_compounds or not right_compounds:
                return "错误：方程式两边都必须有化合物", {}
            
            all_elements = set()
            left_comp_data = []
            right_comp_data = []
            
            for formula, charge in left_compounds:
                counts = ChemicalFormulaParser.parse_formula(formula)
                left_comp_data.append((counts, charge))
                all_elements.update(counts.keys())
            
            for formula, charge in right_compounds:
                counts = ChemicalFormulaParser.parse_formula(formula)
                right_comp_data.append((counts, charge))
                all_elements.update(counts.keys())
            
            elements = sorted(all_elements)
            n_left = len(left_compounds)
            n_right = len(right_compounds)
            n_unknowns = n_left + n_right
            
            max_try = 30
            best_solution = None
            best_error = float('inf')
            
            for first_coeff in range(1, max_try + 1):
                A = []
                b = []
                for elem in elements:
                    row = []
                    for counts, _ in left_comp_data:
                        row.append(counts.get(elem, 0))
                    for counts, _ in right_comp_data:
                        row.append(-counts.get(elem, 0))
                    A.append(row)
                    b.append(0)
                
                charge_row = []
                for _, charge in left_comp_data:
                    charge_row.append(charge)
                for _, charge in right_comp_data:
                    charge_row.append(-charge)
                A.append(charge_row)
                b.append(0)
                
                A = np.array(A, dtype=float)
                b = np.array(b, dtype=float)
                
                if n_unknowns > 0 and A.shape[1] > 0:
                    if A.shape[1] > 1:
                        A_reduced = A[:, 1:]
                        b_reduced = b - A[:, 0] * first_coeff
                        try:
                            solution = np.linalg.lstsq(A_reduced, b_reduced, rcond=None)[0]
                            coeffs = [first_coeff] + list(solution)
                            while len(coeffs) < n_unknowns:
                                coeffs.append(1)
                            
                            valid = True
                            int_coeffs = []
                            for c in coeffs[:n_unknowns]:
                                if c < 0.01:
                                    valid = False
                                    break
                                ic = round(c)
                                if abs(ic - c) > 1e-3:
                                    valid = False
                                    break
                                int_coeffs.append(ic)
                            
                            if valid and len(int_coeffs) == n_unknowns:
                                error = sum(abs(A @ coeffs[:n_unknowns] - b))
                                if error < best_error:
                                    best_error = error
                                    best_solution = int_coeffs
                        except np.linalg.LinAlgError:
                            continue
                    else:
                        coeffs = [first_coeff]
                        int_coeffs = [first_coeff]
                        error = sum(abs(A @ coeffs - b))
                        if error < best_error:
                            best_error = error
                            best_solution = int_coeffs
            
            if best_solution and best_error < 1e-5:
                g = best_solution[0]
                for c in best_solution[1:]:
                    g = gcd(g, c)
                if g > 1:
                    best_solution = [c // g for c in best_solution]
                
                left_parts = []
                for i, (formula, charge) in enumerate(left_compounds):
                    if i < len(best_solution):
                        coeff = best_solution[i]
                        formatted = f"{coeff if coeff > 1 else ''}{formula}"
                        if charge != 0:
                            formatted += '*' * abs(charge)
                        left_parts.append(formatted)
                
                right_parts = []
                for i, (formula, charge) in enumerate(right_compounds):
                    idx = n_left + i
                    if idx < len(best_solution):
                        coeff = best_solution[idx]
                        formatted = f"{coeff if coeff > 1 else ''}{formula}"
                        if charge != 0:
                            formatted += '*' * abs(charge)
                        right_parts.append(formatted)
                
                return f"{'+'.join(left_parts)} = {'+'.join(right_parts)}", {}
            
            return "错误：无法配平该方程式", {}
        except Exception as e:
            return f"配平失败: {str(e)}", {}

# ==================== 元素周期表数据 ====================
class PeriodicTable:
    elements_data = {
        "H": {"name": "氢", "atomic": 1, "mass": 1.008, "group": 1, "period": 1, "config": "1s¹", "desc": "最轻的元素"},
        "He": {"name": "氦", "atomic": 2, "mass": 4.0026, "group": 18, "period": 1, "config": "1s²", "desc": "稀有气体"},
        "Li": {"name": "锂", "atomic": 3, "mass": 6.94, "group": 1, "period": 2, "config": "[He] 2s¹", "desc": "最轻的金属"},
        "Be": {"name": "铍", "atomic": 4, "mass": 9.0122, "group": 2, "period": 2, "config": "[He] 2s²", "desc": "轻金属"},
        "B": {"name": "硼", "atomic": 5, "mass": 10.81, "group": 13, "period": 2, "config": "[He] 2s² 2p¹", "desc": "类金属"},
        "C": {"name": "碳", "atomic": 6, "mass": 12.011, "group": 14, "period": 2, "config": "[He] 2s² 2p²", "desc": "生命的基础"},
        "N": {"name": "氮", "atomic": 7, "mass": 14.007, "group": 15, "period": 2, "config": "[He] 2s² 2p³", "desc": "大气主要成分"},
        "O": {"name": "氧", "atomic": 8, "mass": 15.999, "group": 16, "period": 2, "config": "[He] 2s² 2p⁴", "desc": "支持燃烧"},
        "F": {"name": "氟", "atomic": 9, "mass": 18.998, "group": 17, "period": 2, "config": "[He] 2s² 2p⁵", "desc": "最活泼的非金属"},
        "Ne": {"name": "氖", "atomic": 10, "mass": 20.18, "group": 18, "period": 2, "config": "[He] 2s² 2p⁶", "desc": "用于霓虹灯"},
        "Na": {"name": "钠", "atomic": 11, "mass": 22.99, "group": 1, "period": 3, "config": "[Ne] 3s¹", "desc": "碱金属"},
        "Mg": {"name": "镁", "atomic": 12, "mass": 24.305, "group": 2, "period": 3, "config": "[Ne] 3s²", "desc": "轻金属"},
        "Al": {"name": "铝", "atomic": 13, "mass": 26.982, "group": 13, "period": 3, "config": "[Ne] 3s² 3p¹", "desc": "地壳中含量最丰富的金属"},
        "Si": {"name": "硅", "atomic": 14, "mass": 28.086, "group": 14, "period": 3, "config": "[Ne] 3s² 3p²", "desc": "半导体材料"},
        "P": {"name": "磷", "atomic": 15, "mass": 30.974, "group": 15, "period": 3, "config": "[Ne] 3s² 3p³", "desc": "白磷易燃"},
        "S": {"name": "硫", "atomic": 16, "mass": 32.06, "group": 16, "period": 3, "config": "[Ne] 3s² 3p⁴", "desc": "黄色固体"},
        "Cl": {"name": "氯", "atomic": 17, "mass": 35.45, "group": 17, "period": 3, "config": "[Ne] 3s² 3p⁵", "desc": "黄绿色气体"},
        "Ar": {"name": "氩", "atomic": 18, "mass": 39.95, "group": 18, "period": 3, "config": "[Ne] 3s² 3p⁶", "desc": "稀有气体"},
        "K": {"name": "钾", "atomic": 19, "mass": 39.098, "group": 1, "period": 4, "config": "[Ar] 4s¹", "desc": "活泼金属"},
        "Ca": {"name": "钙", "atomic": 20, "mass": 40.078, "group": 2, "period": 4, "config": "[Ar] 4s²", "desc": "骨骼主要成分"},
        "Fe": {"name": "铁", "atomic": 26, "mass": 55.845, "group": 8, "period": 4, "config": "[Ar] 3d⁶ 4s²", "desc": "最常用的金属"},
        "Cu": {"name": "铜", "atomic": 29, "mass": 63.546, "group": 11, "period": 4, "config": "[Ar] 3d¹⁰ 4s¹", "desc": "导电性好"},
        "Zn": {"name": "锌", "atomic": 30, "mass": 65.38, "group": 12, "period": 4, "config": "[Ar] 3d¹⁰ 4s²", "desc": "防腐镀层"},
        "Ag": {"name": "银", "atomic": 47, "mass": 107.87, "group": 11, "period": 5, "config": "[Kr] 4d¹⁰ 5s¹", "desc": "贵金属"},
        "Au": {"name": "金", "atomic": 79, "mass": 196.97, "group": 11, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s¹", "desc": "延展性好"},
        "Hg": {"name": "汞", "atomic": 80, "mass": 200.59, "group": 12, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s²", "desc": "唯一液态金属"},
        "U": {"name": "铀", "atomic": 92, "mass": 238.03, "group": 3, "period": 7, "config": "[Rn] 5f³ 6d¹ 7s²", "desc": "核燃料"},
    }
    
    @classmethod
    def get_element(cls, symbol):
        return cls.elements_data.get(symbol)

# ==================== 主应用程序 ====================
class ChemistryToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title("化学工具箱 v1.0")
        self.root.geometry("1200x800")
        
        self.default_font = ("Microsoft YaHei", 10)
        self.title_font = ("Microsoft YaHei", 12, "bold")
        
        # 创建菜单栏
        self.create_menubar()
        
        # 顶部按钮框架
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # 主要功能按钮
        self.create_main_buttons()
        
        # 状态栏
        self.status_frame = tk.Frame(root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tk.Label(self.status_frame, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 内容区域
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 默认显示配平界面
        self.show_balance()
    
    def create_menubar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出结果", command=self.export_result)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="单位换算", command=self.show_unit_converter)
        tools_menu.add_command(label="实验记录", command=self.show_lab_notebook)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用教程", command=self.show_tutorial)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_main_buttons(self):
        # 第一行：主要功能按钮
        main_buttons = [
            ("配平", self.show_balance),
            ("元素周期表", self.show_periodic),
            ("计算", self.show_calculator_menu),
            ("实用功能", self.show_utility_menu),
            ("关于", self.show_about),
            ("帮助", self.show_help),
        ]
        
        for i, (text, command) in enumerate(main_buttons):
            btn = tk.Button(self.button_frame, text=text, width=12, 
                          font=self.title_font, command=command)
            btn.grid(row=0, column=i, padx=3, pady=2)
    
    def show_utility_menu(self):
        """显示实用功能菜单"""
        utility_menu = tk.Menu(self.root, tearoff=0)
        
        utility_menu.add_command(label="pH计算器", command=self.show_ph_calculator)
        utility_menu.add_command(label="气体定律", command=self.show_gas_law)
        utility_menu.add_command(label="热化学计算", command=self.show_thermochemistry)
        utility_menu.add_command(label="氧化还原分析", command=self.show_redox)
        utility_menu.add_command(label="有机化学工具", command=self.show_organic)
        utility_menu.add_command(label="溶解度查询", command=self.show_solubility)
        utility_menu.add_command(label="缓冲溶液计算", command=self.show_buffer)
        utility_menu.add_command(label="酸碱滴定计算", command=self.show_titration)
        utility_menu.add_command(label="光谱分析", command=self.show_spectroscopy)
        utility_menu.add_command(label="化学动力学", command=self.show_kinetics)
        
        # 获取按钮位置
        btn = self.button_frame.grid_slaves(row=0, column=3)[0]
        utility_menu.post(btn.winfo_rootx(), btn.winfo_rooty() + btn.winfo_height())
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update()
    
    def format_subscript(self, text):
        subscript_map = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
                        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'}
        result = ""
        i = 0
        while i < len(text):
            if text[i].isdigit():
                num_start = i
                while i < len(text) and text[i].isdigit():
                    i += 1
                for digit in text[num_start:i]:
                    result += subscript_map.get(digit, digit)
            else:
                result += text[i]
                i += 1
        return result
    
    # ==================== 1. 配平功能 ====================
    def show_balance(self):
        self.clear_content()
        self.update_status("配平模式 - 离子用星号标注（如 MnO4** 表示 MnO₄⁻）")
        
        tk.Label(self.content_frame, text="化学方程式配平", font=self.title_font, fg="blue").pack(pady=10)
        
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(pady=15)
        tk.Label(input_frame, text="方程式:").pack(side=tk.LEFT)
        self.equation_entry = tk.Entry(input_frame, width=60, font=("Courier", 11))
        self.equation_entry.pack(side=tk.LEFT, padx=10)
        self.equation_entry.bind('<Return>', lambda e: self.do_balance())
        
        tk.Button(input_frame, text="配平", command=self.do_balance, bg="lightblue").pack(side=tk.LEFT)
        
        result_frame = tk.LabelFrame(self.content_frame, text="结果", font=self.title_font)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.balance_result = tk.Text(result_frame, height=12, font=("Courier", 11))
        self.balance_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        examples = [("H2+O2=H2O", "氢气燃烧"), ("Fe2O3+CO=Fe+CO2", "炼铁"), 
                   ("Cu+AgNO3=Cu(NO3)2+Ag", "置换"), ("MnO4**+Fe**=Mn**+Fe**", "氧化还原")]
        example_frame = tk.Frame(self.content_frame)
        example_frame.pack(pady=5)
        tk.Label(example_frame, text="示例:").pack(side=tk.LEFT)
        for eq, desc in examples:
            tk.Button(example_frame, text=desc, command=lambda e=eq: self.load_balance_example(e),
                     font=self.default_font).pack(side=tk.LEFT, padx=5)
    
    def load_balance_example(self, equation):
        self.equation_entry.delete(0, tk.END)
        self.equation_entry.insert(0, equation)
        self.do_balance()
    
    def do_balance(self):
        equation = self.equation_entry.get().strip()
        if not equation:
            messagebox.showwarning("警告", "请输入方程式")
            return
        result, _ = EquationBalancer.balance(equation)
        self.balance_result.delete(1.0, tk.END)
        self.balance_result.insert(tk.END, result)
    
    # ==================== 2. 元素周期表 ====================
    def show_periodic(self):
        self.clear_content()
        self.update_status("元素周期表 - 点击元素查看详细信息")
        
        canvas = tk.Canvas(self.content_frame)
        scrollbar = tk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable = tk.Frame(canvas)
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        rows = [
            [("H",1), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("He",18)],
            [("Li",1), ("Be",2), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("B",13), ("C",14), ("N",15), ("O",16), ("F",17), ("Ne",18)],
            [("Na",1), ("Mg",2), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("Al",13), ("Si",14), ("P",15), ("S",16), ("Cl",17), ("Ar",18)],
            [("K",1), ("Ca",2), ("Sc",3), ("Ti",4), ("V",5), ("Cr",6), ("Mn",7), ("Fe",8), ("Co",9), ("Ni",10), ("Cu",11), ("Zn",12), ("Ga",13), ("Ge",14), ("As",15), ("Se",16), ("Br",17), ("Kr",18)],
            [("Rb",1), ("Sr",2), ("Y",3), ("Zr",4), ("Nb",5), ("Mo",6), ("Tc",7), ("Ru",8), ("Rh",9), ("Pd",10), ("Ag",11), ("Cd",12), ("In",13), ("Sn",14), ("Sb",15), ("Te",16), ("I",17), ("Xe",18)],
            [("Cs",1), ("Ba",2), ("La",3), ("Hf",4), ("Ta",5), ("W",6), ("Re",7), ("Os",8), ("Ir",9), ("Pt",10), ("Au",11), ("Hg",12), ("Tl",13), ("Pb",14), ("Bi",15), ("Po",16), ("At",17), ("Rn",18)],
        ]
        
        for r, row in enumerate(rows):
            for c, (symbol, _) in enumerate(row):
                if symbol:
                    data = PeriodicTable.get_element(symbol)
                    if data:
                        color = "#ffcccc" if data["group"] == 1 else "#ccffcc" if data["group"] == 2 else "#ccccff" if 3 <= data["group"] <= 12 else "#ffffcc"
                        btn = tk.Button(scrollable, text=f"{symbol}\n{data['atomic']}", width=6, height=3,
                                      bg=color, command=lambda s=symbol: self.show_element_info(s))
                        btn.grid(row=r, column=c, padx=1, pady=1)
    
    def show_element_info(self, symbol):
        data = PeriodicTable.get_element(symbol)
        if data:
            info = f"元素: {symbol}\n名称: {data['name']}\n原子序数: {data['atomic']}\n原子量: {data['mass']}\n族: {data['group']}\n周期: {data['period']}\n电子排布: {data['config']}\n简介: {data['desc']}"
            messagebox.showinfo(f"元素信息 - {symbol}", info)
    
    # ==================== 3. 计算功能菜单 ====================
    def show_calculator_menu(self):
        self.clear_content()
        self.update_status("计算功能")
        
        tk.Label(self.content_frame, text="化学计算工具", font=self.title_font, fg="blue").pack(pady=10)
        
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 摩尔质量计算
        molar_frame = tk.Frame(notebook)
        notebook.add(molar_frame, text="摩尔质量")
        self.create_molar_calc(molar_frame)
        
        # 浓度计算
        conc_frame = tk.Frame(notebook)
        notebook.add(conc_frame, text="浓度计算")
        self.create_concentration_calc(conc_frame)
        
        # 稀释计算
        dilute_frame = tk.Frame(notebook)
        notebook.add(dilute_frame, text="稀释计算")
        self.create_dilution_calc(dilute_frame)
        
        # 比例求解
        ratio_frame = tk.Frame(notebook)
        notebook.add(ratio_frame, text="比例求解")
        self.create_ratio_calc(ratio_frame)
    
    def create_molar_calc(self, parent):
        tk.Label(parent, text="输入化学式:", font=self.default_font).pack(pady=5)
        self.molar_entry = tk.Entry(parent, width=40, font=("Courier", 11))
        self.molar_entry.pack(pady=5)
        self.molar_entry.bind('<Return>', lambda e: self.calc_molar_mass())
        
        tk.Button(parent, text="计算", command=self.calc_molar_mass, bg="lightblue").pack(pady=5)
        
        self.molar_result = tk.Text(parent, height=10, font=self.default_font)
        self.molar_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_molar_mass(self):
        formula = self.molar_entry.get().strip()
        if not formula:
            return
        mass, detail = ChemicalFormulaParser.calculate_molar_mass(formula)
        self.molar_result.delete(1.0, tk.END)
        if mass > 0:
            self.molar_result.insert(tk.END, f"化学式: {formula}\n相对分子质量: {mass}\n\n计算过程:\n{detail}")
        else:
            self.molar_result.insert(tk.END, detail)
    
    def create_concentration_calc(self, parent):
        tk.Label(parent, text="溶质质量 (g):").grid(row=0, column=0, padx=5, pady=5)
        self.solute_mass = tk.Entry(parent, width=15)
        self.solute_mass.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(parent, text="溶液体积 (L):").grid(row=1, column=0, padx=5, pady=5)
        self.solution_vol = tk.Entry(parent, width=15)
        self.solution_vol.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(parent, text="摩尔质量 (g/mol):").grid(row=2, column=0, padx=5, pady=5)
        self.molar_mass_conc = tk.Entry(parent, width=15)
        self.molar_mass_conc.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Button(parent, text="计算浓度", command=self.calc_concentration, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        
        self.conc_result = tk.Text(parent, height=8, font=self.default_font)
        self.conc_result.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        parent.grid_rowconfigure(4, weight=1)
        parent.grid_columnconfigure(1, weight=1)
    
    def calc_concentration(self):
        try:
            mass = float(self.solute_mass.get())
            volume = float(self.solution_vol.get())
            molar_mass = float(self.molar_mass_conc.get())
            moles = mass / molar_mass
            concentration = moles / volume
            self.conc_result.delete(1.0, tk.END)
            self.conc_result.insert(tk.END, f"溶质的量: {moles:.4f} mol\n溶液体积: {volume} L\n物质的量浓度: {concentration:.4f} mol/L")
        except:
            self.conc_result.delete(1.0, tk.END)
            self.conc_result.insert(tk.END, "输入错误，请检查")
    
    def create_dilution_calc(self, parent):
        tk.Label(parent, text="初始浓度 (mol/L):").grid(row=0, column=0, padx=5, pady=5)
        self.c1_entry = tk.Entry(parent, width=15)
        self.c1_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(parent, text="初始体积 (L):").grid(row=1, column=0, padx=5, pady=5)
        self.v1_entry = tk.Entry(parent, width=15)
        self.v1_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(parent, text="最终体积 (L):").grid(row=2, column=0, padx=5, pady=5)
        self.v2_entry = tk.Entry(parent, width=15)
        self.v2_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Button(parent, text="计算最终浓度", command=self.calc_dilution, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        
        self.dilute_result = tk.Text(parent, height=6, font=self.default_font)
        self.dilute_result.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
    
    def calc_dilution(self):
        try:
            c1 = float(self.c1_entry.get())
            v1 = float(self.v1_entry.get())
            v2 = float(self.v2_entry.get())
            c2 = c1 * v1 / v2
            self.dilute_result.delete(1.0, tk.END)
            self.dilute_result.insert(tk.END, f"C₁V₁ = C₂V₂\n{c1} × {v1} = C₂ × {v2}\nC₂ = {c2:.4f} mol/L")
        except:
            self.dilute_result.delete(1.0, tk.END)
            self.dilute_result.insert(tk.END, "输入错误")
    
    def create_ratio_calc(self, parent):
        """比例求解功能"""
        tk.Label(parent, text="比例求解", font=self.title_font, fg="blue").pack(pady=10)
        
        # 说明
        info_frame = tk.LabelFrame(parent, text="使用说明", font=self.default_font)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(info_frame, text="格式1: a / b = c / x  → 求解 x = (b × c) / a\n格式2: a / b = x / d  → 求解 x = (a × d) / b", 
                font=self.default_font, justify=tk.LEFT).pack(pady=5, padx=10)
        
        # 选择比例类型
        type_frame = tk.Frame(parent)
        type_frame.pack(pady=10)
        
        self.ratio_type = tk.StringVar(value="type1")
        tk.Radiobutton(type_frame, text="a / b = c / x", variable=self.ratio_type, value="type1", 
                      command=self.update_ratio_inputs, font=self.default_font).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(type_frame, text="a / b = x / d", variable=self.ratio_type, value="type2",
                      command=self.update_ratio_inputs, font=self.default_font).pack(side=tk.LEFT, padx=10)
        
        # 输入框架
        self.ratio_input_frame = tk.Frame(parent)
        self.ratio_input_frame.pack(pady=20)
        
        # 标签和输入框
        self.ratio_labels = {}
        self.ratio_entries = {}
        
        self.update_ratio_inputs()
        
        # 计算按钮
        tk.Button(parent, text="计算 x", command=self.calc_ratio, bg="lightblue", 
                 width=15, font=self.default_font).pack(pady=10)
        
        # 结果显示
        result_frame = tk.LabelFrame(parent, text="计算结果", font=self.default_font)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.ratio_result = tk.Text(result_frame, height=6, font=("Courier", 11))
        self.ratio_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 示例按钮
        example_frame = tk.Frame(parent)
        example_frame.pack(pady=5)
        tk.Label(example_frame, text="示例:").pack(side=tk.LEFT)
        
        tk.Button(example_frame, text="2/3=4/x", command=lambda: self.load_ratio_example("type1", 2, 3, 4),
                 font=self.default_font).pack(side=tk.LEFT, padx=3)
        tk.Button(example_frame, text="2/3=x/6", command=lambda: self.load_ratio_example("type2", 2, 3, 6),
                 font=self.default_font).pack(side=tk.LEFT, padx=3)
    
    def update_ratio_inputs(self):
        """根据比例类型更新输入框"""
        # 清除原有输入框
        for widget in self.ratio_input_frame.winfo_children():
            widget.destroy()
        
        if self.ratio_type.get() == "type1":
            # a / b = c / x
            labels = ["a =", "b =", "c =", "x = ?"]
            self.ratio_vars = ["a", "b", "c"]
        else:
            # a / b = x / d
            labels = ["a =", "b =", "d =", "x = ?"]
            self.ratio_vars = ["a", "b", "d"]
        
        for i, label in enumerate(labels):
            tk.Label(self.ratio_input_frame, text=label, font=self.default_font).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(self.ratio_input_frame, width=15, font=("Courier", 11))
            entry.grid(row=i, column=1, padx=10, pady=5)
            
            if i < 3:  # 前三个是输入框
                self.ratio_entries[self.ratio_vars[i]] = entry
            else:  # x的位置，只显示不可输入
                entry.config(state='disabled', bg='#f0f0f0')
                self.ratio_entries["x_display"] = entry
    
    def load_ratio_example(self, ratio_type, a, b, c_or_d):
        """加载示例"""
        self.ratio_type.set(ratio_type)
        self.update_ratio_inputs()
        
        if ratio_type == "type1":
            self.ratio_entries["a"].delete(0, tk.END)
            self.ratio_entries["a"].insert(0, str(a))
            self.ratio_entries["b"].delete(0, tk.END)
            self.ratio_entries["b"].insert(0, str(b))
            self.ratio_entries["c"].delete(0, tk.END)
            self.ratio_entries["c"].insert(0, str(c_or_d))
        else:
            self.ratio_entries["a"].delete(0, tk.END)
            self.ratio_entries["a"].insert(0, str(a))
            self.ratio_entries["b"].delete(0, tk.END)
            self.ratio_entries["b"].insert(0, str(b))
            self.ratio_entries["d"].delete(0, tk.END)
            self.ratio_entries["d"].insert(0, str(c_or_d))
        
        self.calc_ratio()
    
    def calc_ratio(self):
        """计算比例中的x值"""
        try:
            if self.ratio_type.get() == "type1":
                # a / b = c / x  → x = (b × c) / a
                a = float(self.ratio_entries["a"].get())
                b = float(self.ratio_entries["b"].get())
                c = float(self.ratio_entries["c"].get())
                
                if a == 0:
                    self.ratio_result.delete(1.0, tk.END)
                    self.ratio_result.insert(tk.END, "错误：分母 a 不能为0")
                    return
                
                x = (b * c) / a
                
                self.ratio_result.delete(1.0, tk.END)
                self.ratio_result.insert(tk.END, f"比例式: {a} / {b} = {c} / x\n\n")
                self.ratio_result.insert(tk.END, f"解: x = (b × c) / a\n")
                self.ratio_result.insert(tk.END, f"   x = ({b} × {c}) / {a}\n")
                self.ratio_result.insert(tk.END, f"   x = {b * c} / {a}\n")
                self.ratio_result.insert(tk.END, f"   x = {x}\n\n", "blue_coeff")
                self.ratio_result.insert(tk.END, f"验证: {a}/{b} = {a/b:.4f}, {c}/{x} = {c/x:.4f}")
                
                # 显示结果在x位置
                self.ratio_entries["x_display"].config(state='normal')
                self.ratio_entries["x_display"].delete(0, tk.END)
                self.ratio_entries["x_display"].insert(0, f"{x:.6g}")
                self.ratio_entries["x_display"].config(state='disabled')
                
            else:
                # a / b = x / d  → x = (a × d) / b
                a = float(self.ratio_entries["a"].get())
                b = float(self.ratio_entries["b"].get())
                d = float(self.ratio_entries["d"].get())
                
                if b == 0:
                    self.ratio_result.delete(1.0, tk.END)
                    self.ratio_result.insert(tk.END, "错误：分母 b 不能为0")
                    return
                
                x = (a * d) / b
                
                self.ratio_result.delete(1.0, tk.END)
                self.ratio_result.insert(tk.END, f"比例式: {a} / {b} = x / {d}\n\n")
                self.ratio_result.insert(tk.END, f"解: x = (a × d) / b\n")
                self.ratio_result.insert(tk.END, f"   x = ({a} × {d}) / {b}\n")
                self.ratio_result.insert(tk.END, f"   x = {a * d} / {b}\n")
                self.ratio_result.insert(tk.END, f"   x = {x}\n\n", "blue_coeff")
                self.ratio_result.insert(tk.END, f"验证: {a}/{b} = {a/b:.4f}, {x}/{d} = {x/d:.4f}")
                
                # 显示结果在x位置
                self.ratio_entries["x_display"].config(state='normal')
                self.ratio_entries["x_display"].delete(0, tk.END)
                self.ratio_entries["x_display"].insert(0, f"{x:.6g}")
                self.ratio_entries["x_display"].config(state='disabled')
                
        except ValueError:
            self.ratio_result.delete(1.0, tk.END)
            self.ratio_result.insert(tk.END, "错误：请输入有效的数字")
        except KeyError:
            self.ratio_result.delete(1.0, tk.END)
            self.ratio_result.insert(tk.END, "错误：请完整填写所有输入框")
        except Exception as e:
            self.ratio_result.delete(1.0, tk.END)
            self.ratio_result.insert(tk.END, f"计算错误：{str(e)}")
    
    # ==================== 4. pH计算 ====================
    def show_ph_calculator(self):
        self.clear_content()
        self.update_status("pH计算器")
        
        tk.Label(self.content_frame, text="pH值计算", font=self.title_font, fg="blue").pack(pady=10)
        
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 强酸强碱
        frame1 = tk.Frame(notebook)
        notebook.add(frame1, text="强酸/强碱")
        tk.Label(frame1, text="浓度 (mol/L):").pack(pady=5)
        self.ph_conc = tk.Entry(frame1, width=20)
        self.ph_conc.pack(pady=5)
        tk.Label(frame1, text="类型:").pack(pady=5)
        self.ph_type = ttk.Combobox(frame1, values=["强酸", "强碱"], width=15)
        self.ph_type.pack(pady=5)
        self.ph_type.set("强酸")
        tk.Button(frame1, text="计算pH", command=self.calc_ph, bg="lightblue").pack(pady=10)
        self.ph_result = tk.Text(frame1, height=5, width=40)
        self.ph_result.pack(pady=10)
        
        # 弱酸弱碱
        frame2 = tk.Frame(notebook)
        notebook.add(frame2, text="弱酸/弱碱")
        tk.Label(frame2, text="浓度 (mol/L):").pack(pady=5)
        self.weak_conc = tk.Entry(frame2, width=20)
        self.weak_conc.pack(pady=5)
        tk.Label(frame2, text="Ka/Kb:").pack(pady=5)
        self.ka_kb = tk.Entry(frame2, width=20)
        self.ka_kb.pack(pady=5)
        tk.Label(frame2, text="类型:").pack(pady=5)
        self.weak_type = ttk.Combobox(frame2, values=["弱酸", "弱碱"], width=15)
        self.weak_type.pack(pady=5)
        self.weak_type.set("弱酸")
        tk.Button(frame2, text="计算pH", command=self.calc_weak_ph, bg="lightblue").pack(pady=10)
        self.weak_result = tk.Text(frame2, height=5, width=40)
        self.weak_result.pack(pady=10)
    
    def calc_ph(self):
        try:
            conc = float(self.ph_conc.get())
            if conc <= 0:
                raise ValueError
            if self.ph_type.get() == "强酸":
                ph = -log10(conc)
                self.ph_result.delete(1.0, tk.END)
                self.ph_result.insert(tk.END, f"[H⁺] = {conc} mol/L\npH = {ph:.2f}")
            else:
                poh = -log10(conc)
                ph = 14 - poh
                self.ph_result.delete(1.0, tk.END)
                self.ph_result.insert(tk.END, f"[OH⁻] = {conc} mol/L\npOH = {poh:.2f}\npH = {ph:.2f}")
        except:
            self.ph_result.delete(1.0, tk.END)
            self.ph_result.insert(tk.END, "输入错误")
    
    def calc_weak_ph(self):
        try:
            conc = float(self.weak_conc.get())
            ka = float(self.ka_kb.get())
            if self.weak_type.get() == "弱酸":
                h_conc = (ka * conc) ** 0.5
                ph = -log10(h_conc)
                self.weak_result.delete(1.0, tk.END)
                self.weak_result.insert(tk.END, f"[H⁺] = √(Ka×C) = √({ka}×{conc}) = {h_conc:.2e} mol/L\npH = {ph:.2f}")
            else:
                oh_conc = (ka * conc) ** 0.5
                poh = -log10(oh_conc)
                ph = 14 - poh
                self.weak_result.delete(1.0, tk.END)
                self.weak_result.insert(tk.END, f"[OH⁻] = √(Kb×C) = √({ka}×{conc}) = {oh_conc:.2e} mol/L\npOH = {poh:.2f}\npH = {ph:.2f}")
        except:
            self.weak_result.delete(1.0, tk.END)
            self.weak_result.insert(tk.END, "输入错误")
    
    # ==================== 5. 气体定律 ====================
    def show_gas_law(self):
        self.clear_content()
        self.update_status("理想气体状态方程")
        
        tk.Label(self.content_frame, text="理想气体状态方程 PV = nRT", font=self.title_font, fg="blue").pack(pady=10)
        
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="压力 P (atm):").grid(row=0, column=0, padx=5, pady=5)
        self.pressure = tk.Entry(input_frame, width=15)
        self.pressure.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="体积 V (L):").grid(row=1, column=0, padx=5, pady=5)
        self.volume = tk.Entry(input_frame, width=15)
        self.volume.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="物质的量 n (mol):").grid(row=2, column=0, padx=5, pady=5)
        self.moles = tk.Entry(input_frame, width=15)
        self.moles.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="温度 T (K):").grid(row=3, column=0, padx=5, pady=5)
        self.temperature = tk.Entry(input_frame, width=15)
        self.temperature.grid(row=3, column=1, padx=5, pady=5)
        
        tk.Button(input_frame, text="计算", command=self.calc_gas_law, bg="lightblue").grid(row=4, column=0, columnspan=2, pady=10)
        
        self.gas_result = tk.Text(self.content_frame, height=10, font=self.default_font)
        self.gas_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_gas_law(self):
        R = 0.0821
        result_text = ""
        try:
            if self.pressure.get() and self.volume.get() and self.moles.get():
                P = float(self.pressure.get())
                V = float(self.volume.get())
                n = float(self.moles.get())
                T = P * V / (n * R)
                result_text = f"温度 T = PV/(nR) = {P:.2f}×{V:.2f}/({n:.2f}×{R:.4f}) = {T:.2f} K"
            elif self.pressure.get() and self.volume.get() and self.temperature.get():
                P = float(self.pressure.get())
                V = float(self.volume.get())
                T = float(self.temperature.get())
                n = P * V / (R * T)
                result_text = f"物质的量 n = PV/(RT) = {P:.2f}×{V:.2f}/({R:.4f}×{T:.2f}) = {n:.4f} mol"
            elif self.pressure.get() and self.moles.get() and self.temperature.get():
                P = float(self.pressure.get())
                n = float(self.moles.get())
                T = float(self.temperature.get())
                V = n * R * T / P
                result_text = f"体积 V = nRT/P = {n:.2f}×{R:.4f}×{T:.2f}/{P:.2f} = {V:.2f} L"
            elif self.volume.get() and self.moles.get() and self.temperature.get():
                V = float(self.volume.get())
                n = float(self.moles.get())
                T = float(self.temperature.get())
                P = n * R * T / V
                result_text = f"压力 P = nRT/V = {n:.2f}×{R:.4f}×{T:.2f}/{V:.2f} = {P:.2f} atm"
            else:
                result_text = "请输入至少三个变量"
        except:
            result_text = "输入错误"
        
        self.gas_result.delete(1.0, tk.END)
        self.gas_result.insert(tk.END, result_text)
    
    # ==================== 6. 热化学 ====================
    def show_thermochemistry(self):
        self.clear_content()
        self.update_status("热化学计算")
        
        tk.Label(self.content_frame, text="热化学计算", font=self.title_font, fg="blue").pack(pady=10)
        
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 热量计算
        heat_frame = tk.Frame(notebook)
        notebook.add(heat_frame, text="热量计算")
        tk.Label(heat_frame, text="质量 m (g):").grid(row=0, column=0, padx=5, pady=5)
        self.heat_mass = tk.Entry(heat_frame, width=15)
        self.heat_mass.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(heat_frame, text="比热容 c (J/g·K):").grid(row=1, column=0, padx=5, pady=5)
        self.heat_c = tk.Entry(heat_frame, width=15)
        self.heat_c.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(heat_frame, text="温度变化 ΔT (K):").grid(row=2, column=0, padx=5, pady=5)
        self.heat_dt = tk.Entry(heat_frame, width=15)
        self.heat_dt.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(heat_frame, text="计算热量", command=self.calc_heat, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        self.heat_result = tk.Text(heat_frame, height=5)
        self.heat_result.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        
        # 燃烧热
        combustion_frame = tk.Frame(notebook)
        notebook.add(combustion_frame, text="燃烧热")
        tk.Label(combustion_frame, text="燃烧热 ΔH (kJ/mol):").grid(row=0, column=0, padx=5, pady=5)
        self.dh_comb = tk.Entry(combustion_frame, width=15)
        self.dh_comb.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(combustion_frame, text="物质的量 n (mol):").grid(row=1, column=0, padx=5, pady=5)
        self.n_comb = tk.Entry(combustion_frame, width=15)
        self.n_comb.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(combustion_frame, text="计算放热", command=self.calc_combustion, bg="lightblue").grid(row=2, column=0, columnspan=2, pady=10)
        self.comb_result = tk.Text(combustion_frame, height=5)
        self.comb_result.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
    
    def calc_heat(self):
        try:
            m = float(self.heat_mass.get())
            c = float(self.heat_c.get())
            dt = float(self.heat_dt.get())
            q = m * c * dt
            self.heat_result.delete(1.0, tk.END)
            self.heat_result.insert(tk.END, f"Q = m·c·ΔT\nQ = {m} × {c} × {dt}\nQ = {q:.2f} J")
        except:
            self.heat_result.delete(1.0, tk.END)
            self.heat_result.insert(tk.END, "输入错误")
    
    def calc_combustion(self):
        try:
            dh = float(self.dh_comb.get())
            n = float(self.n_comb.get())
            q = dh * n
            self.comb_result.delete(1.0, tk.END)
            self.comb_result.insert(tk.END, f"Q = ΔH × n\nQ = {dh} × {n}\nQ = {q:.2f} kJ")
        except:
            self.comb_result.delete(1.0, tk.END)
            self.comb_result.insert(tk.END, "输入错误")
    
    # ==================== 7. 氧化还原 ====================
    def show_redox(self):
        self.clear_content()
        self.update_status("氧化还原反应")
        
        tk.Label(self.content_frame, text="氧化数计算", font=self.title_font, fg="blue").pack(pady=10)
        
        tk.Label(self.content_frame, text="输入化合物（如 H2O, Fe2O3）:").pack(pady=5)
        self.redox_formula = tk.Entry(self.content_frame, width=30, font=("Courier", 11))
        self.redox_formula.pack(pady=5)
        
        tk.Button(self.content_frame, text="计算氧化数", command=self.calc_oxidation, bg="lightblue").pack(pady=10)
        
        self.redox_result = tk.Text(self.content_frame, height=10, font=self.default_font)
        self.redox_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 常见氧化剂还原剂
        common_frame = tk.LabelFrame(self.content_frame, text="常见氧化剂/还原剂", font=self.title_font)
        common_frame.pack(fill=tk.X, padx=10, pady=10)
        text = "氧化剂: KMnO₄, K₂Cr₂O₇, H₂O₂, HNO₃, O₂\n还原剂: Fe²⁺, Zn, H₂, CO, SO₂"
        tk.Label(common_frame, text=text, font=self.default_font).pack(pady=5)
    
    def calc_oxidation(self):
        formula = self.redox_formula.get().strip()
        if not formula:
            return
        
        counts = ChemicalFormulaParser.parse_formula(formula)
        self.redox_result.delete(1.0, tk.END)
        self.redox_result.insert(tk.END, f"化合物: {formula}\n\n元素氧化数:\n")
        
        for element, count in counts.items():
            valence = ValenceData.get_valence(element)
            self.redox_result.insert(tk.END, f"{element}: {valence[0] if valence else 0} (常见)\n")
    
    # ==================== 8. 有机物 ====================
    def show_organic(self):
        self.clear_content()
        self.update_status("有机化学工具")
        
        tk.Label(self.content_frame, text="有机化合物信息", font=self.title_font, fg="blue").pack(pady=10)
        
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 官能团识别
        func_frame = tk.Frame(notebook)
        notebook.add(func_frame, text="官能团识别")
        tk.Label(func_frame, text="输入有机物名称:").pack(pady=5)
        self.org_name = tk.Entry(func_frame, width=40)
        self.org_name.pack(pady=5)
        tk.Button(func_frame, text="识别", command=self.identify_functional, bg="lightblue").pack(pady=5)
        self.func_result = tk.Text(func_frame, height=10)
        self.func_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 同分异构体
        isomer_frame = tk.Frame(notebook)
        notebook.add(isomer_frame, text="同分异构体")
        tk.Label(isomer_frame, text="分子式 (如 C5H12):").pack(pady=5)
        self.isomer_formula = tk.Entry(isomer_frame, width=20)
        self.isomer_formula.pack(pady=5)
        tk.Button(isomer_frame, text="计算异构体数", command=self.calc_isomers, bg="lightblue").pack(pady=5)
        self.isomer_result = tk.Text(isomer_frame, height=10)
        self.isomer_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def identify_functional(self):
        name = self.org_name.get().lower()
        self.func_result.delete(1.0, tk.END)
        
        functional_groups = {
            "醇": ["醇", "乙醇", "甲醇", "丙醇"],
            "醛": ["醛", "乙醛", "甲醛"],
            "酮": ["酮", "丙酮"],
            "羧酸": ["酸", "乙酸", "甲酸"],
            "酯": ["酯", "乙酸乙酯"],
            "醚": ["醚", "乙醚"],
            "胺": ["胺", "甲胺"],
            "烯烃": ["烯", "乙烯", "丙烯"],
            "炔烃": ["炔", "乙炔"],
            "芳香烃": ["苯", "甲苯", "二甲苯"]
        }
        
        found = []
        for group, keywords in functional_groups.items():
            for keyword in keywords:
                if keyword in name:
                    found.append(group)
                    break
        
        if found:
            self.func_result.insert(tk.END, f"化合物: {name}\n\n可能含有的官能团: {', '.join(set(found))}")
        else:
            self.func_result.insert(tk.END, "未识别出常见官能团")
    
    def calc_isomers(self):
        formula = self.isomer_formula.get().strip()
        self.isomer_result.delete(1.0, tk.END)
        
        isomers = {
            "C5H12": 3, "C6H14": 5, "C7H16": 9, "C8H18": 18,
            "C4H10": 2, "C3H8": 1, "C2H6": 1
        }
        
        if formula in isomers:
            self.isomer_result.insert(tk.END, f"分子式 {formula} 的同分异构体数目: {isomers[formula]} 种")
        else:
            self.isomer_result.insert(tk.END, "暂不支持该分子式\n常见烷烃异构体数:\nC₄H₁₀: 2, C₅H₁₂: 3, C₆H₁₄: 5, C₇H₁₆: 9")
    
    # ==================== 9. 溶解度 ====================
    def show_solubility(self):
        self.clear_content()
        self.update_status("溶解度查询")
        
        tk.Label(self.content_frame, text="物质溶解度查询", font=self.title_font, fg="blue").pack(pady=10)
        
        # 常见物质溶解度
        common = [
            ("NaCl", 36.0), ("KCl", 34.0), ("KNO3", 31.6), ("NH4Cl", 37.2),
            ("Ca(OH)2", 0.173), ("AgNO3", 216), ("CuSO4", 20.7), ("NaOH", 109)
        ]
        
        tree = ttk.Treeview(self.content_frame, columns=("物质", "溶解度"), show="headings", height=10)
        tree.heading("物质", text="物质")
        tree.heading("溶解度", text="溶解度 (g/100g水, 20°C)")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for substance, solubility in common:
            tree.insert("", tk.END, values=(substance, solubility))
        
        tk.Label(self.content_frame, text="溶解度规则:\n• 碱金属盐大多可溶\n• 硝酸盐全部可溶\n• 氯化物、溴化物、碘化物除Ag⁺、Pb²⁺外可溶\n• 硫酸盐除Ba²⁺、Pb²⁺、Ca²⁺外可溶\n• 碳酸盐、磷酸盐大多不溶",
                font=self.default_font, justify=tk.LEFT).pack(pady=10)
    
    # ==================== 10. 缓冲溶液 ====================
    def show_buffer(self):
        self.clear_content()
        self.update_status("缓冲溶液计算")
        
        tk.Label(self.content_frame, text="缓冲溶液 pH 计算 (Henderson-Hasselbalch方程)", font=self.title_font, fg="blue").pack(pady=10)
        
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="pKa:").grid(row=0, column=0, padx=5, pady=5)
        self.pka_entry = tk.Entry(input_frame, width=15)
        self.pka_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="[A⁻] (mol/L):").grid(row=1, column=0, padx=5, pady=5)
        self.base_conc = tk.Entry(input_frame, width=15)
        self.base_conc.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="[HA] (mol/L):").grid(row=2, column=0, padx=5, pady=5)
        self.acid_conc = tk.Entry(input_frame, width=15)
        self.acid_conc.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Button(input_frame, text="计算pH", command=self.calc_buffer_ph, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        
        self.buffer_result = tk.Text(self.content_frame, height=8, font=self.default_font)
        self.buffer_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_buffer_ph(self):
        try:
            pka = float(self.pka_entry.get())
            base = float(self.base_conc.get())
            acid = float(self.acid_conc.get())
            ph = pka + log10(base / acid)
            self.buffer_result.delete(1.0, tk.END)
            self.buffer_result.insert(tk.END, f"pH = pKa + log([A⁻]/[HA])\npH = {pka} + log({base}/{acid})\npH = {pka} + {log10(base/acid):.2f}\npH = {ph:.2f}")
        except:
            self.buffer_result.delete(1.0, tk.END)
            self.buffer_result.insert(tk.END, "输入错误")
    
    # ==================== 11. 滴定计算 ====================
    def show_titration(self):
        self.clear_content()
        self.update_status("酸碱滴定计算")
        
        tk.Label(self.content_frame, text="酸碱滴定计算", font=self.title_font, fg="blue").pack(pady=10)
        
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="酸浓度 (mol/L):").grid(row=0, column=0, padx=5, pady=5)
        self.acid_conc_tit = tk.Entry(input_frame, width=15)
        self.acid_conc_tit.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="酸体积 (L):").grid(row=1, column=0, padx=5, pady=5)
        self.acid_vol_tit = tk.Entry(input_frame, width=15)
        self.acid_vol_tit.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="碱浓度 (mol/L):").grid(row=2, column=0, padx=5, pady=5)
        self.base_conc_tit = tk.Entry(input_frame, width=15)
        self.base_conc_tit.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Button(input_frame, text="计算碱体积", command=self.calc_titration, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        
        self.titration_result = tk.Text(self.content_frame, height=8, font=self.default_font)
        self.titration_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_titration(self):
        try:
            ca = float(self.acid_conc_tit.get())
            va = float(self.acid_vol_tit.get())
            cb = float(self.base_conc_tit.get())
            vb = ca * va / cb
            self.titration_result.delete(1.0, tk.END)
            self.titration_result.insert(tk.END, f"CaVa = CbVb\n{ca} × {va} = {cb} × Vb\nVb = {vb:.4f} L = {vb*1000:.2f} mL")
        except:
            self.titration_result.delete(1.0, tk.END)
            self.titration_result.insert(tk.END, "输入错误")
    
    # ==================== 12. 光谱分析 ====================
    def show_spectroscopy(self):
        self.clear_content()
        self.update_status("光谱分析")
        
        tk.Label(self.content_frame, text="光谱分析工具", font=self.title_font, fg="blue").pack(pady=10)
        
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 波长能量转换
        wave_frame = tk.Frame(notebook)
        notebook.add(wave_frame, text="波长-能量转换")
        tk.Label(wave_frame, text="波长 λ (nm):").pack(pady=5)
        self.wavelength = tk.Entry(wave_frame, width=20)
        self.wavelength.pack(pady=5)
        tk.Button(wave_frame, text="转换", command=self.convert_wavelength, bg="lightblue").pack(pady=5)
        self.wave_result = tk.Text(wave_frame, height=5)
        self.wave_result.pack(pady=10)
        
        # 常见颜色
        color_frame = tk.Frame(notebook)
        notebook.add(color_frame, text="颜色与波长")
        colors = [
            ("紫", "400-450"), ("蓝", "450-500"), ("青", "500-550"),
            ("绿", "550-580"), ("黄", "580-600"), ("橙", "600-650"), ("红", "650-750")
        ]
        for color, wavelength in colors:
            tk.Label(color_frame, text=f"{color}: {wavelength} nm", font=self.default_font).pack(pady=2)
    
    def convert_wavelength(self):
        try:
            lam = float(self.wavelength.get()) * 1e-9  # 转换为米
            c = 3e8
            h = 6.626e-34
            energy = h * c / lam
            self.wave_result.delete(1.0, tk.END)
            self.wave_result.insert(tk.END, f"波长: {self.wavelength.get()} nm\n能量: {energy:.2e} J\n能量: {energy/1.602e-19:.2f} eV")
        except:
            self.wave_result.delete(1.0, tk.END)
            self.wave_result.insert(tk.END, "输入错误")
    
    # ==================== 13. 化学动力学 ====================
    def show_kinetics(self):
        self.clear_content()
        self.update_status("化学动力学")
        
        tk.Label(self.content_frame, text="阿伦尼乌斯方程", font=self.title_font, fg="blue").pack(pady=10)
        
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="活化能 Ea (J/mol):").grid(row=0, column=0, padx=5, pady=5)
        self.ea_entry = tk.Entry(input_frame, width=15)
        self.ea_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="温度 T (K):").grid(row=1, column=0, padx=5, pady=5)
        self.temp_kin = tk.Entry(input_frame, width=15)
        self.temp_kin.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="指前因子 A:").grid(row=2, column=0, padx=5, pady=5)
        self.a_factor = tk.Entry(input_frame, width=15)
        self.a_factor.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Button(input_frame, text="计算速率常数", command=self.calc_rate_constant, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        
        self.kinetics_result = tk.Text(self.content_frame, height=8, font=self.default_font)
        self.kinetics_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 半衰期计算
        half_frame = tk.LabelFrame(self.content_frame, text="半衰期计算", font=self.title_font)
        half_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(half_frame, text="速率常数 k (s⁻¹):").pack(side=tk.LEFT, padx=5)
        self.k_half = tk.Entry(half_frame, width=15)
        self.k_half.pack(side=tk.LEFT, padx=5)
        tk.Button(half_frame, text="计算半衰期", command=self.calc_half_life, bg="lightblue").pack(side=tk.LEFT, padx=5)
        self.half_result = tk.Label(half_frame, text="", font=self.default_font)
        self.half_result.pack(side=tk.LEFT, padx=10)
    
    def calc_rate_constant(self):
        try:
            ea = float(self.ea_entry.get())
            t = float(self.temp_kin.get())
            a = float(self.a_factor.get())
            r = 8.314
            k = a * np.exp(-ea / (r * t))
            self.kinetics_result.delete(1.0, tk.END)
            self.kinetics_result.insert(tk.END, f"k = A·exp(-Ea/RT)\nk = {a:.2e} × exp(-{ea:.2e}/{r:.3f}×{t:.2f})\nk = {k:.2e} s⁻¹")
        except:
            self.kinetics_result.delete(1.0, tk.END)
            self.kinetics_result.insert(tk.END, "输入错误")
    
    def calc_half_life(self):
        try:
            k = float(self.k_half.get())
            t_half = np.log(2) / k
            self.half_result.config(text=f"t₁/₂ = {t_half:.2f} s")
        except:
            self.half_result.config(text="输入错误")
    
    # ==================== 辅助功能 ====================
    def export_result(self):
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("化学工具箱 v1.0 计算结果\n")
                    f.write(f"导出时间: {datetime.datetime.now()}\n\n")
                    f.write("请从界面复制具体计算结果\n")
                messagebox.showinfo("成功", f"结果已保存到 {filename}")
        except:
            messagebox.showerror("错误", "保存失败")
    
    def show_unit_converter(self):
        messagebox.showinfo("单位换算", "常用换算:\n1 mol/L = 1000 mmol/L\n1 atm = 101.325 kPa\n1 cal = 4.184 J\n0°C = 273.15 K")
    
    def show_lab_notebook(self):
        self.clear_content()
        self.update_status("实验记录本")
        
        tk.Label(self.content_frame, text="实验记录本", font=self.title_font, fg="blue").pack(pady=10)
        
        text_area = scrolledtext.ScrolledText(self.content_frame, height=20, font=self.default_font)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_area.insert(tk.END, f"实验日期: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        btn_frame = tk.Frame(self.content_frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="保存记录", command=lambda: self.save_notebook(text_area.get(1.0, tk.END)), bg="lightblue").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="清空", command=lambda: text_area.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
    
    def save_notebook(self, content):
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件", "*.txt")])
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", "实验记录已保存")
        except:
            messagebox.showerror("错误", "保存失败")
    
    def show_tutorial(self):
        tutorial = """化学工具箱 v1.0 使用教程

主要功能按钮：
1. 配平 - 化学方程式配平（支持离子方程式）
2. 元素周期表 - 118种元素查询
3. 计算 - 摩尔质量、浓度、稀释、比例求解
4. 实用功能 - 包含10个专业化学工具

实用功能列表：
- pH计算器：强酸强碱、弱酸弱碱的pH计算
- 气体定律：理想气体状态方程PV=nRT
- 热化学计算：热量计算、燃烧热
- 氧化还原分析：氧化数计算
- 有机化学工具：官能团识别、同分异构体
- 溶解度查询：常见物质溶解度
- 缓冲溶液计算：Henderson-Hasselbalch方程
- 酸碱滴定计算：滴定终点体积
- 光谱分析：波长-能量转换
- 化学动力学：阿伦尼乌斯方程、半衰期

离子方程式格式：
- 负离子：MnO4** (两个星号表示-2价)
- 正离子：Fe** (两个星号表示+2价)

快捷键：
- 回车键：执行当前功能计算
- Ctrl+E：导出结果

注意事项：
- 氯的相对原子质量为35.5
- 温度使用开尔文(K)单位
- 浓度单位使用mol/L"""
        
        messagebox.showinfo("使用教程", tutorial)
    
    def show_about(self):
        about = """化学工具箱 v1.0

完整功能列表：
1. 化学方程式配平（支持离子方程式）
2. 元素周期表（118种元素）
3. 计算功能（摩尔质量、浓度、稀释、比例求解）
4. pH计算（强酸强碱、弱酸弱碱）
5. 气体定律（理想气体状态方程）
6. 热化学（热量计算、燃烧热）
7. 氧化还原（氧化数计算）
8. 有机化学（官能团识别、同分异构体）
9. 溶解度查询
10. 缓冲溶液计算
11. 酸碱滴定计算
12. 光谱分析（波长-能量转换）
13. 化学动力学（阿伦尼乌斯方程）
14. 单位换算
15. 实验记录本

开发者: 化学爱好者
版本日期: 2025年3月28日
开源协议: MIT License

感谢使用！"""
        
        messagebox.showinfo("关于", about)
    
    def show_help(self):
        help_text = """化学工具箱 v1.0 帮助

快速入门：
1. 点击顶部按钮选择功能
2. 在输入框中输入数据
3. 点击"计算"或"确定"按钮

离子方程式格式：
- 负离子：MnO4** (两个星号表示-2价)
- 正离子：Fe** (两个星号表示+2价)

常用快捷键：
- 回车键：执行当前功能计算
- Ctrl+E：导出结果

注意事项：
- 氯的相对原子质量为35.5
- 温度使用开尔文(K)单位
- 浓度单位使用mol/L

比例求解功能：
- 支持两种格式：a/b = c/x 或 a/b = x/d
- 自动显示计算过程和结果

技术支持：请查看"使用教程"获取详细信息"""
        
        messagebox.showinfo("帮助", help_text)

# ==================== 程序入口 ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = ChemistryToolbox(root)
    root.mainloop()