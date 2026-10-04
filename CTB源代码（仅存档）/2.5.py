#此版本修复了一个大bug(2.4)
#之前的版本，配平有单质的化学方程式时，单质的化合价不能正确显示为0价(2.4)
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import re
from collections import defaultdict
import numpy as np
from math import gcd, log10, floor, exp
import datetime
import random
import webbrowser
import os

# ==================== 化合价数据 ====================
class ValenceData:
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
    def calculate_percent_composition(formula):
        counts = ChemicalFormulaParser.parse_formula(formula)
        if not counts:
            return None, None
        total_mass = 0
        for element, count in counts.items():
            total_mass += AtomicMass.get_mass(element) * count
        if total_mass == 0:
            return None, None
        percent = {}
        for element, count in counts.items():
            mass = AtomicMass.get_mass(element) * count
            percent[element] = (mass / total_mass) * 100
        return total_mass, percent
    
    @staticmethod
    def calculate_oxidation_states(formula):
        counts = ChemicalFormulaParser.parse_formula(formula)
        if not counts:
            return {}
        # ----- 新增单质判断 -----
        if len(counts) == 1:
            element = list(counts.keys())[0]
            return {element: 0}
        element_valence = {}
        def get_electronegativity(e):
            en = {'F': 4.0, 'O': 3.5, 'Cl': 3.2, 'N': 3.0, 'Br': 3.0, 
                  'S': 2.6, 'C': 2.6, 'P': 2.2, 'H': 2.2, 'B': 2.0}
            return en.get(e, 2.5)
        elements = list(counts.keys())
        elements.sort(key=get_electronegativity, reverse=True)
        for element in elements:
            valences = ValenceData.get_valence(element, formula)
            element_valence[element] = valences[0] if valences else 0
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

