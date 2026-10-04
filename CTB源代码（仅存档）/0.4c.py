import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import re
from collections import defaultdict
import numpy as np
from math import gcd

# ==================== 化合价数据 ====================
class ValenceData:
    """化合价数据库"""
    
    # 常见元素的常见化合价
    element_valences = {
        # 第1族
        'H': [1, -1], 'Li': [1], 'Na': [1], 'K': [1], 'Rb': [1], 'Cs': [1], 'Fr': [1],
        # 第2族
        'Be': [2], 'Mg': [2], 'Ca': [2], 'Sr': [2], 'Ba': [2], 'Ra': [2],
        # 第13族
        'B': [3], 'Al': [3], 'Ga': [3], 'In': [3], 'Tl': [1, 3],
        # 第14族
        'C': [4, 2, -4], 'Si': [4], 'Ge': [4, 2], 'Sn': [2, 4], 'Pb': [2, 4],
        # 第15族
        'N': [5, 3, 1, 2, 4, -3], 'P': [5, 3, -3], 'As': [5, 3, -3], 
        'Sb': [5, 3], 'Bi': [3, 5],
        # 第16族
        'O': [-2, -1], 'S': [6, 4, 2, -2], 'Se': [6, 4, -2], 'Te': [6, 4, -2], 'Po': [4, 2],
        # 第17族
        'F': [-1], 'Cl': [7, 5, 3, 1, -1], 'Br': [7, 5, 3, 1, -1], 'I': [7, 5, 3, 1, -1], 'At': [-1],
        # 第18族
        'He': [0], 'Ne': [0], 'Ar': [0], 'Kr': [0], 'Xe': [0], 'Rn': [0],
        # 过渡金属
        'Sc': [3], 'Ti': [4, 3], 'V': [5, 4, 3, 2], 'Cr': [6, 3, 2], 
        'Mn': [7, 6, 4, 3, 2], 'Fe': [3, 2], 'Co': [3, 2], 'Ni': [2, 3],
        'Cu': [2, 1], 'Zn': [2], 'Ag': [1], 'Au': [3, 1], 'Hg': [2, 1],
        'Cd': [2], 'Pt': [4, 2], 'Pd': [2, 4], 'Ir': [4, 3], 'Os': [4, 3],
        'Rh': [3], 'Ru': [3], 'Nb': [5], 'Mo': [6, 5, 4, 3], 'Tc': [7],
        'Re': [7, 6, 4], 'W': [6], 'Ta': [5], 'Zr': [4], 'Hf': [4],
    }
    
    @classmethod
    def get_valence(cls, element, compound_context=None):
        """获取元素的常见化合价"""
        if element in cls.element_valences:
            return cls.element_valences[element]
        return [0]

# ==================== 相对原子质量数据 ====================
class AtomicMass:
    """相对原子质量数据库"""
    
    atomic_masses = {
        'H': 1, 'He': 4, 'Li': 7, 'Be': 9, 'B': 11, 'C': 12, 'N': 14, 'O': 16, 'F': 19, 'Ne': 20,
        'Na': 23, 'Mg': 24, 'Al': 27, 'Si': 28, 'P': 31, 'S': 32, 'Cl': 35.5, 'Ar': 40,
        'K': 39, 'Ca': 40, 'Sc': 45, 'Ti': 48, 'V': 51, 'Cr': 52, 'Mn': 55, 'Fe': 56,
        'Co': 59, 'Ni': 59, 'Cu': 64, 'Zn': 65, 'Ga': 70, 'Ge': 73, 'As': 75, 'Se': 79,
        'Br': 80, 'Kr': 84, 'Rb': 85, 'Sr': 88, 'Y': 89, 'Zr': 91, 'Nb': 93, 'Mo': 96,
        'Tc': 98, 'Ru': 101, 'Rh': 103, 'Pd': 106, 'Ag': 108, 'Cd': 112, 'In': 115,
        'Sn': 119, 'Sb': 122, 'Te': 128, 'I': 127, 'Xe': 131, 'Cs': 133, 'Ba': 137,
        'La': 139, 'Ce': 140, 'Pr': 141, 'Nd': 144, 'Pm': 145, 'Sm': 150, 'Eu': 152,
        'Gd': 157, 'Tb': 159, 'Dy': 163, 'Ho': 165, 'Er': 167, 'Tm': 169, 'Yb': 173,
        'Lu': 175, 'Hf': 179, 'Ta': 181, 'W': 184, 'Re': 186, 'Os': 190, 'Ir': 192,
        'Pt': 195, 'Au': 197, 'Hg': 201, 'Tl': 204, 'Pb': 207, 'Bi': 209, 'Po': 209,
        'At': 210, 'Rn': 222, 'Fr': 223, 'Ra': 226, 'Ac': 227, 'Th': 232, 'Pa': 231,
        'U': 238, 'Np': 237, 'Pu': 244, 'Am': 243, 'Cm': 247, 'Bk': 247, 'Cf': 251,
        'Es': 252, 'Fm': 257, 'Md': 258, 'No': 259, 'Lr': 262, 'Rf': 267, 'Db': 268,
        'Sg': 269, 'Bh': 270, 'Hs': 269, 'Mt': 278, 'Ds': 281, 'Rg': 282, 'Cn': 285,
        'Nh': 286, 'Fl': 289, 'Mc': 290, 'Lv': 293, 'Ts': 294, 'Og': 294,
    }
    
    @classmethod
    def get_mass(cls, element):
        return cls.atomic_masses.get(element, 0)

