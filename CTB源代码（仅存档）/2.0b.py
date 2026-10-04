import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import re
from collections import defaultdict
import numpy as np
from math import gcd, log10, floor, exp, sqrt, pi
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
        'HSO4': -1, 'HCO3': -1, 'HPO4': -2, 'H2PO4': -1,
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

# ==================== 格式化工具 ====================
class FormulaFormatter:
    @staticmethod
    def convert_to_subscript(text):
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
    
    @staticmethod
    def calculate_oxidation_states(formula):
        counts = ChemicalFormulaParser.parse_formula(formula)
        if not counts:
            return {}
        element_valence = {}
        def get_electronegativity(e):
            en = {'F': 4.0, 'O': 3.5, 'Cl': 3.2, 'N': 3.0, 'Br': 3.0, 
                  'S': 2.6, 'C': 2.6, 'P': 2.2, 'H': 2.2, 'B': 2.0}
            return en.get(e, 2.5)
        elements = list(counts.keys())
        elements.sort(key=get_electronegativity, reverse=True)
        for element in elements:
            valences = ValenceData.get_valence(element, formula)
            if valences:
                element_valence[element] = valences[0] if valences else 0
            else:
                element_valence[element] = 0
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
    @staticmethod
    def parse_compound_with_charge(compound):
        cation_pattern = r'(\*+)$'
        anion_pattern = r'(\^+)$'
        cation_match = re.search(cation_pattern, compound)
        anion_match = re.search(anion_pattern, compound)
        if cation_match:
            stars = cation_match.group(1)
            charge = len(stars)
            formula = compound[:cation_match.start()]
        elif anion_match:
            carets = anion_match.group(1)
            charge = -len(carets)
            formula = compound[:anion_match.start()]
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
                        if valid and len(int_coeffs) == n_unknowns:
                            error = sum(abs(A @ coeffs[:n_unknowns] - b))
                            if error < best_error:
                                best_error = error
                                best_solution = int_coeffs
                    except np.linalg.LinAlgError:
                        continue
                elif n_unknowns == 1:
                    if abs(A[0, 0] * first_coeff - b[0]) < 1e-5:
                        best_solution = [first_coeff]
                        best_error = 0
                        break
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
                    if charge > 0:
                        formatted += '*' * charge
                    elif charge < 0:
                        formatted += '^' * abs(charge)
                    left_parts.append(formatted)
                right_parts = []
                for i, (formula, charge) in enumerate(right_compounds):
                    coeff = best_solution[n_left + i] if (n_left + i) < len(best_solution) else 1
                    formatted = f"{coeff if coeff > 1 else ''}{formula}"
                    if charge > 0:
                        formatted += '*' * charge
                    elif charge < 0:
                        formatted += '^' * abs(charge)
                    right_parts.append(formatted)
                balanced_eq = f"{'+'.join(left_parts)} = {'+'.join(right_parts)}"
                valence_info = {}
                for idx, (formula, _) in enumerate(left_compounds):
                    valence_info[f'L{idx}'] = ChemicalFormulaParser.calculate_oxidation_states(formula)
                for idx, (formula, _) in enumerate(right_compounds):
                    valence_info[f'R{idx}'] = ChemicalFormulaParser.calculate_oxidation_states(formula)
                return balanced_eq, valence_info
            return "错误：无法配平该方程式，请检查输入格式", {}
        except Exception as e:
            return f"配平失败: {str(e)}", {}