# ==================== 扩展元素周期表数据 ====================
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
        "Xe": "2,8,18,18,8", "Cs": "2,8,18,18,8,1", "Ba": "2,8,18,18,8,2", "La": "2,8,18,18,9,2",
        "Ce": "2,8,18,19,9,2", "Pr": "2,8,18,21,8,2", "Nd": "2,8,18,22,8,2", "Pm": "2,8,18,23,8,2",
        "Sm": "2,8,18,24,8,2", "Eu": "2,8,18,25,8,2", "Gd": "2,8,18,25,9,2", "Tb": "2,8,18,27,8,2",
        "Dy": "2,8,18,28,8,2", "Ho": "2,8,18,29,8,2", "Er": "2,8,18,30,8,2", "Tm": "2,8,18,31,8,2",
        "Yb": "2,8,18,32,8,2", "Lu": "2,8,18,32,9,2", "Hf": "2,8,18,32,10,2", "Ta": "2,8,18,32,11,2",
        "W": "2,8,18,32,12,2", "Re": "2,8,18,32,13,2", "Os": "2,8,18,32,14,2", "Ir": "2,8,18,32,15,2",
        "Pt": "2,8,18,32,17,1", "Au": "2,8,18,32,18,1", "Hg": "2,8,18,32,18,2", "Tl": "2,8,18,32,18,3",
        "Pb": "2,8,18,32,18,4", "Bi": "2,8,18,32,18,5", "Po": "2,8,18,32,18,6", "At": "2,8,18,32,18,7", "Rn": "2,8,18,32,18,8",
        "Fr": "2,8,18,32,18,8,1", "Ra": "2,8,18,32,18,8,2", "Ac": "2,8,18,32,18,9,2", "Th": "2,8,18,32,18,10,2",
        "Pa": "2,8,18,32,20,9,2", "U": "2,8,18,32,21,9,2", "Np": "2,8,18,32,22,9,2", "Pu": "2,8,18,32,24,8,2", "Am": "2,8,18,32,25,8,2",
    }
    electronegativity = {
        'H': 2.20, 'He': 0.00, 'Li': 0.98, 'Be': 1.57, 'B': 2.04, 'C': 2.55, 'N': 3.04, 'O': 3.44, 'F': 3.98, 'Ne': 0.00,
        'Na': 0.93, 'Mg': 1.31, 'Al': 1.61, 'Si': 1.90, 'P': 2.19, 'S': 2.58, 'Cl': 3.16, 'Ar': 0.00, 'K': 0.82, 'Ca': 1.00,
        'Sc': 1.36, 'Ti': 1.54, 'V': 1.63, 'Cr': 1.66, 'Mn': 1.55, 'Fe': 1.83, 'Co': 1.88, 'Ni': 1.91, 'Cu': 1.90, 'Zn': 1.65,
        'Ga': 1.81, 'Ge': 2.01, 'As': 2.18, 'Se': 2.55, 'Br': 2.96, 'Kr': 3.00, 'Rb': 0.82, 'Sr': 0.95, 'Y': 1.22, 'Zr': 1.33,
        'Nb': 1.60, 'Mo': 2.16, 'Tc': 1.90, 'Ru': 2.20, 'Rh': 2.28, 'Pd': 2.20, 'Ag': 1.93, 'Cd': 1.69, 'In': 1.78, 'Sn': 1.96,
        'Sb': 2.05, 'Te': 2.10, 'I': 2.66, 'Xe': 2.60, 'Cs': 0.79, 'Ba': 0.89, 'La': 1.10, 'Ce': 1.12, 'Pr': 1.13, 'Nd': 1.14,
        'Pm': 1.13, 'Sm': 1.17, 'Eu': 1.20, 'Gd': 1.20, 'Tb': 1.10, 'Dy': 1.22, 'Ho': 1.23, 'Er': 1.24, 'Tm': 1.25, 'Yb': 1.10,
        'Lu': 1.27, 'Hf': 1.30, 'Ta': 1.50, 'W': 2.36, 'Re': 1.90, 'Os': 2.20, 'Ir': 2.20, 'Pt': 2.28, 'Au': 2.54, 'Hg': 2.00,
        'Tl': 1.62, 'Pb': 2.33, 'Bi': 2.02, 'Po': 2.00, 'At': 2.20, 'Rn': 2.20, 'Fr': 0.70, 'Ra': 0.89, 'Ac': 1.10, 'Th': 1.30,
        'Pa': 1.50, 'U': 1.38, 'Np': 1.36, 'Pu': 1.28, 'Am': 1.30, 'Cm': 1.30, 'Bk': 1.30, 'Cf': 1.30, 'Es': 1.30, 'Fm': 1.30,
        'Md': 1.30, 'No': 1.30, 'Lr': 1.30, 'Rf': 1.30, 'Db': 1.30, 'Sg': 1.30, 'Bh': 1.30, 'Hs': 1.30, 'Mt': 1.30, 'Ds': 1.30,
        'Rg': 1.30, 'Cn': 1.30, 'Nh': 1.30, 'Fl': 1.30, 'Mc': 1.30, 'Lv': 1.30, 'Ts': 1.30, 'Og': 1.30,
    }
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
        "Ag": {"name": "银", "atomic": 47, "mass": 107.87, "group": 11, "period": 5, "config": "[Kr] 4d¹⁰ 5s¹", "desc": "贵金属，导电性最佳"},
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
        "Ce": {"name": "铈", "atomic": 58, "mass": 140.12, "group": 3, "period": 6, "config": "[Xe] 4f¹ 5d¹ 6s²", "desc": "稀土元素"},
        "Pr": {"name": "镨", "atomic": 59, "mass": 140.91, "group": 3, "period": 6, "config": "[Xe] 4f³ 6s²", "desc": "稀土元素"},
        "Nd": {"name": "钕", "atomic": 60, "mass": 144.24, "group": 3, "period": 6, "config": "[Xe] 4f⁴ 6s²", "desc": "用于永磁体"},
        "Pm": {"name": "钷", "atomic": 61, "mass": 145, "group": 3, "period": 6, "config": "[Xe] 4f⁵ 6s²", "desc": "放射性稀土元素"},
        "Sm": {"name": "钐", "atomic": 62, "mass": 150.36, "group": 3, "period": 6, "config": "[Xe] 4f⁶ 6s²", "desc": "稀土元素"},
        "Eu": {"name": "铕", "atomic": 63, "mass": 151.96, "group": 3, "period": 6, "config": "[Xe] 4f⁷ 6s²", "desc": "用于荧光粉"},
        "Gd": {"name": "钆", "atomic": 64, "mass": 157.25, "group": 3, "period": 6, "config": "[Xe] 4f⁷ 5d¹ 6s²", "desc": "核反应堆控制棒"},
        "Tb": {"name": "铽", "atomic": 65, "mass": 158.93, "group": 3, "period": 6, "config": "[Xe] 4f⁹ 6s²", "desc": "稀土元素"},
        "Dy": {"name": "镝", "atomic": 66, "mass": 162.50, "group": 3, "period": 6, "config": "[Xe] 4f¹⁰ 6s²", "desc": "稀土元素"},
        "Ho": {"name": "钬", "atomic": 67, "mass": 164.93, "group": 3, "period": 6, "config": "[Xe] 4f¹¹ 6s²", "desc": "稀土元素"},
        "Er": {"name": "铒", "atomic": 68, "mass": 167.26, "group": 3, "period": 6, "config": "[Xe] 4f¹² 6s²", "desc": "稀土元素"},
        "Tm": {"name": "铥", "atomic": 69, "mass": 168.93, "group": 3, "period": 6, "config": "[Xe] 4f¹³ 6s²", "desc": "稀土元素"},
        "Yb": {"name": "镱", "atomic": 70, "mass": 173.05, "group": 3, "period": 6, "config": "[Xe] 4f¹⁴ 6s²", "desc": "稀土元素"},
        "Lu": {"name": "镥", "atomic": 71, "mass": 174.97, "group": 3, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹ 6s²", "desc": "稀土元素"},
        "Hf": {"name": "铪", "atomic": 72, "mass": 178.49, "group": 4, "period": 6, "config": "[Xe] 4f¹⁴ 5d² 6s²", "desc": "耐热合金"},
        "Ta": {"name": "钽", "atomic": 73, "mass": 180.95, "group": 5, "period": 6, "config": "[Xe] 4f¹⁴ 5d³ 6s²", "desc": "耐腐蚀金属"},
        "W": {"name": "钨", "atomic": 74, "mass": 183.84, "group": 6, "period": 6, "config": "[Xe] 4f¹⁴ 5d⁴ 6s²", "desc": "熔点最高的金属"},
        "Re": {"name": "铼", "atomic": 75, "mass": 186.21, "group": 7, "period": 6, "config": "[Xe] 4f¹⁴ 5d⁵ 6s²", "desc": "高熔点金属"},
        "Os": {"name": "锇", "atomic": 76, "mass": 190.23, "group": 8, "period": 6, "config": "[Xe] 4f¹⁴ 5d⁶ 6s²", "desc": "密度最大金属"},
        "Ir": {"name": "铱", "atomic": 77, "mass": 192.22, "group": 9, "period": 6, "config": "[Xe] 4f¹⁴ 5d⁷ 6s²", "desc": "耐腐蚀"},
        "Pt": {"name": "铂", "atomic": 78, "mass": 195.08, "group": 10, "period": 6, "config": "[Xe] 4f¹⁴ 5d⁹ 6s¹", "desc": "贵金属，催化剂"},
        "Au": {"name": "金", "atomic": 79, "mass": 196.97, "group": 11, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s¹", "desc": "延展性好，不氧化"},
        "Hg": {"name": "汞", "atomic": 80, "mass": 200.59, "group": 12, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s²", "desc": "唯一液态金属"},
        "Tl": {"name": "铊", "atomic": 81, "mass": 204.38, "group": 13, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p¹", "desc": "剧毒"},
        "Pb": {"name": "铅", "atomic": 82, "mass": 207.2, "group": 14, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p²", "desc": "重金属，有毒"},
        "Bi": {"name": "铋", "atomic": 83, "mass": 208.98, "group": 15, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p³", "desc": "低熔点金属"},
        "Po": {"name": "钋", "atomic": 84, "mass": 209, "group": 16, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁴", "desc": "放射性"},
        "At": {"name": "砹", "atomic": 85, "mass": 210, "group": 17, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁵", "desc": "稀有放射性元素"},
        "Rn": {"name": "氡", "atomic": 86, "mass": 222, "group": 18, "period": 6, "config": "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁶", "desc": "放射性气体"},
        "Fr": {"name": "钫", "atomic": 87, "mass": 223, "group": 1, "period": 7, "config": "[Rn] 7s¹", "desc": "放射性碱金属"},
        "Ra": {"name": "镭", "atomic": 88, "mass": 226, "group": 2, "period": 7, "config": "[Rn] 7s²", "desc": "放射性，用于放疗"},
        "Ac": {"name": "锕", "atomic": 89, "mass": 227, "group": 3, "period": 7, "config": "[Rn] 6d¹ 7s²", "desc": "放射性元素"},
        "Th": {"name": "钍", "atomic": 90, "mass": 232.04, "group": 3, "period": 7, "config": "[Rn] 6d² 7s²", "desc": "放射性，核燃料"},
        "Pa": {"name": "镤", "atomic": 91, "mass": 231.04, "group": 3, "period": 7, "config": "[Rn] 5f² 6d¹ 7s²", "desc": "放射性元素"},
        "U": {"name": "铀", "atomic": 92, "mass": 238.03, "group": 3, "period": 7, "config": "[Rn] 5f³ 6d¹ 7s²", "desc": "核燃料，放射性"},
        "Np": {"name": "镎", "atomic": 93, "mass": 237, "group": 3, "period": 7, "config": "[Rn] 5f⁴ 6d¹ 7s²", "desc": "人工合成放射性元素"},
        "Pu": {"name": "钚", "atomic": 94, "mass": 244, "group": 3, "period": 7, "config": "[Rn] 5f⁶ 7s²", "desc": "核武器原料"},
        "Am": {"name": "镅", "atomic": 95, "mass": 243, "group": 3, "period": 7, "config": "[Rn] 5f⁷ 7s²", "desc": "烟雾探测器"},
        "Cm": {"name": "锔", "atomic": 96, "mass": 247, "group": 3, "period": 7, "config": "[Rn] 5f⁷ 6d¹ 7s²", "desc": "放射性元素"},
        "Bk": {"name": "锫", "atomic": 97, "mass": 247, "group": 3, "period": 7, "config": "[Rn] 5f⁹ 7s²", "desc": "人工合成元素"},
        "Cf": {"name": "锎", "atomic": 98, "mass": 251, "group": 3, "period": 7, "config": "[Rn] 5f¹⁰ 7s²", "desc": "中子源"},
        "Es": {"name": "锿", "atomic": 99, "mass": 252, "group": 3, "period": 7, "config": "[Rn] 5f¹¹ 7s²", "desc": "人工合成元素"},
        "Fm": {"name": "镄", "atomic": 100, "mass": 257, "group": 3, "period": 7, "config": "[Rn] 5f¹² 7s²", "desc": "人工合成元素"},
        "Md": {"name": "钔", "atomic": 101, "mass": 258, "group": 3, "period": 7, "config": "[Rn] 5f¹³ 7s²", "desc": "人工合成元素"},
        "No": {"name": "锘", "atomic": 102, "mass": 259, "group": 3, "period": 7, "config": "[Rn] 5f¹⁴ 7s²", "desc": "人工合成元素"},
        "Lr": {"name": "铹", "atomic": 103, "mass": 262, "group": 3, "period": 7, "config": "[Rn] 5f¹⁴ 6d¹ 7s²", "desc": "人工合成元素"},
        "Rf": {"name": "𬬻", "atomic": 104, "mass": 267, "group": 4, "period": 7, "config": "[Rn] 5f¹⁴ 6d² 7s²", "desc": "人工合成元素"},
        "Db": {"name": "𬭊", "atomic": 105, "mass": 268, "group": 5, "period": 7, "config": "[Rn] 5f¹⁴ 6d³ 7s²", "desc": "人工合成元素"},
        "Sg": {"name": "𬭳", "atomic": 106, "mass": 269, "group": 6, "period": 7, "config": "[Rn] 5f¹⁴ 6d⁴ 7s²", "desc": "人工合成元素"},
        "Bh": {"name": "𬭛", "atomic": 107, "mass": 270, "group": 7, "period": 7, "config": "[Rn] 5f¹⁴ 6d⁵ 7s²", "desc": "人工合成元素"},
        "Hs": {"name": "𬭶", "atomic": 108, "mass": 269, "group": 8, "period": 7, "config": "[Rn] 5f¹⁴ 6d⁶ 7s²", "desc": "人工合成元素"},
        "Mt": {"name": "鿏", "atomic": 109, "mass": 278, "group": 9, "period": 7, "config": "[Rn] 5f¹⁴ 6d⁷ 7s²", "desc": "人工合成元素"},
        "Ds": {"name": "𫟼", "atomic": 110, "mass": 281, "group": 10, "period": 7, "config": "[Rn] 5f¹⁴ 6d⁸ 7s²", "desc": "人工合成元素"},
        "Rg": {"name": "𬬭", "atomic": 111, "mass": 282, "group": 11, "period": 7, "config": "[Rn] 5f¹⁴ 6d⁹ 7s²", "desc": "人工合成元素"},
        "Cn": {"name": "鎶", "atomic": 112, "mass": 285, "group": 12, "period": 7, "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s²", "desc": "人工合成元素"},
        "Nh": {"name": "鉨", "atomic": 113, "mass": 286, "group": 13, "period": 7, "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p¹", "desc": "人工合成元素"},
        "Fl": {"name": "𫓧", "atomic": 114, "mass": 289, "group": 14, "period": 7, "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p²", "desc": "人工合成元素"},
        "Mc": {"name": "镆", "atomic": 115, "mass": 290, "group": 15, "period": 7, "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p³", "desc": "人工合成元素"},
        "Lv": {"name": "𫟷", "atomic": 116, "mass": 293, "group": 16, "period": 7, "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁴", "desc": "人工合成元素"},
        "Ts": {"name": "鿬", "atomic": 117, "mass": 294, "group": 17, "period": 7, "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁵", "desc": "人工合成元素"},
        "Og": {"name": "气奥", "atomic": 118, "mass": 294, "group": 18, "period": 7, "config": "[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁶", "desc": "人工合成元素"},
    }

# ==================== 主应用程序 ====================
import importlib.util

class ChemistryToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title("化学工具箱 v2.5")      # 版本号改为 2.5
        self.root.geometry("1200x800")
        self.default_font = ("Microsoft YaHei", 10)
        self.title_font = ("Microsoft YaHei", 12, "bold")
         # 暴露核心类给插件使用
        self.ChemicalFormulaParser = ChemicalFormulaParser
        self.AtomicMass = AtomicMass
        self.ValenceData = ValenceData
        self.EquationBalancer = EquationBalancer
        self.ExtendedPeriodicTable = ExtendedPeriodicTable
        
        self.plugins = []
        self.create_menubar()
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.create_main_buttons()
        self.status_frame = tk.Frame(root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tk.Label(self.status_frame, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.load_plugins()
        self.show_balance()
    
    def load_plugins(self):
        """扫描 plugins 文件夹并加载插件"""
        plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
            # 创建示例插件文件
            example_plugin = os.path.join(plugin_dir, "example_plugin.py")
            if not os.path.exists(example_plugin):
                with open(example_plugin, 'w', encoding='utf-8') as f:
                    f.write('''# 示例插件
import tkinter                            
class Plugin:
                            
    def __init__(self, app):
        self.app = app
        self.name = "示例插件"
    
    def get_menu_name(self):
        return self.name
    
    def run(self):
        self.app.clear_content()
        tkinter.Label(self.app.content_frame, text="这是一个示例插件", font=self.app.title_font).pack(pady=20)
        tkinter.Label(self.app.content_frame, text="你可以在这里添加自定义功能", font=self.app.default_font).pack()
''')
        # 遍历加载
        for file in os.listdir(plugin_dir):
            if file.endswith(".py") and not file.startswith("_"):
                try:
                    spec = importlib.util.spec_from_file_location(file[:-3], os.path.join(plugin_dir, file))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, "Plugin"):
                        plugin_instance = module.Plugin(self)
                        self.plugins.append(plugin_instance)
                        self.update_status(f"已加载插件: {plugin_instance.name}")
                except Exception as e:
                    print(f"加载插件 {file} 失败: {e}")
        # 如果有插件，在实用功能菜单中添加插件入口
        if self.plugins:
            self.update_status(f"共加载 {len(self.plugins)} 个插件")
    
    def show_plugin_menu(self):
        """显示插件菜单（由实用功能菜单调用）"""
        plugin_menu = tk.Menu(self.root, tearoff=0)
        for plugin in self.plugins:
            plugin_menu.add_command(label=plugin.get_menu_name(), command=plugin.run)
        # 获取实用功能按钮位置
        btn = self.button_frame.grid_slaves(row=0, column=3)[0]
        plugin_menu.post(btn.winfo_rootx(), btn.winfo_rooty() + btn.winfo_height())
    
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
            btn = tk.Button(self.button_frame, text=text, width=12, font=self.title_font, command=command)
            btn.grid(row=0, column=i, padx=3, pady=2)
    
    def show_utility_menu(self):
        utility_menu = tk.Menu(self.root, tearoff=0)
        # 原有10项
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
        # 新增6项
        utility_menu.add_separator()
        utility_menu.add_command(label="电化学计算（能斯特方程）", command=self.show_electrochem)
        utility_menu.add_command(label="化学平衡计算", command=self.show_equilibrium)
        utility_menu.add_command(label="热力学计算（ΔG, ΔH, ΔS）", command=self.show_thermodynamics)
        utility_menu.add_command(label="气体分压计算", command=self.show_partial_pressure)
        utility_menu.add_command(label="核化学计算（半衰期）", command=self.show_nuclear)
        utility_menu.add_command(label="溶液配制计算", command=self.show_solution_prep)
        # 如果有插件，添加插件菜单入口
        if self.plugins:
            utility_menu.add_separator()
            utility_menu.add_command(label="插件功能", command=self.show_plugin_menu)
        btn = self.button_frame.grid_slaves(row=0, column=3)[0]
        utility_menu.post(btn.winfo_rootx(), btn.winfo_rooty() + btn.winfo_height())
    
    def show_calculator_menu(self):
        self.clear_content()
        self.update_status("计算功能")
        tk.Label(self.content_frame, text="化学计算工具", font=self.title_font, fg="blue").pack(pady=10)
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        # 原有4个标签页
        molar_frame = tk.Frame(notebook)
        notebook.add(molar_frame, text="摩尔质量")
        self.create_molar_calc(molar_frame)
        conc_frame = tk.Frame(notebook)
        notebook.add(conc_frame, text="浓度计算")
        self.create_concentration_calc(conc_frame)
        dilute_frame = tk.Frame(notebook)
        notebook.add(dilute_frame, text="稀释计算")
        self.create_dilution_calc(dilute_frame)
        ratio_frame = tk.Frame(notebook)
        notebook.add(ratio_frame, text="比例求解")
        self.create_ratio_calc(ratio_frame)
        # 新增4个标签页
        percent_frame = tk.Frame(notebook)
        notebook.add(percent_frame, text="元素百分比")
        self.create_percent_composition_calc(percent_frame)
        empirical_frame = tk.Frame(notebook)
        notebook.add(empirical_frame, text="经验式确定")
        self.create_empirical_formula_calc(empirical_frame)
        conc_convert_frame = tk.Frame(notebook)
        notebook.add(conc_convert_frame, text="浓度换算")
        self.create_concentration_convert_calc(conc_convert_frame)
        yield_frame = tk.Frame(notebook)
        notebook.add(yield_frame, text="产率计算")
        self.create_yield_calc(yield_frame)
    
    # ---------- 原计算功能的实现 ----------
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
        tk.Label(parent, text="比例求解", font=self.title_font, fg="blue").pack(pady=10)
        info_frame = tk.LabelFrame(parent, text="使用说明", font=self.default_font)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(info_frame, text="格式1: a / b = c / x  → 求解 x = (b × c) / a\n格式2: a / b = x / d  → 求解 x = (a × d) / b", 
                font=self.default_font, justify=tk.LEFT).pack(pady=5, padx=10)
        type_frame = tk.Frame(parent)
        type_frame.pack(pady=10)
        self.ratio_type = tk.StringVar(value="type1")
        tk.Radiobutton(type_frame, text="a / b = c / x", variable=self.ratio_type, value="type1", 
                      command=self.update_ratio_inputs, font=self.default_font).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(type_frame, text="a / b = x / d", variable=self.ratio_type, value="type2",
                      command=self.update_ratio_inputs, font=self.default_font).pack(side=tk.LEFT, padx=10)
        self.ratio_input_frame = tk.Frame(parent)
        self.ratio_input_frame.pack(pady=20)
        self.ratio_entries = {}
        self.update_ratio_inputs()
        tk.Button(parent, text="计算 x", command=self.calc_ratio, bg="lightblue", width=15, font=self.default_font).pack(pady=10)
        result_frame = tk.LabelFrame(parent, text="计算结果", font=self.default_font)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.ratio_result = tk.Text(result_frame, height=6, font=("Courier", 11))
        self.ratio_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        example_frame = tk.Frame(parent)
        example_frame.pack(pady=5)
        tk.Label(example_frame, text="示例:").pack(side=tk.LEFT)
        tk.Button(example_frame, text="2/3=4/x", command=lambda: self.load_ratio_example("type1", 2, 3, 4), font=self.default_font).pack(side=tk.LEFT, padx=3)
        tk.Button(example_frame, text="2/3=x/6", command=lambda: self.load_ratio_example("type2", 2, 3, 6), font=self.default_font).pack(side=tk.LEFT, padx=3)
    
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
            tk.Label(self.ratio_input_frame, text=label, font=self.default_font).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(self.ratio_input_frame, width=15, font=("Courier", 11))
            entry.grid(row=i, column=1, padx=10, pady=5)
            if i < 3:
                self.ratio_entries[self.ratio_vars[i]] = entry
            else:
                entry.config(state='disabled', bg='#f0f0f0')
                self.ratio_entries["x_display"] = entry
    
    def load_ratio_example(self, ratio_type, a, b, c_or_d):
        self.ratio_type.set(ratio_type)
        self.update_ratio_inputs()
        if ratio_type == "type1":
            self.ratio_entries["a"].delete(0, tk.END); self.ratio_entries["a"].insert(0, str(a))
            self.ratio_entries["b"].delete(0, tk.END); self.ratio_entries["b"].insert(0, str(b))
            self.ratio_entries["c"].delete(0, tk.END); self.ratio_entries["c"].insert(0, str(c_or_d))
        else:
            self.ratio_entries["a"].delete(0, tk.END); self.ratio_entries["a"].insert(0, str(a))
            self.ratio_entries["b"].delete(0, tk.END); self.ratio_entries["b"].insert(0, str(b))
            self.ratio_entries["d"].delete(0, tk.END); self.ratio_entries["d"].insert(0, str(c_or_d))
        self.calc_ratio()
    
    def calc_ratio(self):
        try:
            if self.ratio_type.get() == "type1":
                a = float(self.ratio_entries["a"].get())
                b = float(self.ratio_entries["b"].get())
                c = float(self.ratio_entries["c"].get())
                if a == 0:
                    raise ValueError("分母 a 不能为0")
                x = (b * c) / a
                self.ratio_result.delete(1.0, tk.END)
                self.ratio_result.insert(tk.END, f"比例式: {a} / {b} = {c} / x\n\n解: x = (b × c) / a = ({b}×{c})/{a} = {x:.6g}")
                self.ratio_entries["x_display"].config(state='normal')
                self.ratio_entries["x_display"].delete(0, tk.END); self.ratio_entries["x_display"].insert(0, f"{x:.6g}")
                self.ratio_entries["x_display"].config(state='disabled')
            else:
                a = float(self.ratio_entries["a"].get())
                b = float(self.ratio_entries["b"].get())
                d = float(self.ratio_entries["d"].get())
                if b == 0:
                    raise ValueError("分母 b 不能为0")
                x = (a * d) / b
                self.ratio_result.delete(1.0, tk.END)
                self.ratio_result.insert(tk.END, f"比例式: {a} / {b} = x / {d}\n\n解: x = (a × d) / b = ({a}×{d})/{b} = {x:.6g}")
                self.ratio_entries["x_display"].config(state='normal')
                self.ratio_entries["x_display"].delete(0, tk.END); self.ratio_entries["x_display"].insert(0, f"{x:.6g}")
                self.ratio_entries["x_display"].config(state='disabled')
        except Exception as e:
            self.ratio_result.delete(1.0, tk.END)
            self.ratio_result.insert(tk.END, f"错误：{str(e)}")
    
    # ---------- 新增计算功能 ----------
    def create_percent_composition_calc(self, parent):
        tk.Label(parent, text="输入化学式:", font=self.default_font).pack(pady=5)
        self.percent_formula = tk.Entry(parent, width=40, font=("Courier", 11))
        self.percent_formula.pack(pady=5)
        tk.Button(parent, text="计算元素百分比", command=self.calc_percent_composition, bg="lightblue").pack(pady=5)
        self.percent_result = tk.Text(parent, height=12, font=self.default_font)
        self.percent_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_percent_composition(self):
        formula = self.percent_formula.get().strip()
        if not formula:
            return
        total_mass, percent = ChemicalFormulaParser.calculate_percent_composition(formula)
        if total_mass is None:
            self.percent_result.delete(1.0, tk.END)
            self.percent_result.insert(tk.END, "无效的化学式")
            return
        self.percent_result.delete(1.0, tk.END)
        self.percent_result.insert(tk.END, f"化学式: {formula}\n摩尔质量: {total_mass:.4f} g/mol\n\n各元素质量分数:\n")
        for element in sorted(percent.keys()):
            self.percent_result.insert(tk.END, f"{element}: {percent[element]:.2f}%\n")
    
    def create_empirical_formula_calc(self, parent):
        tk.Label(parent, text="输入元素质量或百分比（格式：元素 数值，每行一个）", font=self.default_font).pack(pady=5)
        self.empirical_text = tk.Text(parent, height=8, width=50)
        self.empirical_text.pack(pady=5)
        tk.Label(parent, text="例如:\nC 40\nH 6.7\nO 53.3", font=self.default_font, fg="gray").pack()
        tk.Button(parent, text="确定经验式", command=self.calc_empirical_formula, bg="lightblue").pack(pady=5)
        self.empirical_result = tk.Text(parent, height=5, font=self.default_font)
        self.empirical_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_empirical_formula(self):
        data = self.empirical_text.get(1.0, tk.END).strip()
        if not data:
            return
        lines = data.split('\n')
        masses = {}
        total_mass = 0
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) != 2:
                self.empirical_result.delete(1.0, tk.END)
                self.empirical_result.insert(tk.END, "格式错误，每行应为：元素 数值")
                return
            elem = parts[0].capitalize()
            try:
                val = float(parts[1])
            except:
                self.empirical_result.delete(1.0, tk.END)
                self.empirical_result.insert(tk.END, "数值无效")
                return
            masses[elem] = val
            total_mass += val
        # 转换为摩尔数
        moles = {}
        for elem, mass in masses.items():
            atomic = AtomicMass.get_mass(elem)
            if atomic == 0:
                self.empirical_result.delete(1.0, tk.END)
                self.empirical_result.insert(tk.END, f"未知元素 {elem}")
                return
            moles[elem] = mass / atomic
        min_mole = min(moles.values())
        ratios = {elem: mole / min_mole for elem, mole in moles.items()}
        # 乘以整数因子得到整数
        for factor in range(1, 20):
            int_ratios = {elem: round(ratios[elem] * factor) for elem in ratios}
            if all(abs(ratios[elem] * factor - int_ratios[elem]) < 0.01 for elem in ratios):
                formula = "".join(f"{elem}{int_ratios[elem] if int_ratios[elem]>1 else ''}" for elem in sorted(int_ratios.keys()))
                self.empirical_result.delete(1.0, tk.END)
                self.empirical_result.insert(tk.END, f"经验式: {formula}")
                return
        self.empirical_result.delete(1.0, tk.END)
        self.empirical_result.insert(tk.END, "无法确定整数比")
    
    def create_concentration_convert_calc(self, parent):
        tk.Label(parent, text="质量分数 (%) :").grid(row=0, column=0, padx=5, pady=5)
        self.wt_percent = tk.Entry(parent, width=15)
        self.wt_percent.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(parent, text="溶液密度 (g/mL):").grid(row=1, column=0, padx=5, pady=5)
        self.density = tk.Entry(parent, width=15)
        self.density.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(parent, text="溶质摩尔质量 (g/mol):").grid(row=2, column=0, padx=5, pady=5)
        self.molar_mass_convert = tk.Entry(parent, width=15)
        self.molar_mass_convert.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(parent, text="计算摩尔浓度", command=self.calc_concentration_convert, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        self.convert_result = tk.Text(parent, height=6, font=self.default_font)
        self.convert_result.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
    
    def calc_concentration_convert(self):
        try:
            w = float(self.wt_percent.get())
            d = float(self.density.get())
            M = float(self.molar_mass_convert.get())
            c = (w * d * 10) / M
            self.convert_result.delete(1.0, tk.END)
            self.convert_result.insert(tk.END, f"摩尔浓度 = (质量分数 × 密度 × 10) / 摩尔质量\n= ({w} × {d} × 10) / {M} = {c:.4f} mol/L")
        except:
            self.convert_result.delete(1.0, tk.END)
            self.convert_result.insert(tk.END, "输入错误")
    
    def create_yield_calc(self, parent):
        tk.Label(parent, text="实际产量 (g):").grid(row=0, column=0, padx=5, pady=5)
        self.actual_yield = tk.Entry(parent, width=15)
        self.actual_yield.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(parent, text="理论产量 (g):").grid(row=1, column=0, padx=5, pady=5)
        self.theoretical_yield = tk.Entry(parent, width=15)
        self.theoretical_yield.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(parent, text="计算产率", command=self.calc_yield, bg="lightblue").grid(row=2, column=0, columnspan=2, pady=10)
        self.yield_result = tk.Text(parent, height=5, font=self.default_font)
        self.yield_result.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
    
    def calc_yield(self):
        try:
            actual = float(self.actual_yield.get())
            theoretical = float(self.theoretical_yield.get())
            percent = (actual / theoretical) * 100
            self.yield_result.delete(1.0, tk.END)
            self.yield_result.insert(tk.END, f"产率 = (实际产量 / 理论产量) × 100% = ({actual}/{theoretical})×100% = {percent:.2f}%")
        except:
            self.yield_result.delete(1.0, tk.END)
            self.yield_result.insert(tk.END, "输入错误")
    
    # -------------------- 实用功能（全部完整实现）--------------------
    def show_balance(self):
        self.clear_content()
        self.update_status("配平模式 - *表示阳离子，^表示阴离子（如 H* 表示 H⁺，HCO3^ 表示 HCO₃⁻）")
        tk.Label(self.content_frame, text="化学方程式配平 v2.5", font=self.title_font, fg="blue").pack(pady=10)  # 版本号更新
        help_frame = tk.Frame(self.content_frame)
        help_frame.pack(pady=5)
        tk.Label(help_frame, text="支持格式:", font=("Microsoft YaHei", 9, "bold")).pack(side=tk.LEFT)
        tk.Label(help_frame, text=" H2+O2=H2O  |  Fe2O3+CO=Fe+CO2  |  HCO3^+H*=CO2+H2O", 
                font=self.default_font, fg="green").pack(side=tk.LEFT, padx=5)
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(pady=15)
        tk.Label(input_frame, text="请输入方程式:", font=self.default_font).pack(side=tk.LEFT)
        self.equation_entry = tk.Entry(input_frame, width=60, font=("Courier", 11))
        self.equation_entry.pack(side=tk.LEFT, padx=10)
        self.equation_entry.bind('<Return>', lambda e: self.do_balance())
        self.balance_btn = tk.Button(input_frame, text="配平", command=self.do_balance, bg="lightblue", width=10)
        self.balance_btn.pack(side=tk.LEFT, padx=5)
        result_frame = tk.LabelFrame(self.content_frame, text="配平结果", font=self.title_font)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.result_text = tk.Text(result_frame, height=12, font=("Courier", 12), wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.result_text.tag_configure("blue_coeff", foreground="blue", font=("Courier", 12, "bold"))
        self.result_text.tag_configure("green_valence", foreground="green", font=("Courier", 10))
        self.result_text.tag_configure("red_valence", foreground="red", font=("Courier", 10))
        self.result_text.tag_configure("normal", foreground="black", font=("Courier", 12))
        example_frame = tk.Frame(self.content_frame)
        example_frame.pack(pady=5)
        tk.Label(example_frame, text="示例:").pack(side=tk.LEFT)
        examples = [("H2+O2=H2O", "氢气燃烧"), ("Fe2O3+CO=Fe+CO2", "炼铁"), ("Cu+AgNO3=Cu(NO3)2+Ag", "置换反应"), ("HCO3^+H*=CO2+H2O", "碳酸氢根与酸反应")]
        for eq, desc in examples:
            btn = tk.Button(example_frame, text=desc, command=lambda e=eq: self.load_example(e), font=self.default_font, bg="#f0f0f0")
            btn.pack(side=tk.LEFT, padx=5)
    
    def load_example(self, equation):
        self.equation_entry.delete(0, tk.END)
        self.equation_entry.insert(0, equation)
        self.do_balance()
    
    def do_balance(self):
        equation = self.equation_entry.get().strip()
        if not equation:
            messagebox.showwarning("警告", "请输入化学方程式")
            return
        self.update_status("正在配平方程式...")
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
                self.update_status("显示错误")
    
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
        rows_data = [
            [("H",1), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("He",18)],
            [("Li",1), ("Be",2), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("B",13), ("C",14), ("N",15), ("O",16), ("F",17), ("Ne",18)],
            [("Na",1), ("Mg",2), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("Al",13), ("Si",14), ("P",15), ("S",16), ("Cl",17), ("Ar",18)],
            [("K",1), ("Ca",2), ("Sc",3), ("Ti",4), ("V",5), ("Cr",6), ("Mn",7), ("Fe",8), ("Co",9), ("Ni",10), ("Cu",11), ("Zn",12), ("Ga",13), ("Ge",14), ("As",15), ("Se",16), ("Br",17), ("Kr",18)],
            [("Rb",1), ("Sr",2), ("Y",3), ("Zr",4), ("Nb",5), ("Mo",6), ("Tc",7), ("Ru",8), ("Rh",9), ("Pd",10), ("Ag",11), ("Cd",12), ("In",13), ("Sn",14), ("Sb",15), ("Te",16), ("I",17), ("Xe",18)],
            [("Cs",1), ("Ba",2), ("La",3), ("Hf",4), ("Ta",5), ("W",6), ("Re",7), ("Os",8), ("Ir",9), ("Pt",10), ("Au",11), ("Hg",12), ("Tl",13), ("Pb",14), ("Bi",15), ("Po",16), ("At",17), ("Rn",18)],
            [("Fr",1), ("Ra",2), ("Ac",3), ("Rf",4), ("Db",5), ("Sg",6), ("Bh",7), ("Hs",8), ("Mt",9), ("Ds",10), ("Rg",11), ("Cn",12), ("Nh",13), ("Fl",14), ("Mc",15), ("Lv",16), ("Ts",17), ("Og",18)],
        ]
        for r, row in enumerate(rows_data):
            for c, (symbol, _) in enumerate(row):
                if symbol and symbol in ExtendedPeriodicTable.elements_data:
                    data = ExtendedPeriodicTable.elements_data[symbol]
                    color = "#ffcccc" if data["group"] == 1 else "#ccffcc" if data["group"] == 2 else "#ccccff" if 3 <= data["group"] <= 12 else "#ffffcc"
                    btn = tk.Button(scrollable, text=f"{symbol}\n{data['atomic']}", width=6, height=3, bg=color, command=lambda s=symbol: self.show_element_info(s))
                    btn.grid(row=r, column=c, padx=1, pady=1)
        # 镧系锕系单独添加
        lanthanides = ["Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"]
        actinides = ["Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr"]
        lanthanide_frame = tk.Frame(scrollable)
        lanthanide_frame.grid(row=len(rows_data), column=0, columnspan=18, pady=5, sticky=tk.W)
        tk.Label(lanthanide_frame, text="镧系:", font=self.default_font).pack(side=tk.LEFT, padx=5)
        for symbol in lanthanides:
            if symbol in ExtendedPeriodicTable.elements_data:
                btn = tk.Button(lanthanide_frame, text=symbol, width=4, height=1, bg="#ffffcc", command=lambda s=symbol: self.show_element_info(s))
                btn.pack(side=tk.LEFT, padx=1)
        actinide_frame = tk.Frame(scrollable)
        actinide_frame.grid(row=len(rows_data)+1, column=0, columnspan=18, pady=5, sticky=tk.W)
        tk.Label(actinide_frame, text="锕系:", font=self.default_font).pack(side=tk.LEFT, padx=5)
        for symbol in actinides:
            if symbol in ExtendedPeriodicTable.elements_data:
                btn = tk.Button(actinide_frame, text=symbol, width=4, height=1, bg="#ffcc99", command=lambda s=symbol: self.show_element_info(s))
                btn.pack(side=tk.LEFT, padx=1)
        legend_frame = tk.Frame(scrollable)
        legend_frame.grid(row=len(rows_data)+2, column=0, columnspan=18, pady=10)
        legends = [("碱金属", "#ffcccc"), ("碱土金属", "#ccffcc"), ("过渡金属", "#ccccff"), ("非金属", "#ffffcc"), ("卤素", "#ffcc99"), ("稀有气体", "#99ccff"), ("镧系", "#ffffcc"), ("锕系", "#ffcc99")]
        for text, color in legends:
            frame = tk.Frame(legend_frame)
            frame.pack(side=tk.LEFT, padx=8)
            tk.Label(frame, text="  ", bg=color, width=2).pack(side=tk.LEFT)
            tk.Label(frame, text=text, font=self.default_font).pack(side=tk.LEFT)
    
    def show_element_info(self, symbol):
        data = ExtendedPeriodicTable.elements_data.get(symbol)
        if data:
            electron_layers = ExtendedPeriodicTable.electron_config.get(symbol, "未知")
            en = ExtendedPeriodicTable.electronegativity.get(symbol, "未知")
            mass = AtomicMass.get_mass(symbol)
            info = f"元素: {symbol}\n名称: {data['name']}\n原子序数: {data['atomic']}\n原子量: {data['mass']}\n电负性: {en}\n族: {data['group']}\n周期: {data['period']}\n电子排布: {data['config']}\n电子层: {electron_layers}\n简介: {data['desc']}"
            messagebox.showinfo("元素信息", info)
        else:
            messagebox.showinfo("元素信息", f"未找到 {symbol} 的详细信息")
    
    # -------------------- 原有实用功能完整实现 --------------------
    def show_ph_calculator(self):
        self.clear_content()
        self.update_status("pH计算器")
        tk.Label(self.content_frame, text="pH值计算", font=self.title_font, fg="blue").pack(pady=10)
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
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
            if conc <= 0: raise ValueError
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
        try:
            if self.pressure.get() and self.volume.get() and self.moles.get():
                P, V, n = float(self.pressure.get()), float(self.volume.get()), float(self.moles.get())
                T = P * V / (n * R)
                self.gas_result.delete(1.0, tk.END)
                self.gas_result.insert(tk.END, f"温度 T = PV/(nR) = {P:.2f}×{V:.2f}/({n:.2f}×{R:.4f}) = {T:.2f} K")
            elif self.pressure.get() and self.volume.get() and self.temperature.get():
                P, V, T = float(self.pressure.get()), float(self.volume.get()), float(self.temperature.get())
                n = P * V / (R * T)
                self.gas_result.delete(1.0, tk.END)
                self.gas_result.insert(tk.END, f"物质的量 n = PV/(RT) = {P:.2f}×{V:.2f}/({R:.4f}×{T:.2f}) = {n:.4f} mol")
            elif self.pressure.get() and self.moles.get() and self.temperature.get():
                P, n, T = float(self.pressure.get()), float(self.moles.get()), float(self.temperature.get())
                V = n * R * T / P
                self.gas_result.delete(1.0, tk.END)
                self.gas_result.insert(tk.END, f"体积 V = nRT/P = {n:.2f}×{R:.4f}×{T:.2f}/{P:.2f} = {V:.2f} L")
            elif self.volume.get() and self.moles.get() and self.temperature.get():
                V, n, T = float(self.volume.get()), float(self.moles.get()), float(self.temperature.get())
                P = n * R * T / V
                self.gas_result.delete(1.0, tk.END)
                self.gas_result.insert(tk.END, f"压力 P = nRT/V = {n:.2f}×{R:.4f}×{T:.2f}/{V:.2f} = {P:.2f} atm")
            else:
                self.gas_result.delete(1.0, tk.END)
                self.gas_result.insert(tk.END, "请输入至少三个变量")
        except:
            self.gas_result.delete(1.0, tk.END)
            self.gas_result.insert(tk.END, "输入错误")
    
    def show_thermochemistry(self):
        self.clear_content()
        self.update_status("热化学计算")
        tk.Label(self.content_frame, text="热化学计算", font=self.title_font, fg="blue").pack(pady=10)
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
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
            m, c, dt = float(self.heat_mass.get()), float(self.heat_c.get()), float(self.heat_dt.get())
            q = m * c * dt
            self.heat_result.delete(1.0, tk.END)
            self.heat_result.insert(tk.END, f"Q = m·c·ΔT\nQ = {m} × {c} × {dt}\nQ = {q:.2f} J")
        except:
            self.heat_result.delete(1.0, tk.END)
            self.heat_result.insert(tk.END, "输入错误")
    
    def calc_combustion(self):
        try:
            dh, n = float(self.dh_comb.get()), float(self.n_comb.get())
            q = dh * n
            self.comb_result.delete(1.0, tk.END)
            self.comb_result.insert(tk.END, f"Q = ΔH × n\nQ = {dh} × {n}\nQ = {q:.2f} kJ")
        except:
            self.comb_result.delete(1.0, tk.END)
            self.comb_result.insert(tk.END, "输入错误")
    
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
    
    def show_organic(self):
        self.clear_content()
        self.update_status("有机化学工具")
        tk.Label(self.content_frame, text="有机化合物信息", font=self.title_font, fg="blue").pack(pady=10)
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        func_frame = tk.Frame(notebook)
        notebook.add(func_frame, text="官能团识别")
        tk.Label(func_frame, text="输入有机物名称:").pack(pady=5)
        self.org_name = tk.Entry(func_frame, width=40)
        self.org_name.pack(pady=5)
        tk.Button(func_frame, text="识别", command=self.identify_functional, bg="lightblue").pack(pady=5)
        self.func_result = tk.Text(func_frame, height=10)
        self.func_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
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
            "醇": ["醇", "乙醇", "甲醇", "丙醇"], "醛": ["醛", "乙醛", "甲醛"], "酮": ["酮", "丙酮"],
            "羧酸": ["酸", "乙酸", "甲酸"], "酯": ["酯", "乙酸乙酯"], "醚": ["醚", "乙醚"],
            "胺": ["胺", "甲胺"], "烯烃": ["烯", "乙烯", "丙烯"], "炔烃": ["炔", "乙炔"],
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
        isomers = {"C5H12": 3, "C6H14": 5, "C7H16": 9, "C8H18": 18, "C4H10": 2, "C3H8": 1, "C2H6": 1}
        if formula in isomers:
            self.isomer_result.insert(tk.END, f"分子式 {formula} 的同分异构体数目: {isomers[formula]} 种")
        else:
            self.isomer_result.insert(tk.END, "暂不支持该分子式\n常见烷烃异构体数:\nC₄H₁₀: 2, C₅H₁₂: 3, C₆H₁₄: 5, C₇H₁₆: 9")
    
    def show_solubility(self):
        self.clear_content()
        self.update_status("溶解度查询")
        tk.Label(self.content_frame, text="物质溶解度查询", font=self.title_font, fg="blue").pack(pady=10)
        common = [("NaCl", 36.0), ("KCl", 34.0), ("KNO3", 31.6), ("NH4Cl", 37.2), ("Ca(OH)2", 0.173), ("AgNO3", 216), ("CuSO4", 20.7), ("NaOH", 109)]
        tree = ttk.Treeview(self.content_frame, columns=("物质", "溶解度"), show="headings", height=10)
        tree.heading("物质", text="物质")
        tree.heading("溶解度", text="溶解度 (g/100g水, 20°C)")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for substance, solubility in common:
            tree.insert("", tk.END, values=(substance, solubility))
        tk.Label(self.content_frame, text="溶解度规则:\n• 碱金属盐大多可溶\n• 硝酸盐全部可溶\n• 氯化物、溴化物、碘化物除Ag⁺、Pb²⁺外可溶\n• 硫酸盐除Ba²⁺、Pb²⁺、Ca²⁺外可溶\n• 碳酸盐、磷酸盐大多不溶", font=self.default_font, justify=tk.LEFT).pack(pady=10)
    
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
            ca, va, cb = float(self.acid_conc_tit.get()), float(self.acid_vol_tit.get()), float(self.base_conc_tit.get())
            vb = ca * va / cb
            self.titration_result.delete(1.0, tk.END)
            self.titration_result.insert(tk.END, f"CaVa = CbVb\n{ca} × {va} = {cb} × Vb\nVb = {vb:.4f} L = {vb*1000:.2f} mL")
        except:
            self.titration_result.delete(1.0, tk.END)
            self.titration_result.insert(tk.END, "输入错误")
    
    def show_spectroscopy(self):
        self.clear_content()
        self.update_status("光谱分析")
        tk.Label(self.content_frame, text="光谱分析工具", font=self.title_font, fg="blue").pack(pady=10)
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        wave_frame = tk.Frame(notebook)
        notebook.add(wave_frame, text="波长-能量转换")
        tk.Label(wave_frame, text="波长 λ (nm):").pack(pady=5)
        self.wavelength = tk.Entry(wave_frame, width=20)
        self.wavelength.pack(pady=5)
        tk.Button(wave_frame, text="转换", command=self.convert_wavelength, bg="lightblue").pack(pady=5)
        self.wave_result = tk.Text(wave_frame, height=5)
        self.wave_result.pack(pady=10)
        color_frame = tk.Frame(notebook)
        notebook.add(color_frame, text="颜色与波长")
        colors = [("紫", "400-450"), ("蓝", "450-500"), ("青", "500-550"), ("绿", "550-580"), ("黄", "580-600"), ("橙", "600-650"), ("红", "650-750")]
        for color, wavelength in colors:
            tk.Label(color_frame, text=f"{color}: {wavelength} nm", font=self.default_font).pack(pady=2)
    
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
            ea, T, A = float(self.ea_entry.get()), float(self.temp_kin.get()), float(self.a_factor.get())
            R = 8.314
            k = A * np.exp(-ea / (R * T))
            self.kinetics_result.delete(1.0, tk.END)
            self.kinetics_result.insert(tk.END, f"k = A·exp(-Ea/RT)\nk = {A:.2e} × exp(-{ea:.2e}/{R:.3f}×{T:.2f})\nk = {k:.2e} s⁻¹")
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
    
    # -------------------- 新增6项实用功能 --------------------
    def show_electrochem(self):
        self.clear_content()
        tk.Label(self.content_frame, text="能斯特方程 E = E° - (RT/nF) lnQ", font=self.title_font, fg="blue").pack(pady=10)
        frame = tk.Frame(self.content_frame)
        frame.pack(pady=10)
        tk.Label(frame, text="标准电势 E° (V):").grid(row=0, column=0, padx=5, pady=5)
        self.e0_entry = tk.Entry(frame, width=15)
        self.e0_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="温度 T (K):").grid(row=1, column=0, padx=5, pady=5)
        self.temp_nernst = tk.Entry(frame, width=15)
        self.temp_nernst.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame, text="电子转移数 n:").grid(row=2, column=0, padx=5, pady=5)
        self.n_electron = tk.Entry(frame, width=15)
        self.n_electron.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(frame, text="反应商 Q:").grid(row=3, column=0, padx=5, pady=5)
        self.q_value = tk.Entry(frame, width=15)
        self.q_value.grid(row=3, column=1, padx=5, pady=5)
        tk.Button(frame, text="计算电极电势", command=self.calc_nernst, bg="lightblue").grid(row=4, column=0, columnspan=2, pady=10)
        self.nernst_result = tk.Text(self.content_frame, height=8)
        self.nernst_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_nernst(self):
        try:
            e0 = float(self.e0_entry.get())
            T = float(self.temp_nernst.get())
            n = float(self.n_electron.get())
            Q = float(self.q_value.get())
            R = 8.314; F = 96485
            E = e0 - (R * T / (n * F)) * np.log(Q)
            self.nernst_result.delete(1.0, tk.END)
            self.nernst_result.insert(tk.END, f"E = E° - (RT/nF) lnQ\n= {e0} - ({R}×{T}/{n}/{F}) ln({Q})\n= {E:.4f} V")
        except:
            self.nernst_result.delete(1.0, tk.END)
            self.nernst_result.insert(tk.END, "输入错误")
    
    def show_equilibrium(self):
        self.clear_content()
        tk.Label(self.content_frame, text="化学平衡 ΔG° = -RT lnK", font=self.title_font, fg="blue").pack(pady=10)
        frame = tk.Frame(self.content_frame)
        frame.pack(pady=10)
        tk.Label(frame, text="温度 T (K):").grid(row=0, column=0, padx=5, pady=5)
        self.temp_eq = tk.Entry(frame, width=15)
        self.temp_eq.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="平衡常数 K:").grid(row=1, column=0, padx=5, pady=5)
        self.k_eq = tk.Entry(frame, width=15)
        self.k_eq.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(frame, text="计算 ΔG°", command=self.calc_deltaG, bg="lightblue").grid(row=2, column=0, columnspan=2, pady=10)
        self.eq_result = tk.Text(self.content_frame, height=8)
        self.eq_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_deltaG(self):
        try:
            T = float(self.temp_eq.get())
            K = float(self.k_eq.get())
            R = 8.314
            dG = -R * T * np.log(K)
            self.eq_result.delete(1.0, tk.END)
            self.eq_result.insert(tk.END, f"ΔG° = -RT lnK\n= -{R} × {T} × ln({K})\n= {dG:.2f} J/mol = {dG/1000:.2f} kJ/mol")
        except:
            self.eq_result.delete(1.0, tk.END)
            self.eq_result.insert(tk.END, "输入错误")
    
    def show_thermodynamics(self):
        self.clear_content()
        tk.Label(self.content_frame, text="吉布斯自由能 ΔG = ΔH - TΔS", font=self.title_font, fg="blue").pack(pady=10)
        frame = tk.Frame(self.content_frame)
        frame.pack(pady=10)
        tk.Label(frame, text="ΔH (kJ/mol):").grid(row=0, column=0, padx=5, pady=5)
        self.dh = tk.Entry(frame, width=15)
        self.dh.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="ΔS (J/(mol·K)):").grid(row=1, column=0, padx=5, pady=5)
        self.ds = tk.Entry(frame, width=15)
        self.ds.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame, text="温度 T (K):").grid(row=2, column=0, padx=5, pady=5)
        self.temp_thermo = tk.Entry(frame, width=15)
        self.temp_thermo.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(frame, text="计算 ΔG", command=self.calc_gibbs, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        self.thermo_result = tk.Text(self.content_frame, height=8)
        self.thermo_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_gibbs(self):
        try:
            H = float(self.dh.get()) * 1000
            S = float(self.ds.get())
            T = float(self.temp_thermo.get())
            G = H - T * S
            self.thermo_result.delete(1.0, tk.END)
            self.thermo_result.insert(tk.END, f"ΔG = ΔH - TΔS\n= {H/1000:.2f} kJ - {T} × {S:.2f} J/K\n= {G/1000:.2f} kJ/mol")
        except:
            self.thermo_result.delete(1.0, tk.END)
            self.thermo_result.insert(tk.END, "输入错误")
    
    def show_partial_pressure(self):
        self.clear_content()
        tk.Label(self.content_frame, text="道尔顿分压定律 P_total = ΣP_i", font=self.title_font, fg="blue").pack(pady=10)
        frame = tk.Frame(self.content_frame)
        frame.pack(pady=10)
        tk.Label(frame, text="总压 (atm):").grid(row=0, column=0, padx=5, pady=5)
        self.total_p = tk.Entry(frame, width=15)
        self.total_p.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="组分1摩尔分数:").grid(row=1, column=0, padx=5, pady=5)
        self.mole_frac1 = tk.Entry(frame, width=15)
        self.mole_frac1.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame, text="组分2摩尔分数:").grid(row=2, column=0, padx=5, pady=5)
        self.mole_frac2 = tk.Entry(frame, width=15)
        self.mole_frac2.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(frame, text="计算分压", command=self.calc_partial_pressure, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        self.partial_result = tk.Text(self.content_frame, height=8)
        self.partial_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_partial_pressure(self):
        try:
            P = float(self.total_p.get())
            x1 = float(self.mole_frac1.get()) if self.mole_frac1.get() else 0
            x2 = float(self.mole_frac2.get()) if self.mole_frac2.get() else 0
            p1, p2 = P * x1, P * x2
            self.partial_result.delete(1.0, tk.END)
            self.partial_result.insert(tk.END, f"组分1分压: {p1:.4f} atm\n组分2分压: {p2:.4f} atm\n总和: {p1+p2:.4f} atm")
        except:
            self.partial_result.delete(1.0, tk.END)
            self.partial_result.insert(tk.END, "输入错误")
    
    def show_nuclear(self):
        self.clear_content()
        tk.Label(self.content_frame, text="放射性衰变 N = N₀·e^{-λt}", font=self.title_font, fg="blue").pack(pady=10)
        frame = tk.Frame(self.content_frame)
        frame.pack(pady=10)
        tk.Label(frame, text="半衰期 t₁/₂ (s):").grid(row=0, column=0, padx=5, pady=5)
        self.half_life = tk.Entry(frame, width=15)
        self.half_life.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="初始原子数 N₀:").grid(row=1, column=0, padx=5, pady=5)
        self.n0 = tk.Entry(frame, width=15)
        self.n0.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame, text="经过时间 t (s):").grid(row=2, column=0, padx=5, pady=5)
        self.time_nuclear = tk.Entry(frame, width=15)
        self.time_nuclear.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(frame, text="计算剩余原子数", command=self.calc_nuclear, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        self.nuclear_result = tk.Text(self.content_frame, height=8)
        self.nuclear_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_nuclear(self):
        try:
            t12 = float(self.half_life.get())
            N0 = float(self.n0.get())
            t = float(self.time_nuclear.get())
            lam = np.log(2) / t12
            N = N0 * np.exp(-lam * t)
            self.nuclear_result.delete(1.0, tk.END)
            self.nuclear_result.insert(tk.END, f"衰变常数 λ = ln2 / t₁/₂ = {lam:.4e} s⁻¹\n剩余原子数 N = N₀·e^(-λt) = {N0} * exp(-{lam:.4e}×{t}) = {N:.2f}")
        except:
            self.nuclear_result.delete(1.0, tk.END)
            self.nuclear_result.insert(tk.END, "输入错误")
    
    def show_solution_prep(self):
        self.clear_content()
        tk.Label(self.content_frame, text="溶液配制计算", font=self.title_font, fg="blue").pack(pady=10)
        frame = tk.Frame(self.content_frame)
        frame.pack(pady=10)
        tk.Label(frame, text="目标浓度 C (mol/L):").grid(row=0, column=0, padx=5, pady=5)
        self.target_c = tk.Entry(frame, width=15)
        self.target_c.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="目标体积 V (L):").grid(row=1, column=0, padx=5, pady=5)
        self.target_v = tk.Entry(frame, width=15)
        self.target_v.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame, text="溶质摩尔质量 M (g/mol):").grid(row=2, column=0, padx=5, pady=5)
        self.solute_m = tk.Entry(frame, width=15)
        self.solute_m.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(frame, text="计算所需溶质质量", command=self.calc_solution_prep, bg="lightblue").grid(row=3, column=0, columnspan=2, pady=10)
        self.prep_result = tk.Text(self.content_frame, height=6)
        self.prep_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def calc_solution_prep(self):
        try:
            C = float(self.target_c.get())
            V = float(self.target_v.get())
            M = float(self.solute_m.get())
            mass = C * V * M
            self.prep_result.delete(1.0, tk.END)
            self.prep_result.insert(tk.END, f"所需溶质质量 = C × V × M = {C} × {V} × {M} = {mass:.4f} g")
        except:
            self.prep_result.delete(1.0, tk.END)
            self.prep_result.insert(tk.END, "输入错误")
    
    # -------------------- 辅助功能 --------------------
    def export_result(self):
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".txt")
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("化学工具箱 v2.5 计算结果\n")   # 版本号更新
                    f.write(f"导出时间: {datetime.datetime.now()}\n")
                messagebox.showinfo("成功", f"已保存到 {filename}")
        except:
            messagebox.showerror("错误", "保存失败")
    
    def show_unit_converter(self):
        messagebox.showinfo("单位换算", "常用换算:\n1 mol/L = 1000 mmol/L\n1 atm = 101.325 kPa\n1 cal = 4.184 J\n0°C = 273.15 K")
    
    def show_lab_notebook(self):
        self.clear_content()
        tk.Label(self.content_frame, text="实验记录本", font=self.title_font).pack()
        text_area = scrolledtext.ScrolledText(self.content_frame, height=20)
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, f"实验日期: {datetime.datetime.now()}\n\n")
        def save():
            try:
                with filedialog.asksaveasfile(mode='w', defaultextension=".txt") as f:
                    if f:
                        f.write(text_area.get(1.0, tk.END))
                        messagebox.showinfo("成功", "已保存")
            except:
                pass
        tk.Button(self.content_frame, text="保存", command=save).pack()
    
    # ==================== 帮助（HTML） ====================
    def show_help(self):
        """打开 HTML 帮助页面（每次重新生成）"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        help_dir = os.path.join(base_dir, "help")
        os.makedirs(help_dir, exist_ok=True)
        help_file = os.path.join(help_dir, "help.html")

        if os.path.exists(help_file):
            try:
                os.remove(help_file)
            except Exception as e:
                messagebox.showerror("错误", f"无法删除旧的帮助文件：{e}")
                return

        html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>化学工具箱 v2.5 - 帮助与实验演示</title>
    <style>
        /* ===== 基础与导航样式 ===== */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Microsoft YaHei', 'Segoe UI', system-ui, sans-serif; 
            margin: 0; 
            background: #f5f5f5; 
            min-height: 100vh;
        }
        
        .top-nav {
            background: linear-gradient(135deg, #1a5fb4, #0d3b8c);
            padding: 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        .nav-inner {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
        }
        .nav-title {
            color: #fff;
            font-size: 18px;
            font-weight: 600;
            padding: 14px 0;
        }
        .nav-tabs {
            display: flex;
            gap: 4px;
        }
        .nav-tab {
            padding: 14px 24px;
            color: rgba(255,255,255,0.7);
            cursor: pointer;
            border: none;
            background: transparent;
            font-size: 15px;
            font-weight: 500;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
            font-family: inherit;
        }
        .nav-tab:hover {
            color: #fff;
            background: rgba(255,255,255,0.1);
        }
        .nav-tab.active {
            color: #fff;
            border-bottom-color: #64d2ff;
            background: rgba(255,255,255,0.15);
        }

        /* ===== 页面面板 ===== */
        .page-panel { display: none; }
        .page-panel.active { display: block; }

        /* ===== 帮助页面样式 ===== */
        .help-body {
            background: #f5f5f5;
            padding: 40px 20px;
        }
        .help-container { 
            max-width: 900px; 
            margin: auto; 
            background: white; 
            padding: 30px; 
            border-radius: 8px; 
            box-shadow: 0 0 10px rgba(0,0,0,0.1); 
        }
        .help-container h1 { 
            color: #2c3e50; 
            border-bottom: 2px solid #3498db; 
            padding-bottom: 10px; 
            font-size: 28px;
            margin-bottom: 16px;
        }
        .help-container h2 { 
            color: #2980b9; 
            margin-top: 25px; 
            font-size: 20px;
            margin-bottom: 10px;
        }
        .help-container ul { 
            line-height: 1.8; 
            padding-left: 24px;
            margin-bottom: 12px;
        }
        .help-container li {
            margin-bottom: 6px;
        }
        .help-container p {
            line-height: 1.8;
            margin-bottom: 12px;
            color: #333;
        }
        .help-container code {
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #c0392b;
        }
        .help-footer { 
            margin-top: 30px; 
            color: #7f8c8d; 
            font-size: 0.9em; 
            text-align: center; 
        }
        .warning-box {
            background: #fff3cd;
            border-left: 4px solid #f0ad4e;
            padding: 12px 16px;
            margin: 12px 0;
            border-radius: 0 8px 8px 0;
            color: #856404;
        }
        .warning-box strong {
            color: #d9534f;
        }

        /* ===== 实验演示页面样式 (继承2.5.html) ===== */
        .experiment-body {
            background: #0a0e27; 
            color: #e0e6ed; 
            min-height: 100vh;
            padding: 16px;
        }
        #app { max-width: 1200px; margin: 0 auto; }
        .exp-header { text-align: center; margin-bottom: 24px; }
        .exp-header h1 { font-size: 28px; color: #64d2ff; margin: 0 0 8px 0; text-shadow: 0 0 20px rgba(100,210,255,0.3); }
        .exp-header p { color: #8b9dc3; margin: 0; font-size: 14px; }
        .exp-tabs { display: flex; gap: 8px; margin-bottom: 20px; justify-content: center; }
        .exp-tab { 
            padding: 10px 24px; 
            border-radius: 8px; 
            border: 1px solid #1e3a5f; 
            background: #0f1a3a; 
            color: #8b9dc3; 
            cursor: pointer; 
            transition: all 0.3s; 
            font-weight: 500; 
            font-family: inherit;
            font-size: 14px;
        }
        .exp-tab.active { 
            background: linear-gradient(135deg, #1a5fb4, #0d3b8c); 
            color: #fff; 
            border-color: #3584e4; 
            box-shadow: 0 0 15px rgba(53,132,228,0.3); 
        }
        .exp-tab:hover:not(.active) { background: #1a2744; }
        .exp-panel { display: none; }
        .exp-panel.active { display: block; }
        .exp-card { 
            background: #111936; 
            border: 1px solid #1e3a5f; 
            border-radius: 12px; 
            padding: 20px; 
            margin-bottom: 16px; 
        }
        .exp-card-title { 
            font-size: 18px; 
            color: #64d2ff; 
            margin: 0 0 12px 0; 
            display: flex; 
            align-items: center; 
            gap: 8px; 
        }
        .exp-controls { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 16px; 
            margin-bottom: 16px; 
        }
        .exp-control-group { 
            display: flex; 
            flex-direction: column; 
            gap: 6px; 
        }
        .exp-control-group label { 
            font-size: 13px; 
            color: #8b9dc3; 
            font-weight: 500; 
        }
        .exp-control-group input[type="range"] { 
            width: 100%; 
            accent-color: #3584e4; 
        }
        .exp-control-group select { 
            padding: 8px; 
            border-radius: 6px; 
            background: #0a0e27; 
            color: #e0e6ed; 
            border: 1px solid #1e3a5f; 
            font-family: inherit;
        }
        .exp-control-group .value { 
            font-size: 14px; 
            color: #64d2ff; 
            font-weight: 600; 
        }
        .exp-btn { 
            padding: 10px 20px; 
            border-radius: 8px; 
            border: none; 
            cursor: pointer; 
            font-weight: 600; 
            transition: all 0.2s; 
            font-size: 14px; 
            font-family: inherit;
        }
        .exp-btn-primary { 
            background: linear-gradient(135deg, #3584e4, #1a5fb4); 
            color: #fff; 
        }
        .exp-btn-primary:hover { 
            transform: translateY(-1px); 
            box-shadow: 0 4px 15px rgba(53,132,228,0.4); 
        }
        .exp-btn-danger { 
            background: linear-gradient(135deg, #e74c3c, #c0392b); 
            color: #fff; 
        }
        .exp-btn-success { 
            background: linear-gradient(135deg, #27ae60, #1e8449); 
            color: #fff; 
        }
        .exp-btn-group { 
            display: flex; 
            gap: 10px; 
            flex-wrap: wrap; 
        }
        .exp-canvas { 
            border-radius: 8px; 
            background: #050814; 
            border: 1px solid #1e3a5f; 
            width: 100%; 
        }
        .exp-stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); 
            gap: 12px; 
            margin-top: 12px; 
        }
        .exp-stat-box { 
            background: #0a0e27; 
            border: 1px solid #1e3a5f; 
            border-radius: 8px; 
            padding: 12px; 
            text-align: center; 
        }
        .exp-stat-box .number { 
            font-size: 24px; 
            font-weight: 700; 
            color: #64d2ff; 
        }
        .exp-stat-box .label { 
            font-size: 12px; 
            color: #8b9dc3; 
            margin-top: 4px; 
        }
        .exp-legend { 
            display: flex; 
            gap: 20px; 
            flex-wrap: wrap; 
            margin-top: 12px; 
            font-size: 13px; 
        }
        .exp-legend-item { 
            display: flex; 
            align-items: center; 
            gap: 6px; 
        }
        .exp-legend-dot { 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
        }
        .exp-info-box { 
            background: #0d1b2a; 
            border-left: 3px solid #3584e4; 
            padding: 12px 16px; 
            border-radius: 0 8px 8px 0; 
            margin: 12px 0; 
            font-size: 14px; 
            line-height: 1.6; 
            color: #e0e6ed;
        }
        .exp-atom-container { 
            position: relative; 
            width: 100%; 
            height: 500px; 
            background: #050814; 
            border-radius: 8px; 
            border: 1px solid #1e3a5f; 
            overflow: hidden; 
        }
        .exp-nucleus { 
            position: absolute; 
            width: 20px; 
            height: 20px; 
            background: radial-gradient(circle, #ff6b6b, #c0392b); 
            border-radius: 50%; 
            top: 50%; 
            left: 50%; 
            transform: translate(-50%, -50%); 
            box-shadow: 0 0 30px rgba(255,107,107,0.6); 
            z-index: 10; 
        }
        .exp-electron-orbit { 
            position: absolute; 
            border: 1px solid rgba(100,210,255,0.2); 
            border-radius: 50%; 
            top: 50%; 
            left: 50%; 
            transform: translate(-50%, -50%); 
        }
        .exp-electron { 
            position: absolute; 
            width: 8px; 
            height: 8px; 
            background: radial-gradient(circle, #64d2ff, #3584e4); 
            border-radius: 50%; 
            box-shadow: 0 0 10px rgba(100,210,255,0.8); 
        }
        .range-value { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
        }

        @media (max-width: 768px) {
            .nav-inner { flex-direction: column; }
            .nav-tab { padding: 10px 16px; font-size: 14px; }
            .help-container { padding: 20px; }
            .exp-controls { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

    <!-- 顶部导航 -->
    <nav class="top-nav">
        <div class="nav-inner">
            <div class="nav-title">化学工具箱 v2.5</div>
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="switchPage('help')">帮助文档</button>
                <button class="nav-tab" onclick="switchPage('experiment')">实验演示</button>
            </div>
        </div>
    </nav>

    <!-- 帮助文档面板 -->
    <div id="help-page" class="page-panel active">
        <div class="help-body">
            <div class="help-container">
                <h1>化学工具箱 v2.5 帮助文档</h1>
                <p>欢迎使用化学工具箱！本软件集成了化学方程式配平、元素周期表、多种计算工具及实用功能，并支持插件扩展。</p>
                
                <h2>主要功能</h2>
                <ul>
                    <li><strong>配平：</strong>支持化学方程式及离子方程式（用 <code>*</code> 表示正电荷，<code>^</code> 表示负电荷）。</li>
                    <li><strong>元素周期表：</strong>点击元素查看详细信息（原子量、电负性、电子排布等）。</li>
                    <li><strong>计算工具：</strong>摩尔质量、浓度、稀释、比例、元素百分比、经验式、浓度换算、产率。</li>
                    <li><strong>实用功能：</strong>pH计算、气体定律、热化学、氧化还原、有机化学、溶解度、缓冲溶液、滴定、光谱、动力学、电化学、平衡常数、热力学、分压、核化学、溶液配制。</li>
                </ul>
                
                <h2>插件系统</h2>
                <p>将自定义插件（.py文件)放入 <code>plugins</code> 文件夹，程序启动时自动加载，并在"实用功能"菜单下显示。</p>
                
                <h2>使用提示及注意事项</h2>
                <ul>
                    <li>化学式区分大小写（如 Co 和 CO 不同）。</li>
                    <li>配平时，若无法配平请检查输入的化学方程式是否准确。</li>
                    <li>计算结果均为近似值，适用于教学和一般计算。</li>
                    <li>请勿导入任何不信任的、来源不明的插件。</li>
                </ul>

                <div class="warning-box">
                    <strong>免责声明：</strong> 本软件中数据由AI收集，不保证准确，请仔细判断。本软件数据由AI添加，部分功能由AI开发，所以本软件不保证任何数据以及功能计算出的结果准确，也不保证结论正确，由本软件造成的任何问题，本软件开发者不承担任何责任。"实验演示模块"是测试功能，不稳定，请谨慎使用<br><br>
                    <strong>使用协议：</strong> 如果开始使用本软件，则认为已经同意上述说明。若不同意，则应立即停止使用本软件。
                </div>
                
                <h2>版本信息</h2>
                <p>化学工具箱 v2.5，新增多项功能、插件支持及<strong>实验演示</strong>模块。</p>
                <div class="help-footer">© 化学爱好者 | 使用愉快！</div>
            </div>
        </div>
    </div>

    <!-- 实验演示面板 -->
    <div id="experiment-page" class="page-panel">
        <div class="experiment-body">
            <div id="app">
                <div class="exp-header">
                    <h1>卢瑟福α粒子散射实验模拟器</h1>
                    <p>运用计算机编程模拟原子结构 —— 核式模型与散射实验</p>
                </div>

                <div class="exp-tabs">
                    <div class="exp-tab active" onclick="switchExpTab('scattering')">α粒子散射实验</div>
                    <div class="exp-tab" onclick="switchExpTab('atomic')">核式原子结构模型</div>
                </div>

                <!-- 散射实验面板 -->
                <div id="scattering" class="exp-panel active">
                    <div class="exp-card">
                        <div class="exp-card-title">实验控制面板</div>
                        <div class="exp-controls">
                            <div class="exp-control-group">
                                <label>α粒子能量 (keV)</label>
                                <input type="range" id="energy" min="100" max="10000" value="5000" oninput="updateValue('energyVal', this.value)">
                                <div class="range-value"><span class="value" id="energyVal">5000</span> keV</div>
                            </div>
                            <div class="exp-control-group">
                                <label>入射角度 (°)</label>
                                <input type="range" id="angle" min="-30" max="30" value="0" oninput="updateValue('angleVal', this.value)">
                                <div class="range-value"><span class="value" id="angleVal">0</span>°</div>
                            </div>
                            <div class="exp-control-group">
                                <label>碰撞参数 b (fm)</label>
                                <input type="range" id="impact" min="1" max="50" value="10" oninput="updateValue('impactVal', this.value)">
                                <div class="range-value"><span class="value" id="impactVal">10</span> fm</div>
                            </div>
                            <div class="exp-control-group">
                                <label>原子核电荷数 Z</label>
                                <input type="range" id="charge" min="1" max="92" value="79" oninput="updateValue('chargeVal', this.value)">
                                <div class="range-value"><span class="value" id="chargeVal">79</span> (Au)</div>
                            </div>
                        </div>
                        <div class="exp-btn-group">
                            <button class="exp-btn exp-btn-primary" onclick="startScattering()">发射α粒子</button>
                            <button class="exp-btn exp-btn-success" onclick="startAuto()">连续发射</button>
                            <button class="exp-btn exp-btn-danger" onclick="stopAuto()">停止</button>
                            <button class="exp-btn exp-btn-primary" onclick="clearCanvas()">清空轨迹</button>
                        </div>
                    </div>

                    <div class="exp-card">
                        <div class="exp-card-title">实验视窗</div>
                        <canvas id="scatterCanvas" width="1100" height="500" class="exp-canvas"></canvas>
                        <div class="exp-legend">
                            <div class="exp-legend-item"><div class="exp-legend-dot" style="background:#f1c40f"></div> α粒子</div>
                            <div class="exp-legend-item"><div class="exp-legend-dot" style="background:#e74c3c"></div> 金原子核</div>
                            <div class="exp-legend-item"><div class="exp-legend-dot" style="background:#64d2ff"></div> 电子</div>
                            <div class="exp-legend-item"><div class="exp-legend-dot" style="background:rgba(100,210,255,0.1)"></div> 原子轨道</div>
                        </div>
                        <div class="exp-stats">
                            <div class="exp-stat-box"><div class="number" id="scatterAngle">--</div><div class="label">散射角度</div></div>
                            <div class="exp-stat-box"><div class="number" id="closest">--</div><div class="label">最近距离 (fm)</div></div>
                            <div class="exp-stat-box"><div class="number" id="particleCount">0</div><div class="label">发射粒子数</div></div>
                            <div class="exp-stat-box"><div class="number" id="backCount">0</div><div class="label">大角度偏转</div></div>
                        </div>
                    </div>

                    <div class="exp-card">
                        <div class="exp-card-title">实验原理</div>
                        <div class="exp-info-box">
                            <strong>卢瑟福散射公式：</strong> 当α粒子（He²⁺）接近重原子核时，受到库仑斥力作用发生偏转。散射角θ与碰撞参数b的关系为：<br>
                            cot(θ/2) = 2E·b / (k·Z₁Z₂e²) <br>
                            其中 E 为粒子动能，Z 为原子核电荷数。当 b→0 时，θ→180°，发生背向散射。
                        </div>
                    </div>
                </div>

                <!-- 原子结构面板 -->
                <div id="atomic" class="exp-panel">
                    <div class="exp-card">
                        <div class="exp-card-title">原子模型控制</div>
                        <div class="exp-controls">
                            <div class="exp-control-group">
                                <label>元素选择</label>
                                <select id="element" onchange="changeElement()">
                                    <option value="1">氢 (H) - Z=1</option>
                                    <option value="2">氦 (He) - Z=2</option>
                                    <option value="6">碳 (C) - Z=6</option>
                                    <option value="8">氧 (O) - Z=8</option>
                                    <option value="11">钠 (Na) - Z=11</option>
                                    <option value="26">铁 (Fe) - Z=26</option>
                                    <option value="29">铜 (Cu) - Z=29</option>
                                    <option value="47">银 (Ag) - Z=47</option>
                                    <option value="79" selected>金 (Au) - Z=79</option>
                                    <option value="92">铀 (U) - Z=92</option>
                                </select>
                            </div>
                            <div class="exp-control-group">
                                <label>电子层数</label>
                                <input type="range" id="shells" min="1" max="7" value="6" oninput="updateValue('shellsVal', this.value); updateAtom()">
                                <div class="range-value"><span class="value" id="shellsVal">6</span> 层</div>
                            </div>
                            <div class="exp-control-group">
                                <label>旋转速度</label>
                                <input type="range" id="speed" min="0" max="100" value="50" oninput="updateValue('speedVal', this.value)">
                                <div class="range-value"><span class="value" id="speedVal">50</span>%</div>
                            </div>
                            <div class="exp-control-group">
                                <label>显示模式</label>
                                <select id="viewMode" onchange="updateAtom()">
                                    <option value="solar">太阳系模型</option>
                                    <option value="cloud">电子云模型</option>
                                    <option value="both">混合显示</option>
                                </select>
                            </div>
                        </div>
                        <div class="exp-btn-group">
                            <button class="exp-btn exp-btn-primary" onclick="toggleAnimation()" id="animBtn">暂停</button>
                            <button class="exp-btn exp-btn-success" onclick="addElectron()">添加电子</button>
                            <button class="exp-btn exp-btn-danger" onclick="removeElectron()">移除电子</button>
                            <button class="exp-btn exp-btn-primary" onclick="resetAtom()">重置</button>
                        </div>
                    </div>

                    <div class="exp-card">
                        <div class="exp-card-title">核式原子模型</div>
                        <div class="exp-atom-container" id="atomContainer">
                            <div class="exp-nucleus" id="nucleus"></div>
                        </div>
                        <div class="exp-stats">
                            <div class="exp-stat-box"><div class="number" id="protonNum">79</div><div class="label">质子数</div></div>
                            <div class="exp-stat-box"><div class="number" id="neutronNum">118</div><div class="label">中子数</div></div>
                            <div class="exp-stat-box"><div class="number" id="electronNum">79</div><div class="label">电子数</div></div>
                            <div class="exp-stat-box"><div class="number" id="massNum">197</div><div class="label">质量数</div></div>
                        </div>
                    </div>

                    <div class="exp-card">
                        <div class="exp-card-title">核式结构理论</div>
                        <div class="exp-info-box">
                            <strong>卢瑟福核式模型要点：</strong><br>
                            1. 原子中心有一个带正电的原子核，体积极小但集中了几乎全部质量<br>
                            2. 电子在核外空间绕核运动，如同行星绕太阳<br>
                            3. 原子核由质子和中子组成，质子带正电，中子不带电<br>
                            4. 原子序数 = 核电荷数 = 质子数 = 核外电子数（电中性时）
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ========== 页面切换 ==========
        function switchPage(page) {
            document.querySelectorAll('.page-panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            
            if (page === 'help') {
                document.getElementById('help-page').classList.add('active');
                document.querySelectorAll('.nav-tab')[0].classList.add('active');
            } else {
                document.getElementById('experiment-page').classList.add('active');
                document.querySelectorAll('.nav-tab')[1].classList.add('active');
                // 切换到实验页面时初始化原子动画
                setTimeout(() => {
                    if (electrons.length === 0) updateAtom();
                    if (!animationRunning) {
                        animationRunning = true;
                        document.getElementById('animBtn').textContent = '暂停';
                        animateElectrons();
                    }
                }, 100);
            }
        }

        // ========== 实验页面标签切换 ==========
        function switchExpTab(tab) {
            document.querySelectorAll('.exp-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.exp-panel').forEach(p => p.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab).classList.add('active');
            if (tab === 'atomic') {
                setTimeout(() => updateAtom(), 100);
            }
        }

        function updateValue(id, val) {
            document.getElementById(id).textContent = val;
        }

        // ========== 散射实验 ==========
        const canvas = document.getElementById('scatterCanvas');
        const ctx = canvas.getContext('2d');
        const SCALE = 2;
        const NUCLEUS_X = 550;
        const NUCLEUS_Y = 250;

        function drawNucleus() {
            const z = parseInt(document.getElementById('charge').value);
            const radius = 3 + Math.sqrt(z) * 0.5;
            
            ctx.beginPath();
            ctx.arc(NUCLEUS_X, NUCLEUS_Y, radius, 0, Math.PI * 2);
            ctx.fillStyle = '#e74c3c';
            ctx.shadowBlur = 20;
            ctx.shadowColor = 'rgba(231,76,60,0.6)';
            ctx.fill();
            ctx.shadowBlur = 0;
            
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 12px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('Au', NUCLEUS_X, NUCLEUS_Y + 4);
            
            ctx.strokeStyle = 'rgba(100,210,255,0.08)';
            ctx.lineWidth = 1;
            for (let r = 40; r < 200; r += 30) {
                ctx.beginPath();
                ctx.arc(NUCLEUS_X, NUCLEUS_Y, r, 0, Math.PI * 2);
                ctx.stroke();
            }
        }

        function drawGrid() {
            ctx.strokeStyle = 'rgba(100,210,255,0.05)';
            ctx.lineWidth = 0.5;
            for (let x = 0; x < canvas.width; x += 50) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
            }
            for (let y = 0; y < canvas.height; y += 50) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
            }
        }

        function simulateTrajectory() {
            const energy = parseFloat(document.getElementById('energy').value);
            const angleDeg = parseFloat(document.getElementById('angle').value);
            const impact = parseFloat(document.getElementById('impact').value);
            const Z = parseInt(document.getElementById('charge').value);
            
            const angleRad = angleDeg * Math.PI / 180;
            const Z1 = 2, Z2 = Z;
            const E = energy / 1000;
            
            let x = 50;
            let y = NUCLEUS_Y + impact * SCALE + Math.tan(angleRad) * (NUCLEUS_X - x);
            const vx0 = Math.cos(angleRad) * 5;
            const vy0 = Math.sin(angleRad) * 5;
            let vx = vx0, vy = vy0;
            
            const trajectory = [];
            let minDist = Infinity;
            let finalAngle = 0;
            
            for (let step = 0; step < 500; step++) {
                const dx = NUCLEUS_X - x;
                const dy = NUCLEUS_Y - y;
                const r = Math.sqrt(dx*dx + dy*dy) / SCALE;
                if (r < 1) break;
                
                const dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < minDist) minDist = dist;
                
                const F = 200 * Z1 * Z2 / (r * r + 10);
                const ax = F * dx / dist;
                const ay = F * dy / dist;
                
                vx += ax * 0.01;
                vy += ay * 0.01;
                x += vx;
                y += vy;
                
                trajectory.push({x, y});
                
                if (x > canvas.width + 50 || y < -50 || y > canvas.height + 50) break;
            }
            
            if (trajectory.length > 10) {
                const last = trajectory[trajectory.length - 1];
                const prev = trajectory[trajectory.length - 5];
                finalAngle = Math.atan2(last.y - prev.y, last.x - prev.x) * 180 / Math.PI;
            }
            
            return { trajectory, minDist: (minDist / SCALE).toFixed(1), scatterAngle: finalAngle.toFixed(1) };
        }

        function drawTrajectory(data, color) {
            if (data.trajectory.length < 2) return;
            ctx.beginPath();
            ctx.moveTo(data.trajectory[0].x, data.trajectory[0].y);
            for (let i = 1; i < data.trajectory.length; i++) {
                ctx.lineTo(data.trajectory[i].x, data.trajectory[i].y);
            }
            ctx.strokeStyle = color || 'rgba(241,196,15,0.6)';
            ctx.lineWidth = 1.5;
            ctx.stroke();
            
            const last = data.trajectory[data.trajectory.length - 1];
            ctx.beginPath();
            ctx.arc(last.x, last.y, 3, 0, Math.PI * 2);
            ctx.fillStyle = '#f1c40f';
            ctx.fill();
        }

        function startScattering() {
            particleCount++;
            const data = simulateTrajectory();
            drawTrajectory(data);
            
            document.getElementById('scatterAngle').textContent = data.scatterAngle + '°';
            document.getElementById('closest').textContent = data.minDist;
            document.getElementById('particleCount').textContent = particleCount;
            
            if (Math.abs(parseFloat(data.scatterAngle)) > 90) {
                backCount++;
                document.getElementById('backCount').textContent = backCount;
            }
        }

        function startAuto() {
            if (autoInterval) return;
            autoInterval = setInterval(() => {
                document.getElementById('impact').value = 5 + Math.random() * 40;
                document.getElementById('angle').value = (Math.random() - 0.5) * 20;
                updateValue('impactVal', document.getElementById('impact').value);
                updateValue('angleVal', document.getElementById('angle').value);
                startScattering();
            }, 200);
        }

        function stopAuto() {
            clearInterval(autoInterval);
            autoInterval = null;
        }

        function clearCanvas() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawGrid();
            drawNucleus();
            particleCount = 0;
            backCount = 0;
            document.getElementById('particleCount').textContent = '0';
            document.getElementById('backCount').textContent = '0';
            document.getElementById('scatterAngle').textContent = '--';
            document.getElementById('closest').textContent = '--';
        }

        drawGrid();
        drawNucleus();

        // ========== 原子模型 ==========
        let autoInterval = null;
        let particleCount = 0;
        let backCount = 0;
        let animationRunning = true;
        let electrons = [];
        let animationId = null;

        function getElementData(z) {
            const elements = {
                1: { name: 'H', neutrons: 0, shells: [1] },
                2: { name: 'He', neutrons: 2, shells: [2] },
                6: { name: 'C', neutrons: 6, shells: [2, 4] },
                8: { name: 'O', neutrons: 8, shells: [2, 6] },
                11: { name: 'Na', neutrons: 12, shells: [2, 8, 1] },
                26: { name: 'Fe', neutrons: 30, shells: [2, 8, 14, 2] },
                29: { name: 'Cu', neutrons: 35, shells: [2, 8, 18, 1] },
                47: { name: 'Ag', neutrons: 61, shells: [2, 8, 18, 18, 1] },
                79: { name: 'Au', neutrons: 118, shells: [2, 8, 18, 32, 18, 1] },
                92: { name: 'U', neutrons: 146, shells: [2, 8, 18, 32, 21, 9, 2] }
            };
            return elements[z] || { name: 'X', neutrons: Math.round(z*1.5), shells: [z] };
        }

        function changeElement() {
            const z = parseInt(document.getElementById('element').value);
            const data = getElementData(z);
            document.getElementById('shells').value = data.shells.length;
            updateValue('shellsVal', data.shells.length);
            updateAtom();
        }

        function updateAtom() {
            const container = document.getElementById('atomContainer');
            const z = parseInt(document.getElementById('element').value);
            const data = getElementData(z);
            const viewMode = document.getElementById('viewMode').value;
            
            const old = container.querySelectorAll('.exp-electron-orbit, .exp-electron, .cloud-dot');
            old.forEach(e => e.remove());
            
            document.getElementById('protonNum').textContent = z;
            document.getElementById('neutronNum').textContent = data.neutrons;
            document.getElementById('electronNum').textContent = z;
            document.getElementById('massNum').textContent = z + data.neutrons;
            
            const nucleus = document.getElementById('nucleus');
            const nSize = 12 + Math.sqrt(z) * 1.5;
            nucleus.style.width = nSize + 'px';
            nucleus.style.height = nSize + 'px';
            
            electrons = [];
            const shellRadii = [60, 100, 140, 180, 220, 260, 300];
            
            for (let s = 0; s < data.shells.length && s < 7; s++) {
                const count = data.shells[s];
                const radius = shellRadii[s];
                
                if (viewMode === 'solar' || viewMode === 'both') {
                    const orbit = document.createElement('div');
                    orbit.className = 'exp-electron-orbit';
                    orbit.style.width = radius * 2 + 'px';
                    orbit.style.height = radius * 2 + 'px';
                    container.appendChild(orbit);
                }
                
                for (let e = 0; e < count; e++) {
                    const angle = (e / count) * Math.PI * 2;
                    const ele = document.createElement('div');
                    ele.className = 'exp-electron';
                    
                    if (viewMode === 'cloud') {
                        ele.style.width = '3px';
                        ele.style.height = '3px';
                        ele.style.opacity = '0.6';
                        const r = radius + (Math.random() - 0.5) * 40;
                        const a = Math.random() * Math.PI * 2;
                        ele.style.left = (50 + r * Math.cos(a) / 5) + '%';
                        ele.style.top = (50 + r * Math.sin(a) / 5) + '%';
                    } else {
                        ele.style.left = '50%';
                        ele.style.top = '50%';
                    }
                    
                    container.appendChild(ele);
                    electrons.push({
                        element: ele,
                        shell: s,
                        index: e,
                        totalInShell: count,
                        radius: radius,
                        angle: angle,
                        speed: (0.5 + Math.random() * 0.5) * (1 - s * 0.1)
                    });
                }
            }
            
            if (animationRunning) animateElectrons();
        }

        function animateElectrons() {
            if (animationId) cancelAnimationFrame(animationId);
            const speed = parseInt(document.getElementById('speed').value) / 50;
            const viewMode = document.getElementById('viewMode').value;
            
            function frame() {
                if (!animationRunning) return;
                
                electrons.forEach(e => {
                    if (viewMode === 'cloud') return;
                    e.angle += e.speed * 0.02 * speed;
                    const x = Math.cos(e.angle) * e.radius;
                    const y = Math.sin(e.angle) * e.radius;
                    e.element.style.transform = `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`;
                });
                
                animationId = requestAnimationFrame(frame);
            }
            frame();
        }

        function toggleAnimation() {
            animationRunning = !animationRunning;
            document.getElementById('animBtn').textContent = animationRunning ? '暂停' : '播放';
            if (animationRunning) animateElectrons();
        }

        function addElectron() {
            const z = parseInt(document.getElementById('element').value);
            if (z < 92) {
                document.getElementById('element').value = z + 1;
                changeElement();
            }
        }

        function removeElectron() {
            const z = parseInt(document.getElementById('element').value);
            if (z > 1) {
                document.getElementById('element').value = z - 1;
                changeElement();
            }
        }

        function resetAtom() {
            document.getElementById('element').value = 79;
            document.getElementById('shells').value = 6;
            document.getElementById('speed').value = 50;
            document.getElementById('viewMode').value = 'solar';
            updateValue('shellsVal', 6);
            updateValue('speedVal', 50);
            changeElement();
        }

        // 页面加载时初始化散射画布
        window.addEventListener('load', () => {
            drawGrid();
            drawNucleus();
        });
    </script>
</body>
</html>"""

        try:
            with open(help_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            webbrowser.open(help_file)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建或打开帮助文件：{e}")

    def show_tutorial(self):
        """菜单中的“使用教程”同样调用 show_help"""
        self.show_help()

    # ==================== 关于（HTML） ====================
    def show_about(self):
        """打开 HTML 关于页面（每次重新生成）"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        about_dir = os.path.join(base_dir, "about")
        os.makedirs(about_dir, exist_ok=True)
        about_file = os.path.join(about_dir, "about.html")

        if os.path.exists(about_file):
            try:
                os.remove(about_file)
            except Exception as e:
                messagebox.showerror("错误", f"无法删除旧的关于文件：{e}")
                return

        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>关于 化学工具箱 v2.5</title>
    <style>
        body { font-family: 'Microsoft YaHei', sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 700px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); text-align: center; }
        h1 { color: #2c3e50; }
        .version { font-size: 1.5em; color: #2980b9; margin: 10px 0; }
        .desc { line-height: 1.8; text-align: left; margin: 20px 0; }
        .footer { margin-top: 30px; color: #7f8c8d; font-size: 0.9em; }
    </style>
</head>
<body>
<div class="container">
    <h1>化学工具箱</h1>
    <div class="version">版本 2.5</div>
    <div class="desc">
        <p><strong>发布日期：</strong>2026年7月19日</p>
        <p><strong>开发语言：</strong>Python 3 + Tkinter</p>
        <p><strong>核心功能：</strong></p>
        <ul style="text-align:left;">
            <li>化学方程式配平（支持离子方程式）</li>
            <li>交互式元素周期表（118种元素）</li>
            <li>8种化学计算工具（摩尔质量、浓度、稀释、比例、元素百分比、经验式、浓度换算、产率）</li>
            <li>16种实用功能（pH、气体定律、热化学、氧化还原、有机化学、溶解度、缓冲溶液、滴定、光谱、动力学、电化学、平衡常数、热力学、分压、核化学、溶液配制）</li>
            <li>可扩展的插件系统</li>
        </ul>
        <p><strong>作者：</strong>化学爱好者</p>
        <p><strong>致谢：</strong>感谢所有测试和反馈的用户！</p>
    </div>
    <h2>注意事项</h2>
    <ul>
        <li>§§计算结果均为近似值，适用于教学和一般计算。</li>
        <li>§§本软件中数据由AI收集，不保证准确，请仔细判断。本软件数据由AI添加，部分功能由AI开发，所以本软件不保证任何数据以及功能计算出的结果准确，由本软件造成的任何问题，本软件开发者不承担任何责任。</li>
        <li>§§如果开始使用本软件，则认为已经同意上述说明。若不同意，则应立即停止使用本软件。</li>
        <li>§§请勿导入任何不信任的，来源不明的插件</li>
    </ul>
    <div class="footer">© 2026 化学工具箱 | 开源免费</div>
</div>
</body>
</html>"""

        try:
            with open(about_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            webbrowser.open(about_file)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建或打开关于文件：{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChemistryToolbox(root)
    root.mainloop()