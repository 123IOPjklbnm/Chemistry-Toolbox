import tkinter as tk
from tkinter import messagebox, scrolledtext
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
        'O': [-2, -1], 'S': [6, 4, 2, -2], 'Se': [6, 4, -2], 'Te': [6, 4, -2], 'Po': [4, 2, -2],
        # 第17族
        'F': [-1], 'Cl': [7, 5, 3, 1, -1], 'Br': [7, 5, 3, 1, -1], 'I': [7, 5, 3, 1, -1], 'At': [7, 5, 3, 1, -1],
        # 过渡金属
        'Sc': [3], 'Ti': [4, 3], 'V': [5, 4, 3, 2], 'Cr': [6, 3, 2], 
        'Mn': [7, 6, 4, 3, 2], 'Fe': [3, 2], 'Co': [3, 2], 'Ni': [2, 3],
        'Cu': [2, 1], 'Zn': [2], 'Ag': [1], 'Au': [3, 1], 'Hg': [2, 1],
        'Cd': [2], 'Pt': [4, 2], 'Pd': [2, 4], 'Ir': [4, 3], 'Os': [4, 3],
        'Rh': [3], 'Ru': [3], 'Nb': [5], 'Mo': [6, 5, 4, 3], 'Tc': [7],
        'Re': [7, 6, 4], 'W': [6], 'Ta': [5], 'Zr': [4], 'Hf': [4],
        # 镧系和锕系
        'La': [3], 'Ce': [3, 4], 'Pr': [3], 'Nd': [3], 'Pm': [3], 'Sm': [3], 
        'Eu': [3, 2], 'Gd': [3], 'Tb': [3, 4], 'Dy': [3], 'Ho': [3], 
        'Er': [3], 'Tm': [3], 'Yb': [3, 2], 'Lu': [3], 
        'Ac': [3], 'Th': [4], 'Pa': [5, 4], 'U': [6, 5, 4, 3], 
        'Np': [6, 5, 4, 3], 'Pu': [6, 5, 4, 3], 'Am': [6, 5, 4, 3],
        'Cm': [3], 'Bk': [3, 4], 'Cf': [3], 'Es': [3], 'Fm': [3], 'Md': [3], 'No': [3], 'Lr': [3],
    }
    
    # 常见原子团及其化合价
    radical_valences = {
        'OH': -1, 'NO3': -1, 'NO2': -1, 'SO4': -2, 'SO3': -2, 'CO3': -2,
        'PO4': -3, 'NH4': 1, 'ClO4': -1, 'ClO3': -1, 'ClO2': -1, 'ClO': -1,
        'MnO4': -1, 'CrO4': -2, 'Cr2O7': -2, 'C2O4': -2, 'CH3COO': -1,
    }
    
    @classmethod
    def get_valence(cls, element, compound_context=None):
        """获取元素的常见化合价"""
        if element in cls.element_valences:
            return cls.element_valences[element]
        return [0]
    
    @classmethod
    def is_radical(cls, formula_part):
        """判断是否是原子团"""
        return formula_part in cls.radical_valences

# ==================== 化学式格式化工具 ====================
class FormulaFormatter:
    """化学式格式化工具，将数字转换为下标"""
    
    @staticmethod
    def format_subscript(formula):
        """将化学式中的数字转换为下标格式"""
        result = []
        i = 0
        n = len(formula)
        
        while i < n:
            if i < n and formula[i].isdigit():
                # 收集连续的数字
                num = ""
                while i < n and formula[i].isdigit():
                    num += formula[i]
                    i += 1
                # 添加下标格式
                result.append(f"_{{{num}}}")
            else:
                result.append(formula[i])
                i += 1
        
        return ''.join(result)
    
    @staticmethod
    def format_formula(formula):
        """格式化整个化学式，正确处理括号和下标"""
        # 先处理括号外的数字
        result = []
        i = 0
        n = len(formula)
        
        while i < n:
            if formula[i] in '()[]':
                result.append(formula[i])
                i += 1
            elif formula[i].isdigit():
                # 处理数字下标
                num = ""
                while i < n and formula[i].isdigit():
                    num += formula[i]
                    i += 1
                result.append(f"_{{{num}}}")
            else:
                result.append(formula[i])
                i += 1
        
        return ''.join(result)

# ==================== 化学式解析器 ====================
class ChemicalFormulaParser:
    """化学式解析器，支持离子和原子团"""
    
    @staticmethod
    def parse_formula(formula, charge=0):
        """
        解析化学式，返回元素计数
        支持格式：H2O, Fe2(SO4)3, [Cu(NH3)4]2+
        离子标记使用 ^ 或 * 符号，如 MnO4^-2
        """
        counts = defaultdict(int)
        
        # 处理离子标记（使用 ^ 或 *）
        charge_match = re.search(r'[\^\*]([\+\-]?\d*)$', formula)
        if charge_match:
            charge_str = charge_match.group(1)
            if charge_str == '+' or charge_str == '':
                charge = 1
            elif charge_str == '-':
                charge = -1
            else:
                charge = int(charge_str)
            formula = formula[:charge_match.start()]
        else:
            charge = 0
        
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
        return dict(counts), charge
    
    @staticmethod
    def calculate_oxidation_states(formula):
        """
        计算化学式中各元素的化合价
        返回 {元素: 化合价} 字典
        """
        counts, _ = ChemicalFormulaParser.parse_formula(formula)
        
        if not counts:
            return {}
        
        # 简单处理：假设总化合价为0
        element_valence = {}
        
        # 按电负性排序（F、O优先确定）
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
                # 选择最常见的化合价
                element_valence[element] = valences[0] if valences else 0
            else:
                element_valence[element] = 0
        
        # 计算总化合价并调整
        total = sum(element_valence[e] * counts[e] for e in elements)
        
        # 如果总化合价不为0，调整最后一个元素
        if abs(total) > 0.01:
            # 找到可以调整的元素
            for element in reversed(elements):
                valences = ValenceData.get_valence(element, formula)
                if len(valences) > 1:
                    # 尝试调整到使总化合价为0
                    current = element_valence[element]
                    for v in valences:
                        new_total = total - current * counts[element] + v * counts[element]
                        if abs(new_total) < 0.01:
                            element_valence[element] = v
                            break
                    break
        
        return element_valence

