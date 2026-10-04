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
        # 镧系和锕系
        'La': [3], 'Ce': [3, 4], 'Pr': [3], 'Nd': [3], 'Pm': [3], 'Sm': [3, 2],
        'Eu': [3, 2], 'Gd': [3], 'Tb': [3, 4], 'Dy': [3], 'Ho': [3], 'Er': [3],
        'Tm': [3], 'Yb': [3, 2], 'Lu': [3], 'Ac': [3], 'Th': [4], 'Pa': [5, 4],
        'U': [6, 5, 4, 3], 'Np': [6, 5, 4], 'Pu': [6, 5, 4, 3], 'Am': [6, 5, 4, 3],
        'Cm': [3], 'Bk': [3, 4], 'Cf': [3], 'Es': [3], 'Fm': [3], 'Md': [3],
        'No': [3], 'Lr': [3],
    }
    
    # 常见原子团及其化合价
    radical_valences = {
        'OH': -1, 'NO3': -1, 'NO2': -1, 'SO4': -2, 'SO3': -2, 'CO3': -2,
        'PO4': -3, 'NH4': 1, 'ClO4': -1, 'ClO3': -1, 'ClO2': -1, 'ClO': -1,
        'MnO4': -1, 'CrO4': -2, 'Cr2O7': -2, 'C2O4': -2, 'CH3COO': -1,
        'HSO4': -1, 'HCO3': -1, 'HPO4': -2, 'H2PO4': -1,
    }
    
    @classmethod
    def get_valence(cls, element, compound_context=None):
        """获取元素的常见化合价"""
        if element in cls.element_valences:
            return cls.element_valences[element]
        return [0]

# ==================== 相对原子质量数据 ====================
class AtomicMass:
    """相对原子质量数据库（四舍五入到整数，氯为35.5）"""
    
    atomic_masses = {
        # 第1周期
        'H': 1, 'He': 4,
        # 第2周期
        'Li': 7, 'Be': 9, 'B': 11, 'C': 12, 'N': 14, 'O': 16, 'F': 19, 'Ne': 20,
        # 第3周期
        'Na': 23, 'Mg': 24, 'Al': 27, 'Si': 28, 'P': 31, 'S': 32, 'Cl': 35.5, 'Ar': 40,
        # 第4周期
        'K': 39, 'Ca': 40, 'Sc': 45, 'Ti': 48, 'V': 51, 'Cr': 52, 'Mn': 55, 'Fe': 56,
        'Co': 59, 'Ni': 59, 'Cu': 64, 'Zn': 65, 'Ga': 70, 'Ge': 73, 'As': 75, 'Se': 79,
        'Br': 80, 'Kr': 84,
        # 第5周期
        'Rb': 85, 'Sr': 88, 'Y': 89, 'Zr': 91, 'Nb': 93, 'Mo': 96, 'Tc': 98, 'Ru': 101,
        'Rh': 103, 'Pd': 106, 'Ag': 108, 'Cd': 112, 'In': 115, 'Sn': 119, 'Sb': 122,
        'Te': 128, 'I': 127, 'Xe': 131,
        # 第6周期
        'Cs': 133, 'Ba': 137, 'La': 139, 'Ce': 140, 'Pr': 141, 'Nd': 144, 'Pm': 145,
        'Sm': 150, 'Eu': 152, 'Gd': 157, 'Tb': 159, 'Dy': 163, 'Ho': 165, 'Er': 167,
        'Tm': 169, 'Yb': 173, 'Lu': 175, 'Hf': 179, 'Ta': 181, 'W': 184, 'Re': 186,
        'Os': 190, 'Ir': 192, 'Pt': 195, 'Au': 197, 'Hg': 201, 'Tl': 204, 'Pb': 207,
        'Bi': 209, 'Po': 209, 'At': 210, 'Rn': 222,
        # 第7周期
        'Fr': 223, 'Ra': 226, 'Ac': 227, 'Th': 232, 'Pa': 231, 'U': 238, 'Np': 237,
        'Pu': 244, 'Am': 243, 'Cm': 247, 'Bk': 247, 'Cf': 251, 'Es': 252, 'Fm': 257,
        'Md': 258, 'No': 259, 'Lr': 262, 'Rf': 267, 'Db': 268, 'Sg': 269, 'Bh': 270,
        'Hs': 269, 'Mt': 278, 'Ds': 281, 'Rg': 282, 'Cn': 285, 'Nh': 286, 'Fl': 289,
        'Mc': 290, 'Lv': 293, 'Ts': 294, 'Og': 294,
    }
    
    @classmethod
    def get_mass(cls, element):
        """获取元素的相对原子质量"""
        return cls.atomic_masses.get(element, 0)

# ==================== 格式化工具 ====================
class FormulaFormatter:
    """化学式格式化工具"""
    
    @staticmethod
    def convert_to_subscript(text):
        """将数字转换为真正的下标字符"""
        subscript_map = {
            '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
            '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
        }
        
        result = ""
        i = 0
        while i < len(text):
            if text[i].isdigit():
                num_start = i
                while i < len(text) and text[i].isdigit():
                    i += 1
                num = text[num_start:i]
                for digit in num:
                    result += subscript_map.get(digit, digit)
            else:
                result += text[i]
                i += 1
        return result

# ==================== 化学式解析器 ====================
class ChemicalFormulaParser:
    """化学式解析器"""
    
    @staticmethod
    def parse_formula(formula):
        """
        解析化学式，返回元素计数
        支持格式：H2O, Fe2(SO4)3
        """
        counts = defaultdict(int)
        
        def parse_simple(formula_part, multiplier=1):
            """解析简单化学式（无括号）"""
            i = 0
            n = len(formula_part)
            while i < n:
                if formula_part[i].isupper():
                    element = formula_part[i]
                    i += 1
                    if i < n and formula_part[i].islower():
                        element += formula_part[i]
                        i += 1
                    
                    # 读取数字
                    num = ""
                    while i < n and formula_part[i].isdigit():
                        num += formula_part[i]
                        i += 1
                    count = int(num) if num else 1
                    counts[element] += count * multiplier
                elif formula_part[i] in '([':
                    # 处理括号
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
                    
                    # 读取括号后的数字
                    num = ""
                    while i < n and formula_part[i].isdigit():
                        num += formula_part[i]
                        i += 1
                    bracket_multiplier = int(num) if num else 1
                    
                    # 递归解析括号内容
                    parse_simple(bracket_content, multiplier * bracket_multiplier)
                else:
                    i += 1
        
        parse_simple(formula)
        return dict(counts)
    
    @staticmethod
    def calculate_molar_mass(formula):
        """
        计算化学式的摩尔质量（相对分子质量）
        返回计算结果和详细过程
        """
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
            
            detail_str = " + ".join(details)
            return total_mass, f"{detail_str} = {total_mass}"
            
        except Exception as e:
            return 0, f"计算错误：{str(e)}"
    
    @staticmethod
    def calculate_oxidation_states(formula):
        """计算化学式中各元素的化合价"""
        counts, _ = ChemicalFormulaParser.parse_formula(formula)
        
        if not counts:
            return {}
        
        element_valence = {}
        
        # 按电负性排序
        def get_electronegativity(e):
            en = {'F': 4.0, 'O': 3.5, 'Cl': 3.2, 'N': 3.0, 'Br': 3.0, 
                  'S': 2.6, 'C': 2.6, 'P': 2.2, 'H': 2.2, 'B': 2.0}
            return en.get(e, 2.5)
        
        elements = list(counts.keys())
        elements.sort(key=get_electronegativity, reverse=True)
        
        # 为每个元素分配化合价
        for element in elements:
            valences = ValenceData.get_valence(element, formula)
            if valences:
                element_valence[element] = valences[0] if valences else 0
            else:
                element_valence[element] = 0
        
        # 计算总化合价并调整
        total = sum(element_valence[e] * counts[e] for e in elements)
        
        if abs(total) > 1e-5:
            for element in reversed(elements):
                valences = ValenceData.get_valence(element, formula)
                if len(valences) > 1:
                    current = element_valence[element]
                    for v in valences:
                        new_total = total - current * counts[element] + v * counts[element]
                        if abs(new_total) < 1e-5:
                            element_valence[element] = v
                            break
                    break
        
        return element_valence