# ==================== 完整元素周期表数据 ====================
class PeriodicTableData:
    """完整的元素周期表数据"""
    
    # 所有元素数据（原子序数，符号，名称，周期，族）
    elements = [
        # 周期1
        (1, "H", "氢", 1, 1), (2, "He", "氦", 1, 18),
        # 周期2
        (3, "Li", "锂", 2, 1), (4, "Be", "铍", 2, 2), (5, "B", "硼", 2, 13), (6, "C", "碳", 2, 14),
        (7, "N", "氮", 2, 15), (8, "O", "氧", 2, 16), (9, "F", "氟", 2, 17), (10, "Ne", "氖", 2, 18),
        # 周期3
        (11, "Na", "钠", 3, 1), (12, "Mg", "镁", 3, 2), (13, "Al", "铝", 3, 13), (14, "Si", "硅", 3, 14),
        (15, "P", "磷", 3, 15), (16, "S", "硫", 3, 16), (17, "Cl", "氯", 3, 17), (18, "Ar", "氩", 3, 18),
        # 周期4
        (19, "K", "钾", 4, 1), (20, "Ca", "钙", 4, 2), (21, "Sc", "钪", 4, 3), (22, "Ti", "钛", 4, 4),
        (23, "V", "钒", 4, 5), (24, "Cr", "铬", 4, 6), (25, "Mn", "锰", 4, 7), (26, "Fe", "铁", 4, 8),
        (27, "Co", "钴", 4, 9), (28, "Ni", "镍", 4, 10), (29, "Cu", "铜", 4, 11), (30, "Zn", "锌", 4, 12),
        (31, "Ga", "镓", 4, 13), (32, "Ge", "锗", 4, 14), (33, "As", "砷", 4, 15), (34, "Se", "硒", 4, 16),
        (35, "Br", "溴", 4, 17), (36, "Kr", "氪", 4, 18),
        # 周期5
        (37, "Rb", "铷", 5, 1), (38, "Sr", "锶", 5, 2), (39, "Y", "钇", 5, 3), (40, "Zr", "锆", 5, 4),
        (41, "Nb", "铌", 5, 5), (42, "Mo", "钼", 5, 6), (43, "Tc", "锝", 5, 7), (44, "Ru", "钌", 5, 8),
        (45, "Rh", "铑", 5, 9), (46, "Pd", "钯", 5, 10), (47, "Ag", "银", 5, 11), (48, "Cd", "镉", 5, 12),
        (49, "In", "铟", 5, 13), (50, "Sn", "锡", 5, 14), (51, "Sb", "锑", 5, 15), (52, "Te", "碲", 5, 16),
        (53, "I", "碘", 5, 17), (54, "Xe", "氙", 5, 18),
        # 周期6
        (55, "Cs", "铯", 6, 1), (56, "Ba", "钡", 6, 2), 
        (57, "La", "镧", 6, 3), (58, "Ce", "铈", 6, 3), (59, "Pr", "镨", 6, 3), (60, "Nd", "钕", 6, 3),
        (61, "Pm", "钷", 6, 3), (62, "Sm", "钐", 6, 3), (63, "Eu", "铕", 6, 3), (64, "Gd", "钆", 6, 3),
        (65, "Tb", "铽", 6, 3), (66, "Dy", "镝", 6, 3), (67, "Ho", "钬", 6, 3), (68, "Er", "铒", 6, 3),
        (69, "Tm", "铥", 6, 3), (70, "Yb", "镱", 6, 3), (71, "Lu", "镥", 6, 3),
        (72, "Hf", "铪", 6, 4), (73, "Ta", "钽", 6, 5), (74, "W", "钨", 6, 6), (75, "Re", "铼", 6, 7),
        (76, "Os", "锇", 6, 8), (77, "Ir", "铱", 6, 9), (78, "Pt", "铂", 6, 10), (79, "Au", "金", 6, 11),
        (80, "Hg", "汞", 6, 12), (81, "Tl", "铊", 6, 13), (82, "Pb", "铅", 6, 14), (83, "Bi", "铋", 6, 15),
        (84, "Po", "钋", 6, 16), (85, "At", "砹", 6, 17), (86, "Rn", "氡", 6, 18),
        # 周期7
        (87, "Fr", "钫", 7, 1), (88, "Ra", "镭", 7, 2),
        (89, "Ac", "锕", 7, 3), (90, "Th", "钍", 7, 3), (91, "Pa", "镤", 7, 3), (92, "U", "铀", 7, 3),
        (93, "Np", "镎", 7, 3), (94, "Pu", "钚", 7, 3), (95, "Am", "镅", 7, 3), (96, "Cm", "锔", 7, 3),
        (97, "Bk", "锫", 7, 3), (98, "Cf", "锎", 7, 3), (99, "Es", "锿", 7, 3), (100, "Fm", "镄", 7, 3),
        (101, "Md", "钔", 7, 3), (102, "No", "锘", 7, 3), (103, "Lr", "铹", 7, 3),
        (104, "Rf", "𬬻", 7, 4), (105, "Db", "𬭊", 7, 5), (106, "Sg", "𬭳", 7, 6), (107, "Bh", "𬭛", 7, 7),
        (108, "Hs", "𬭶", 7, 8), (109, "Mt", "鿏", 7, 9), (110, "Ds", "𫟼", 7, 10), (111, "Rg", "𬬭", 7, 11),
        (112, "Cn", "鎶", 7, 12), (113, "Nh", "鉨", 7, 13), (114, "Fl", "𫓧", 7, 14), (115, "Mc", "镆", 7, 15),
        (116, "Lv", "𫟷", 7, 16), (117, "Ts", "鿬", 7, 17), (118, "Og", "气奥", 7, 18),
    ]
    
    # 创建符号到数据的映射
    element_map = {}
    for atomic, symbol, name, period, group in elements:
        element_map[symbol] = {
            "atomic": atomic, "name": name, "period": period, "group": group,
            "mass": AtomicMass.get_mass(symbol),
            "config": get_electron_config(symbol, atomic),
            "desc": get_element_description(symbol)
        }
    
    @classmethod
    def get_element(cls, symbol):
        return cls.element_map.get(symbol)