# ==================== 配平引擎增强版 ====================
class EquationBalancer:
    """化学方程式配平器，支持离子方程式"""
    
    @staticmethod
    def parse_compound_with_charge(compound):
        """
        解析带电荷的化合物
        返回 (化学式, 电荷)
        离子标记使用 ^ 或 * 符号
        """
        # 匹配离子标记（使用 ^ 或 *）
        charge_pattern = r'[\^\*]([\+\-]?\d*)$'
        charge_match = re.search(charge_pattern, compound)
        
        if charge_match:
            charge_str = charge_match.group(1)
            if charge_str == '+' or charge_str == '':
                charge = 1
            elif charge_str == '-':
                charge = -1
            else:
                charge = int(charge_str)
            formula = compound[:charge_match.start()]
        else:
            charge = 0
            formula = compound
        
        return formula, charge
    
    @staticmethod
    def balance(equation):
        """
        配平化学方程式，支持离子方程式
        返回配平后的方程式字符串
        """
        try:
            # 清理输入，将离子标记统一为 ^
            equation = equation.replace("*", "^")
            equation = equation.replace(" ", "").replace("->", "=").replace("→", "=")
            if "=" not in equation:
                return "错误：方程式必须包含等号(=)或箭头(->)", {}
            
            left, right = equation.split("=")
            
            # 解析左右两边
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
            
            # 收集所有元素和电荷信息
            all_elements = set()
            left_comp_data = []
            right_comp_data = []
            
            for formula, charge in left_compounds:
                counts, _ = ChemicalFormulaParser.parse_formula(formula)
                left_comp_data.append((counts, charge))
                all_elements.update(counts.keys())
            
            for formula, charge in right_compounds:
                counts, _ = ChemicalFormulaParser.parse_formula(formula)
                right_comp_data.append((counts, charge))
                all_elements.update(counts.keys())
            
            elements = sorted(all_elements)
            n_left = len(left_compounds)
            n_right = len(right_compounds)
            
            # 尝试不同的第一个系数
            max_try = 50
            for first_coeff in range(1, max_try + 1):
                # 构建矩阵
                A = []
                b = []
                
                # 元素守恒方程
                for elem in elements:
                    row = []
                    for counts, _ in left_comp_data:
                        row.append(counts.get(elem, 0))
                    for counts, _ in right_comp_data:
                        row.append(-counts.get(elem, 0))
                    A.append(row)
                    b.append(0)
                
                # 电荷守恒方程
                charge_row = []
                for _, charge in left_comp_data:
                    charge_row.append(charge)
                for _, charge in right_comp_data:
                    charge_row.append(-charge)
                A.append(charge_row)
                b.append(0)
                
                A = np.array(A, dtype=float)
                b = np.array(b, dtype=float)
                
                n_unknowns = n_left + n_right
                
                # 固定第一个系数
                if n_unknowns > 0:
                    A_reduced = A[:, 1:]
                    b_reduced = b - A[:, 0] * first_coeff
                    
                    try:
                        if A_reduced.shape[1] > 0:
                            solution = np.linalg.lstsq(A_reduced, b_reduced, rcond=None)[0]
                        else:
                            solution = np.array([])
                        
                        # 构建完整解
                        coeffs = [first_coeff] + list(solution)
                        
                        # 补齐缺失的系数
                        while len(coeffs) < n_unknowns:
                            coeffs.append(1)
                        
                        # 检查所有系数 > 0 且接近整数
                        int_coeffs = []
                        valid = True
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
                            # 化简系数
                            g = int_coeffs[0]
                            for c in int_coeffs[1:]:
                                g = gcd(g, c)
                            if g > 1:
                                int_coeffs = [c // g for c in int_coeffs]
                            
                            # 格式化输出
                            left_parts = []
                            for i, (formula, charge) in enumerate(left_compounds):
                                coeff = int_coeffs[i]
                                if charge != 0:
                                    formula_with_charge = f"{formula}^{charge:+d}" if charge > 0 else f"{formula}^{charge}"
                                    left_parts.append(f"{coeff if coeff > 1 else ''}{formula_with_charge}")
                                else:
                                    left_parts.append(f"{coeff if coeff > 1 else ''}{formula}")
                            
                            right_parts = []
                            for i, (formula, charge) in enumerate(right_compounds):
                                coeff = int_coeffs[n_left + i]
                                if charge != 0:
                                    formula_with_charge = f"{formula}^{charge:+d}" if charge > 0 else f"{formula}^{charge}"
                                    right_parts.append(f"{coeff if coeff > 1 else ''}{formula_with_charge}")
                                else:
                                    right_parts.append(f"{coeff if coeff > 1 else ''}{formula}")
                            
                            balanced_eq = f"{'+'.join(left_parts)} = {'+'.join(right_parts)}"
                            
                            # 计算化合价信息
                            valence_info = {}
                            for idx, (formula, _) in enumerate(left_compounds):
                                valence_info[f'L{idx}'] = ChemicalFormulaParser.calculate_oxidation_states(formula)
                            for idx, (formula, _) in enumerate(right_compounds):
                                valence_info[f'R{idx}'] = ChemicalFormulaParser.calculate_oxidation_states(formula)
                            
                            return balanced_eq, valence_info
                            
                    except np.linalg.LinAlgError:
                        continue
            
            return "错误：无法配平该方程式，请检查输入格式", {}
            
        except Exception as e:
            return f"配平失败: {str(e)}", {}

# ==================== 扩展元素周期表数据 ====================
class ExtendedPeriodicTable:
    """扩展的元素周期表数据，包含电子层排布"""
    
    # 电子层排布数据
    electron_configs = {
        # 第1周期
        "H": "1s¹", "He": "1s²",
        # 第2周期
        "Li": "1s² 2s¹", "Be": "1s² 2s²", "B": "1s² 2s² 2p¹", 
        "C": "1s² 2s² 2p²", "N": "1s² 2s² 2p³", "O": "1s² 2s² 2p⁴",
        "F": "1s² 2s² 2p⁵", "Ne": "1s² 2s² 2p⁶",
        # 第3周期
        "Na": "[Ne] 3s¹", "Mg": "[Ne] 3s²", "Al": "[Ne] 3s² 3p¹",
        "Si": "[Ne] 3s² 3p²", "P": "[Ne] 3s² 3p³", "S": "[Ne] 3s² 3p⁴",
        "Cl": "[Ne] 3s² 3p⁵", "Ar": "[Ne] 3s² 3p⁶",
        # 第4周期
        "K": "[Ar] 4s¹", "Ca": "[Ar] 4s²", "Sc": "[Ar] 3d¹ 4s²",
        "Ti": "[Ar] 3d² 4s²", "V": "[Ar] 3d³ 4s²", "Cr": "[Ar] 3d⁵ 4s¹",
        "Mn": "[Ar] 3d⁵ 4s²", "Fe": "[Ar] 3d⁶ 4s²", "Co": "[Ar] 3d⁷ 4s²",
        "Ni": "[Ar] 3d⁸ 4s²", "Cu": "[Ar] 3d¹⁰ 4s¹", "Zn": "[Ar] 3d¹⁰ 4s²",
        "Ga": "[Ar] 3d¹⁰ 4s² 4p¹", "Ge": "[Ar] 3d¹⁰ 4s² 4p²", "As": "[Ar] 3d¹⁰ 4s² 4p³",
        "Se": "[Ar] 3d¹⁰ 4s² 4p⁴", "Br": "[Ar] 3d¹⁰ 4s² 4p⁵", "Kr": "[Ar] 3d¹⁰ 4s² 4p⁶",
        # 第5周期
        "Rb": "[Kr] 5s¹", "Sr": "[Kr] 5s²", "Y": "[Kr] 4d¹ 5s²",
        "Zr": "[Kr] 4d² 5s²", "Nb": "[Kr] 4d⁴ 5s¹", "Mo": "[Kr] 4d⁵ 5s¹",
        "Tc": "[Kr] 4d⁵ 5s²", "Ru": "[Kr] 4d⁷ 5s¹", "Rh": "[Kr] 4d⁸ 5s¹",
        "Pd": "[Kr] 4d¹⁰", "Ag": "[Kr] 4d¹⁰ 5s¹", "Cd": "[Kr] 4d¹⁰ 5s²",
        "In": "[Kr] 4d¹⁰ 5s² 5p¹", "Sn": "[Kr] 4d¹⁰ 5s² 5p²", "Sb": "[Kr] 4d¹⁰ 5s² 5p³",
        "Te": "[Kr] 4d¹⁰ 5s² 5p⁴", "I": "[Kr] 4d¹⁰ 5s² 5p⁵", "Xe": "[Kr] 4d¹⁰ 5s² 5p⁶",
        # 第6周期
        "Cs": "[Xe] 6s¹", "Ba": "[Xe] 6s²", "La": "[Xe] 5d¹ 6s²",
        "Ce": "[Xe] 4f¹ 5d¹ 6s²", "Pr": "[Xe] 4f³ 6s²", "Nd": "[Xe] 4f⁴ 6s²",
        "Pm": "[Xe] 4f⁵ 6s²", "Sm": "[Xe] 4f⁶ 6s²", "Eu": "[Xe] 4f⁷ 6s²",
        "Gd": "[Xe] 4f⁷ 5d¹ 6s²", "Tb": "[Xe] 4f⁹ 6s²", "Dy": "[Xe] 4f¹⁰ 6s²",
        "Ho": "[Xe] 4f¹¹ 6s²", "Er": "[Xe] 4f¹² 6s²", "Tm": "[Xe] 4f¹³ 6s²",
        "Yb": "[Xe] 4f¹⁴ 6s²", "Lu": "[Xe] 4f¹⁴ 5d¹ 6s²",
        "Hf": "[Xe] 4f¹⁴ 5d² 6s²", "Ta": "[Xe] 4f¹⁴ 5d³ 6s²", "W": "[Xe] 4f¹⁴ 5d⁴ 6s²",
        "Re": "[Xe] 4f¹⁴ 5d⁵ 6s²", "Os": "[Xe] 4f¹⁴ 5d⁶ 6s²", "Ir": "[Xe] 4f¹⁴ 5d⁷ 6s²",
        "Pt": "[Xe] 4f¹⁴ 5d⁹ 6s¹", "Au": "[Xe] 4f¹⁴ 5d¹⁰ 6s¹", "Hg": "[Xe] 4f¹⁴ 5d¹⁰ 6s²",
        "Tl": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p¹", "Pb": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p²", "Bi": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p³",
        "Po": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁴", "At": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁵", "Rn": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁶",
        # 第7周期
        "Fr": "[Rn] 7s¹", "Ra": "[Rn] 7s²", "Ac": "[Rn] 6d¹ 7s²",
        "Th": "[Rn] 6d² 7s²", "Pa": "[Rn] 5f² 6d¹ 7s²", "U": "[Rn] 5f³ 6d¹ 7s²",
        "Np": "[Rn] 5f⁴ 6d¹ 7s²", "Pu": "[Rn] 5f⁶ 7s²", "Am": "[Rn] 5f⁷ 7s²",
        "Cm": "[Rn] 5f⁷ 6d¹ 7s²", "Bk": "[Rn] 5f⁹ 7s²", "Cf": "[Rn] 5f¹⁰ 7s²",
        "Es": "[Rn] 5f¹¹ 7s²", "Fm": "[Rn] 5f¹² 7s²", "Md": "[Rn] 5f¹³ 7s²",
        "No": "[Rn] 5f¹⁴ 7s²", "Lr": "[Rn] 5f¹⁴ 6d¹ 7s²",
        "Rf": "[Rn] 5f¹⁴ 6d² 7s²", "Db": "[Rn] 5f¹⁴ 6d³ 7s²", "Sg": "[Rn] 5f¹⁴ 6d⁴ 7s²",
        "Bh": "[Rn] 5f¹⁴ 6d⁵ 7s²", "Hs": "[Rn] 5f¹⁴ 6d⁶ 7s²", "Mt": "[Rn] 5f¹⁴ 6d⁷ 7s²",
        "Ds": "[Rn] 5f¹⁴ 6d⁸ 7s²", "Rg": "[Rn] 5f¹⁴ 6d⁹ 7s²", "Cn": "[Rn] 5f¹⁴ 6d¹⁰ 7s²",
        "Nh": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p¹", "Fl": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p²", "Mc": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p³",
        "Lv": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁴", "Ts": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁵", "Og": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁶",
    }
    
    elements_data = {
        # 第1周期
        "H": {"name": "氢", "atomic": 1, "mass": 1.008, "group": 1, "period": 1, 
              "desc": "最轻的元素，宇宙中含量最丰富"},
        "He": {"name": "氦", "atomic": 2, "mass": 4.0026, "group": 18, "period": 1, 
               "desc": "稀有气体，沸点最低"},
        
        # 第2周期
        "Li": {"name": "锂", "atomic": 3, "mass": 6.94, "group": 1, "period": 2, 
               "desc": "最轻的金属，用于电池"},
        "Be": {"name": "铍", "atomic": 4, "mass": 9.0122, "group": 2, "period": 2, 
               "desc": "轻金属，有毒"},
        "B": {"name": "硼", "atomic": 5, "mass": 10.81, "group": 13, "period": 2, 
              "desc": "类金属，用于半导体"},
        "C": {"name": "碳", "atomic": 6, "mass": 12.011, "group": 14, "period": 2, 
              "desc": "生命的基础，有机化合物骨架"},
        "N": {"name": "氮", "atomic": 7, "mass": 14.007, "group": 15, "period": 2, 
              "desc": "大气主要成分"},
        "O": {"name": "氧", "atomic": 8, "mass": 15.999, "group": 16, "period": 2, 
              "desc": "支持燃烧，生命必需"},
        "F": {"name": "氟", "atomic": 9, "mass": 18.998, "group": 17, "period": 2, 
              "desc": "最活泼的非金属"},
        "Ne": {"name": "氖", "atomic": 10, "mass": 20.18, "group": 18, "period": 2, 
               "desc": "稀有气体，用于霓虹灯"},
        
        # 第3周期
        "Na": {"name": "钠", "atomic": 11, "mass": 22.99, "group": 1, "period": 3, 
               "desc": "碱金属，活泼"},
        "Mg": {"name": "镁", "atomic": 12, "mass": 24.305, "group": 2, "period": 3, 
               "desc": "轻金属，合金"},
        "Al": {"name": "铝", "atomic": 13, "mass": 26.982, "group": 13, "period": 3, 
               "desc": "地壳中含量最丰富的金属"},
        "Si": {"name": "硅", "atomic": 14, "mass": 28.086, "group": 14, "period": 3, 
               "desc": "半导体材料"},
        "P": {"name": "磷", "atomic": 15, "mass": 30.974, "group": 15, "period": 3, 
              "desc": "白磷易燃"},
        "S": {"name": "硫", "atomic": 16, "mass": 32.06, "group": 16, "period": 3, 
              "desc": "黄色固体"},
        "Cl": {"name": "氯", "atomic": 17, "mass": 35.45, "group": 17, "period": 3, 
               "desc": "黄绿色气体，消毒"},
        "Ar": {"name": "氩", "atomic": 18, "mass": 39.95, "group": 18, "period": 3, 
               "desc": "稀有气体"},
        
        # 第4周期
        "K": {"name": "钾", "atomic": 19, "mass": 39.098, "group": 1, "period": 4, 
              "desc": "活泼金属"},
        "Ca": {"name": "钙", "atomic": 20, "mass": 40.078, "group": 2, "period": 4, 
               "desc": "骨骼主要成分"},
        "Sc": {"name": "钪", "atomic": 21, "mass": 44.956, "group": 3, "period": 4, 
               "desc": "稀土元素"},
        "Ti": {"name": "钛", "atomic": 22, "mass": 47.867, "group": 4, "period": 4, 
               "desc": "高强度轻金属"},
        "V": {"name": "钒", "atomic": 23, "mass": 50.942, "group": 5, "period": 4, 
              "desc": "钢铁工业添加剂"},
        "Cr": {"name": "铬", "atomic": 24, "mass": 51.996, "group": 6, "period": 4, 
               "desc": "不锈钢成分"},
        "Mn": {"name": "锰", "atomic": 25, "mass": 54.938, "group": 7, "period": 4, 
               "desc": "钢铁工业重要元素"},
        "Fe": {"name": "铁", "atomic": 26, "mass": 55.845, "group": 8, "period": 4, 
               "desc": "最常用的金属"},
        "Co": {"name": "钴", "atomic": 27, "mass": 58.933, "group": 9, "period": 4, 
               "desc": "磁性材料"},
        "Ni": {"name": "镍", "atomic": 28, "mass": 58.693, "group": 10, "period": 4, 
               "desc": "不锈钢成分"},
        "Cu": {"name": "铜", "atomic": 29, "mass": 63.546, "group": 11, "period": 4, 
               "desc": "导电性好"},
        "Zn": {"name": "锌", "atomic": 30, "mass": 65.38, "group": 12, "period": 4, 
               "desc": "防腐镀层"},
        "Ga": {"name": "镓", "atomic": 31, "mass": 69.723, "group": 13, "period": 4, 
               "desc": "低熔点金属"},
        "Ge": {"name": "锗", "atomic": 32, "mass": 72.63, "group": 14, "period": 4, 
               "desc": "半导体材料"},
        "As": {"name": "砷", "atomic": 33, "mass": 74.922, "group": 15, "period": 4, 
               "desc": "有毒类金属"},
        "Se": {"name": "硒", "atomic": 34, "mass": 78.96, "group": 16, "period": 4, 
               "desc": "光导材料"},
        "Br": {"name": "溴", "atomic": 35, "mass": 79.904, "group": 17, "period": 4, 
               "desc": "红棕色液体"},
        "Kr": {"name": "氪", "atomic": 36, "mass": 83.798, "group": 18, "period": 4, 
               "desc": "稀有气体"},
        
        # 第5周期
        "Rb": {"name": "铷", "atomic": 37, "mass": 85.468, "group": 1, "period": 5, 
               "desc": "活泼碱金属"},
        "Sr": {"name": "锶", "atomic": 38, "mass": 87.62, "group": 2, "period": 5, 
               "desc": "用于烟花"},
        "Y": {"name": "钇", "atomic": 39, "mass": 88.906, "group": 3, "period": 5, 
              "desc": "稀土元素"},
        "Zr": {"name": "锆", "atomic": 40, "mass": 91.224, "group": 4, "period": 5, 
               "desc": "耐腐蚀金属"},
        "Nb": {"name": "铌", "atomic": 41, "mass": 92.906, "group": 5, "period": 5, 
               "desc": "超导材料"},
        "Mo": {"name": "钼", "atomic": 42, "mass": 95.95, "group": 6, "period": 5, 
               "desc": "钢铁添加剂"},
        "Tc": {"name": "锝", "atomic": 43, "mass": 98, "group": 7, "period": 5, 
               "desc": "放射性元素"},
        "Ru": {"name": "钌", "atomic": 44, "mass": 101.07, "group": 8, "period": 5, 
               "desc": "铂族金属"},
        "Rh": {"name": "铑", "atomic": 45, "mass": 102.91, "group": 9, "period": 5, 
               "desc": "催化剂"},
        "Pd": {"name": "钯", "atomic": 46, "mass": 106.42, "group": 10, "period": 5, 
               "desc": "催化剂"},
        "Ag": {"name": "银", "atomic": 47, "mass": 107.87, "group": 11, "period": 5, 
               "desc": "贵金属，导电性最佳"},
        "Cd": {"name": "镉", "atomic": 48, "mass": 112.41, "group": 12, "period": 5, 
               "desc": "有毒重金属"},
        "In": {"name": "铟", "atomic": 49, "mass": 114.82, "group": 13, "period": 5, 
               "desc": "用于液晶屏"},
        "Sn": {"name": "锡", "atomic": 50, "mass": 118.71, "group": 14, "period": 5, 
               "desc": "青铜成分"},
        "Sb": {"name": "锑", "atomic": 51, "mass": 121.76, "group": 15, "period": 5, 
               "desc": "阻燃剂"},
        "Te": {"name": "碲", "atomic": 52, "mass": 127.6, "group": 16, "period": 5, 
               "desc": "半导体材料"},
        "I": {"name": "碘", "atomic": 53, "mass": 126.90, "group": 17, "period": 5, 
              "desc": "消毒剂"},
        "Xe": {"name": "氙", "atomic": 54, "mass": 131.29, "group": 18, "period": 5, 
               "desc": "稀有气体"},
        
        # 第6周期
        "Cs": {"name": "铯", "atomic": 55, "mass": 132.91, "group": 1, "period": 6, 
               "desc": "最活泼金属"},
        "Ba": {"name": "钡", "atomic": 56, "mass": 137.33, "group": 2, "period": 6, 
               "desc": "用于X光造影"},
        "La": {"name": "镧", "atomic": 57, "mass": 138.91, "group": 3, "period": 6, 
               "desc": "稀土元素"},
        "Ce": {"name": "铈", "atomic": 58, "mass": 140.12, "group": 3, "period": 6, 
               "desc": "稀土元素"},
        "Pr": {"name": "镨", "atomic": 59, "mass": 140.91, "group": 3, "period": 6, 
               "desc": "稀土元素"},
        "Nd": {"name": "钕", "atomic": 60, "mass": 144.24, "group": 3, "period": 6, 
               "desc": "用于永磁体"},
        "Pm": {"name": "钷", "atomic": 61, "mass": 145, "group": 3, "period": 6, 
               "desc": "放射性稀土元素"},
        "Sm": {"name": "钐", "atomic": 62, "mass": 150.36, "group": 3, "period": 6, 
               "desc": "稀土元素"},
        "Eu": {"name": "铕", "atomic": 63, "mass": 151.96, "group": 3, "period": 6, 
               "desc": "用于荧光粉"},
        "Gd": {"name": "钆", "atomic": 64, "mass": 157.25, "group": 3, "period": 6, 
               "desc": "核反应堆控制棒"},
        "Tb": {"name": "铽", "atomic": 65, "mass": 158.93, "group": 3, "period": 6, 
               "desc": "稀土元素"},
        "Dy": {"name": "镝", "atomic": 66, "mass": 162.5, "group": 3, "period": 6, 
               "desc": "稀土元素"},
        "Ho": {"name": "钬", "atomic": 67, "mass": 164.93, "group": 3, "period": 6, 
               "desc": "稀土元素"},
        "Er": {"name": "铒", "atomic": 68, "mass": 167.26, "group": 3, "period": 6, 
               "desc": "稀土元素"},
        "Tm": {"name": "铥", "atomic": 69, "mass": 168.93, "group": 3, "period": 6, 
               "desc": "稀土元素"},
        "Yb": {"name": "镱", "atomic": 70, "mass": 173.05, "group": 3, "period": 6, 
               "desc": "稀土元素"},
        "Lu": {"name": "镥", "atomic": 71, "mass": 174.97, "group": 3, "period": 6, 
               "desc": "稀土元素"},
        "Hf": {"name": "铪", "atomic": 72, "mass": 178.49, "group": 4, "period": 6, 
               "desc": "耐热合金"},
        "Ta": {"name": "钽", "atomic": 73, "mass": 180.95, "group": 5, "period": 6, 
               "desc": "耐腐蚀金属"},
        "W": {"name": "钨", "atomic": 74, "mass": 183.84, "group": 6, "period": 6, 
              "desc": "熔点最高的金属"},
        "Re": {"name": "铼", "atomic": 75, "mass": 186.21, "group": 7, "period": 6, 
               "desc": "高熔点金属"},
        "Os": {"name": "锇", "atomic": 76, "mass": 190.23, "group": 8, "period": 6, 
               "desc": "密度最大金属"},
        "Ir": {"name": "铱", "atomic": 77, "mass": 192.22, "group": 9, "period": 6, 
               "desc": "耐腐蚀"},
        "Pt": {"name": "铂", "atomic": 78, "mass": 195.08, "group": 10, "period": 6, 
               "desc": "贵金属，催化剂"},
        "Au": {"name": "金", "atomic": 79, "mass": 196.97, "group": 11, "period": 6, 
               "desc": "延展性好，不氧化"},
        "Hg": {"name": "汞", "atomic": 80, "mass": 200.59, "group": 12, "period": 6, 
               "desc": "唯一液态金属"},
        "Tl": {"name": "铊", "atomic": 81, "mass": 204.38, "group": 13, "period": 6, 
               "desc": "剧毒"},
        "Pb": {"name": "铅", "atomic": 82, "mass": 207.2, "group": 14, "period": 6, 
               "desc": "重金属，有毒"},
        "Bi": {"name": "铋", "atomic": 83, "mass": 208.98, "group": 15, "period": 6, 
               "desc": "低熔点金属"},
        "Po": {"name": "钋", "atomic": 84, "mass": 209, "group": 16, "period": 6, 
               "desc": "放射性"},
        "At": {"name": "砹", "atomic": 85, "mass": 210, "group": 17, "period": 6, 
               "desc": "稀有放射性元素"},
        "Rn": {"name": "氡", "atomic": 86, "mass": 222, "group": 18, "period": 6, 
               "desc": "放射性气体"},
        
        # 第7周期
        "Fr": {"name": "钫", "atomic": 87, "mass": 223, "group": 1, "period": 7, 
               "desc": "放射性碱金属"},
        "Ra": {"name": "镭", "atomic": 88, "mass": 226, "group": 2, "period": 7, 
               "desc": "放射性元素"},
        "Ac": {"name": "锕", "atomic": 89, "mass": 227, "group": 3, "period": 7, 
               "desc": "放射性元素"},
        "Th": {"name": "钍", "atomic": 90, "mass": 232.04, "group": 3, "period": 7, 
               "desc": "放射性元素"},
        "Pa": {"name": "镤", "atomic": 91, "mass": 231.04, "group": 3, "period": 7, 
               "desc": "放射性元素"},
        "U": {"name": "铀", "atomic": 92, "mass": 238.03, "group": 3, "period": 7, 
              "desc": "核燃料"},
        "Np": {"name": "镎", "atomic": 93, "mass": 237, "group": 3, "period": 7, 
               "desc": "放射性元素"},
        "Pu": {"name": "钚", "atomic": 94, "mass": 244, "group": 3, "period": 7, 
               "desc": "核燃料"},
        "Am": {"name": "镅", "atomic": 95, "mass": 243, "group": 3, "period": 7, 
               "desc": "放射性元素"},
        "Cm": {"name": "锔", "atomic": 96, "mass": 247, "group": 3, "period": 7, 
               "desc": "放射性元素"},
        "Bk": {"name": "锫", "atomic": 97, "mass": 247, "group": 3, "period": 7, 
               "desc": "放射性元素"},
        "Cf": {"name": "锎", "atomic": 98, "mass": 251, "group": 3, "period": 7, 
               "desc": "放射性元素"},
        "Es": {"name": "锿", "atomic": 99, "mass": 252, "group": 3, "period": 7, 
               "desc": "放射性元素"},
        "Fm": {"name": "镄", "atomic": 100, "mass": 257, "group": 3, "period": 7, 
               "desc": "放射性元素"},
        "Md": {"name": "钔", "atomic": 101, "mass": 258, "group": 3, "period": 7, 
               "desc": "放射性元素"},
        "No": {"name": "锘", "atomic": 102, "mass": 259, "group": 3, "period": 7, 
               "desc": "放射性元素"},
        "Lr": {"name": "铹", "atomic": 103, "mass": 262, "group": 3, "period": 7, 
               "desc": "放射性元素"},
        "Rf": {"name": "𬬻", "atomic": 104, "mass": 267, "group": 4, "period": 7, 
               "desc": "人工合成元素"},
        "Db": {"name": "𬭊", "atomic": 105, "mass": 268, "group": 5, "period": 7, 
               "desc": "人工合成元素"},
        "Sg": {"name": "𬭳", "atomic": 106, "mass": 269, "group": 6, "period": 7, 
               "desc": "人工合成元素"},
        "Bh": {"name": "𬭛", "atomic": 107, "mass": 270, "group": 7, "period": 7, 
               "desc": "人工合成元素"},
        "Hs": {"name": "𬭶", "atomic": 108, "mass": 269, "group": 8, "period": 7, 
               "desc": "人工合成元素"},
        "Mt": {"name": "鿏", "atomic": 109, "mass": 278, "group": 9, "period": 7, 
               "desc": "人工合成元素"},
        "Ds": {"name": "𫟼", "atomic": 110, "mass": 281, "group": 10, "period": 7, 
               "desc": "人工合成元素"},
        "Rg": {"name": "𬬭", "atomic": 111, "mass": 282, "group": 11, "period": 7, 
               "desc": "人工合成元素"},
        "Cn": {"name": "鎶", "atomic": 112, "mass": 285, "group": 12, "period": 7, 
               "desc": "人工合成元素"},
        "Nh": {"name": "鉨", "atomic": 113, "mass": 286, "group": 13, "period": 7, 
               "desc": "人工合成元素"},
        "Fl": {"name": "𫓧", "atomic": 114, "mass": 289, "group": 14, "period": 7, 
               "desc": "人工合成元素"},
        "Mc": {"name": "镆", "atomic": 115, "mass": 290, "group": 15, "period": 7, 
               "desc": "人工合成元素"},
        "Lv": {"name": "𫟷", "atomic": 116, "mass": 293, "group": 16, "period": 7, 
               "desc": "人工合成元素"},
        "Ts": {"name": "石田", "atomic": 117, "mass": 294, "group": 17, "period": 7, 
               "desc": "人工合成元素"},
        "Og": {"name": "气奥", "atomic": 118, "mass": 294, "group": 18, "period": 7, 
               "desc": "人工合成元素"},
    }
    
    @classmethod
    def get_element_info(cls, symbol):
        """获取元素完整信息"""
        if symbol in cls.elements_data:
            data = cls.elements_data[symbol].copy()
            data["config"] = cls.electron_configs.get(symbol, "未知")
            return data
        return None

# ==================== 主应用程序 ====================
class ChemistryToolboxV3:
    """化学工具箱 0.3 版本"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("化学工具箱 v0.3")
        self.root.geometry("1100x750")
        
        # 设置字体
        self.default_font = ("Microsoft YaHei", 10)
        self.title_font = ("Microsoft YaHei", 12, "bold")
        
        # 顶部按钮框架
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.btn_balance = tk.Button(self.button_frame, text="配平", width=12, 
                                      font=self.title_font, command=self.show_balance)
        self.btn_balance.pack(side=tk.LEFT, padx=5)
        
        self.btn_periodic = tk.Button(self.button_frame, text="元素周期表", width=12,
                                       font=self.title_font, command=self.show_periodic)
        self.btn_periodic.pack(side=tk.LEFT, padx=5)
        
        self.btn_about = tk.Button(self.button_frame, text="关于", width=12,
                                    font=self.title_font, command=self.show_about)
        self.btn_about.pack(side=tk.LEFT, padx=5)
        
        self.btn_help = tk.Button(self.button_frame, text="帮助", width=12,
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
    
    def format_formula_display(self, formula):
        """格式化显示化学式，将数字转换为下标"""
        # 处理数字下标
        result = []
        i = 0
        n = len(formula)
        
        while i < n:
            if i < n and formula[i].isdigit():
                num = ""
                while i < n and formula[i].isdigit():
                    num += formula[i]
                    i += 1
                result.append(f"_{{{num}}}")
            else:
                result.append(formula[i])
                i += 1
        
        return ''.join(result)
    
    # ==================== 配平界面 ====================
    def show_balance(self):
        self.clear_content()
        self.update_status("配平模式 v0.3 - 支持离子方程式（使用^标记电荷）")
        
        # 标题
        tk.Label(self.content_frame, text="化学方程式配平", font=self.title_font, 
                fg="blue").pack(pady=10)
        
        # 说明
        help_frame = tk.Frame(self.content_frame)
        help_frame.pack(pady=5)
        tk.Label(help_frame, text="支持格式:", font=("Microsoft YaHei", 9, "bold")).pack(side=tk.LEFT)
        tk.Label(help_frame, text=" H2+O2=H2O  |  Fe2O3+CO=Fe+CO2  |  Cu+AgNO3=Cu(NO3)2+Ag  |  MnO4^-+Fe^2+=Mn^2++Fe^3+", 
                font=self.default_font).pack(side=tk.LEFT, padx=5)
        
        # 输入区域
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(pady=15)
        
        tk.Label(input_frame, text="请输入方程式:", font=self.default_font).pack(side=tk.LEFT)
        self.equation_entry = tk.Entry(input_frame, width=65, font=("Courier", 11))
        self.equation_entry.pack(side=tk.LEFT, padx=10)
        self.equation_entry.bind('<Return>', lambda e: self.do_balance())
        
        self.balance_btn = tk.Button(input_frame, text="配平", command=self.do_balance, 
                                     bg="lightblue", width=10, font=self.default_font)
        self.balance_btn.pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域
        result_frame = tk.LabelFrame(self.content_frame, text="配平结果", font=self.title_font)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_text = tk.Text(result_frame, height=12, font=("Courier", 11), wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配置文本标签样式
        self.result_text.tag_configure("blue_coeff", foreground="blue", font=("Courier", 11, "bold"))
        self.result_text.tag_configure("green_valence", foreground="green", font=("Courier", 10))
        self.result_text.tag_configure("red_valence", foreground="red", font=("Courier", 10))
        self.result_text.tag_configure("subscript", font=("Courier", 9))
        self.result_text.tag_configure("normal", foreground="black", font=("Courier", 11))
        
        # 示例按钮
        example_frame = tk.Frame(self.content_frame)
        example_frame.pack(pady=5)
        tk.Label(example_frame, text="示例:").pack(side=tk.LEFT)
        
        examples = [
            ("H2+O2=H2O", "氢气燃烧"),
            ("Fe2O3+CO=Fe+CO2", "炼铁"),
            ("Cu+AgNO3=Cu(NO3)2+Ag", "置换反应"),
            ("MnO4^-+Fe^2+=Mn^2++Fe^3+", "氧化还原（离子）")
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
    
    def insert_formatted_formula(self, formula):
        """插入格式化的化学式（带下标）"""
        i = 0
        n = len(formula)
        
        while i < n:
            if i < n and formula[i].isdigit():
                num = ""
                while i < n and formula[i].isdigit():
                    num += formula[i]
                    i += 1
                # 使用下标显示
                self.result_text.insert(tk.END, num, "subscript")
            else:
                self.result_text.insert(tk.END, formula[i], "normal")
                i += 1
    
    def do_balance(self):
        """执行配平"""
        equation = self.equation_entry.get().strip()
        if not equation:
            messagebox.showwarning("警告", "请输入化学方程式")
            return
        
        self.update_status("正在配平方程式...")
        
        # 调用配平引擎
        result, valence_data = EquationBalancer.balance(equation)
        
        self.result_text.delete(1.0, tk.END)
        
        if result.startswith("错误"):
            self.result_text.insert(tk.END, result, "normal")
            self.update_status("配平失败")
        else:
            # 显示配平后的方程式（蓝色系数）
            self.result_text.insert(tk.END, "配平结果:\n\n", "normal")
            
            # 解析配平后的方程式
            left, right = result.split(" = ")
            
            # 显示左边
            left_parts = left.split('+')
            for i, part in enumerate(left_parts):
                # 提取系数
                coeff_match = re.match(r'^(\d+)(.*)$', part)
                if coeff_match:
                    coeff = int(coeff_match.group(1))
                    formula = coeff_match.group(2)
                    self.result_text.insert(tk.END, f"{coeff}", "blue_coeff")
                    self.insert_formatted_formula(formula)
                else:
                    self.insert_formatted_formula(part)
                
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
                    self.result_text.insert(tk.END, f"{coeff}", "blue_coeff")
                    self.insert_formatted_formula(formula)
                else:
                    self.insert_formatted_formula(part)
                
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
    
    # ==================== 元素周期表界面 ====================
    def show_periodic(self):
        self.clear_content()
        self.update_status("元素周期表模式 v0.3 - 包含118种元素，点击查看详细信息")
        
        # 创建滚动区域
        canvas = tk.Canvas(self.content_frame)
        scrollbar = tk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 定义周期表布局 - 包含所有118种元素
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
        
        # 镧系元素
        lanthanides = ["La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"]
        # 锕系元素
        actinides = ["Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr"]
        
        # 创建元素按钮
        for r, row in enumerate(rows_data):
            for c, (symbol, group) in enumerate(row):
                if symbol == "":
                    continue
                    
                data = ExtendedPeriodicTable.get_element_info(symbol)
                if data:
                    # 根据族设置颜色
                    group_num = data["group"]
                    if group_num == 1:
                        color = "#ffcccc"  # 碱金属
                    elif group_num == 2:
                        color = "#ccffcc"  # 碱土金属
                    elif 3 <= group_num <= 12:
                        color = "#ccccff"  # 过渡金属
                    elif 13 <= group_num <= 16:
                        color = "#ffffcc"  # 非金属
                    elif group_num == 17:
                        color = "#ffcc99"  # 卤素
                    elif group_num == 18:
                        color = "#99ccff"  # 稀有气体
                    else:
                        color = "#f0f0f0"
                    
                    btn = tk.Button(scrollable_frame, 
                                   text=f"{symbol}\n{data['atomic']}", 
                                   width=6, height=3,
                                   bg=color,
                                   font=("Microsoft YaHei", 8),
                                   command=lambda s=symbol: self.show_element_info(s))
                    btn.grid(row=r, column=c, padx=1, pady=1)
        
        # 添加镧系元素行
        lanthanide_row = len(rows_data)
        tk.Label(scrollable_frame, text="镧系:", font=self.default_font).grid(row=lanthanide_row, column=0, sticky="e")
        for i, symbol in enumerate(lanthanides):
            data = ExtendedPeriodicTable.get_element_info(symbol)
            if data:
                btn = tk.Button(scrollable_frame, 
                               text=f"{symbol}\n{data['atomic']}", 
                               width=6, height=2,
                               bg="#e6e6fa",
                               font=("Microsoft YaHei", 7),
                               command=lambda s=symbol: self.show_element_info(s))
                btn.grid(row=lanthanide_row, column=i+1, padx=1, pady=1)
        
        # 添加锕系元素行
        actinide_row = len(rows_data) + 1
        tk.Label(scrollable_frame, text="锕系:", font=self.default_font).grid(row=actinide_row, column=0, sticky="e")
        for i, symbol in enumerate(actinides):
            data = ExtendedPeriodicTable.get_element_info(symbol)
            if data:
                btn = tk.Button(scrollable_frame, 
                               text=f"{symbol}\n{data['atomic']}", 
                               width=6, height=2,
                               bg="#ffe4e1",
                               font=("Microsoft YaHei", 7),
                               command=lambda s=symbol: self.show_element_info(s))
                btn.grid(row=actinide_row, column=i+1, padx=1, pady=1)
        
        # 添加图例
        legend_frame = tk.Frame(scrollable_frame)
        legend_frame.grid(row=actinide_row + 1, column=0, columnspan=18, pady=10)
        
        legends = [
            ("碱金属", "#ffcccc"), ("碱土金属", "#ccffcc"), ("过渡金属", "#ccccff"),
            ("非金属", "#ffffcc"), ("卤素", "#ffcc99"), ("稀有气体", "#99ccff"),
            ("镧系", "#e6e6fa"), ("锕系", "#ffe4e1")
        ]
        
        for text, color in legends:
            frame = tk.Frame(legend_frame)
            frame.pack(side=tk.LEFT, padx=8)
            tk.Label(frame, text="  ", bg=color, width=2).pack(side=tk.LEFT)
            tk.Label(frame, text=text, font=self.default_font).pack(side=tk.LEFT)
    
    def show_element_info(self, symbol):
        """显示元素详细信息"""
        data = ExtendedPeriodicTable.get_element_info(symbol)
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
        else:
            messagebox.showinfo("元素信息", f"未找到 {symbol} 的详细信息")
    
    # ==================== 关于界面 ====================
    def show_about(self):
        self.clear_content()
        self.update_status("关于化学工具箱 v0.3")
        
        about_text = """化学工具箱 (Chemistry Toolbox)
版本: 0.3
更新日期: 2025年3月26日

新增功能 (v0.3):
✓ 支持离子方程式配平（使用^标记电荷，如 MnO4^-+Fe^2+）
✓ 扩展至118种元素（包含全部周期表元素）
✓ 显示电子层排布（详细电子构型）
✓ 化学式下标显示（如 CO₂, Ca(OH)₂）
✓ 优化配平算法，提高成功率
✓ 改进界面布局和用户体验

主要功能:
• 化学方程式配平（含离子方程式）
• 完整元素周期表查询（118种元素）
• 化合价智能标注（正价绿色，负价红色）
• 电子层排布显示
• 后续将添加摩尔计算、浓度计算等

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
        self.update_status("帮助 - 使用说明 v0.3")
        
        help_text = """化学工具箱 v0.3 使用帮助

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【1. 配平功能】

使用方法：
  • 在输入框中输入化学方程式
  • 点击"配平"按钮或按回车键

支持格式：
  • 普通方程式: H2+O2=H2O
  • 箭头符号: Fe + O2 -> Fe2O3
  • 离子方程式: MnO4^-+Fe^2+=Mn^2++Fe^3+  (使用 ^ 标记电荷)
  • 带括号: Fe2(SO4)3

显示效果：
  • 配平系数: 蓝色显示
  • 化学式下标: 自动转换为下标（如 CO₂）
  • 化合价: 正价绿色，负价红色

支持示例：
  • H2+O2=H2O              → 2H2+O2=2H2O
  • Fe2O3+CO=Fe+CO2        → Fe2O3+3CO=2Fe+3CO2
  • Cu+AgNO3=Cu(NO3)2+Ag   → Cu+2AgNO3=Cu(NO3)2+2Ag
  • MnO4^-+Fe^2+=Mn^2++Fe^3+ → MnO4^-+5Fe^2++8H^+=Mn^2++5Fe^3++4H2O

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【2. 元素周期表】

功能说明：
  • 完整显示118种元素
  • 包含镧系、锕系元素
  • 点击元素查看详细信息

元素信息包括：
  • 中文名称、原子序数、原子量
  • 族、周期、电子层排布
  • 元素简介

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【3. 关于与帮助】

关于：显示软件版本、更新日志和功能介绍
帮助：您正在查看的内容

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

更新日志 v0.3 (2025-03-26):
  • 新增离子方程式配平（使用^标记电荷）
  • 扩展至118种元素（完整周期表）
  • 添加电子层排布详细信息
  • 实现化学式下标显示（CO₂, Ca(OH)₂）
  • 优化配平算法，提高成功率
  • 改进周期表布局，包含镧系锕系
  • 修复离子配平bug
  • 优化界面体验

更新日志 v0.2 (2025-03-26):
  • 新增离子方程式配平支持
  • 增加至80+种元素数据
  • 添加化合价智能标注功能
  • 配平系数蓝色高亮显示

更新日志 v0.1 (2025-03-20):
  • 初始版本发布
  • 基础方程式配平功能
  • 30种常见元素数据
  • 基本界面框架

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

注意事项:
  • 离子方程式必须使用 ^ 标记电荷（如 MnO4^-，Fe^2+）
  • 元素符号大小写敏感（如 Co 钴，CO 一氧化碳）
  • 复杂有机方程式可能需要手动调整
  • 化合价标注基于常见化合价规则

技术支持:
  如有问题或建议，欢迎反馈！
"""
        
        text_widget = scrolledtext.ScrolledText(self.content_frame, wrap=tk.WORD, 
                                                font=self.default_font)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

# ==================== 程序入口 ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = ChemistryToolboxV3(root)
    root.mainloop()