# ==================== 扩展元素数据 ====================
class ExtendedPeriodicTable:
    electron_config = {
        "H": "1", "He": "2", "Li": "2,1", "Be": "2,2", "B": "2,3", "C": "2,4", "N": "2,5", "O": "2,6", "F": "2,7", "Ne": "2,8",
        "Na": "2,8,1", "Mg": "2,8,2", "Al": "2,8,3", "Si": "2,8,4", "P": "2,8,5", "S": "2,8,6", "Cl": "2,8,7", "Ar": "2,8,8",
        "K": "2,8,8,1", "Ca": "2,8,8,2", "Sc": "2,8,9,2", "Ti": "2,8,10,2", "V": "2,8,11,2", 
        "Cr": "2,8,13,1", "Mn": "2,8,13,2", "Fe": "2,8,14,2", "Co": "2,8,15,2", "Ni": "2,8,16,2",
        "Cu": "2,8,18,1", "Zn": "2,8,18,2", "Ga": "2,8,18,3", "Ge": "2,8,18,4", "As": "2,8,18,5",
        "Se": "2,8,18,6", "Br": "2,8,18,7", "Kr": "2,8,18,8", "Rb": "2,8,18,8,1", "Sr": "2,8,18,8,2",
        "Y": "2,8,18,9,2", "Zr": "2,8,18,10,2", "Nb": "2,8,18,12,1", "Mo": "2,8,18,13,1", "Tc": "2,8,18,13,2",
        "Ru": "2,8,18,15,1", "Rh": "2,8,18,16,1", "Pd": "2,8,18,18", "Ag": "2,8,18,18,1", "Cd": "2,8,18,18,2",
        "In": "2,8,18,18,3", "Sn": "2,8,18,18,4", "Sb": "2,8,18,18,5", "Te": "2,8,18,18,6", "I": "2,8,18,18,7",
        "Xe": "2,8,18,18,8", "Cs": "2,8,18,18,8,1", "Ba": "2,8,18,18,8,2", "La": "2,8,18,18,9,2", "Ce": "2,8,18,19,9,2",
        "Pr": "2,8,18,21,8,2", "Nd": "2,8,18,22,8,2", "Pm": "2,8,18,23,8,2", "Sm": "2,8,18,24,8,2", "Eu": "2,8,18,25,8,2",
        "Gd": "2,8,18,25,9,2", "Tb": "2,8,18,27,8,2", "Dy": "2,8,18,28,8,2", "Ho": "2,8,18,29,8,2", "Er": "2,8,18,30,8,2",
        "Tm": "2,8,18,31,8,2", "Yb": "2,8,18,32,8,2", "Lu": "2,8,18,32,9,2", "Hf": "2,8,18,32,10,2", "Ta": "2,8,18,32,11,2",
        "W": "2,8,18,32,12,2", "Re": "2,8,18,32,13,2", "Os": "2,8,18,32,14,2", "Ir": "2,8,18,32,15,2", "Pt": "2,8,18,32,17,1",
        "Au": "2,8,18,32,18,1", "Hg": "2,8,18,32,18,2", "Tl": "2,8,18,32,18,3", "Pb": "2,8,18,32,18,4", "Bi": "2,8,18,32,18,5",
        "Po": "2,8,18,32,18,6", "At": "2,8,18,32,18,7", "Rn": "2,8,18,32,18,8", "Fr": "2,8,18,32,18,8,1", "Ra": "2,8,18,32,18,8,2",
        "Ac": "2,8,18,32,18,9,2", "Th": "2,8,18,32,18,10,2", "Pa": "2,8,18,32,20,9,2", "U": "2,8,18,32,21,9,2",
    }
    
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
        "Sc": {"name": "钪", "atomic": 21, "mass": 44.956, "group": 3, "period": 4, "config": "[Ar] 3d¹ 4s²", "desc": "稀土元素"},
        "Ti": {"name": "钛", "atomic": 22, "mass": 47.867, "group": 4, "period": 4, "config": "[Ar] 3d² 4s²", "desc": "高强度轻金属"},
        "V": {"name": "钒", "atomic": 23, "mass": 50.942, "group": 5, "period": 4, "config": "[Ar] 3d³ 4s²", "desc": "钢铁工业添加剂"},
        "Cr": {"name": "铬", "atomic": 24, "mass": 51.996, "group": 6, "period": 4, "config": "[Ar] 3d⁵ 4s¹", "desc": "不锈钢成分"},
        "Mn": {"name": "锰", "atomic": 25, "mass": 54.938, "group": 7, "period": 4, "config": "[Ar] 3d⁵ 4s²", "desc": "钢铁工业重要元素"},
        "Fe": {"name": "铁", "atomic": 26, "mass": 55.845, "group": 8, "period": 4, "config": "[Ar] 3d⁶ 4s²", "desc": "最常用的金属"},
        "Co": {"name": "钴", "atomic": 27, "mass": 58.933, "group": 9, "period": 4, "config": "[Ar] 3d⁷ 4s²", "desc": "磁性材料"},
        "Ni": {"name": "镍", "atomic": 28, "mass": 58.693, "group": 10, "period": 4, "config": "[Ar] 3d⁸ 4s²", "desc": "不锈钢成分"},
        "Cu": {"name": "铜", "atomic": 29, "mass": 63.546, "group": 11, "period": 4, "config": "[Ar] 3d¹⁰ 4s¹", "desc": "导电性好"},
        "Zn": {"name": "锌", "atomic": 30, "mass": 65.38, "group": 12, "period": 4, "config": "[Ar] 3d¹⁰ 4s²", "desc": "防腐镀层"},
        "Ga": {"name": "镓", "atomic": 31, "mass": 69.723, "group": 13, "period": 4, "config": "[Ar] 3d¹⁰ 4s² 4p¹", "desc": "低熔点金属"},
        "Ge": {"name": "锗", "atomic": 32, "mass": 72.63, "group": 14, "period": 4, "config": "[Ar] 3d¹⁰ 4s² 4p²", "desc": "半导体材料"},
        "As": {"name": "砷", "atomic": 33, "mass": 74.922, "group": 15, "period": 4, "config": "[Ar] 3d¹⁰ 4s² 4p³", "desc": "有毒类金属"},
        "Se": {"name": "硒", "atomic": 34, "mass": 78.96, "group": 16, "period": 4, "config": "[Ar] 3d¹⁰ 4s² 4p⁴", "desc": "光导材料"},
        "Br": {"name": "溴", "atomic": 35, "mass": 79.904, "group": 17, "period": 4, "config": "[Ar] 3d¹⁰ 4s² 4p⁵", "desc": "红棕色液体"},
        "Kr": {"name": "氪", "atomic": 36, "mass": 83.798, "group": 18, "period": 4, "config": "[Ar] 3d¹⁰ 4s² 4p⁶", "desc": "稀有气体"},
        "Rb": {"name": "铷", "atomic": 37, "mass": 85.468, "group": 1, "period": 5, "config": "[Kr] 5s¹", "desc": "活泼碱金属"},
        "Sr": {"name": "锶", "atomic": 38, "mass": 87.62, "group": 2, "period": 5, "config": "[Kr] 5s²", "desc": "用于烟花"},
        "Y": {"name": "钇", "atomic": 39, "mass": 88.906, "group": 3, "period": 5, "config": "[Kr] 4d¹ 5s²", "desc": "稀土元素"},
        "Zr": {"name": "锆", "atomic": 40, "mass": 91.224, "group": 4, "period": 5, "config": "[Kr] 4d² 5s²", "desc": "耐腐蚀金属"},
        "Nb": {"name": "铌", "atomic": 41, "mass": 92.906, "group": 5, "period": 5, "config": "[Kr] 4d⁴ 5s¹", "desc": "超导材料"},
        "Mo": {"name": "钼", "atomic": 42, "mass": 95.95, "group": 6, "period": 5, "config": "[Kr] 4d⁵ 5s¹", "desc": "钢铁添加剂"},
        "Tc": {"name": "锝", "atomic": 43, "mass": 98, "group": 7, "period": 5, "config": "[Kr] 4d⁵ 5s²", "desc": "放射性元素"},
        "Ru": {"name": "钌", "atomic": 44, "mass": 101.07, "group": 8, "period": 5, "config": "[Kr] 4d⁷ 5s¹", "desc": "铂族金属"},
        "Rh": {"name": "铑", "atomic": 45, "mass": 102.91, "group": 9, "period": 5, "config": "[Kr] 4d⁸ 5s¹", "desc": "催化剂"},
        "Pd": {"name": "钯", "atomic": 46, "mass": 106.42, "group": 10, "period": 5, "config": "[Kr] 4d¹⁰", "desc": "催化剂"},
        "Ag": {"name": "银", "atomic": 47, "mass": 107.87, "group": 11, "period": 5, "config": "[Kr] 4d¹⁰ 5s¹", "desc": "贵金属"},
        "Cd": {"name": "镉", "atomic": 48, "mass": 112.41, "group": 12, "period": 5, "config": "[Kr] 4d¹⁰ 5s²", "desc": "有毒重金属"},
        "In": {"name": "铟", "atomic": 49, "mass": 114.82, "group": 13, "period": 5, "config": "[Kr] 4d¹⁰ 5s² 5p¹", "desc": "用于液晶屏"},
        "Sn": {"name": "锡", "atomic": 50, "mass": 118.71, "group": 14, "period": 5, "config": "[Kr] 4d¹⁰ 5s² 5p²", "desc": "青铜成分"},
        "Sb": {"name": "锑", "atomic": 51, "mass": 121.76, "group": 15, "period": 5, "config": "[Kr] 4d¹⁰ 5s² 5p³", "desc": "阻燃剂"},
        "Te": {"name": "碲", "atomic": 52, "mass": 127.6, "group": 16, "period": 5, "config": "[Kr] 4d¹⁰ 5s² 5p⁴", "desc": "半导体材料"},
        "I": {"name": "碘", "atomic": 53, "mass": 126.90, "group": 17, "period": 5, "config": "[Kr] 4d¹⁰ 5s² 5p⁵", "desc": "消毒剂"},
        "Xe": {"name": "氙", "atomic": 54, "mass": 131.29, "group": 18, "period": 5, "config": "[Kr] 4d¹⁰ 5s² 5p⁶", "desc": "稀有气体"},
        "Cs": {"name": "铯", "atomic": 55, "mass": 132.91, "group": 1, "period": 6, "config": "[Xe] 6s¹", "desc": "最活泼金属"},
        "Ba": {"name": "钡", "atomic": 56, "mass": 137.33, "group": 2, "period": 6, "config": "[Xe] 6s²", "desc": "用于X光造影"},
        "La": {"name": "镧", "atomic": 57, "mass": 138.91, "group": 3, "period": 6, "config": "[Xe] 5d¹ 6s²", "desc": "稀土元素"},
        "Hf": {"name": "铪", "atomic": 72, "mass": 178.49, "group": 4, "period": 6, "config": "[Xe] 4f¹⁴ 5d² 6s²", "desc": "耐热合金"},
        "Ta": {"name": "钽", "atomic": 73, "mass": 180.95, "group": 5, "period": 6, "config": "[Xe] 4f¹⁴ 5d³ 6s²", "desc": "耐腐蚀金属"},
        "W": {"name": "钨", "atomic": 74, "mass": 183.84, "group": 6, "period": 6, "config": "[Xe] 4f¹⁴ 5d⁴ 6s²", "desc": "熔点最高的金属"},
        "Re": {"name": "铼", "atomic": 75, "mass": 186.21, "group": 7, "period": 6, "config": "[Xe] 4f¹⁴ 5d⁵ 6s²", "desc": "高熔点金属"},
        "Os": {"name": "锇", "atomic": 76, "mass": 190.23, "group": 8, "period": 6, "config": "[Xe] 4f¹⁴ 5d⁶ 6s²", "desc": "密度最大金属"},
        "Ir": {"name": "铱", "atomic": 77, "mass": 192.22, "group": 9, "period": 6, "config": "[Xe] 4f¹⁴ 5d⁷ 6s²", "desc": "耐腐蚀"},
        "Pt": {"name": "铂", "atomic": 78, "mass": 195.08, "group": 10, "period": 6, "config": "[Xe] 4f¹⁴ 5d⁹ 6s¹", "desc": "贵金属，催化剂"},
        "Au": {"name": "金", "atomic": 79, "mass": 196.97, "group": 11, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s¹", "desc": "延展性好"},
        "Hg": {"name": "汞", "atomic": 80, "mass": 200.59, "group": 12, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s²", "desc": "唯一液态金属"},
        "Tl": {"name": "铊", "atomic": 81, "mass": 204.38, "group": 13, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p¹", "desc": "剧毒"},
        "Pb": {"name": "铅", "atomic": 82, "mass": 207.2, "group": 14, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p²", "desc": "重金属"},
        "Bi": {"name": "铋", "atomic": 83, "mass": 208.98, "group": 15, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p³", "desc": "低熔点金属"},
        "Po": {"name": "钋", "atomic": 84, "mass": 209, "group": 16, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁴", "desc": "放射性"},
        "At": {"name": "砹", "atomic": 85, "mass": 210, "group": 17, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁵", "desc": "稀有放射性元素"},
        "Rn": {"name": "氡", "atomic": 86, "mass": 222, "group": 18, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁶", "desc": "放射性气体"},
        "U": {"name": "铀", "atomic": 92, "mass": 238.03, "group": 3, "period": 7, "config": "[Rn] 5f³ 6d¹ 7s²", "desc": "核燃料"},
    }
    
    @classmethod
    def get_element(cls, symbol):
        return cls.elements_data.get(symbol)

# ==================== 主应用程序 ====================
class ChemistryToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title("化学工具箱 v2.0")
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
    
    def create_menubar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出结果", command=self.export_result)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="单位换算", command=self.show_unit_converter)
        tools_menu.add_command(label="实验记录", command=self.show_lab_notebook)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用教程", command=self.show_tutorial)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_main_buttons(self):
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
        
        # 修复：使用 self.button_frame 而不是 self.root
        btn = self.button_frame.grid_slaves(row=0, column=3)[0]
        utility_menu.post(btn.winfo_rootx(), btn.winfo_rooty() + btn.winfo_height())
    
    # ==================== 配平界面 ====================
    def show_balance(self):
        self.clear_content()
        self.update_status("配平模式 - *表示阳离子，^表示阴离子（如 H* 表示 H⁺，HCO3^ 表示 HCO₃⁻）")
        
        tk.Label(self.content_frame, text="化学方程式配平 v2.0", font=self.title_font, fg="blue").pack(pady=10)
        
        help_frame = tk.Frame(self.content_frame)
        help_frame.pack(pady=5)
        tk.Label(help_frame, text="支持格式:", font=("Microsoft YaHei", 9, "bold")).pack(side=tk.LEFT)
        tk.Label(help_frame, text=" H2+O2=H2O  |  Fe2O3+CO=Fe+CO2  |  HCO3^+H*=CO2+H2O", 
                font=self.default_font, fg="green").pack(side=tk.LEFT, padx=5)
        
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(pady=15)
        tk.Label(input_frame, text="方程式:").pack(side=tk.LEFT)
        self.equation_entry = tk.Entry(input_frame, width=60, font=("Courier", 11))
        self.equation_entry.pack(side=tk.LEFT, padx=10)
        self.equation_entry.bind('<Return>', lambda e: self.do_balance())
        self.balance_btn = tk.Button(input_frame, text="配平", command=self.do_balance, bg="lightblue")
        self.balance_btn.pack(side=tk.LEFT, padx=5)
        
        result_frame = tk.LabelFrame(self.content_frame, text="配平结果", font=self.title_font)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.result_text = tk.Text(result_frame, height=12, font=("Courier", 12), wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.result_text.tag_configure("blue_coeff", foreground="blue", font=("Courier", 12, "bold"))
        self.result_text.tag_configure("green_valence", foreground="green")
        self.result_text.tag_configure("red_valence", foreground="red")
        self.result_text.tag_configure("normal", foreground="black")
        
        example_frame = tk.Frame(self.content_frame)
        example_frame.pack(pady=5)
        tk.Label(example_frame, text="示例:").pack(side=tk.LEFT)
        examples = [("H2+O2=H2O", "氢气燃烧"), ("Fe2O3+CO=Fe+CO2", "炼铁"), 
                   ("Cu+AgNO3=Cu(NO3)2+Ag", "置换"), ("HCO3^+H*=CO2+H2O", "碳酸氢根与酸")]
        for eq, desc in examples:
            btn = tk.Button(example_frame, text=desc, command=lambda e=eq: self.load_balance_example(e),
                           font=self.default_font, bg="#f0f0f0")
            btn.pack(side=tk.LEFT, padx=5)
    
    def load_balance_example(self, equation):
        self.equation_entry.delete(0, tk.END)
        self.equation_entry.insert(0, equation)
        self.do_balance()
    
    def do_balance(self):
        equation = self.equation_entry.get().strip()
        if not equation:
            messagebox.showwarning("警告", "请输入方程式")
            return
        self.update_status("正在配平...")
        result, valence_data = EquationBalancer.balance(equation)
        self.result_text.delete(1.0, tk.END)
        if result.startswith("错误") or result.startswith("配平失败"):
            self.result_text.insert(tk.END, result, "normal")
            self.update_status("配平失败")
        else:
            self.result_text.insert(tk.END, "配平结果:\n\n", "normal")
            try:
                display_result = result
                display_result = re.sub(r'\*+', lambda m: '⁺' * len(m.group()), display_result)
                display_result = re.sub(r'\^+', lambda m: '⁻' * len(m.group()), display_result)
                left, right = display_result.split(" = ")
                left_parts = left.split('+')
                for i, part in enumerate(left_parts):
                    coeff_match = re.match(r'^(\d+)(.*)$', part)
                    if coeff_match:
                        coeff = int(coeff_match.group(1))
                        formula = coeff_match.group(2)
                        charge_match = re.search(r'([⁺⁻]+)$', formula)
                        if charge_match:
                            charge = charge_match.group(1)
                            formula_clean = formula[:charge_match.start()]
                        else:
                            formula_clean = formula
                            charge = ""
                        self.result_text.insert(tk.END, f"{coeff}", "blue_coeff")
                        self.result_text.insert(tk.END, self.format_subscript(formula_clean), "normal")
                        if charge:
                            self.result_text.insert(tk.END, charge, "normal")
                    else:
                        charge_match = re.search(r'([⁺⁻]+)$', part)
                        if charge_match:
                            charge = charge_match.group(1)
                            formula_clean = part[:charge_match.start()]
                        else:
                            formula_clean = part
                            charge = ""
                        self.result_text.insert(tk.END, self.format_subscript(formula_clean), "normal")
                        if charge:
                            self.result_text.insert(tk.END, charge, "normal")
                    if i < len(left_parts) - 1:
                        self.result_text.insert(tk.END, " + ", "normal")
                self.result_text.insert(tk.END, " = ", "normal")
                right_parts = right.split('+')
                for i, part in enumerate(right_parts):
                    coeff_match = re.match(r'^(\d+)(.*)$', part)
                    if coeff_match:
                        coeff = int(coeff_match.group(1))
                        formula = coeff_match.group(2)
                        charge_match = re.search(r'([⁺⁻]+)$', formula)
                        if charge_match:
                            charge = charge_match.group(1)
                            formula_clean = formula[:charge_match.start()]
                        else:
                            formula_clean = formula
                            charge = ""
                        self.result_text.insert(tk.END, f"{coeff}", "blue_coeff")
                        self.result_text.insert(tk.END, self.format_subscript(formula_clean), "normal")
                        if charge:
                            self.result_text.insert(tk.END, charge, "normal")
                    else:
                        charge_match = re.search(r'([⁺⁻]+)$', part)
                        if charge_match:
                            charge = charge_match.group(1)
                            formula_clean = part[:charge_match.start()]
                        else:
                            formula_clean = part
                            charge = ""
                        self.result_text.insert(tk.END, self.format_subscript(formula_clean), "normal")
                        if charge:
                            self.result_text.insert(tk.END, charge, "normal")
                    if i < len(right_parts) - 1:
                        self.result_text.insert(tk.END, " + ", "normal")
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
            except Exception as e:
                self.result_text.insert(tk.END, f"显示错误: {str(e)}", "normal")
    
    # ==================== 元素周期表界面 ====================
    def show_periodic(self):
        self.clear_content()
        self.update_status("元素周期表模式 - 点击元素查看详细信息")
        
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
            [("Fr",1), ("Ra",2), ("Ac",3), ("Rf",4), ("Db",5), ("Sg",6), ("Bh",7), ("Hs",8), ("Mt",9), ("Ds",10), ("Rg",11), ("Cn",12), ("Nh",13), ("Fl",14), ("Mc",15), ("Lv",16), ("Ts",17), ("Og",18)],
        ]
        
        for r, row in enumerate(rows):
            for c, (symbol, _) in enumerate(row):
                if symbol:
                    data = ExtendedPeriodicTable.get_element(symbol)
                    if data:
                        color = "#ffcccc" if data["group"] == 1 else "#ccffcc" if data["group"] == 2 else "#ccccff" if 3 <= data["group"] <= 12 else "#ffffcc"
                        btn = tk.Button(scrollable, text=f"{symbol}\n{data['atomic']}", width=6, height=3,
                                      bg=color, command=lambda s=symbol: self.show_element_info(s))
                        btn.grid(row=r, column=c, padx=1, pady=1)
    
    def show_element_info(self, symbol):
        data = ExtendedPeriodicTable.get_element(symbol)
        if data:
            electron_layers = ExtendedPeriodicTable.electron_config.get(symbol, "未知")
            atomic_mass = AtomicMass.get_mass(symbol)
            info = f"元素符号: {symbol}\n名称: {data['name']}\n原子序数: {data['atomic']}\n原子量: {data['mass']}\n族: {data['group']}\n周期: {data['period']}\n电子排布: {data['config']}\n电子层: {electron_layers}\n简介: {data['desc']}"
            messagebox.showinfo(f"元素信息 - {symbol}", info)
    
    # ==================== 计算功能菜单 ====================
    def show_calculator_menu(self):
        self.clear_content()
        self.update_status("计算功能")
        
        tk.Label(self.content_frame, text="化学计算工具 v2.0", font=self.title_font, fg="blue").pack(pady=10)
        
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
        
        # 百分组成
        percent_frame = tk.Frame(notebook)
        notebook.add(percent_frame, text="百分组成")
        self.create_percent_calc(percent_frame)
        
        # 产率计算
        yield_frame = tk.Frame(notebook)
        notebook.add(yield_frame, text="产率计算")
        self.create_yield_calc(yield_frame)
        
        # 实验式
        empirical_frame = tk.Frame(notebook)
        notebook.add(empirical_frame, text="实验式")
        self.create_empirical_calc(empirical_frame)
    
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
        tk.Label(parent, text="物质的量浓度 (mol/L)", font=self.title_font, fg="blue").pack(pady=5)
        conc_frame = tk.Frame(parent)
        conc_frame.pack(pady=5)
        tk.Label(conc_frame, text="溶质质量 (g):").grid(row=0, column=0, padx=5, pady=5)
        self.solute_mass = tk.Entry(conc_frame, width=15)
        self.solute_mass.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(conc_frame, text="体积 (L):").grid(row=1, column=0, padx=5, pady=5)
        self.solution_vol = tk.Entry(conc_frame, width=15)
        self.solution_vol.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(conc_frame, text="摩尔质量 (g/mol):").grid(row=2, column=0, padx=5, pady=5)
        self.molar_mass_conc = tk.Entry(conc_frame, width=15)
        self.molar_mass_conc.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(conc_frame, text="计算浓度", command=self.calc_concentration, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        
        tk.Label(parent, text="质量分数 (%)", font=self.title_font, fg="blue").pack(pady=5)
        mass_frame = tk.Frame(parent)
        mass_frame.pack(pady=5)
        tk.Label(mass_frame, text="溶质质量 (g):").grid(row=0, column=0, padx=5, pady=5)
        self.solute_mass_pct = tk.Entry(mass_frame, width=15)
        self.solute_mass_pct.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(mass_frame, text="溶液质量 (g):").grid(row=1, column=0, padx=5, pady=5)
        self.solution_mass_pct = tk.Entry(mass_frame, width=15)
        self.solution_mass_pct.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(mass_frame, text="计算质量分数", command=self.calc_mass_percent, bg="lightblue").grid(row=2, column=0, columnspan=2, pady=10)
        
        self.conc_result = tk.Text(parent, height=8, font=self.default_font)
        self.conc_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_concentration(self):
        try:
            mass = float(self.solute_mass.get())
            volume = float(self.solution_vol.get())
            molar_mass = float(self.molar_mass_conc.get())
            moles = mass / molar_mass
            concentration = moles / volume
            self.conc_result.delete(1.0, tk.END)
            self.conc_result.insert(tk.END, f"计算过程:\n")
            self.conc_result.insert(tk.END, f"物质的量 n = {mass} / {molar_mass} = {moles:.4f} mol\n")
            self.conc_result.insert(tk.END, f"浓度 c = n / V = {moles:.4f} / {volume} = {concentration:.4f} mol/L")
        except:
            self.conc_result.delete(1.0, tk.END)
            self.conc_result.insert(tk.END, "输入错误，请检查")
    
    def calc_mass_percent(self):
        try:
            solute = float(self.solute_mass_pct.get())
            solution = float(self.solution_mass_pct.get())
            percent = (solute / solution) * 100
            self.conc_result.insert(tk.END, f"\n\n质量分数:\n")
            self.conc_result.insert(tk.END, f"w = ({solute} / {solution}) × 100% = {percent:.2f}%")
        except:
            self.conc_result.insert(tk.END, "\n质量分数计算错误")
    
    def create_dilution_calc(self, parent):
        tk.Label(parent, text="C₁V₁ = C₂V₂", font=self.title_font, fg="blue").pack(pady=5)
        input_frame = tk.Frame(parent)
        input_frame.pack(pady=10)
        tk.Label(input_frame, text="C₁ (mol/L):").grid(row=0, column=0, padx=5, pady=5)
        self.c1_entry = tk.Entry(input_frame, width=15)
        self.c1_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(input_frame, text="V₁ (L):").grid(row=1, column=0, padx=5, pady=5)
        self.v1_entry = tk.Entry(input_frame, width=15)
        self.v1_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(input_frame, text="C₂ (mol/L):").grid(row=2, column=0, padx=5, pady=5)
        self.c2_entry = tk.Entry(input_frame, width=15)
        self.c2_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(input_frame, text="V₂ (L):").grid(row=3, column=0, padx=5, pady=5)
        self.v2_entry = tk.Entry(input_frame, width=15)
        self.v2_entry.grid(row=3, column=1, padx=5, pady=5)
        tk.Button(parent, text="计算未知量", command=self.calc_dilution, bg="lightblue").pack(pady=10)
        self.dilute_result = tk.Text(parent, height=8, font=self.default_font)
        self.dilute_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_dilution(self):
        try:
            c1 = self.c1_entry.get()
            v1 = self.v1_entry.get()
            c2 = self.c2_entry.get()
            v2 = self.v2_entry.get()
            if c1 and v1 and c2:
                c1_f = float(c1); v1_f = float(v1); c2_f = float(c2)
                v2_f = c1_f * v1_f / c2_f
                self.dilute_result.delete(1.0, tk.END)
                self.dilute_result.insert(tk.END, f"C₁V₁ = C₂V₂\n{c1_f} × {v1_f} = {c2_f} × V₂\nV₂ = {v2_f:.4f} L")
            elif c1 and v1 and v2:
                c1_f = float(c1); v1_f = float(v1); v2_f = float(v2)
                c2_f = c1_f * v1_f / v2_f
                self.dilute_result.delete(1.0, tk.END)
                self.dilute_result.insert(tk.END, f"C₁V₁ = C₂V₂\n{c1_f} × {v1_f} = C₂ × {v2_f}\nC₂ = {c2_f:.4f} mol/L")
            else:
                self.dilute_result.delete(1.0, tk.END)
                self.dilute_result.insert(tk.END, "请输入三个已知量")
        except:
            self.dilute_result.delete(1.0, tk.END)
            self.dilute_result.insert(tk.END, "输入错误")
    
    def create_ratio_calc(self, parent):
        tk.Label(parent, text="比例求解", font=self.title_font, fg="blue").pack(pady=10)
        info_frame = tk.LabelFrame(parent, text="使用说明", font=self.default_font)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(info_frame, text="格式1: a / b = c / x  → 求解 x = (b × c) / a\n格式2: a / b = x / d  → 求解 x = (a × d) / b", 
                font=self.default_font).pack(pady=5)
        
        type_frame = tk.Frame(parent)
        type_frame.pack(pady=10)
        self.ratio_type = tk.StringVar(value="type1")
        tk.Radiobutton(type_frame, text="a / b = c / x", variable=self.ratio_type, value="type1", 
                      command=self.update_ratio_inputs).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(type_frame, text="a / b = x / d", variable=self.ratio_type, value="type2",
                      command=self.update_ratio_inputs).pack(side=tk.LEFT, padx=10)
        
        self.ratio_input_frame = tk.Frame(parent)
        self.ratio_input_frame.pack(pady=20)
        self.ratio_entries = {}
        self.update_ratio_inputs()
        
        tk.Button(parent, text="计算 x", command=self.calc_ratio, bg="lightblue", width=15).pack(pady=10)
        self.ratio_result = tk.Text(parent, height=8, font=("Courier", 11))
        self.ratio_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def update_ratio_inputs(self):
        for widget in self.ratio_input_frame.winfo_children():
            widget.destroy()
        if self.ratio_type.get() == "type1":
            labels = ["a =", "b =", "c =", "x = ?"]
            self.ratio_vars = ["a", "b", "c"]
        else:
            labels = ["a =", "b =", "d =", "x = ?"]
            self.ratio_vars = ["a", "b", "d"]
        for i, label in enumerate(labels):
            tk.Label(self.ratio_input_frame, text=label).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(self.ratio_input_frame, width=15)
            entry.grid(row=i, column=1, padx=10, pady=5)
            if i < 3:
                self.ratio_entries[self.ratio_vars[i]] = entry
            else:
                entry.config(state='disabled', bg='#f0f0f0')
                self.ratio_entries["x_display"] = entry
    
    def calc_ratio(self):
        try:
            if self.ratio_type.get() == "type1":
                a = float(self.ratio_entries["a"].get())
                b = float(self.ratio_entries["b"].get())
                c = float(self.ratio_entries["c"].get())
                if a == 0:
                    raise ValueError("分母不能为0")
                x = (b * c) / a
                self.ratio_result.delete(1.0, tk.END)
                self.ratio_result.insert(tk.END, f"{a} / {b} = {c} / x\nx = ({b} × {c}) / {a} = {x}")
                self.ratio_entries["x_display"].config(state='normal')
                self.ratio_entries["x_display"].delete(0, tk.END)
                self.ratio_entries["x_display"].insert(0, f"{x:.6g}")
                self.ratio_entries["x_display"].config(state='disabled')
            else:
                a = float(self.ratio_entries["a"].get())
                b = float(self.ratio_entries["b"].get())
                d = float(self.ratio_entries["d"].get())
                if b == 0:
                    raise ValueError("分母不能为0")
                x = (a * d) / b
                self.ratio_result.delete(1.0, tk.END)
                self.ratio_result.insert(tk.END, f"{a} / {b} = x / {d}\nx = ({a} × {d}) / {b} = {x}")
                self.ratio_entries["x_display"].config(state='normal')
                self.ratio_entries["x_display"].delete(0, tk.END)
                self.ratio_entries["x_display"].insert(0, f"{x:.6g}")
                self.ratio_entries["x_display"].config(state='disabled')
        except Exception as e:
            self.ratio_result.delete(1.0, tk.END)
            self.ratio_result.insert(tk.END, f"错误: {str(e)}")
    
    def create_percent_calc(self, parent):
        tk.Label(parent, text="化合物百分组成计算", font=self.title_font, fg="blue").pack(pady=10)
        tk.Label(parent, text="输入化学式:").pack(pady=5)
        self.percent_formula = tk.Entry(parent, width=40, font=("Courier", 11))
        self.percent_formula.pack(pady=5)
        tk.Button(parent, text="计算百分组成", command=self.calc_percent_composition, bg="lightblue").pack(pady=5)
        self.percent_result = tk.Text(parent, height=10, font=self.default_font)
        self.percent_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_percent_composition(self):
        formula = self.percent_formula.get().strip()
        if not formula:
            return
        mass, _ = ChemicalFormulaParser.calculate_molar_mass(formula)
        if mass <= 0:
            self.percent_result.delete(1.0, tk.END)
            self.percent_result.insert(tk.END, "无效的化学式")
            return
        counts = ChemicalFormulaParser.parse_formula(formula)
        self.percent_result.delete(1.0, tk.END)
        self.percent_result.insert(tk.END, f"化合物: {formula}\n摩尔质量: {mass} g/mol\n\n元素百分组成:\n")
        for element, count in sorted(counts.items()):
            element_mass = AtomicMass.get_mass(element) * count
            percent = (element_mass / mass) * 100
            self.percent_result.insert(tk.END, f"{element}: {percent:.2f}%\n")
    
    def create_yield_calc(self, parent):
        tk.Label(parent, text="产率计算", font=self.title_font, fg="blue").pack(pady=10)
        input_frame = tk.Frame(parent)
        input_frame.pack(pady=10)
        tk.Label(input_frame, text="实际产量 (g):").grid(row=0, column=0, padx=5, pady=5)
        self.actual_yield = tk.Entry(input_frame, width=15)
        self.actual_yield.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(input_frame, text="理论产量 (g):").grid(row=1, column=0, padx=5, pady=5)
        self.theoretical_yield = tk.Entry(input_frame, width=15)
        self.theoretical_yield.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(parent, text="计算产率", command=self.calc_yield, bg="lightblue").pack(pady=10)
        self.yield_result = tk.Text(parent, height=6, font=self.default_font)
        self.yield_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_yield(self):
        try:
            actual = float(self.actual_yield.get())
            theoretical = float(self.theoretical_yield.get())
            percent = (actual / theoretical) * 100
            self.yield_result.delete(1.0, tk.END)
            self.yield_result.insert(tk.END, f"产率 = (实际产量 / 理论产量) × 100%\n")
            self.yield_result.insert(tk.END, f"产率 = ({actual} / {theoretical}) × 100% = {percent:.2f}%")
        except:
            self.yield_result.delete(1.0, tk.END)
            self.yield_result.insert(tk.END, "输入错误")
    
    def create_empirical_calc(self, parent):
        tk.Label(parent, text="实验式（最简式）计算", font=self.title_font, fg="blue").pack(pady=10)
        tk.Label(parent, text="输入分子式:").pack(pady=5)
        self.empirical_formula = tk.Entry(parent, width=40, font=("Courier", 11))
        self.empirical_formula.pack(pady=5)
        tk.Button(parent, text="计算实验式", command=self.calc_empirical_formula, bg="lightblue").pack(pady=5)
        self.empirical_result = tk.Text(parent, height=6, font=self.default_font)
        self.empirical_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_empirical_formula(self):
        formula = self.empirical_formula.get().strip()
        if not formula:
            return
        counts = ChemicalFormulaParser.parse_formula(formula)
        if not counts:
            self.empirical_result.delete(1.0, tk.END)
            self.empirical_result.insert(tk.END, "无效的化学式")
            return
        g = None
        for c in counts.values():
            if g is None:
                g = c
            else:
                g = gcd(g, c)
        if g and g > 1:
            empirical = "".join(f"{e}{c//g if c//g > 1 else ''}" for e, c in sorted(counts.items()))
        else:
            empirical = formula
        self.empirical_result.delete(1.0, tk.END)
        self.empirical_result.insert(tk.END, f"分子式: {formula}\n实验式（最简式）: {empirical}")
    
    # ==================== pH计算器 ====================
    def show_ph_calculator(self):
        self.clear_content()
        self.update_status("pH计算器")
        
        tk.Label(self.content_frame, text="pH值计算 v2.0", font=self.title_font, fg="blue").pack(pady=10)
        
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
        self.ph_result = tk.Text(frame1, height=6, width=50)
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
        self.weak_result = tk.Text(frame2, height=6, width=50)
        self.weak_result.pack(pady=10)
        
        # pH到浓度转换
        frame3 = tk.Frame(notebook)
        notebook.add(frame3, text="pH转浓度")
        tk.Label(frame3, text="pH值:").pack(pady=5)
        self.ph_value = tk.Entry(frame3, width=20)
        self.ph_value.pack(pady=5)
        tk.Button(frame3, text="转换", command=self.convert_ph_to_conc, bg="lightblue").pack(pady=10)
        self.ph_conc_result = tk.Text(frame3, height=6, width=50)
        self.ph_conc_result.pack(pady=10)
    
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
                h_conc = sqrt(ka * conc)
                ph = -log10(h_conc)
                self.weak_result.delete(1.0, tk.END)
                self.weak_result.insert(tk.END, f"[H⁺] = √(Ka×C) = {h_conc:.2e} mol/L\npH = {ph:.2f}")
            else:
                oh_conc = sqrt(ka * conc)
                poh = -log10(oh_conc)
                ph = 14 - poh
                self.weak_result.delete(1.0, tk.END)
                self.weak_result.insert(tk.END, f"[OH⁻] = √(Kb×C) = {oh_conc:.2e} mol/L\npOH = {poh:.2f}\npH = {ph:.2f}")
        except:
            self.weak_result.delete(1.0, tk.END)
            self.weak_result.insert(tk.END, "输入错误")
    
    def convert_ph_to_conc(self):
        try:
            ph = float(self.ph_value.get())
            conc = 10 ** (-ph)
            self.ph_conc_result.delete(1.0, tk.END)
            self.ph_conc_result.insert(tk.END, f"pH = {ph}\n[H⁺] = {conc:.2e} mol/L")
        except:
            self.ph_conc_result.delete(1.0, tk.END)
            self.ph_conc_result.insert(tk.END, "输入错误")
    
    # ==================== 气体定律 ====================
    def show_gas_law(self):
        self.clear_content()
        self.update_status("气体定律计算")
        
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
        tk.Button(input_frame, text="计算", command=self.calc_ideal_gas, bg="lightblue").grid(row=4, column=0, columnspan=2, pady=10)
        self.gas_result = tk.Text(self.content_frame, height=10, font=self.default_font)
        self.gas_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_ideal_gas(self):
        R = 0.0821
        result_text = ""
        try:
            if self.pressure.get() and self.volume.get() and self.moles.get():
                P = float(self.pressure.get()); V = float(self.volume.get()); n = float(self.moles.get())
                T = P * V / (n * R)
                result_text = f"温度 T = PV/(nR) = {T:.2f} K"
            elif self.pressure.get() and self.volume.get() and self.temperature.get():
                P = float(self.pressure.get()); V = float(self.volume.get()); T = float(self.temperature.get())
                n = P * V / (R * T)
                result_text = f"物质的量 n = PV/(RT) = {n:.4f} mol"
            elif self.pressure.get() and self.moles.get() and self.temperature.get():
                P = float(self.pressure.get()); n = float(self.moles.get()); T = float(self.temperature.get())
                V = n * R * T / P
                result_text = f"体积 V = nRT/P = {V:.2f} L"
            elif self.volume.get() and self.moles.get() and self.temperature.get():
                V = float(self.volume.get()); n = float(self.moles.get()); T = float(self.temperature.get())
                P = n * R * T / V
                result_text = f"压力 P = nRT/V = {P:.2f} atm"
            else:
                result_text = "请输入至少三个变量"
        except:
            result_text = "输入错误"
        self.gas_result.delete(1.0, tk.END)
        self.gas_result.insert(tk.END, result_text)
    
    # ==================== 热化学 ====================
    def show_thermochemistry(self):
        self.clear_content()
        self.update_status("热化学计算")
        
        tk.Label(self.content_frame, text="热化学计算 v2.0", font=self.title_font, fg="blue").pack(pady=10)
        
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 热量计算
        frame1 = tk.Frame(notebook)
        notebook.add(frame1, text="热量计算")
        tk.Label(frame1, text="Q = m·c·ΔT", font=self.title_font, fg="blue").pack(pady=5)
        input_frame = tk.Frame(frame1)
        input_frame.pack(pady=10)
        tk.Label(input_frame, text="质量 m (g):").grid(row=0, column=0, padx=5, pady=5)
        self.heat_mass = tk.Entry(input_frame, width=15)
        self.heat_mass.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(input_frame, text="比热容 c (J/g·K):").grid(row=1, column=0, padx=5, pady=5)
        self.heat_c = tk.Entry(input_frame, width=15)
        self.heat_c.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(input_frame, text="ΔT (K):").grid(row=2, column=0, padx=5, pady=5)
        self.heat_dt = tk.Entry(input_frame, width=15)
        self.heat_dt.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(input_frame, text="计算热量", command=self.calc_heat, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        self.heat_result = tk.Text(frame1, height=8)
        self.heat_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 燃烧热
        frame2 = tk.Frame(notebook)
        notebook.add(frame2, text="燃烧热")
        tk.Label(frame2, text="Q = ΔH × n", font=self.title_font, fg="blue").pack(pady=5)
        input_frame2 = tk.Frame(frame2)
        input_frame2.pack(pady=10)
        tk.Label(input_frame2, text="ΔH (kJ/mol):").grid(row=0, column=0, padx=5, pady=5)
        self.dh_comb = tk.Entry(input_frame2, width=15)
        self.dh_comb.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(input_frame2, text="n (mol):").grid(row=1, column=0, padx=5, pady=5)
        self.n_comb = tk.Entry(input_frame2, width=15)
        self.n_comb.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(input_frame2, text="计算放热", command=self.calc_combustion, bg="lightblue").grid(row=2, column=0, columnspan=2, pady=10)
        self.comb_result = tk.Text(frame2, height=8)
        self.comb_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 吉布斯自由能
        frame3 = tk.Frame(notebook)
        notebook.add(frame3, text="吉布斯自由能")
        tk.Label(frame3, text="ΔG = ΔH - TΔS", font=self.title_font, fg="blue").pack(pady=5)
        input_frame3 = tk.Frame(frame3)
        input_frame3.pack(pady=10)
        tk.Label(input_frame3, text="ΔH (kJ/mol):").grid(row=0, column=0, padx=5, pady=5)
        self.dh_gibbs = tk.Entry(input_frame3, width=15)
        self.dh_gibbs.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(input_frame3, text="ΔS (J/mol·K):").grid(row=1, column=0, padx=5, pady=5)
        self.ds_gibbs = tk.Entry(input_frame3, width=15)
        self.ds_gibbs.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(input_frame3, text="T (K):").grid(row=2, column=0, padx=5, pady=5)
        self.t_gibbs = tk.Entry(input_frame3, width=15)
        self.t_gibbs.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(input_frame3, text="计算ΔG", command=self.calc_gibbs, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        self.gibbs_result = tk.Text(frame3, height=8)
        self.gibbs_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_heat(self):
        try:
            m = float(self.heat_mass.get())
            c = float(self.heat_c.get())
            dt = float(self.heat_dt.get())
            q = m * c * dt
            self.heat_result.delete(1.0, tk.END)
            self.heat_result.insert(tk.END, f"Q = {m} × {c} × {dt} = {q:.2f} J")
        except:
            self.heat_result.delete(1.0, tk.END)
            self.heat_result.insert(tk.END, "输入错误")
    
    def calc_combustion(self):
        try:
            dh = float(self.dh_comb.get())
            n = float(self.n_comb.get())
            q = dh * n
            self.comb_result.delete(1.0, tk.END)
            self.comb_result.insert(tk.END, f"Q = {dh} × {n} = {q:.2f} kJ")
        except:
            self.comb_result.delete(1.0, tk.END)
            self.comb_result.insert(tk.END, "输入错误")
    
    def calc_gibbs(self):
        try:
            dh = float(self.dh_gibbs.get()) * 1000
            ds = float(self.ds_gibbs.get())
            t = float(self.t_gibbs.get())
            dg = dh - t * ds
            self.gibbs_result.delete(1.0, tk.END)
            self.gibbs_result.insert(tk.END, f"ΔG = ΔH - TΔS\nΔG = {dh/1000}×1000 - {t}×{ds}\nΔG = {dg/1000:.2f} kJ/mol")
            if dg < 0:
                self.gibbs_result.insert(tk.END, "\n反应自发进行")
            else:
                self.gibbs_result.insert(tk.END, "\n反应非自发")
        except:
            self.gibbs_result.delete(1.0, tk.END)
            self.gibbs_result.insert(tk.END, "输入错误")
    
    # ==================== 氧化还原 ====================
    def show_redox(self):
        self.clear_content()
        self.update_status("氧化还原分析")
        
        tk.Label(self.content_frame, text="氧化数计算", font=self.title_font, fg="blue").pack(pady=10)
        
        tk.Label(self.content_frame, text="输入化合物（如 H2O, Fe2O3）:").pack(pady=5)
        self.redox_formula = tk.Entry(self.content_frame, width=30, font=("Courier", 11))
        self.redox_formula.pack(pady=5)
        tk.Button(self.content_frame, text="计算氧化数", command=self.calc_oxidation, bg="lightblue").pack(pady=10)
        self.redox_result = tk.Text(self.content_frame, height=10, font=self.default_font)
        self.redox_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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
    
    # ==================== 有机化学 ====================
    def show_organic(self):
        self.clear_content()
        self.update_status("有机化学工具")
        
        tk.Label(self.content_frame, text="有机化学工具 v2.0", font=self.title_font, fg="blue").pack(pady=10)
        
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 官能团识别
        frame1 = tk.Frame(notebook)
        notebook.add(frame1, text="官能团识别")
        tk.Label(frame1, text="输入有机物名称:").pack(pady=5)
        self.org_name = tk.Entry(frame1, width=40)
        self.org_name.pack(pady=5)
        tk.Button(frame1, text="识别", command=self.identify_functional, bg="lightblue").pack(pady=5)
        self.func_result = tk.Text(frame1, height=10)
        self.func_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 同分异构体
        frame2 = tk.Frame(notebook)
        notebook.add(frame2, text="同分异构体")
        tk.Label(frame2, text="分子式 (如 C5H12):").pack(pady=5)
        self.isomer_formula = tk.Entry(frame2, width=20)
        self.isomer_formula.pack(pady=5)
        tk.Button(frame2, text="计算异构体数", command=self.calc_isomers, bg="lightblue").pack(pady=5)
        self.isomer_result = tk.Text(frame2, height=10)
        self.isomer_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 不饱和度
        frame3 = tk.Frame(notebook)
        notebook.add(frame3, text="不饱和度")
        tk.Label(frame3, text="分子式 (如 C6H6):").pack(pady=5)
        self.unsat_formula = tk.Entry(frame3, width=20)
        self.unsat_formula.pack(pady=5)
        tk.Button(frame3, text="计算不饱和度", command=self.calc_unsaturation, bg="lightblue").pack(pady=5)
        self.unsat_result = tk.Text(frame3, height=6)
        self.unsat_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def identify_functional(self):
        name = self.org_name.get().lower()
        self.func_result.delete(1.0, tk.END)
        functional_groups = {
            "醇": ["醇", "乙醇", "甲醇", "丙醇"], "醛": ["醛", "乙醛", "甲醛"],
            "酮": ["酮", "丙酮"], "羧酸": ["酸", "乙酸", "甲酸"], "酯": ["酯", "乙酸乙酯"],
            "醚": ["醚", "乙醚"], "胺": ["胺", "甲胺"], "烯烃": ["烯", "乙烯", "丙烯"],
            "炔烃": ["炔", "乙炔"], "芳香烃": ["苯", "甲苯", "二甲苯"]
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
        isomers = {"C5H12": 3, "C6H14": 5, "C7H16": 9, "C8H18": 18, "C4H10": 2, "C3H8": 1}
        if formula in isomers:
            self.isomer_result.insert(tk.END, f"分子式 {formula} 的同分异构体数目: {isomers[formula]} 种")
        else:
            self.isomer_result.insert(tk.END, "暂不支持该分子式\n常见烷烃异构体数:\nC₄H₁₀: 2, C₅H₁₂: 3, C₆H₁₄: 5, C₇H₁₆: 9")
    
    def calc_unsaturation(self):
        formula = self.unsat_formula.get().strip()
        self.unsat_result.delete(1.0, tk.END)
        try:
            c_count = re.findall(r'C(\d*)', formula)
            h_count = re.findall(r'H(\d*)', formula)
            n_count = re.findall(r'N(\d*)', formula)
            c = int(c_count[0]) if c_count else 0
            h = int(h_count[0]) if h_count else 0
            n = int(n_count[0]) if n_count else 0
            du = (2 * c + 2 + n - h) / 2
            self.unsat_result.insert(tk.END, f"分子式: {formula}\n不饱和度: {du:.1f}\n")
            if du == 0:
                self.unsat_result.insert(tk.END, "无环饱和化合物")
            elif du == 1:
                self.unsat_result.insert(tk.END, "一个双键或一个环")
            elif du == 2:
                self.unsat_result.insert(tk.END, "两个双键，或一个三键，或一个双键一个环")
            elif du >= 4:
                self.unsat_result.insert(tk.END, "可能含有苯环")
        except:
            self.unsat_result.insert(tk.END, "输入错误")
    
    # ==================== 溶解度查询 ====================
    def show_solubility(self):
        self.clear_content()
        self.update_status("溶解度查询")
        
        tk.Label(self.content_frame, text="物质溶解度查询 v2.0", font=self.title_font, fg="blue").pack(pady=10)
        
        tree = ttk.Treeview(self.content_frame, columns=("物质", "溶解度"), show="headings", height=15)
        tree.heading("物质", text="物质")
        tree.heading("溶解度", text="溶解度 (g/100g水, 20°C)")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        common = [("NaCl", 36.0), ("KCl", 34.0), ("KNO3", 31.6), ("NH4Cl", 37.2),
                  ("Ca(OH)2", 0.173), ("AgNO3", 216), ("CuSO4", 20.7), ("NaOH", 109)]
        for substance, solubility in common:
            tree.insert("", tk.END, values=(substance, solubility))
        
        rules_frame = tk.LabelFrame(self.content_frame, text="溶解度规则", font=self.title_font)
        rules_frame.pack(fill=tk.X, padx=10, pady=10)
        rules = """• 碱金属盐大多可溶\n• 硝酸盐全部可溶\n• 氯化物、溴化物、碘化物除Ag⁺、Pb²⁺外可溶\n• 硫酸盐除Ba²⁺、Pb²⁺、Ca²⁺外可溶\n• 碳酸盐、磷酸盐大多不溶"""
        tk.Label(rules_frame, text=rules, font=self.default_font, justify=tk.LEFT).pack(pady=5, padx=10)
    
    # ==================== 缓冲溶液 ====================
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
            self.buffer_result.insert(tk.END, f"pH = pKa + log([A⁻]/[HA])\npH = {pka} + log({base}/{acid})\npH = {ph:.2f}")
        except:
            self.buffer_result.delete(1.0, tk.END)
            self.buffer_result.insert(tk.END, "输入错误")
    
    # ==================== 酸碱滴定 ====================
    def show_titration(self):
        self.clear_content()
        self.update_status("酸碱滴定计算")
        
        tk.Label(self.content_frame, text="酸碱滴定计算 v2.0", font=self.title_font, fg="blue").pack(pady=10)
        
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
    
    # ==================== 光谱分析 ====================
    def show_spectroscopy(self):
        self.clear_content()
        self.update_status("光谱分析")
        
        tk.Label(self.content_frame, text="光谱分析工具 v2.0", font=self.title_font, fg="blue").pack(pady=10)
        
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 波长能量转换
        frame1 = tk.Frame(notebook)
        notebook.add(frame1, text="波长-能量转换")
        tk.Label(frame1, text="波长 λ (nm):").pack(pady=5)
        self.wavelength = tk.Entry(frame1, width=20)
        self.wavelength.pack(pady=5)
        tk.Button(frame1, text="转换", command=self.convert_wavelength, bg="lightblue").pack(pady=5)
        self.wave_result = tk.Text(frame1, height=6)
        self.wave_result.pack(pady=10)
        
        # 颜色与波长
        frame2 = tk.Frame(notebook)
        notebook.add(frame2, text="颜色与波长")
        colors = [("紫", "400-450"), ("蓝", "450-500"), ("青", "500-550"),
                  ("绿", "550-580"), ("黄", "580-600"), ("橙", "600-650"), ("红", "650-750")]
        for color, wavelength in colors:
            tk.Label(frame2, text=f"{color}: {wavelength} nm", font=self.default_font).pack(pady=2)
    
    def convert_wavelength(self):
        try:
            lam = float(self.wavelength.get()) * 1e-9
            c = 3e8
            h = 6.626e-34
            energy = h * c / lam
            self.wave_result.delete(1.0, tk.END)
            self.wave_result.insert(tk.END, f"波长: {self.wavelength.get()} nm\n能量: {energy:.2e} J\n能量: {energy/1.602e-19:.2f} eV")
        except:
            self.wave_result.delete(1.0, tk.END)
            self.wave_result.insert(tk.END, "输入错误")
    
    # ==================== 化学动力学 ====================
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
            k = a * exp(-ea / (r * t))
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
            filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件", "*.txt")])
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("化学工具箱 v2.0 计算结果\n")
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
        tutorial = """化学工具箱 v2.0 使用教程

主要功能按钮：
1. 配平 - 化学方程式配平（支持离子方程式）
2. 元素周期表 - 118种元素查询
3. 计算 - 摩尔质量、浓度、稀释、比例、百分组成、产率、实验式
4. 实用功能 - pH计算器、气体定律、热化学、氧化还原、有机化学、溶解度、缓冲溶液、酸碱滴定、光谱分析、化学动力学

离子方程式格式：
- 阳离子：H* 表示 H⁺，Ca** 表示 Ca²⁺
- 阴离子：HCO3^ 表示 HCO₃⁻，SO4^^ 表示 SO₄²⁻
- 示例：HCO3^+H*=CO2+H2O

快捷键：
- 回车键：执行当前功能计算
- Ctrl+E：导出结果

注意事项：
- 氯的相对原子质量为35.5
- 温度使用开尔文(K)单位
- 浓度单位使用mol/L"""
        
        messagebox.showinfo("使用教程", tutorial)
    
    def show_about(self):
        about = """化学工具箱 v2.0

完整功能列表：
1. 化学方程式配平（支持离子方程式）
2. 元素周期表（118种元素）
3. 计算功能（摩尔质量、浓度、稀释、比例、百分组成、产率、实验式）
4. pH计算（强酸强碱、弱酸弱碱、pH转浓度）
5. 气体定律（理想气体状态方程）
6. 热化学（热量计算、燃烧热、吉布斯自由能）
7. 氧化还原（氧化数计算）
8. 有机化学（官能团识别、同分异构体、不饱和度）
9. 溶解度查询
10. 缓冲溶液计算
11. 酸碱滴定计算
12. 光谱分析（波长-能量转换）
13. 化学动力学（阿伦尼乌斯方程、半衰期）
14. 单位换算
15. 实验记录本

开发者: 化学爱好者
版本: 2.0
版本日期: 2025年4月4日
开源协议: MIT License

感谢使用！"""
        
        messagebox.showinfo("关于", about)
    
    def show_help(self):
        help_text = """化学工具箱 v2.0 帮助

快速入门：
1. 点击顶部按钮选择功能
2. 在输入框中输入数据
3. 点击"计算"或"确定"按钮

离子方程式格式：
- 阳离子：H* 表示 H⁺，Ca** 表示 Ca²⁺
- 阴离子：HCO3^ 表示 HCO₃⁻，SO4^^ 表示 SO₄²⁻
- 示例：HCO3^+H*=CO2+H2O

常用快捷键：
- 回车键：执行当前功能计算
- Ctrl+E：导出结果

注意事项：
- 氯的相对原子质量为35.5
- 温度使用开尔文(K)单位
- 浓度单位使用mol/L

技术支持：请查看"使用教程"获取详细信息"""
        
        messagebox.showinfo("帮助", help_text)

# ==================== 程序入口 ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = ChemistryToolbox(root)
    root.mainloop()