def get_electron_config(symbol, atomic):
    """获取电子排布简写"""
    configs = {
        'H': "1s¹", 'He': "1s²", 'Li': "[He] 2s¹", 'Be': "[He] 2s²", 'B': "[He] 2s² 2p¹",
        'C': "[He] 2s² 2p²", 'N': "[He] 2s² 2p³", 'O': "[He] 2s² 2p⁴", 'F': "[He] 2s² 2p⁵",
        'Ne': "[He] 2s² 2p⁶", 'Na': "[Ne] 3s¹", 'Mg': "[Ne] 3s²", 'Al': "[Ne] 3s² 3p¹",
        'Si': "[Ne] 3s² 3p²", 'P': "[Ne] 3s² 3p³", 'S': "[Ne] 3s² 3p⁴", 'Cl': "[Ne] 3s² 3p⁵",
        'Ar': "[Ne] 3s² 3p⁶", 'K': "[Ar] 4s¹", 'Ca': "[Ar] 4s²", 'Fe': "[Ar] 3d⁶ 4s²",
        'Cu': "[Ar] 3d¹⁰ 4s¹", 'Zn': "[Ar] 3d¹⁰ 4s²", 'Ag': "[Kr] 4d¹⁰ 5s¹", 'Au': "[Xe] 4f¹⁴ 5d¹⁰ 6s¹",
        'Hg': "[Xe] 4f¹⁴ 5d¹⁰ 6s²", 'Pb': "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p²", 'U': "[Rn] 5f³ 6d¹ 7s²",
    }
    return configs.get(symbol, "未知")

def get_element_description(symbol):
    """获取元素描述"""
    descs = {
        'H': "最轻的元素，宇宙中含量最丰富", 'He': "稀有气体，沸点最低",
        'Li': "最轻的金属，用于电池", 'Be': "轻金属，有毒", 'B': "类金属，用于半导体",
        'C': "生命的基础，有机化合物骨架", 'N': "大气主要成分", 'O': "支持燃烧，生命必需",
        'F': "最活泼的非金属", 'Ne': "稀有气体，用于霓虹灯", 'Na': "碱金属，活泼",
        'Mg': "轻金属，合金", 'Al': "地壳中含量最丰富的金属", 'Si': "半导体材料",
        'P': "白磷易燃", 'S': "黄色固体", 'Cl': "黄绿色气体，消毒", 'Ar': "稀有气体",
        'K': "活泼金属", 'Ca': "骨骼主要成分", 'Fe': "最常用的金属", 'Cu': "导电性好",
        'Zn': "防腐镀层", 'Ag': "贵金属，导电性最佳", 'Au': "延展性好，不氧化",
        'Hg': "唯一液态金属", 'Pb': "重金属，有毒", 'U': "核燃料，放射性",
    }
    return descs.get(symbol, "常见元素")