# ==================== 配平引擎 ====================
class EquationBalancer:
    """化学方程式配平器"""
    
    @staticmethod
    def parse_compound_with_charge(compound):
        """解析带电荷的化合物（使用星号标注）"""
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
        """配平化学方程式"""
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
                
                if n_unknowns > 0 and A.shape[1] > 1:
                    A_reduced = A[:, 1:]
                    b_reduced = b - A[:, 0] * first_coeff
                    
                    try:
                        if A_reduced.shape[1] > 0:
                            solution = np.linalg.lstsq(A_reduced, b_reduced, rcond=None)[0]
                        else:
                            solution = np.array([])
                        
                        coeffs = [first_coeff] + list(solution)
                        while len(coeffs) < n_unknowns:
                            coeffs.append(1)
                        
                        valid = True
                        int_coeffs = []
                        for i, c in enumerate(coeffs[:n_unknowns]):
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
            
            if best_solution and best_error < 1e-5:
                g = best_solution[0]
                for c in best_solution[1:]:
                    g = gcd(g, c)
                if g > 1:
                    best_solution = [c // g for c in best_solution]
                
                left_parts = []
                for i, (formula, charge) in enumerate(left_compounds):
                    coeff = best_solution[i]
                    formatted = f"{coeff if coeff > 1 else ''}{formula}"
                    if charge != 0:
                        charge_stars = '*' * abs(charge)
                        formatted += charge_stars
                    left_parts.append(formatted)
                
                right_parts = []
                for i, (formula, charge) in enumerate(right_compounds):
                    coeff = best_solution[n_left + i]
                    formatted = f"{coeff if coeff > 1 else ''}{formula}"
                    if charge != 0:
                        charge_stars = '*' * abs(charge)
                        formatted += charge_stars
                    right_parts.append(formatted)
                
                balanced_eq = f"{'+'.join(left_parts)} = {'+'.join(right_parts)}"
                
                valence_info = {}
                for idx, (formula, _) in enumerate(left_compounds):
                    valence_info[f'L{idx}'] = ChemicalFormulaParser.calculate_oxidation_states(formula)
                for idx, (formula, _) in enumerate(right_compounds):
                    valence_info[f'R{idx}'] = ChemicalFormulaParser.calculate_oxidation_states(formula)
                
                return balanced_eq, valence_info
            
            return "错误：无法配平该方程式", {}
            
        except Exception as e:
            return f"配平失败: {str(e)}", {}

# ==================== 扩展元素数据 ====================
class ExtendedPeriodicTable:
    """扩展的元素周期表数据（完整版）"""
    
    # 电子层排布数据
    electron_config = {
        # 周期1
        "H": "1", "He": "2",
        # 周期2
        "Li": "2,1", "Be": "2,2", "B": "2,3", "C": "2,4", "N": "2,5", "O": "2,6", "F": "2,7", "Ne": "2,8",
        # 周期3
        "Na": "2,8,1", "Mg": "2,8,2", "Al": "2,8,3", "Si": "2,8,4", "P": "2,8,5", "S": "2,8,6", "Cl": "2,8,7", "Ar": "2,8,8",
        # 周期4
        "K": "2,8,8,1", "Ca": "2,8,8,2", "Sc": "2,8,9,2", "Ti": "2,8,10,2", "V": "2,8,11,2", 
        "Cr": "2,8,13,1", "Mn": "2,8,13,2", "Fe": "2,8,14,2", "Co": "2,8,15,2", "Ni": "2,8,16,2",
        "Cu": "2,8,18,1", "Zn": "2,8,18,2", "Ga": "2,8,18,3", "Ge": "2,8,18,4", "As": "2,8,18,5",
        "Se": "2,8,18,6", "Br": "2,8,18,7", "Kr": "2,8,18,8",
        # 周期5
        "Rb": "2,8,18,8,1", "Sr": "2,8,18,8,2", "Y": "2,8,18,9,2", "Zr": "2,8,18,10,2",
        "Nb": "2,8,18,12,1", "Mo": "2,8,18,13,1", "Tc": "2,8,18,13,2", "Ru": "2,8,18,15,1",
        "Rh": "2,8,18,16,1", "Pd": "2,8,18,18", "Ag": "2,8,18,18,1", "Cd": "2,8,18,18,2",
        "In": "2,8,18,18,3", "Sn": "2,8,18,18,4", "Sb": "2,8,18,18,5", "Te": "2,8,18,18,6",
        "I": "2,8,18,18,7", "Xe": "2,8,18,18,8",
        # 周期6
        "Cs": "2,8,18,18,8,1", "Ba": "2,8,18,18,8,2", "La": "2,8,18,18,9,2",
        "Ce": "2,8,18,19,9,2", "Pr": "2,8,18,21,8,2", "Nd": "2,8,18,22,8,2",
        "Pm": "2,8,18,23,8,2", "Sm": "2,8,18,24,8,2", "Eu": "2,8,18,25,8,2", "Gd": "2,8,18,25,9,2",
        "Tb": "2,8,18,27,8,2", "Dy": "2,8,18,28,8,2", "Ho": "2,8,18,29,8,2", "Er": "2,8,18,30,8,2",
        "Tm": "2,8,18,31,8,2", "Yb": "2,8,18,32,8,2", "Lu": "2,8,18,32,9,2",
        "Hf": "2,8,18,32,10,2", "Ta": "2,8,18,32,11,2", "W": "2,8,18,32,12,2",
        "Re": "2,8,18,32,13,2", "Os": "2,8,18,32,14,2", "Ir": "2,8,18,32,15,2",
        "Pt": "2,8,18,32,17,1", "Au": "2,8,18,32,18,1", "Hg": "2,8,18,32,18,2",
        "Tl": "2,8,18,32,18,3", "Pb": "2,8,18,32,18,4", "Bi": "2,8,18,32,18,5",
        "Po": "2,8,18,32,18,6", "At": "2,8,18,32,18,7", "Rn": "2,8,18,32,18,8",
        # 周期7
        "Fr": "2,8,18,32,18,8,1", "Ra": "2,8,18,32,18,8,2", "Ac": "2,8,18,32,18,9,2",
        "Th": "2,8,18,32,18,10,2", "Pa": "2,8,18,32,20,9,2", "U": "2,8,18,32,21,9,2",
        "Np": "2,8,18,32,22,9,2", "Pu": "2,8,18,32,24,8,2", "Am": "2,8,18,32,25,8,2",
    }
    
    elements_data = {
        # 第1周期
        "H": {"name": "氢", "atomic": 1, "mass": 1.008, "group": 1, "period": 1, 
              "config": "1s¹", "desc": "最轻的元素，宇宙中含量最丰富"},
        "He": {"name": "氦", "atomic": 2, "mass": 4.0026, "group": 18, "period": 1, 
               "config": "1s²", "desc": "稀有气体，沸点最低"},
        
        # 第2周期
        "Li": {"name": "锂", "atomic": 3, "mass": 6.94, "group": 1, "period": 2, 
               "config": "[He] 2s¹", "desc": "最轻的金属，用于电池"},
        "Be": {"name": "铍", "atomic": 4, "mass": 9.0122, "group": 2, "period": 2, 
               "config": "[He] 2s²", "desc": "轻金属，有毒"},
        "B": {"name": "硼", "atomic": 5, "mass": 10.81, "group": 13, "period": 2, 
              "config": "[He] 2s² 2p¹", "desc": "类金属，用于半导体"},
        "C": {"name": "碳", "atomic": 6, "mass": 12.011, "group": 14, "period": 2, 
              "config": "[He] 2s² 2p²", "desc": "生命的基础，有机化合物骨架"},
        "N": {"name": "氮", "atomic": 7, "mass": 14.007, "group": 15, "period": 2, 
              "config": "[He] 2s² 2p³", "desc": "大气主要成分"},
        "O": {"name": "氧", "atomic": 8, "mass": 15.999, "group": 16, "period": 2, 
              "config": "[He] 2s² 2p⁴", "desc": "支持燃烧，生命必需"},
        "F": {"name": "氟", "atomic": 9, "mass": 18.998, "group": 17, "period": 2, 
              "config": "[He] 2s² 2p⁵", "desc": "最活泼的非金属"},
        "Ne": {"name": "氖", "atomic": 10, "mass": 20.18, "group": 18, "period": 2, 
               "config": "[He] 2s² 2p⁶", "desc": "稀有气体，用于霓虹灯"},
        
        # 第3周期
        "Na": {"name": "钠", "atomic": 11, "mass": 22.99, "group": 1, "period": 3, 
               "config": "[Ne] 3s¹", "desc": "碱金属，活泼"},
        "Mg": {"name": "镁", "atomic": 12, "mass": 24.305, "group": 2, "period": 3, 
               "config": "[Ne] 3s²", "desc": "轻金属，合金"},
        "Al": {"name": "铝", "atomic": 13, "mass": 26.982, "group": 13, "period": 3, 
               "config": "[Ne] 3s² 3p¹", "desc": "地壳中含量最丰富的金属"},
        "Si": {"name": "硅", "atomic": 14, "mass": 28.086, "group": 14, "period": 3, 
               "config": "[Ne] 3s² 3p²", "desc": "半导体材料"},
        "P": {"name": "磷", "atomic": 15, "mass": 30.974, "group": 15, "period": 3, 
              "config": "[Ne] 3s² 3p³", "desc": "白磷易燃"},
        "S": {"name": "硫", "atomic": 16, "mass": 32.06, "group": 16, "period": 3, 
              "config": "[Ne] 3s² 3p⁴", "desc": "黄色固体"},
        "Cl": {"name": "氯", "atomic": 17, "mass": 35.45, "group": 17, "period": 3, 
               "config": "[Ne] 3s² 3p⁵", "desc": "黄绿色气体，消毒"},
        "Ar": {"name": "氩", "atomic": 18, "mass": 39.95, "group": 18, "period": 3, 
               "config": "[Ne] 3s² 3p⁶", "desc": "稀有气体"},
        
        # 第4周期
        "K": {"name": "钾", "atomic": 19, "mass": 39.098, "group": 1, "period": 4, 
              "config": "[Ar] 4s¹", "desc": "活泼金属"},
        "Ca": {"name": "钙", "atomic": 20, "mass": 40.078, "group": 2, "period": 4, 
               "config": "[Ar] 4s²", "desc": "骨骼主要成分"},
        "Sc": {"name": "钪", "atomic": 21, "mass": 44.956, "group": 3, "period": 4, 
               "config": "[Ar] 3d¹ 4s²", "desc": "稀土元素"},
        "Ti": {"name": "钛", "atomic": 22, "mass": 47.867, "group": 4, "period": 4, 
               "config": "[Ar] 3d² 4s²", "desc": "高强度轻金属"},
        "V": {"name": "钒", "atomic": 23, "mass": 50.942, "group": 5, "period": 4, 
              "config": "[Ar] 3d³ 4s²", "desc": "钢铁工业添加剂"},
        "Cr": {"name": "铬", "atomic": 24, "mass": 51.996, "group": 6, "period": 4, 
               "config": "[Ar] 3d⁵ 4s¹", "desc": "不锈钢成分"},
        "Mn": {"name": "锰", "atomic": 25, "mass": 54.938, "group": 7, "period": 4, 
               "config": "[Ar] 3d⁵ 4s²", "desc": "钢铁工业重要元素"},
        "Fe": {"name": "铁", "atomic": 26, "mass": 55.845, "group": 8, "period": 4, 
               "config": "[Ar] 3d⁶ 4s²", "desc": "最常用的金属"},
        "Co": {"name": "钴", "atomic": 27, "mass": 58.933, "group": 9, "period": 4, 
               "config": "[Ar] 3d⁷ 4s²", "desc": "磁性材料"},
        "Ni": {"name": "镍", "atomic": 28, "mass": 58.693, "group": 10, "period": 4, 
               "config": "[Ar] 3d⁸ 4s²", "desc": "不锈钢成分"},
        "Cu": {"name": "铜", "atomic": 29, "mass": 63.546, "group": 11, "period": 4, 
               "config": "[Ar] 3d¹⁰ 4s¹", "desc": "导电性好"},
        "Zn": {"name": "锌", "atomic": 30, "mass": 65.38, "group": 12, "period": 4, 
               "config": "[Ar] 3d¹⁰ 4s²", "desc": "防腐镀层"},
        "Ga": {"name": "镓", "atomic": 31, "mass": 69.723, "group": 13, "period": 4, 
               "config": "[Ar] 3d¹⁰ 4s² 4p¹", "desc": "低熔点金属"},
        "Ge": {"name": "锗", "atomic": 32, "mass": 72.63, "group": 14, "period": 4, 
               "config": "[Ar] 3d¹⁰ 4s² 4p²", "desc": "半导体材料"},
        "As": {"name": "砷", "atomic": 33, "mass": 74.922, "group": 15, "period": 4, 
               "config": "[Ar] 3d¹⁰ 4s² 4p³", "desc": "有毒类金属"},
        "Se": {"name": "硒", "atomic": 34, "mass": 78.96, "group": 16, "period": 4, 
               "config": "[Ar] 3d¹⁰ 4s² 4p⁴", "desc": "光导材料"},
        "Br": {"name": "溴", "atomic": 35, "mass": 79.904, "group": 17, "period": 4, 
               "config": "[Ar] 3d¹⁰ 4s² 4p⁵", "desc": "红棕色液体"},
        "Kr": {"name": "氪", "atomic": 36, "mass": 83.798, "group": 18, "period": 4, 
               "config": "[Ar] 3d¹⁰ 4s² 4p⁶", "desc": "稀有气体"},
        
        # 第5周期
        "Rb": {"name": "铷", "atomic": 37, "mass": 85.468, "group": 1, "period": 5, 
               "config": "[Kr] 5s¹", "desc": "活泼碱金属"},
        "Sr": {"name": "锶", "atomic": 38, "mass": 87.62, "group": 2, "period": 5, 
               "config": "[Kr] 5s²", "desc": "用于烟花"},
        "Y": {"name": "钇", "atomic": 39, "mass": 88.906, "group": 3, "period": 5, 
              "config": "[Kr] 4d¹ 5s²", "desc": "稀土元素"},
        "Zr": {"name": "锆", "atomic": 40, "mass": 91.224, "group": 4, "period": 5, 
               "config": "[Kr] 4d² 5s²", "desc": "耐腐蚀金属"},
        "Nb": {"name": "铌", "atomic": 41, "mass": 92.906, "group": 5, "period": 5, 
               "config": "[Kr] 4d⁴ 5s¹", "desc": "超导材料"},
        "Mo": {"name": "钼", "atomic": 42, "mass": 95.95, "group": 6, "period": 5, 
               "config": "[Kr] 4d⁵ 5s¹", "desc": "钢铁添加剂"},
        "Tc": {"name": "锝", "atomic": 43, "mass": 98, "group": 7, "period": 5, 
               "config": "[Kr] 4d⁵ 5s²", "desc": "放射性元素"},
        "Ru": {"name": "钌", "atomic": 44, "mass": 101.07, "group": 8, "period": 5, 
               "config": "[Kr] 4d⁷ 5s¹", "desc": "铂族金属"},
        "Rh": {"name": "铑", "atomic": 45, "mass": 102.91, "group": 9, "period": 5, 
               "config": "[Kr] 4d⁸ 5s¹", "desc": "催化剂"},
        "Pd": {"name": "钯", "atomic": 46, "mass": 106.42, "group": 10, "period": 5, 
               "config": "[Kr] 4d¹⁰", "desc": "催化剂"},
        "Ag": {"name": "银", "atomic": 47, "mass": 107.87, "group": 11, "period": 5, 
               "config": "[Kr] 4d¹⁰ 5s¹", "desc": "贵金属，导电性最佳"},
        "Cd": {"name": "镉", "atomic": 48, "mass": 112.41, "group": 12, "period": 5, 
               "config": "[Kr] 4d¹⁰ 5s²", "desc": "有毒重金属"},
        "In": {"name": "铟", "atomic": 49, "mass": 114.82, "group": 13, "period": 5, 
               "config": "[Kr] 4d¹⁰ 5s² 5p¹", "desc": "用于液晶屏"},
        "Sn": {"name": "锡", "atomic": 50, "mass": 118.71, "group": 14, "period": 5, 
               "config": "[Kr] 4d¹⁰ 5s² 5p²", "desc": "青铜成分"},
        "Sb": {"name": "锑", "atomic": 51, "mass": 121.76, "group": 15, "period": 5, 
               "config": "[Kr] 4d¹⁰ 5s² 5p³", "desc": "阻燃剂"},
        "Te": {"name": "碲", "atomic": 52, "mass": 127.6, "group": 16, "period": 5, 
               "config": "[Kr] 4d¹⁰ 5s² 5p⁴", "desc": "半导体材料"},
        "I": {"name": "碘", "atomic": 53, "mass": 126.90, "group": 17, "period": 5, 
              "config": "[Kr] 4d¹⁰ 5s² 5p⁵", "desc": "消毒剂"},
        "Xe": {"name": "氙", "atomic": 54, "mass": 131.29, "group": 18, "period": 5, 
               "config": "[Kr] 4d¹⁰ 5s² 5p⁶", "desc": "稀有气体"},
        
        # 第6周期
        "Cs": {"name": "铯", "atomic": 55, "mass": 132.91, "group": 1, "period": 6, 
               "config": "[Xe] 6s¹", "desc": "最活泼金属"},
        "Ba": {"name": "钡", "atomic": 56, "mass": 137.33, "group": 2, "period": 6, 
               "config": "[Xe] 6s²", "desc": "用于X光造影"},
        "La": {"name": "镧", "atomic": 57, "mass": 138.91, "group": 3, "period": 6, 
               "config": "[Xe] 5d¹ 6s²", "desc": "稀土元素"},
        "Ce": {"name": "铈", "atomic": 58, "mass": 140.12, "group": 3, "period": 6, 
               "config": "[Xe] 4f¹ 5d¹ 6s²", "desc": "稀土元素"},
        "Pr": {"name": "镨", "atomic": 59, "mass": 140.91, "group": 3, "period": 6, 
               "config": "[Xe] 4f³ 6s²", "desc": "稀土元素"},
        "Nd": {"name": "钕", "atomic": 60, "mass": 144.24, "group": 3, "period": 6, 
               "config": "[Xe] 4f⁴ 6s²", "desc": "用于永磁体"},
        "Pm": {"name": "钷", "atomic": 61, "mass": 145, "group": 3, "period": 6, 
               "config": "[Xe] 4f⁵ 6s²", "desc": "放射性稀土元素"},
        "Sm": {"name": "钐", "atomic": 62, "mass": 150.36, "group": 3, "period": 6, 
               "config": "[Xe] 4f⁶ 6s²", "desc": "稀土元素"},
        "Eu": {"name": "铕", "atomic": 63, "mass": 151.96, "group": 3, "period": 6, 
               "config": "[Xe] 4f⁷ 6s²", "desc": "用于荧光粉"},
        "Gd": {"name": "钆", "atomic": 64, "mass": 157.25, "group": 3, "period": 6, 
               "config": "[Xe] 4f⁷ 5d¹ 6s²", "desc": "核反应堆控制棒"},
        "Tb": {"name": "铽", "atomic": 65, "mass": 158.93, "group": 3, "period": 6, 
               "config": "[Xe] 4f⁹ 6s²", "desc": "稀土元素"},
        "Dy": {"name": "镝", "atomic": 66, "mass": 162.50, "group": 3, "period": 6, 
               "config": "[Xe] 4f¹⁰ 6s²", "desc": "稀土元素"},
        "Ho": {"name": "钬", "atomic": 67, "mass": 164.93, "group": 3, "period": 6, 
               "config": "[Xe] 4f¹¹ 6s²", "desc": "稀土元素"},
        "Er": {"name": "铒", "atomic": 68, "mass": 167.26, "group": 3, "period": 6, 
               "config": "[Xe] 4f¹² 6s²", "desc": "稀土元素"},
        "Tm": {"name": "铥", "atomic": 69, "mass": 168.93, "group": 3, "period": 6, 
               "config": "[Xe] 4f¹³ 6s²", "desc": "稀土元素"},
        "Yb": {"name": "镱", "atomic": 70, "mass": 173.05, "group": 3, "period": 6, 
               "config": "[Xe] 4f¹⁴ 6s²", "desc": "稀土元素"},
        "Lu": {"name": "镥", "atomic": 71, "mass": 174.97, "group": 3, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d¹ 6s²", "desc": "稀土元素"},
        "Hf": {"name": "铪", "atomic": 72, "mass": 178.49, "group": 4, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d² 6s²", "desc": "耐热合金"},
        "Ta": {"name": "钽", "atomic": 73, "mass": 180.95, "group": 5, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d³ 6s²", "desc": "耐腐蚀金属"},
        "W": {"name": "钨", "atomic": 74, "mass": 183.84, "group": 6, "period": 6, 
              "config": "[Xe] 4f¹⁴ 5d⁴ 6s²", "desc": "熔点最高的金属"},
        "Re": {"name": "铼", "atomic": 75, "mass": 186.21, "group": 7, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d⁵ 6s²", "desc": "高熔点金属"},
        "Os": {"name": "锇", "atomic": 76, "mass": 190.23, "group": 8, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d⁶ 6s²", "desc": "密度最大金属"},
        "Ir": {"name": "铱", "atomic": 77, "mass": 192.22, "group": 9, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d⁷ 6s²", "desc": "耐腐蚀"},
        "Pt": {"name": "铂", "atomic": 78, "mass": 195.08, "group": 10, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d⁹ 6s¹", "desc": "贵金属，催化剂"},
        "Au": {"name": "金", "atomic": 79, "mass": 196.97, "group": 11, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s¹", "desc": "延展性好，不氧化"},
        "Hg": {"name": "汞", "atomic": 80, "mass": 200.59, "group": 12, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s²", "desc": "唯一液态金属"},
        "Tl": {"name": "铊", "atomic": 81, "mass": 204.38, "group": 13, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p¹", "desc": "剧毒"},
        "Pb": {"name": "铅", "atomic": 82, "mass": 207.2, "group": 14, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p²", "desc": "重金属，有毒"},
        "Bi": {"name": "铋", "atomic": 83, "mass": 208.98, "group": 15, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p³", "desc": "低熔点金属"},
        "Po": {"name": "钋", "atomic": 84, "mass": 209, "group": 16, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁴", "desc": "放射性"},
        "At": {"name": "砹", "atomic": 85, "mass": 210, "group": 17, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁵", "desc": "稀有放射性元素"},
        "Rn": {"name": "氡", "atomic": 86, "mass": 222, "group": 18, "period": 6, 
               "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁶", "desc": "放射性气体"},
        
        # 第7周期
        "Fr": {"name": "钫", "atomic": 87, "mass": 223, "group": 1, "period": 7, 
               "config": "[Rn] 7s¹", "desc": "放射性碱金属"},
        "Ra": {"name": "镭", "atomic": 88, "mass": 226, "group": 2, "period": 7, 
               "config": "[Rn] 7s²", "desc": "放射性，用于放疗"},
        "Ac": {"name": "锕", "atomic": 89, "mass": 227, "group": 3, "period": 7, 
               "config": "[Rn] 6d¹ 7s²", "desc": "放射性元素"},
        "Th": {"name": "钍", "atomic": 90, "mass": 232.04, "group": 3, "period": 7, 
               "config": "[Rn] 6d² 7s²", "desc": "放射性，核燃料"},
        "Pa": {"name": "镤", "atomic": 91, "mass": 231.04, "group": 3, "period": 7, 
               "config": "[Rn] 5f² 6d¹ 7s²", "desc": "放射性元素"},
        "U": {"name": "铀", "atomic": 92, "mass": 238.03, "group": 3, "period": 7, 
              "config": "[Rn] 5f³ 6d¹ 7s²", "desc": "核燃料，放射性"},
        "Np": {"name": "镎", "atomic": 93, "mass": 237, "group": 3, "period": 7, 
               "config": "[Rn] 5f⁴ 6d¹ 7s²", "desc": "人工合成放射性元素"},
        "Pu": {"name": "钚", "atomic": 94, "mass": 244, "group": 3, "period": 7, 
               "config": "[Rn] 5f⁶ 7s²", "desc": "核武器原料"},
        "Am": {"name": "镅", "atomic": 95, "mass": 243, "group": 3, "period": 7, 
               "config": "[Rn] 5f⁷ 7s²", "desc": "烟雾探测器"},
        "Cm": {"name": "锔", "atomic": 96, "mass": 247, "group": 3, "period": 7, 
               "config": "[Rn] 5f⁷ 6d¹ 7s²", "desc": "放射性元素"},
        "Bk": {"name": "锫", "atomic": 97, "mass": 247, "group": 3, "period": 7, 
               "config": "[Rn] 5f⁹ 7s²", "desc": "人工合成元素"},
        "Cf": {"name": "锎", "atomic": 98, "mass": 251, "group": 3, "period": 7, 
               "config": "[Rn] 5f¹⁰ 7s²", "desc": "中子源"},
        "Es": {"name": "锿", "atomic": 99, "mass": 252, "group": 3, "period": 7, 
               "config": "[Rn] 5f¹¹ 7s²", "desc": "人工合成元素"},
        "Fm": {"name": "镄", "atomic": 100, "mass": 257, "group": 3, "period": 7, 
               "config": "[Rn] 5f¹² 7s²", "desc": "人工合成元素"},
        "Md": {"name": "钔", "atomic": 101, "mass": 258, "group": 3, "period": 7, 
               "config": "[Rn] 5f¹³ 7s²", "desc": "人工合成元素"},
        "No": {"name": "锘", "atomic": 102, "mass": 259, "group": 3, "period": 7, 
               "config": "[Rn] 5f¹⁴ 7s²", "desc": "人工合成元素"},
        "Lr": {"name": "铹", "atomic": 103, "mass": 262, "group": 3, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d¹ 7s²", "desc": "人工合成元素"},
        "Rf": {"name": "𬬻", "atomic": 104, "mass": 267, "group": 4, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d² 7s²", "desc": "人工合成元素"},
        "Db": {"name": "𬭊", "atomic": 105, "mass": 268, "group": 5, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d³ 7s²", "desc": "人工合成元素"},
        "Sg": {"name": "𬭳", "atomic": 106, "mass": 269, "group": 6, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d⁴ 7s²", "desc": "人工合成元素"},
        "Bh": {"name": "𬭛", "atomic": 107, "mass": 270, "group": 7, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d⁵ 7s²", "desc": "人工合成元素"},
        "Hs": {"name": "𬭶", "atomic": 108, "mass": 269, "group": 8, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d⁶ 7s²", "desc": "人工合成元素"},
        "Mt": {"name": "鿏", "atomic": 109, "mass": 278, "group": 9, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d⁷ 7s²", "desc": "人工合成元素"},
        "Ds": {"name": "𫟼", "atomic": 110, "mass": 281, "group": 10, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d⁸ 7s²", "desc": "人工合成元素"},
        "Rg": {"name": "𬬭", "atomic": 111, "mass": 282, "group": 11, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d⁹ 7s²", "desc": "人工合成元素"},
        "Cn": {"name": "鎶", "atomic": 112, "mass": 285, "group": 12, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s²", "desc": "人工合成元素"},
        "Nh": {"name": "鉨", "atomic": 113, "mass": 286, "group": 13, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p¹", "desc": "人工合成元素"},
        "Fl": {"name": "𫓧", "atomic": 114, "mass": 289, "group": 14, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p²", "desc": "人工合成元素"},
        "Mc": {"name": "镆", "atomic": 115, "mass": 290, "group": 15, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p³", "desc": "人工合成元素"},
        "Lv": {"name": "𫟷", "atomic": 116, "mass": 293, "group": 16, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁴", "desc": "人工合成元素"},
        "Ts": {"name": "鿬", "atomic": 117, "mass": 294, "group": 17, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁵", "desc": "人工合成元素"},
        "Og": {"name": "气奥", "atomic": 118, "mass": 294, "group": 18, "period": 7, 
               "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁶", "desc": "人工合成元素"},
    }

# ==================== 主应用程序 ====================
class ChemistryToolboxV4:
    """化学工具箱 0.4 版本"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("化学工具箱 v0.4")
        self.root.geometry("1000x700")
        
        # 设置字体
        self.default_font = ("Microsoft YaHei", 10)
        self.title_font = ("Microsoft YaHei", 12, "bold")
        
        # 顶部按钮框架
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.btn_balance = tk.Button(self.button_frame, text="配平", width=10, 
                                      font=self.title_font, command=self.show_balance)
        self.btn_balance.pack(side=tk.LEFT, padx=5)
        
        self.btn_periodic = tk.Button(self.button_frame, text="元素周期表", width=12,
                                       font=self.title_font, command=self.show_periodic)
        self.btn_periodic.pack(side=tk.LEFT, padx=5)
        
        # 计算按钮（带下拉菜单）
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
        self.status_frame = tk.Frame(root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tk.Label(self.status_frame, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 内容区域框架
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 默认显示配平界面
        self.show_balance()
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
        self.root.update()
    
    def format_with_subscript(self, text):
        """将数字转换为下标"""
        subscript_map = {
            '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
            '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
        }
        
        result = ""
        i = 0
        while i < len(text):
            if text[i].isdigit():
                num_start = i
                while i < len(text) and text[i].isdigit():
                    i += 1
                num = text[num_start:i]
                for digit in num:
                    result += subscript_map.get(digit, digit)
            else:
                result += text[i]
                i += 1
        return result
    
    # ==================== 配平界面 ====================
    def show_balance(self):
        self.clear_content()
        self.update_status("配平模式 - 离子用星号标注（如 MnO4** 表示 MnO₄⁻）")
        
        # 标题
        tk.Label(self.content_frame, text="化学方程式配平 v0.4", font=self.title_font, 
                fg="blue").pack(pady=10)
        
        # 说明
        help_frame = tk.Frame(self.content_frame)
        help_frame.pack(pady=5)
        tk.Label(help_frame, text="支持格式:", font=("Microsoft YaHei", 9, "bold")).pack(side=tk.LEFT)
        tk.Label(help_frame, text=" H2+O2=H2O  |  Fe2O3+CO=Fe+CO2  |  MnO4**+Fe**=Mn**+Fe**", 
                font=self.default_font, fg="green").pack(side=tk.LEFT, padx=5)
        
        # 输入区域
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(pady=15)
        
        tk.Label(input_frame, text="请输入方程式:", font=self.default_font).pack(side=tk.LEFT)
        self.equation_entry = tk.Entry(input_frame, width=60, font=("Courier", 11))
        self.equation_entry.pack(side=tk.LEFT, padx=10)
        self.equation_entry.bind('<Return>', lambda e: self.do_balance())
        
        self.balance_btn = tk.Button(input_frame, text="配平", command=self.do_balance, 
                                     bg="lightblue", width=10, font=self.default_font)
        self.balance_btn.pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域
        result_frame = tk.LabelFrame(self.content_frame, text="配平结果", font=self.title_font)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_text = tk.Text(result_frame, height=12, font=("Courier", 12), wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配置文本标签样式
        self.result_text.tag_configure("blue_coeff", foreground="blue", font=("Courier", 12, "bold"))
        self.result_text.tag_configure("green_valence", foreground="green", font=("Courier", 10))
        self.result_text.tag_configure("red_valence", foreground="red", font=("Courier", 10))
        self.result_text.tag_configure("normal", foreground="black", font=("Courier", 12))
        
        # 示例按钮
        example_frame = tk.Frame(self.content_frame)
        example_frame.pack(pady=5)
        tk.Label(example_frame, text="示例:").pack(side=tk.LEFT)
        
        examples = [
            ("H2+O2=H2O", "氢气燃烧"),
            ("Fe2O3+CO=Fe+CO2", "炼铁"),
            ("Cu+AgNO3=Cu(NO3)2+Ag", "置换反应"),
            ("MnO4**+Fe**=Mn**+Fe**", "氧化还原（离子）")
        ]
        
        for eq, desc in examples:
            btn = tk.Button(example_frame, text=desc, command=lambda e=eq: self.load_example(e),
                           font=self.default_font, bg="#f0f0f0")
            btn.pack(side=tk.LEFT, padx=5)
    
    def load_example(self, equation):
        """加载示例方程式"""
        self.equation_entry.delete(0, tk.END)
        self.equation_entry.insert(0, equation)
        self.do_balance()
    
    def do_balance(self):
        """执行配平"""
        equation = self.equation_entry.get().strip()
        if not equation:
            messagebox.showwarning("警告", "请输入化学方程式")
            return
        
        self.update_status("正在配平方程式...")
        
        result, valence_data = EquationBalancer.balance(equation)
        
        self.result_text.delete(1.0, tk.END)
        
        if result.startswith("错误"):
            self.result_text.insert(tk.END, result, "normal")
            self.update_status("配平失败")
        else:
            self.result_text.insert(tk.END, "配平结果:\n\n", "normal")
            
            left, right = result.split(" = ")
            
            # 显示左边
            left_parts = left.split('+')
            for i, part in enumerate(left_parts):
                coeff_match = re.match(r'^(\d+)(.*)$', part)
                if coeff_match:
                    coeff = int(coeff_match.group(1))
                    formula = coeff_match.group(2)
                    formula_clean = formula.replace('*', '')
                    self.result_text.insert(tk.END, f"{coeff}", "blue_coeff")
                    self.result_text.insert(tk.END, self.format_with_subscript(formula_clean), "normal")
                    stars_count = formula.count('*')
                    if stars_count > 0:
                        charge_text = f"⁽{'-' if stars_count > 0 else '+'}{stars_count}⁾"
                        self.result_text.insert(tk.END, charge_text, "normal")
                else:
                    formula_clean = part.replace('*', '')
                    self.result_text.insert(tk.END, self.format_with_subscript(formula_clean), "normal")
                    stars_count = part.count('*')
                    if stars_count > 0:
                        charge_text = f"⁽{'-' if stars_count > 0 else '+'}{stars_count}⁾"
                        self.result_text.insert(tk.END, charge_text, "normal")
                
                if i < len(left_parts) - 1:
                    self.result_text.insert(tk.END, " + ", "normal")
            
            self.result_text.insert(tk.END, " = ", "normal")
            
            # 显示右边
            right_parts = right.split('+')
            for i, part in enumerate(right_parts):
                coeff_match = re.match(r'^(\d+)(.*)$', part)
                if coeff_match:
                    coeff = int(coeff_match.group(1))
                    formula = coeff_match.group(2)
                    formula_clean = formula.replace('*', '')
                    self.result_text.insert(tk.END, f"{coeff}", "blue_coeff")
                    self.result_text.insert(tk.END, self.format_with_subscript(formula_clean), "normal")
                    stars_count = formula.count('*')
                    if stars_count > 0:
                        charge_text = f"⁽{'-' if stars_count > 0 else '+'}{stars_count}⁾"
                        self.result_text.insert(tk.END, charge_text, "normal")
                else:
                    formula_clean = part.replace('*', '')
                    self.result_text.insert(tk.END, self.format_with_subscript(formula_clean), "normal")
                    stars_count = part.count('*')
                    if stars_count > 0:
                        charge_text = f"⁽{'-' if stars_count > 0 else '+'}{stars_count}⁾"
                        self.result_text.insert(tk.END, charge_text, "normal")
                
                if i < len(right_parts) - 1:
                    self.result_text.insert(tk.END, " + ", "normal")
            
            # 显示化合价信息
            if valence_data:
                self.result_text.insert(tk.END, "\n\n化合价标注:\n", "normal")
                for key, valences in valence_data.items():
                    if valences:
                        self.result_text.insert(tk.END, f"{key}: ", "normal")
                        for elem, valence in valences.items():
                            if valence > 0:
                                self.result_text.insert(tk.END, f"{elem}({valence:+d}) ", "green_valence")
                            elif valence < 0:
                                self.result_text.insert(tk.END, f"{elem}({valence}) ", "red_valence")
                            else:
                                self.result_text.insert(tk.END, f"{elem}(0) ", "normal")
                        self.result_text.insert(tk.END, "\n", "normal")
            
            self.update_status("配平完成")
    
    # ==================== 化学式量计算 ====================
    def show_molar_mass(self):
        self.clear_content()
        self.update_status("化学式量计算模式 - 计算相对分子质量")
        
        # 标题
        tk.Label(self.content_frame, text="化学式量计算（相对分子质量）", font=self.title_font, 
                fg="blue").pack(pady=10)
        
        # 说明
        info_frame = tk.Frame(self.content_frame)
        info_frame.pack(pady=5)
        tk.Label(info_frame, text="输入化学式（如 H2O、HCl、Fe2(SO4)3）", 
                font=self.default_font).pack()
        tk.Label(info_frame, text="注意：氯的相对原子质量为35.5，其他元素四舍五入为整数", 
                font=self.default_font, fg="gray").pack()
        
        # 输入区域
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="化学式:", font=self.default_font).pack(side=tk.LEFT)
        self.formula_entry = tk.Entry(input_frame, width=30, font=("Courier", 12))
        self.formula_entry.pack(side=tk.LEFT, padx=10)
        self.formula_entry.bind('<Return>', lambda e: self.calculate_molar_mass())
        
        self.calc_btn = tk.Button(input_frame, text="计算", command=self.calculate_molar_mass, 
                                  bg="lightgreen", width=10, font=self.default_font)
        self.calc_btn.pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域
        result_frame = tk.LabelFrame(self.content_frame, text="计算结果", font=self.title_font)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.molar_result_text = tk.Text(result_frame, height=15, font=("Courier", 11), wrap=tk.WORD)
        self.molar_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 示例按钮
        example_frame = tk.Frame(self.content_frame)
        example_frame.pack(pady=5)
        tk.Label(example_frame, text="示例:").pack(side=tk.LEFT)
        
        examples = ["H2O", "HCl", "H2SO4", "NaCl", "CaCO3", "Fe2(SO4)3"]
        for ex in examples:
            btn = tk.Button(example_frame, text=ex, command=lambda e=ex: self.load_formula_example(e),
                           font=self.default_font, bg="#f0f0f0")
            btn.pack(side=tk.LEFT, padx=5)
    
    def load_formula_example(self, formula):
        """加载化学式示例"""
        self.formula_entry.delete(0, tk.END)
        self.formula_entry.insert(0, formula)
        self.calculate_molar_mass()
    
    def calculate_molar_mass(self):
        """计算化学式量"""
        formula = self.formula_entry.get().strip()
        if not formula:
            messagebox.showwarning("警告", "请输入化学式")
            return
        
        self.update_status(f"正在计算 {formula} 的化学式量...")
        
        mass, detail = ChemicalFormulaParser.calculate_molar_mass(formula)
        
        self.molar_result_text.delete(1.0, tk.END)
        
        if mass == 0:
            self.molar_result_text.insert(tk.END, detail, "normal")
            self.update_status("计算失败")
        else:
            # 显示带下标的化学式
            formatted_formula = self.format_with_subscript(formula)
            self.molar_result_text.insert(tk.END, f"化学式: {formatted_formula}\n\n", "normal")
            self.molar_result_text.insert(tk.END, f"计算过程:\n{detail}\n\n", "normal")
            self.molar_result_text.insert(tk.END, f"化学式量（相对分子质量）: {mass}\n", "blue_coeff")
            self.update_status(f"{formula} 的化学式量为 {mass}")
    
    # ==================== 浓度计算 ====================
    def show_concentration(self):
        self.clear_content()
        self.update_status("浓度计算模式 - 计算溶液浓度")
        
        # 标题
        tk.Label(self.content_frame, text="溶液浓度计算", font=self.title_font, 
                fg="blue").pack(pady=10)
        
        # 创建标签页
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 质量分数计算
        mass_frame = tk.Frame(notebook)
        notebook.add(mass_frame, text="质量分数")
        self.create_mass_fraction_calc(mass_frame)
        
        # 物质的量浓度计算
        molar_frame = tk.Frame(notebook)
        notebook.add(molar_frame, text="物质的量浓度")
        self.create_molar_concentration_calc(molar_frame)
    
    def create_mass_fraction_calc(self, parent):
        """创建质量分数计算界面"""
        # 输入区域
        input_frame = tk.LabelFrame(parent, text="输入参数", font=self.title_font)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(input_frame, text="溶质质量 (g):", font=self.default_font).grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        self.solute_mass_entry = tk.Entry(input_frame, width=20, font=self.default_font)
        self.solute_mass_entry.grid(row=0, column=1, pady=5, padx=10)
        
        tk.Label(input_frame, text="溶液质量 (g):", font=self.default_font).grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        self.solution_mass_entry = tk.Entry(input_frame, width=20, font=self.default_font)
        self.solution_mass_entry.grid(row=1, column=1, pady=5, padx=10)
        
        tk.Label(input_frame, text="或", font=self.default_font).grid(row=2, column=0, columnspan=2, pady=5)
        
        tk.Label(input_frame, text="溶质质量 (g):", font=self.default_font).grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        self.solute_mass2_entry = tk.Entry(input_frame, width=20, font=self.default_font)
        self.solute_mass2_entry.grid(row=3, column=1, pady=5, padx=10)
        
        tk.Label(input_frame, text="溶剂质量 (g):", font=self.default_font).grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        self.solvent_mass_entry = tk.Entry(input_frame, width=20, font=self.default_font)
        self.solvent_mass_entry.grid(row=4, column=1, pady=5, padx=10)
        
        # 计算按钮
        calc_btn = tk.Button(input_frame, text="计算质量分数", command=self.calculate_mass_fraction,
                            bg="lightblue", font=self.default_font)
        calc_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # 结果显示区域
        result_frame = tk.LabelFrame(parent, text="计算结果", font=self.title_font)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.mass_fraction_result = tk.Text(result_frame, height=8, font=self.default_font, wrap=tk.WORD)
        self.mass_fraction_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_molar_concentration_calc(self, parent):
        """创建物质的量浓度计算界面"""
        input_frame = tk.LabelFrame(parent, text="输入参数", font=self.title_font)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(input_frame, text="溶质的物质的量 (mol):", font=self.default_font).grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        self.moles_entry = tk.Entry(input_frame, width=20, font=self.default_font)
        self.moles_entry.grid(row=0, column=1, pady=5, padx=10)
        
        tk.Label(input_frame, text="或", font=self.default_font).grid(row=1, column=0, columnspan=2, pady=5)
        
        tk.Label(input_frame, text="溶质质量 (g):", font=self.default_font).grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        self.solute_mass_molar_entry = tk.Entry(input_frame, width=20, font=self.default_font)
        self.solute_mass_molar_entry.grid(row=2, column=1, pady=5, padx=10)
        
        tk.Label(input_frame, text="摩尔质量 (g/mol):", font=self.default_font).grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        self.molar_mass_entry = tk.Entry(input_frame, width=20, font=self.default_font)
        self.molar_mass_entry.grid(row=3, column=1, pady=5, padx=10)
        tk.Label(input_frame, text="（如 H2SO4: 98）", font=self.default_font, fg="gray").grid(row=3, column=2, pady=5, padx=5)
        
        tk.Label(input_frame, text="溶液体积 (L):", font=self.default_font).grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        self.volume_entry = tk.Entry(input_frame, width=20, font=self.default_font)
        self.volume_entry.grid(row=4, column=1, pady=5, padx=10)
        
        calc_btn = tk.Button(input_frame, text="计算浓度", command=self.calculate_molar_concentration,
                            bg="lightblue", font=self.default_font)
        calc_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        result_frame = tk.LabelFrame(parent, text="计算结果", font=self.title_font)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.molar_concentration_result = tk.Text(result_frame, height=8, font=self.default_font, wrap=tk.WORD)
        self.molar_concentration_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def calculate_mass_fraction(self):
        """计算质量分数"""
        try:
            solute_mass = None
            solution_mass = None
            
            # 获取第一种输入方式
            if self.solute_mass_entry.get() and self.solution_mass_entry.get():
                solute_mass = float(self.solute_mass_entry.get())
                solution_mass = float(self.solution_mass_entry.get())
            
            # 获取第二种输入方式
            elif self.solute_mass2_entry.get() and self.solvent_mass_entry.get():
                solute_mass = float(self.solute_mass2_entry.get())
                solvent_mass = float(self.solvent_mass_entry.get())
                solution_mass = solute_mass + solvent_mass
            
            if solute_mass is None or solution_mass is None:
                self.mass_fraction_result.delete(1.0, tk.END)
                self.mass_fraction_result.insert(tk.END, "错误：请完整输入一组数据", "normal")
                return
            
            if solute_mass <= 0 or solution_mass <= 0:
                self.mass_fraction_result.delete(1.0, tk.END)
                self.mass_fraction_result.insert(tk.END, "错误：质量必须为正数", "normal")
                return
            
            mass_fraction = (solute_mass / solution_mass) * 100
            
            self.mass_fraction_result.delete(1.0, tk.END)
            self.mass_fraction_result.insert(tk.END, f"溶质质量: {solute_mass} g\n", "normal")
            self.mass_fraction_result.insert(tk.END, f"溶液质量: {solution_mass} g\n", "normal")
            self.mass_fraction_result.insert(tk.END, f"溶剂质量: {solution_mass - solute_mass} g\n\n", "normal")
            self.mass_fraction_result.insert(tk.END, f"质量分数: {mass_fraction:.2f}%\n", "blue_coeff")
            self.update_status(f"质量分数计算结果: {mass_fraction:.2f}%")
            
        except ValueError:
            self.mass_fraction_result.delete(1.0, tk.END)
            self.mass_fraction_result.insert(tk.END, "错误：请输入有效的数字", "normal")
    
    def calculate_molar_concentration(self):
        """计算物质的量浓度"""
        try:
            moles = None
            volume = None
            
            # 获取物质的量
            if self.moles_entry.get():
                moles = float(self.moles_entry.get())
            elif self.solute_mass_molar_entry.get() and self.molar_mass_entry.get():
                solute_mass = float(self.solute_mass_molar_entry.get())
                molar_mass = float(self.molar_mass_entry.get())
                if molar_mass <= 0:
                    raise ValueError("摩尔质量必须为正数")
                moles = solute_mass / molar_mass
            
            # 获取体积
            if self.volume_entry.get():
                volume = float(self.volume_entry.get())
            
            if moles is None or volume is None:
                self.molar_concentration_result.delete(1.0, tk.END)
                self.molar_concentration_result.insert(tk.END, "错误：请完整输入所需数据", "normal")
                return
            
            if volume <= 0:
                self.molar_concentration_result.delete(1.0, tk.END)
                self.molar_concentration_result.insert(tk.END, "错误：体积必须为正数", "normal")
                return
            
            concentration = moles / volume
            
            self.molar_concentration_result.delete(1.0, tk.END)
            self.molar_concentration_result.insert(tk.END, f"溶质的物质的量: {moles:.4f} mol\n", "normal")
            self.molar_concentration_result.insert(tk.END, f"溶液体积: {volume} L\n\n", "normal")
            self.molar_concentration_result.insert(tk.END, f"物质的量浓度: {concentration:.4f} mol/L\n", "blue_coeff")
            self.update_status(f"浓度计算结果: {concentration:.4f} mol/L")
            
        except ValueError as e:
            self.molar_concentration_result.delete(1.0, tk.END)
            self.molar_concentration_result.insert(tk.END, f"错误：{str(e)}", "normal")
    
    # ==================== 元素周期表界面 ====================
    def show_periodic(self):
        self.clear_content()
        self.update_status("元素周期表模式 - 点击元素查看详细信息（共118种元素）")
        
        # 创建滚动区域
        canvas = tk.Canvas(self.content_frame)
        scrollbar = tk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 定义周期表布局（完整版）
        rows_data = [
            # 周期1
            [("H", 1), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("He", 18)],
            # 周期2
            [("Li", 1), ("Be", 2), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("B", 13), ("C", 14), ("N", 15), ("O", 16), ("F", 17), ("Ne", 18)],
            # 周期3
            [("Na", 1), ("Mg", 2), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("", 0), ("Al", 13), ("Si", 14), ("P", 15), ("S", 16), ("Cl", 17), ("Ar", 18)],
            # 周期4
            [("K", 1), ("Ca", 2), ("Sc", 3), ("Ti", 4), ("V", 5), ("Cr", 6), ("Mn", 7), ("Fe", 8), ("Co", 9), ("Ni", 10), ("Cu", 11), ("Zn", 12), ("Ga", 13), ("Ge", 14), ("As", 15), ("Se", 16), ("Br", 17), ("Kr", 18)],
            # 周期5
            [("Rb", 1), ("Sr", 2), ("Y", 3), ("Zr", 4), ("Nb", 5), ("Mo", 6), ("Tc", 7), ("Ru", 8), ("Rh", 9), ("Pd", 10), ("Ag", 11), ("Cd", 12), ("In", 13), ("Sn", 14), ("Sb", 15), ("Te", 16), ("I", 17), ("Xe", 18)],
            # 周期6
            [("Cs", 1), ("Ba", 2), ("La", 3), ("Hf", 4), ("Ta", 5), ("W", 6), ("Re", 7), ("Os", 8), ("Ir", 9), ("Pt", 10), ("Au", 11), ("Hg", 12), ("Tl", 13), ("Pb", 14), ("Bi", 15), ("Po", 16), ("At", 17), ("Rn", 18)],
            # 周期7
            [("Fr", 1), ("Ra", 2), ("Ac", 3), ("Rf", 4), ("Db", 5), ("Sg", 6), ("Bh", 7), ("Hs", 8), ("Mt", 9), ("Ds", 10), ("Rg", 11), ("Cn", 12), ("Nh", 13), ("Fl", 14), ("Mc", 15), ("Lv", 16), ("Ts", 17), ("Og", 18)],
        ]
        
        # 创建元素按钮
        for r, row in enumerate(rows_data):
            for c, (symbol, group) in enumerate(row):
                if symbol == "":
                    continue
                    
                if symbol in ExtendedPeriodicTable.elements_data:
                    data = ExtendedPeriodicTable.elements_data[symbol]
                    
                    # 根据族设置颜色
                    group_num = data["group"]
                    if group_num == 1:
                        color = "#ffcccc"
                    elif group_num == 2:
                        color = "#ccffcc"
                    elif 3 <= group_num <= 12:
                        color = "#ccccff"
                    elif 13 <= group_num <= 16:
                        color = "#ffffcc"
                    elif group_num == 17:
                        color = "#ffcc99"
                    elif group_num == 18:
                        color = "#99ccff"
                    else:
                        color = "#f0f0f0"
                    
                    btn = tk.Button(scrollable_frame, 
                                   text=f"{symbol}\n{data['atomic']}", 
                                   width=6, height=3,
                                   bg=color,
                                   font=("Microsoft YaHei", 8),
                                   command=lambda s=symbol: self.show_element_info(s))
                    btn.grid(row=r, column=c, padx=1, pady=1)
        
        # 添加镧系锕系元素
        lanthanides = ["Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"]
        actinides = ["Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr"]
        
        lanthanide_frame = tk.Frame(scrollable_frame)
        lanthanide_frame.grid(row=len(rows_data), column=0, columnspan=18, pady=5, sticky=tk.W)
        
        tk.Label(lanthanide_frame, text="镧系:", font=self.default_font).pack(side=tk.LEFT, padx=5)
        for symbol in lanthanides:
            if symbol in ExtendedPeriodicTable.elements_data:
                btn = tk.Button(lanthanide_frame, text=symbol, width=4, height=1,
                               bg="#ffffcc", font=("Microsoft YaHei", 8),
                               command=lambda s=symbol: self.show_element_info(s))
                btn.pack(side=tk.LEFT, padx=1)
        
        actinide_frame = tk.Frame(scrollable_frame)
        actinide_frame.grid(row=len(rows_data)+1, column=0, columnspan=18, pady=5, sticky=tk.W)
        
        tk.Label(actinide_frame, text="锕系:", font=self.default_font).pack(side=tk.LEFT, padx=5)
        for symbol in actinides:
            if symbol in ExtendedPeriodicTable.elements_data:
                btn = tk.Button(actinide_frame, text=symbol, width=4, height=1,
                               bg="#ffcc99", font=("Microsoft YaHei", 8),
                               command=lambda s=symbol: self.show_element_info(s))
                btn.pack(side=tk.LEFT, padx=1)
        
        # 添加图例
        legend_frame = tk.Frame(scrollable_frame)
        legend_frame.grid(row=len(rows_data)+2, column=0, columnspan=18, pady=10)
        
        legends = [
            ("碱金属", "#ffcccc"), ("碱土金属", "#ccffcc"), ("过渡金属", "#ccccff"),
            ("非金属", "#ffffcc"), ("卤素", "#ffcc99"), ("稀有气体", "#99ccff"),
            ("镧系", "#ffffcc"), ("锕系", "#ffcc99")
        ]
        
        for text, color in legends:
            frame = tk.Frame(legend_frame)
            frame.pack(side=tk.LEFT, padx=8)
            tk.Label(frame, text="  ", bg=color, width=2).pack(side=tk.LEFT)
            tk.Label(frame, text=text, font=self.default_font).pack(side=tk.LEFT)
    
    def show_element_info(self, symbol):
        """显示元素详细信息"""
        data = ExtendedPeriodicTable.elements_data.get(symbol)
        if data:
            electron_layers = ExtendedPeriodicTable.electron_config.get(symbol, "未知")
            atomic_mass = AtomicMass.get_mass(symbol)
            
            info = f"元素符号: {symbol}\n"
            info += f"中文名称: {data['name']}\n"
            info += f"原子序数: {data['atomic']}\n"
            info += f"原子量: {data['mass']} ({atomic_mass})\n"
            info += f"族: {data['group']}\n"
            info += f"周期: {data['period']}\n"
            info += f"电子排布: {data['config']}\n"
            info += f"电子层排布: {electron_layers}\n"
            info += f"简介: {data['desc']}\n"
            messagebox.showinfo(f"元素信息 - {symbol}", info)
        else:
            messagebox.showinfo("元素信息", f"未找到 {symbol} 的详细信息")
    
    # ==================== 关于界面 ====================
    def show_about(self):
        self.clear_content()
        self.update_status("关于化学工具箱")
        
        about_text = """化学工具箱 (Chemistry Toolbox)
版本: 0.4
更新日期: 2025年3月26日

新增功能 (v0.4):
✓ 新增计算功能（化学式量计算、浓度计算）
✓ 化学式量计算支持括号和复杂化学式
✓ 浓度计算包含质量分数和物质的量浓度
✓ 扩展元素周期表至118种完整元素
✓ 增加镧系和锕系元素显示
✓ 优化相对原子质量数据

新增功能 (v0.3):
✓ 离子配平使用星号标注
✓ 配平结果显示为下标
✓ 增加电子层排布信息

主要功能:
• 化学方程式配平（含离子方程式）
• 完整元素周期表（118种元素）
• 化学式量计算
• 浓度计算（质量分数、物质的量浓度）
• 化合价智能标注

开发者: 化学爱好者
开源协议: MIT License

感谢使用本软件！"""
        
        text_widget = scrolledtext.ScrolledText(self.content_frame, wrap=tk.WORD, 
                                                font=self.default_font)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, about_text)
        text_widget.config(state=tk.DISABLED)
    
    # ==================== 帮助界面 ====================
    def show_help(self):
        self.clear_content()
        self.update_status("帮助 - 使用说明")
        
        help_text = """化学工具箱 v0.4 使用帮助

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【1. 配平功能】

使用方法：
  • 在输入框中输入化学方程式
  • 点击"配平"按钮或按回车键

离子方程式格式：
  • 使用星号标注离子电荷
  • 负离子：MnO4** 表示 MnO₄⁻
  • 正离子：Fe** 表示 Fe²⁺
  • 示例：MnO4**+Fe**=Mn**+Fe**

支持示例：
  • H2+O2=H2O              → 2H₂+O₂=2H₂O
  • Fe2O3+CO=Fe+CO2        → Fe₂O₃+3CO=2Fe+3CO₂
  • MnO4**+Fe**=Mn**+Fe**  → MnO₄⁻+5Fe²⁺=Mn²⁺+5Fe³⁺

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【2. 计算功能】

化学式量计算：
  • 输入化学式（如 H2O、H2SO4、Fe2(SO4)3）
  • 自动计算相对分子质量
  • 氯的相对原子质量为35.5，其他元素四舍五入

浓度计算：
  • 质量分数：输入溶质和溶液（或溶剂）质量
  • 物质的量浓度：输入物质的量（或质量+摩尔质量）和体积

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【3. 元素周期表】

功能说明：
  • 包含118种完整元素数据
  • 镧系和锕系单独显示
  • 点击元素查看详细信息

元素信息包括：
  • 中文名称、原子序数、原子量
  • 族、周期、电子排布
  • 电子层排布、简要介绍

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

更新日志 v0.4 (2025-03-26):
  • 新增计算功能（化学式量、浓度）
  • 扩展元素周期表至118种完整元素
  • 增加镧系和锕系元素显示
  • 优化相对原子质量数据
  • 改进界面布局

更新日志 v0.3 (2025-03-20):
  • 离子配平改用星号标注
  • 配平结果显示下标
  • 增加电子层排布信息

更新日志 v0.2 (2025-03-15):
  • 新增离子方程式配平支持
  • 增加至80+种元素数据

更新日志 v0.1 (2025-03-10):
  • 初始版本发布
  • 基础方程式配平功能

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

注意事项:
  • 离子必须使用星号标注，不能使用+/-号
  • 元素符号大小写敏感（如 Co 钴，CO 一氧化碳）
  • 氯的相对原子质量为35.5，其他元素为整数
"""
        
        text_widget = scrolledtext.ScrolledText(self.content_frame, wrap=tk.WORD, 
                                                font=self.default_font)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

# ==================== 程序入口 ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = ChemistryToolboxV4(root)
    root.mainloop()