# ==================== 化学式解析器 ====================
class ChemicalFormulaParser:
    """化学式解析器"""
    
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
    """化学方程式配平器"""
    
    @staticmethod
    def parse_compound_with_charge(compound):
        charge_pattern = r'(\*+)$'
        charge_match = re.search(charge_pattern, compound)
        if charge_match:
            stars = charge_match.group(1)
            charge = -len(stars)
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
                
                if n_unknowns > 1:
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
                        
                        if valid:
                            error = sum(abs(A @ coeffs[:n_unknowns] - b))
                            if error < best_error:
                                best_error = error
                                best_solution = int_coeffs
                    except:
                        continue
            
            if best_solution and best_error < 1e-5:
                g = best_solution[0]
                for c in best_solution[1:]:
                    g = gcd(g, c)
                if g > 1:
                    best_solution = [c // g for c in best_solution]
                
                left_parts = []
                for i, (formula, charge) in enumerate(left_compounds):
                    coeff = best_solution[i] if i < len(best_solution) else 1
                    formatted = f"{coeff if coeff > 1 else ''}{formula}"
                    if charge != 0:
                        formatted += '*' * abs(charge)
                    left_parts.append(formatted)
                
                right_parts = []
                for i, (formula, charge) in enumerate(right_compounds):
                    coeff = best_solution[n_left + i] if (n_left + i) < len(best_solution) else 1
                    formatted = f"{coeff if coeff > 1 else ''}{formula}"
                    if charge != 0:
                        formatted += '*' * abs(charge)
                    right_parts.append(formatted)
                
                return f"{'+'.join(left_parts)} = {'+'.join(right_parts)}", {}
            
            return "错误：无法配平该方程式", {}
        except Exception as e:
            return f"配平失败: {str(e)}", {}

# ==================== 主应用程序 ====================
class ChemistryToolboxV4:
    def __init__(self, root):
        self.root = root
        self.root.title("化学工具箱 v0.4")
        self.root.geometry("1100x750")
        
        self.default_font = ("Microsoft YaHei", 10)
        self.title_font = ("Microsoft YaHei", 12, "bold")
        
        # 顶部按钮
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.btn_balance = tk.Button(self.button_frame, text="配平", width=10,
                                      font=self.title_font, command=self.show_balance)
        self.btn_balance.pack(side=tk.LEFT, padx=5)
        
        self.btn_periodic = tk.Button(self.button_frame, text="元素周期表", width=12,
                                       font=self.title_font, command=self.show_periodic)
        self.btn_periodic.pack(side=tk.LEFT, padx=5)
        
        self.btn_calc = tk.Menubutton(self.button_frame, text="计算", width=8,
                                       font=self.title_font, relief=tk.RAISED)
        self.btn_calc.pack(side=tk.LEFT, padx=5)
        self.calc_menu = tk.Menu(self.btn_calc, tearoff=0)
        self.btn_calc.config(menu=self.calc_menu)
        self.calc_menu.add_command(label="化学式量计算", command=self.show_molar_mass)
        self.calc_menu.add_command(label="浓度计算", command=self.show_concentration)
        
        self.btn_about = tk.Button(self.button_frame, text="关于", width=8,
                                    font=self.title_font, command=self.show_about)
        self.btn_about.pack(side=tk.LEFT, padx=5)
        
        self.btn_help = tk.Button(self.button_frame, text="帮助", width=8,
                                   font=self.title_font, command=self.show_help)
        self.btn_help.pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        self.status_label = tk.Label(root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 内容区域
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.show_balance()
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_status(self, msg):
        self.status_label.config(text=msg)
        self.root.update()
    
    def format_subscript(self, text):
        sub_map = {'0':'₀','1':'₁','2':'₂','3':'₃','4':'₄','5':'₅','6':'₆','7':'₇','8':'₈','9':'₉'}
        result = ""
        i = 0
        while i < len(text):
            if text[i].isdigit():
                num_start = i
                while i < len(text) and text[i].isdigit():
                    i += 1
                for d in text[num_start:i]:
                    result += sub_map.get(d, d)
            else:
                result += text[i]
                i += 1
        return result
    
    # ==================== 配平界面 ====================
    def show_balance(self):
        self.clear_content()
        self.update_status("配平模式 - 离子用星号标注（如 MnO4** 表示 MnO₄⁻）")
        
        tk.Label(self.content_frame, text="化学方程式配平", font=self.title_font, fg="blue").pack(pady=10)
        
        info_frame = tk.Frame(self.content_frame)
        info_frame.pack(pady=5)
        tk.Label(info_frame, text="支持格式: H2+O2=H2O | Fe2O3+CO=Fe+CO2 | MnO4**+Fe**=Mn**+Fe**", 
                font=self.default_font, fg="green").pack()
        
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(pady=15)
        tk.Label(input_frame, text="方程式:").pack(side=tk.LEFT)
        self.equation_entry = tk.Entry(input_frame, width=60, font=("Courier", 11))
        self.equation_entry.pack(side=tk.LEFT, padx=10)
        self.equation_entry.bind('<Return>', lambda e: self.do_balance())
        
        tk.Button(input_frame, text="配平", command=self.do_balance, bg="lightblue", width=8).pack(side=tk.LEFT)
        
        result_frame = tk.LabelFrame(self.content_frame, text="配平结果", font=self.title_font)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_text = tk.Text(result_frame, height=12, font=("Courier", 11), wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.result_text.tag_configure("blue", foreground="blue", font=("Courier", 11, "bold"))
        
        example_frame = tk.Frame(self.content_frame)
        example_frame.pack(pady=5)
        tk.Label(example_frame, text="示例:").pack(side=tk.LEFT)
        for eq, desc in [("H2+O2=H2O", "氢气燃烧"), ("Fe2O3+CO=Fe+CO2", "炼铁"), 
                         ("Cu+AgNO3=Cu(NO3)2+Ag", "置换"), ("MnO4**+Fe**=Mn**+Fe**", "离子")]:
            tk.Button(example_frame, text=desc, command=lambda e=eq: self.load_example(e),
                     font=self.default_font).pack(side=tk.LEFT, padx=5)
    
    def load_example(self, eq):
        self.equation_entry.delete(0, tk.END)
        self.equation_entry.insert(0, eq)
        self.do_balance()
    
    def do_balance(self):
        eq = self.equation_entry.get().strip()
        if not eq:
            messagebox.showwarning("警告", "请输入方程式")
            return
        self.update_status("配平中...")
        result, _ = EquationBalancer.balance(eq)
        self.result_text.delete(1.0, tk.END)
        if result.startswith("错误"):
            self.result_text.insert(tk.END, result)
        else:
            self.result_text.insert(tk.END, "配平结果:\n\n", "blue")
            left, right = result.split(" = ")
            for part in left.split('+'):
                m = re.match(r'^(\d+)?(.*)$', part)
                if m and m.group(1):
                    self.result_text.insert(tk.END, m.group(1), "blue")
                    self.result_text.insert(tk.END, self.format_subscript(m.group(2)))
                else:
                    self.result_text.insert(tk.END, self.format_subscript(part))
                self.result_text.insert(tk.END, " + ")
            self.result_text.insert(tk.END, " = ")
            for part in right.split('+'):
                m = re.match(r'^(\d+)?(.*)$', part)
                if m and m.group(1):
                    self.result_text.insert(tk.END, m.group(1), "blue")
                    self.result_text.insert(tk.END, self.format_subscript(m.group(2)))
                else:
                    self.result_text.insert(tk.END, self.format_subscript(part))
                self.result_text.insert(tk.END, " + ")
        self.update_status("配平完成")
    
    # ==================== 元素周期表 ====================
    def show_periodic(self):
        self.clear_content()
        self.update_status("元素周期表 - 点击元素查看详细信息（共118种元素）")
        
        canvas = tk.Canvas(self.content_frame)
        scrollbar = tk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建周期表网格（18列）
        # 定义每个周期有哪些元素（按列位置）
        periodic_layout = {
            1: {1: "H", 18: "He"},
            2: {1: "Li", 2: "Be", 13: "B", 14: "C", 15: "N", 16: "O", 17: "F", 18: "Ne"},
            3: {1: "Na", 2: "Mg", 13: "Al", 14: "Si", 15: "P", 16: "S", 17: "Cl", 18: "Ar"},
            4: {1: "K", 2: "Ca", 3: "Sc", 4: "Ti", 5: "V", 6: "Cr", 7: "Mn", 8: "Fe", 9: "Co", 10: "Ni",
                11: "Cu", 12: "Zn", 13: "Ga", 14: "Ge", 15: "As", 16: "Se", 17: "Br", 18: "Kr"},
            5: {1: "Rb", 2: "Sr", 3: "Y", 4: "Zr", 5: "Nb", 6: "Mo", 7: "Tc", 8: "Ru", 9: "Rh", 10: "Pd",
                11: "Ag", 12: "Cd", 13: "In", 14: "Sn", 15: "Sb", 16: "Te", 17: "I", 18: "Xe"},
            6: {1: "Cs", 2: "Ba", 3: "La", 4: "Hf", 5: "Ta", 6: "W", 7: "Re", 8: "Os", 9: "Ir", 10: "Pt",
                11: "Au", 12: "Hg", 13: "Tl", 14: "Pb", 15: "Bi", 16: "Po", 17: "At", 18: "Rn"},
            7: {1: "Fr", 2: "Ra", 3: "Ac", 4: "Rf", 5: "Db", 6: "Sg", 7: "Bh", 8: "Hs", 9: "Mt", 10: "Ds",
                11: "Rg", 12: "Cn", 13: "Nh", 14: "Fl", 15: "Mc", 16: "Lv", 17: "Ts", 18: "Og"},
        }
        
        # 镧系和锕系元素
        lanthanides = ["La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"]
        actinides = ["Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr"]
        
        # 颜色方案
        def get_color(group):
            if group == 1: return "#ffcccc"      # 碱金属
            if group == 2: return "#ccffcc"      # 碱土金属
            if 3 <= group <= 12: return "#ccccff" # 过渡金属
            if 13 <= group <= 16: return "#ffffcc" # 非金属
            if group == 17: return "#ffcc99"     # 卤素
            if group == 18: return "#99ccff"     # 稀有气体
            return "#f0f0f0"
        
        # 创建周期表
        for period in range(1, 8):
            row_elements = periodic_layout.get(period, {})
            for col in range(1, 19):
                symbol = row_elements.get(col)
                if symbol:
                    data = PeriodicTableData.get_element(symbol)
                    if data:
                        color = get_color(data["group"])
                        btn = tk.Button(scroll_frame, 
                                       text=f"{symbol}\n{data['atomic']}", 
                                       width=6, height=3,
                                       bg=color,
                                       font=("Microsoft YaHei", 9),
                                       command=lambda s=symbol: self.show_element_info(s))
                        btn.grid(row=period-1, column=col-1, padx=1, pady=1)
                else:
                    # 空白占位
                    tk.Label(scroll_frame, width=6, height=3, bg="white").grid(row=period-1, column=col-1, padx=1, pady=1)
        
        # 添加镧系
        lanthanide_frame = tk.Frame(scroll_frame)
        lanthanide_frame.grid(row=7, column=0, columnspan=18, pady=5, sticky=tk.W)
        tk.Label(lanthanide_frame, text="镧系:", font=self.default_font).pack(side=tk.LEFT, padx=5)
        for symbol in lanthanides:
            data = PeriodicTableData.get_element(symbol)
            if data:
                btn = tk.Button(lanthanide_frame, text=symbol, width=4, height=1,
                               bg="#ffffcc", font=("Microsoft YaHei", 8),
                               command=lambda s=symbol: self.show_element_info(s))
                btn.pack(side=tk.LEFT, padx=1)
        
        # 添加锕系
        actinide_frame = tk.Frame(scroll_frame)
        actinide_frame.grid(row=8, column=0, columnspan=18, pady=5, sticky=tk.W)
        tk.Label(actinide_frame, text="锕系:", font=self.default_font).pack(side=tk.LEFT, padx=5)
        for symbol in actinides:
            data = PeriodicTableData.get_element(symbol)
            if data:
                btn = tk.Button(actinide_frame, text=symbol, width=4, height=1,
                               bg="#ffcc99", font=("Microsoft YaHei", 8),
                               command=lambda s=symbol: self.show_element_info(s))
                btn.pack(side=tk.LEFT, padx=1)
        
        # 图例
        legend_frame = tk.Frame(scroll_frame)
        legend_frame.grid(row=9, column=0, columnspan=18, pady=10)
        legends = [("碱金属", "#ffcccc"), ("碱土金属", "#ccffcc"), ("过渡金属", "#ccccff"),
                   ("非金属", "#ffffcc"), ("卤素", "#ffcc99"), ("稀有气体", "#99ccff")]
        for text, color in legends:
            f = tk.Frame(legend_frame)
            f.pack(side=tk.LEFT, padx=10)
            tk.Label(f, text="  ", bg=color, width=2).pack(side=tk.LEFT)
            tk.Label(f, text=text, font=self.default_font).pack(side=tk.LEFT)
    
    def show_element_info(self, symbol):
        data = PeriodicTableData.get_element(symbol)
        if data:
            info = f"元素符号: {symbol}\n"
            info += f"中文名称: {data['name']}\n"
            info += f"原子序数: {data['atomic']}\n"
            info += f"原子量: {data['mass']}\n"
            info += f"族: {data['group']}\n"
            info += f"周期: {data['period']}\n"
            info += f"电子排布: {data['config']}\n"
            info += f"简介: {data['desc']}\n"
            messagebox.showinfo(f"元素信息 - {symbol}", info)
    
    # ==================== 化学式量计算 ====================
    def show_molar_mass(self):
        self.clear_content()
        self.update_status("化学式量计算")
        
        tk.Label(self.content_frame, text="化学式量计算", font=self.title_font, fg="blue").pack(pady=10)
        
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(pady=20)
        tk.Label(input_frame, text="化学式:").pack(side=tk.LEFT)
        self.molar_entry = tk.Entry(input_frame, width=30, font=("Courier", 12))
        self.molar_entry.pack(side=tk.LEFT, padx=10)
        self.molar_entry.bind('<Return>', lambda e: self.calc_molar())
        tk.Button(input_frame, text="计算", command=self.calc_molar, bg="lightgreen").pack(side=tk.LEFT)
        
        self.molar_result = tk.Text(self.content_frame, height=15, font=("Courier", 11), wrap=tk.WORD)
        self.molar_result.pack(fill=tk.BOTH, expand=True, pady=10)
        
        example_frame = tk.Frame(self.content_frame)
        example_frame.pack()
        tk.Label(example_frame, text="示例:").pack(side=tk.LEFT)
        for ex in ["H2O", "HCl", "H2SO4", "NaCl", "CaCO3", "Fe2(SO4)3"]:
            tk.Button(example_frame, text=ex, command=lambda e=ex: self.load_molar_example(e)).pack(side=tk.LEFT, padx=5)
    
    def load_molar_example(self, ex):
        self.molar_entry.delete(0, tk.END)
        self.molar_entry.insert(0, ex)
        self.calc_molar()
    
    def calc_molar(self):
        formula = self.molar_entry.get().strip()
        if not formula:
            return
        mass, detail = ChemicalFormulaParser.calculate_molar_mass(formula)
        self.molar_result.delete(1.0, tk.END)
        if mass == 0:
            self.molar_result.insert(tk.END, detail)
        else:
            self.molar_result.insert(tk.END, f"化学式: {self.format_subscript(formula)}\n\n")
            self.molar_result.insert(tk.END, f"计算过程:\n{detail}\n\n")
            self.molar_result.insert(tk.END, f"化学式量: {mass}", "blue")
        self.update_status(f"{formula} 的化学式量为 {mass}")
    
    # ==================== 浓度计算 ====================
    def show_concentration(self):
        self.clear_content()
        self.update_status("浓度计算")
        
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 质量分数
        mass_frame = tk.Frame(notebook)
        notebook.add(mass_frame, text="质量分数")
        
        tk.Label(mass_frame, text="溶质质量 (g):").grid(row=0, column=0, pady=5, padx=10, sticky=tk.W)
        self.solute_mass = tk.Entry(mass_frame, width=15)
        self.solute_mass.grid(row=0, column=1, pady=5)
        
        tk.Label(mass_frame, text="溶液质量 (g):").grid(row=1, column=0, pady=5, padx=10, sticky=tk.W)
        self.solution_mass = tk.Entry(mass_frame, width=15)
        self.solution_mass.grid(row=1, column=1, pady=5)
        
        tk.Label(mass_frame, text="或").grid(row=2, column=0, columnspan=2, pady=5)
        
        tk.Label(mass_frame, text="溶质质量 (g):").grid(row=3, column=0, pady=5, padx=10, sticky=tk.W)
        self.solute_mass2 = tk.Entry(mass_frame, width=15)
        self.solute_mass2.grid(row=3, column=1, pady=5)
        
        tk.Label(mass_frame, text="溶剂质量 (g):").grid(row=4, column=0, pady=5, padx=10, sticky=tk.W)
        self.solvent_mass = tk.Entry(mass_frame, width=15)
        self.solvent_mass.grid(row=4, column=1, pady=5)
        
        tk.Button(mass_frame, text="计算", command=self.calc_mass_fraction, bg="lightblue").grid(row=5, column=0, columnspan=2, pady=10)
        
        self.mass_result = tk.Text(mass_frame, height=6, width=40, font=self.default_font)
        self.mass_result.grid(row=6, column=0, columnspan=2, pady=10, padx=10)
        
        # 物质的量浓度
        molar_frame = tk.Frame(notebook)
        notebook.add(molar_frame, text="物质的量浓度")
        
        tk.Label(molar_frame, text="溶质的物质的量 (mol):").grid(row=0, column=0, pady=5, padx=10, sticky=tk.W)
        self.moles = tk.Entry(molar_frame, width=15)
        self.moles.grid(row=0, column=1, pady=5)
        
        tk.Label(molar_frame, text="或").grid(row=1, column=0, columnspan=2, pady=5)
        
        tk.Label(molar_frame, text="溶质质量 (g):").grid(row=2, column=0, pady=5, padx=10, sticky=tk.W)
        self.solute_mass_m = tk.Entry(molar_frame, width=15)
        self.solute_mass_m.grid(row=2, column=1, pady=5)
        
        tk.Label(molar_frame, text="摩尔质量 (g/mol):").grid(row=3, column=0, pady=5, padx=10, sticky=tk.W)
        self.molar_mass = tk.Entry(molar_frame, width=15)
        self.molar_mass.grid(row=3, column=1, pady=5)
        
        tk.Label(molar_frame, text="溶液体积 (L):").grid(row=4, column=0, pady=5, padx=10, sticky=tk.W)
        self.volume = tk.Entry(molar_frame, width=15)
        self.volume.grid(row=4, column=1, pady=5)
        
        tk.Button(molar_frame, text="计算", command=self.calc_concentration, bg="lightblue").grid(row=5, column=0, columnspan=2, pady=10)
        
        self.conc_result = tk.Text(molar_frame, height=6, width=40, font=self.default_font)
        self.conc_result.grid(row=6, column=0, columnspan=2, pady=10, padx=10)
    
    def calc_mass_fraction(self):
        try:
            if self.solute_mass.get() and self.solution_mass.get():
                solute = float(self.solute_mass.get())
                solution = float(self.solution_mass.get())
            elif self.solute_mass2.get() and self.solvent_mass.get():
                solute = float(self.solute_mass2.get())
                solvent = float(self.solvent_mass.get())
                solution = solute + solvent
            else:
                self.mass_result.delete(1.0, tk.END)
                self.mass_result.insert(tk.END, "请完整输入一组数据")
                return
            fraction = (solute / solution) * 100
            self.mass_result.delete(1.0, tk.END)
            self.mass_result.insert(tk.END, f"溶质质量: {solute} g\n溶液质量: {solution} g\n质量分数: {fraction:.2f}%")
        except:
            self.mass_result.delete(1.0, tk.END)
            self.mass_result.insert(tk.END, "输入无效")
    
    def calc_concentration(self):
        try:
            if self.moles.get():
                mol = float(self.moles.get())
            elif self.solute_mass_m.get() and self.molar_mass.get():
                mass = float(self.solute_mass_m.get())
                mm = float(self.molar_mass.get())
                mol = mass / mm
            else:
                self.conc_result.delete(1.0, tk.END)
                self.conc_result.insert(tk.END, "请完整输入一组数据")
                return
            vol = float(self.volume.get())
            conc = mol / vol
            self.conc_result.delete(1.0, tk.END)
            self.conc_result.insert(tk.END, f"物质的量: {mol:.4f} mol\n体积: {vol} L\n浓度: {conc:.4f} mol/L")
        except:
            self.conc_result.delete(1.0, tk.END)
            self.conc_result.insert(tk.END, "输入无效")
    
    # ==================== 关于和帮助 ====================
    def show_about(self):
        self.clear_content()
        about = """化学工具箱 v0.4

新增功能:
✓ 完整118种元素周期表
✓ 化学式量计算（支持括号）
✓ 浓度计算（质量分数、物质的量浓度）
✓ 离子方程式配平（星号标注）
✓ 配平结果下标显示

主要功能:
• 化学方程式配平
• 完整元素周期表
• 化学式量计算
• 浓度计算

版本: 0.4
更新: 2025-03-28"""
        text = tk.Text(self.content_frame, font=self.default_font, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, about)
        text.config(state=tk.DISABLED)
    
    def show_help(self):
        self.clear_content()
        help_text = """化学工具箱 v0.4 使用帮助

【配平功能】
• 输入格式: H2+O2=H2O
• 离子标注: MnO4**+Fe**=Mn**+Fe**（星号表示电荷）

【化学式量计算】
• 输入化学式如 H2O、Fe2(SO4)3
• 氯原子量35.5，其他为整数

【浓度计算】
• 质量分数: 输入溶质+溶液质量，或溶质+溶剂质量
• 物质的量浓度: 输入物质的量+体积，或质量+摩尔质量+体积

【元素周期表】
• 包含118种完整元素
• 点击元素查看详细信息

注意事项:
• 离子必须用星号标注
• 元素符号大小写敏感"""
        text = tk.Text(self.content_frame, font=self.default_font, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChemistryToolboxV4(root)
    root.mainloop()