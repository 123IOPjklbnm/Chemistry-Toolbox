import sys
import re
from collections import defaultdict
from math import gcd, log10, floor, exp
import datetime
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QTextEdit, QTabWidget, QFrame,
                             QGridLayout, QGroupBox, QComboBox, QRadioButton, QButtonGroup,
                             QScrollArea, QFileDialog, QMessageBox, QSplitter, QStackedWidget,
                             QToolBar, QAction, QStatusBar, QMenuBar, QMenu)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QPalette

# ==================== 原有核心类（保持不变）====================
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

# ==================== 主窗口 PyQt5 实现 ====================
class ChemistryToolbox(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("化学工具箱 v2.1")
        self.setGeometry(100, 100, 1300, 850)
        
        # 设置全局字体
        font = QFont("Microsoft YaHei", 10)
        self.setFont(font)
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 顶部工具栏
        toolbar = self.addToolBar("工具栏")
        toolbar.setMovable(False)
        self.create_actions()
        toolbar.addAction(self.balance_action)
        toolbar.addAction(self.periodic_action)
        toolbar.addAction(self.calc_action)
        toolbar.addAction(self.utils_action)
        toolbar.addAction(self.about_action)
        toolbar.addAction(self.help_action)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        # 使用QStackedWidget来切换不同功能界面
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # 创建各个功能页面
        self.balance_page = QWidget()
        self.periodic_page = QWidget()
        self.calc_page = QWidget()
        self.utils_page = QWidget()
        self.about_page = QWidget()
        self.help_page = QWidget()
        
        self.stacked_widget.addWidget(self.balance_page)
        self.stacked_widget.addWidget(self.periodic_page)
        self.stacked_widget.addWidget(self.calc_page)
        self.stacked_widget.addWidget(self.utils_page)
        self.stacked_widget.addWidget(self.about_page)
        self.stacked_widget.addWidget(self.help_page)
        
        # 初始化各页面
        self.init_balance_page()
        self.init_periodic_page()
        self.init_calc_page()
        self.init_utils_page()
        self.init_about_page()
        self.init_help_page()
        
        # 默认显示配平页面
        self.stacked_widget.setCurrentWidget(self.balance_page)
    
    def create_actions(self):
        self.balance_action = QAction("配平", self)
        self.balance_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.balance_page))
        self.periodic_action = QAction("元素周期表", self)
        self.periodic_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.periodic_page))
        self.calc_action = QAction("计算", self)
        self.calc_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.calc_page))
        self.utils_action = QAction("实用功能", self)
        self.utils_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.utils_page))
        self.about_action = QAction("关于", self)
        self.about_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.about_page))
        self.help_action = QAction("帮助", self)
        self.help_action.triggered.connect(lambda: self.stacked_widget.setCurrentWidget(self.help_page))
    
    # -------------------- 配平页面 --------------------
    def init_balance_page(self):
        layout = QVBoxLayout(self.balance_page)
        layout.setSpacing(10)
        
        title = QLabel("化学方程式配平")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setStyleSheet("color: blue;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # 说明
        info_label = QLabel("支持格式: H2+O2=H2O  |  Fe2O3+CO=Fe+CO2  |  HCO3^+H*=CO2+H2O")
        info_label.setStyleSheet("color: green;")
        layout.addWidget(info_label, alignment=Qt.AlignCenter)
        
        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("方程式:"))
        self.balance_input = QLineEdit()
        self.balance_input.setFont(QFont("Courier", 11))
        self.balance_input.setMinimumWidth(500)
        self.balance_input.returnPressed.connect(self.do_balance)
        input_layout.addWidget(self.balance_input)
        self.balance_btn = QPushButton("配平")
        self.balance_btn.setStyleSheet("background-color: lightblue;")
        self.balance_btn.clicked.connect(self.do_balance)
        input_layout.addWidget(self.balance_btn)
        input_layout.addStretch()
        layout.addLayout(input_layout)
        
        # 结果显示
        result_group = QGroupBox("配平结果")
        result_layout = QVBoxLayout(result_group)
        self.balance_result = QTextEdit()
        self.balance_result.setFont(QFont("Courier", 12))
        self.balance_result.setReadOnly(True)
        result_layout.addWidget(self.balance_result)
        layout.addWidget(result_group)
        
        # 示例按钮
        examples_layout = QHBoxLayout()
        examples_layout.addWidget(QLabel("示例:"))
        examples = [
            ("H2+O2=H2O", "氢气燃烧"),
            ("Fe2O3+CO=Fe+CO2", "炼铁"),
            ("Cu+AgNO3=Cu(NO3)2+Ag", "置换反应"),
            ("HCO3^+H*=CO2+H2O", "碳酸氢根与酸反应")
        ]
        for eq, desc in examples:
            btn = QPushButton(desc)
            btn.clicked.connect(lambda checked, e=eq: self.load_balance_example(e))
            examples_layout.addWidget(btn)
        examples_layout.addStretch()
        layout.addLayout(examples_layout)
    
    def load_balance_example(self, equation):
        self.balance_input.setText(equation)
        self.do_balance()
    
    def do_balance(self):
        equation = self.balance_input.text().strip()
        if not equation:
            QMessageBox.warning(self, "警告", "请输入化学方程式")
            return
        self.statusBar().showMessage("正在配平方程式...")
        result, valence_data = EquationBalancer.balance(equation)
        self.balance_result.clear()
        if result.startswith("错误") or result.startswith("配平失败"):
            self.balance_result.setText(result)
            self.statusBar().showMessage("配平失败")
        else:
            # 转换显示格式（*->⁺, ^->⁻）
            display_result = result
            display_result = re.sub(r'\*+', lambda m: '⁺' * len(m.group()), display_result)
            display_result = re.sub(r'\^+', lambda m: '⁻' * len(m.group()), display_result)
            self.balance_result.setText(f"配平结果:\n\n{display_result}")
            if valence_data:
                valence_text = "\n\n化合价标注:\n"
                for key, vals in valence_data.items():
                    if vals:
                        valence_text += f"{key}: "
                        for elem, v in vals.items():
                            if v > 0:
                                valence_text += f"{elem}(+{v}) "
                            elif v < 0:
                                valence_text += f"{elem}({v}) "
                            else:
                                valence_text += f"{elem}(0) "
                        valence_text += "\n"
                self.balance_result.append(valence_text)
            self.statusBar().showMessage("配平完成")
    
    # -------------------- 元素周期表页面 --------------------
    def init_periodic_page(self):
        layout = QVBoxLayout(self.periodic_page)
        title = QLabel("元素周期表")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setStyleSheet("color: blue;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        
        rows_data = [
            [("H",1), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("He",18)],
            [("Li",1), ("Be",2), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("B",13), ("C",14), ("N",15), ("O",16), ("F",17), ("Ne",18)],
            [("Na",1), ("Mg",2), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("",0), ("Al",13), ("Si",14), ("P",15), ("S",16), ("Cl",17), ("Ar",18)],
            [("K",1), ("Ca",2), ("Sc",3), ("Ti",4), ("V",5), ("Cr",6), ("Mn",7), ("Fe",8), ("Co",9), ("Ni",10), ("Cu",11), ("Zn",12), ("Ga",13), ("Ge",14), ("As",15), ("Se",16), ("Br",17), ("Kr",18)],
            [("Rb",1), ("Sr",2), ("Y",3), ("Zr",4), ("Nb",5), ("Mo",6), ("Tc",7), ("Ru",8), ("Rh",9), ("Pd",10), ("Ag",11), ("Cd",12), ("In",13), ("Sn",14), ("Sb",15), ("Te",16), ("I",17), ("Xe",18)],
            [("Cs",1), ("Ba",2), ("La",3), ("Hf",4), ("Ta",5), ("W",6), ("Re",7), ("Os",8), ("Ir",9), ("Pt",10), ("Au",11), ("Hg",12), ("Tl",13), ("Pb",14), ("Bi",15), ("Po",16), ("At",17), ("Rn",18)],
            [("Fr",1), ("Ra",2), ("Ac",3), ("Rf",4), ("Db",5), ("Sg",6), ("Bh",7), ("Hs",8), ("Mt",9), ("Ds",10), ("Rg",11), ("Cn",12), ("Nh",13), ("Fl",14), ("Mc",15), ("Lv",16), ("Ts",17), ("Og",18)],
        ]
        
        colors = {
            1: "#ffcccc", 2: "#ccffcc", "transition": "#ccccff", "nonmetal": "#ffffcc",
            17: "#ffcc99", 18: "#99ccff"
        }
        
        for r, row in enumerate(rows_data):
            for c, (symbol, group) in enumerate(row):
                if not symbol:
                    continue
                data = ExtendedPeriodicTable.elements_data.get(symbol)
                if data:
                    g = data["group"]
                    if g == 1:
                        color = colors[1]
                    elif g == 2:
                        color = colors[2]
                    elif 3 <= g <= 12:
                        color = colors["transition"]
                    elif 13 <= g <= 16:
                        color = colors["nonmetal"]
                    elif g == 17:
                        color = colors[17]
                    elif g == 18:
                        color = colors[18]
                    else:
                        color = "#f0f0f0"
                    btn = QPushButton(f"{symbol}\n{data['atomic']}")
                    btn.setFixedSize(70, 60)
                    btn.setStyleSheet(f"background-color: {color};")
                    btn.clicked.connect(lambda checked, s=symbol: self.show_element_info(s))
                    scroll_layout.addWidget(btn, r, c)
        
        # 镧系锕系
        lanthanides = ["Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"]
        actinides = ["Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr"]
        row_l = len(rows_data)
        for i, sym in enumerate(lanthanides):
            btn = QPushButton(sym)
            btn.setFixedSize(50, 40)
            btn.setStyleSheet("background-color: #ffffcc;")
            btn.clicked.connect(lambda checked, s=sym: self.show_element_info(s))
            scroll_layout.addWidget(btn, row_l, i)
        row_a = row_l + 1
        for i, sym in enumerate(actinides):
            btn = QPushButton(sym)
            btn.setFixedSize(50, 40)
            btn.setStyleSheet("background-color: #ffcc99;")
            btn.clicked.connect(lambda checked, s=sym: self.show_element_info(s))
            scroll_layout.addWidget(btn, row_a, i)
        
        # 图例
        legend_layout = QHBoxLayout()
        for text, color in [("碱金属", "#ffcccc"), ("碱土金属", "#ccffcc"), ("过渡金属", "#ccccff"),
                           ("非金属", "#ffffcc"), ("卤素", "#ffcc99"), ("稀有气体", "#99ccff"),
                           ("镧系", "#ffffcc"), ("锕系", "#ffcc99")]:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"background-color: {color}; padding: 2px;")
            legend_layout.addWidget(lbl)
        scroll_layout.addLayout(legend_layout, row_a+1, 0, 1, 18)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
    
    def show_element_info(self, symbol):
        data = ExtendedPeriodicTable.elements_data.get(symbol)
        if data:
            electron_layers = ExtendedPeriodicTable.electron_config.get(symbol, "未知")
            en = ExtendedPeriodicTable.electronegativity.get(symbol, "未知")
            mass = AtomicMass.get_mass(symbol)
            info = f"元素: {symbol}\n名称: {data['name']}\n原子序数: {data['atomic']}\n原子量: {data['mass']}\n电负性: {en}\n族: {data['group']}\n周期: {data['period']}\n电子排布: {data['config']}\n电子层: {electron_layers}\n简介: {data['desc']}"
            QMessageBox.information(self, "元素信息", info)
        else:
            QMessageBox.information(self, "元素信息", f"未找到 {symbol} 的详细信息")
    
    # -------------------- 计算页面 --------------------
    def init_calc_page(self):
        layout = QVBoxLayout(self.calc_page)
        title = QLabel("化学计算工具")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setStyleSheet("color: blue;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        self.calc_tabs = QTabWidget()
        layout.addWidget(self.calc_tabs)
        
        # 摩尔质量
        molar_page = QWidget()
        self.init_molar_calc(molar_page)
        self.calc_tabs.addTab(molar_page, "摩尔质量")
        
        # 浓度计算
        conc_page = QWidget()
        self.init_concentration_calc(conc_page)
        self.calc_tabs.addTab(conc_page, "浓度计算")
        
        # 稀释计算
        dilute_page = QWidget()
        self.init_dilution_calc(dilute_page)
        self.calc_tabs.addTab(dilute_page, "稀释计算")
        
        # 比例求解
        ratio_page = QWidget()
        self.init_ratio_calc(ratio_page)
        self.calc_tabs.addTab(ratio_page, "比例求解")
        
        # 元素百分比
        percent_page = QWidget()
        self.init_percent_calc(percent_page)
        self.calc_tabs.addTab(percent_page, "元素百分比")
        
        # 经验式确定
        empirical_page = QWidget()
        self.init_empirical_calc(empirical_page)
        self.calc_tabs.addTab(empirical_page, "经验式确定")
        
        # 浓度换算
        convert_page = QWidget()
        self.init_convert_calc(convert_page)
        self.calc_tabs.addTab(convert_page, "浓度换算")
        
        # 产率计算
        yield_page = QWidget()
        self.init_yield_calc(yield_page)
        self.calc_tabs.addTab(yield_page, "产率计算")
    
    def init_molar_calc(self, parent):
        layout = QVBoxLayout(parent)
        layout.addWidget(QLabel("输入化学式:"))
        self.molar_input = QLineEdit()
        self.molar_input.setFont(QFont("Courier", 11))
        self.molar_input.returnPressed.connect(self.calc_molar_mass)
        layout.addWidget(self.molar_input)
        btn = QPushButton("计算")
        btn.setStyleSheet("background-color: lightblue;")
        btn.clicked.connect(self.calc_molar_mass)
        layout.addWidget(btn)
        self.molar_result = QTextEdit()
        self.molar_result.setReadOnly(True)
        layout.addWidget(self.molar_result)
    
    def calc_molar_mass(self):
        formula = self.molar_input.text().strip()
        if not formula:
            return
        mass, detail = ChemicalFormulaParser.calculate_molar_mass(formula)
        self.molar_result.clear()
        if mass > 0:
            self.molar_result.setText(f"化学式: {formula}\n相对分子质量: {mass}\n\n计算过程:\n{detail}")
        else:
            self.molar_result.setText(detail)
    
    def init_concentration_calc(self, parent):
        layout = QGridLayout(parent)
        layout.addWidget(QLabel("溶质质量 (g):"), 0, 0)
        self.conc_mass = QLineEdit()
        layout.addWidget(self.conc_mass, 0, 1)
        layout.addWidget(QLabel("溶液体积 (L):"), 1, 0)
        self.conc_vol = QLineEdit()
        layout.addWidget(self.conc_vol, 1, 1)
        layout.addWidget(QLabel("摩尔质量 (g/mol):"), 2, 0)
        self.conc_molar = QLineEdit()
        layout.addWidget(self.conc_molar, 2, 1)
        btn = QPushButton("计算浓度")
        btn.setStyleSheet("background-color: lightblue;")
        btn.clicked.connect(self.calc_concentration)
        layout.addWidget(btn, 3, 0, 1, 2)
        self.conc_result = QTextEdit()
        self.conc_result.setReadOnly(True)
        layout.addWidget(self.conc_result, 4, 0, 1, 2)
        layout.setRowStretch(4, 1)
    
    def calc_concentration(self):
        try:
            mass = float(self.conc_mass.text())
            vol = float(self.conc_vol.text())
            molar = float(self.conc_molar.text())
            moles = mass / molar
            conc = moles / vol
            self.conc_result.setText(f"溶质的量: {moles:.4f} mol\n溶液体积: {vol} L\n物质的量浓度: {conc:.4f} mol/L")
        except:
            self.conc_result.setText("输入错误，请检查")
    
    def init_dilution_calc(self, parent):
        layout = QGridLayout(parent)
        layout.addWidget(QLabel("初始浓度 (mol/L):"), 0, 0)
        self.c1 = QLineEdit()
        layout.addWidget(self.c1, 0, 1)
        layout.addWidget(QLabel("初始体积 (L):"), 1, 0)
        self.v1 = QLineEdit()
        layout.addWidget(self.v1, 1, 1)
        layout.addWidget(QLabel("最终体积 (L):"), 2, 0)
        self.v2 = QLineEdit()
        layout.addWidget(self.v2, 2, 1)
        btn = QPushButton("计算最终浓度")
        btn.setStyleSheet("background-color: lightblue;")
        btn.clicked.connect(self.calc_dilution)
        layout.addWidget(btn, 3, 0, 1, 2)
        self.dilute_result = QTextEdit()
        self.dilute_result.setReadOnly(True)
        layout.addWidget(self.dilute_result, 4, 0, 1, 2)
        layout.setRowStretch(4, 1)
    
    def calc_dilution(self):
        try:
            c1 = float(self.c1.text())
            v1 = float(self.v1.text())
            v2 = float(self.v2.text())
            c2 = c1 * v1 / v2
            self.dilute_result.setText(f"C₁V₁ = C₂V₂\n{c1} × {v1} = C₂ × {v2}\nC₂ = {c2:.4f} mol/L")
        except:
            self.dilute_result.setText("输入错误")
    
    def init_ratio_calc(self, parent):
        layout = QVBoxLayout(parent)
        info = QLabel("格式1: a / b = c / x  →  x = (b × c) / a\n格式2: a / b = x / d  →  x = (a × d) / b")
        info.setWordWrap(True)
        layout.addWidget(info)
        type_group = QHBoxLayout()
        self.ratio_type = "type1"
        rb1 = QRadioButton("a / b = c / x")
        rb1.setChecked(True)
        rb1.toggled.connect(lambda: self.set_ratio_type("type1"))
        rb2 = QRadioButton("a / b = x / d")
        rb2.toggled.connect(lambda: self.set_ratio_type("type2"))
        type_group.addWidget(rb1)
        type_group.addWidget(rb2)
        layout.addLayout(type_group)
        
        self.ratio_inputs = {}
        input_layout = QGridLayout()
        self.ratio_input_layout = input_layout
        layout.addLayout(input_layout)
        self.update_ratio_inputs()
        
        btn = QPushButton("计算 x")
        btn.setStyleSheet("background-color: lightblue;")
        btn.clicked.connect(self.calc_ratio)
        layout.addWidget(btn)
        self.ratio_result = QTextEdit()
        self.ratio_result.setReadOnly(True)
        layout.addWidget(self.ratio_result)
    
    def set_ratio_type(self, t):
        self.ratio_type = t
        self.update_ratio_inputs()
    
    def update_ratio_inputs(self):
        # 清除原有输入框
        for i in reversed(range(self.ratio_input_layout.count())):
            widget = self.ratio_input_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        if self.ratio_type == "type1":
            labels = ["a =", "b =", "c =", "x = ?"]
            self.ratio_vars = ["a", "b", "c"]
        else:
            labels = ["a =", "b =", "d =", "x = ?"]
            self.ratio_vars = ["a", "b", "d"]
        self.ratio_entries = {}
        for i, label in enumerate(labels):
            lbl = QLabel(label)
            self.ratio_input_layout.addWidget(lbl, i, 0)
            entry = QLineEdit()
            if i < 3:
                self.ratio_entries[self.ratio_vars[i]] = entry
            else:
                entry.setReadOnly(True)
                entry.setStyleSheet("background-color: #f0f0f0;")
                self.ratio_entries["x_display"] = entry
            self.ratio_input_layout.addWidget(entry, i, 1)
    
    def calc_ratio(self):
        try:
            if self.ratio_type == "type1":
                a = float(self.ratio_entries["a"].text())
                b = float(self.ratio_entries["b"].text())
                c = float(self.ratio_entries["c"].text())
                if a == 0:
                    raise ValueError("分母 a 不能为0")
                x = (b * c) / a
                self.ratio_result.setText(f"比例式: {a} / {b} = {c} / x\n\n解: x = (b × c) / a = ({b}×{c})/{a} = {x:.6g}")
                self.ratio_entries["x_display"].setText(f"{x:.6g}")
            else:
                a = float(self.ratio_entries["a"].text())
                b = float(self.ratio_entries["b"].text())
                d = float(self.ratio_entries["d"].text())
                if b == 0:
                    raise ValueError("分母 b 不能为0")
                x = (a * d) / b
                self.ratio_result.setText(f"比例式: {a} / {b} = x / {d}\n\n解: x = (a × d) / b = ({a}×{d})/{b} = {x:.6g}")
                self.ratio_entries["x_display"].setText(f"{x:.6g}")
        except Exception as e:
            self.ratio_result.setText(f"错误: {str(e)}")
    
    def init_percent_calc(self, parent):
        layout = QVBoxLayout(parent)
        layout.addWidget(QLabel("输入化学式:"))
        self.percent_input = QLineEdit()
        self.percent_input.setFont(QFont("Courier", 11))
        layout.addWidget(self.percent_input)
        btn = QPushButton("计算元素百分比")
        btn.setStyleSheet("background-color: lightblue;")
        btn.clicked.connect(self.calc_percent_composition)
        layout.addWidget(btn)
        self.percent_result = QTextEdit()
        self.percent_result.setReadOnly(True)
        layout.addWidget(self.percent_result)
    
    def calc_percent_composition(self):
        formula = self.percent_input.text().strip()
        if not formula:
            return
        total_mass, percent = ChemicalFormulaParser.calculate_percent_composition(formula)
        if total_mass is None:
            self.percent_result.setText("无效的化学式")
            return
        text = f"化学式: {formula}\n摩尔质量: {total_mass:.4f} g/mol\n\n各元素质量分数:\n"
        for elem in sorted(percent.keys()):
            text += f"{elem}: {percent[elem]:.2f}%\n"
        self.percent_result.setText(text)
    
    def init_empirical_calc(self, parent):
        layout = QVBoxLayout(parent)
        layout.addWidget(QLabel("输入元素质量或百分比（格式：元素 数值，每行一个）"))
        self.empirical_text = QTextEdit()
        self.empirical_text.setPlaceholderText("例如:\nC 40\nH 6.7\nO 53.3")
        self.empirical_text.setMaximumHeight(150)
        layout.addWidget(self.empirical_text)
        btn = QPushButton("确定经验式")
        btn.setStyleSheet("background-color: lightblue;")
        btn.clicked.connect(self.calc_empirical_formula)
        layout.addWidget(btn)
        self.empirical_result = QTextEdit()
        self.empirical_result.setReadOnly(True)
        layout.addWidget(self.empirical_result)
    
    def calc_empirical_formula(self):
        data = self.empirical_text.toPlainText().strip()
        if not data:
            return
        lines = data.split('\n')
        masses = {}
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) != 2:
                self.empirical_result.setText("格式错误，每行应为：元素 数值")
                return
            elem = parts[0].capitalize()
            try:
                val = float(parts[1])
            except:
                self.empirical_result.setText("数值无效")
                return
            masses[elem] = val
        moles = {}
        for elem, mass in masses.items():
            atomic = AtomicMass.get_mass(elem)
            if atomic == 0:
                self.empirical_result.setText(f"未知元素 {elem}")
                return
            moles[elem] = mass / atomic
        min_mole = min(moles.values())
        ratios = {elem: mole / min_mole for elem, mole in moles.items()}
        for factor in range(1, 20):
            int_ratios = {elem: round(ratios[elem] * factor) for elem in ratios}
            if all(abs(ratios[elem] * factor - int_ratios[elem]) < 0.01 for elem in ratios):
                formula = "".join(f"{elem}{int_ratios[elem] if int_ratios[elem]>1 else ''}" for elem in sorted(int_ratios.keys()))
                self.empirical_result.setText(f"经验式: {formula}")
                return
        self.empirical_result.setText("无法确定整数比")
    
    def init_convert_calc(self, parent):
        layout = QGridLayout(parent)
        layout.addWidget(QLabel("质量分数 (%) :"), 0, 0)
        self.wt_percent = QLineEdit()
        layout.addWidget(self.wt_percent, 0, 1)
        layout.addWidget(QLabel("溶液密度 (g/mL):"), 1, 0)
        self.density = QLineEdit()
        layout.addWidget(self.density, 1, 1)
        layout.addWidget(QLabel("溶质摩尔质量 (g/mol):"), 2, 0)
        self.molar_mass_convert = QLineEdit()
        layout.addWidget(self.molar_mass_convert, 2, 1)
        btn = QPushButton("计算摩尔浓度")
        btn.setStyleSheet("background-color: lightblue;")
        btn.clicked.connect(self.calc_concentration_convert)
        layout.addWidget(btn, 3, 0, 1, 2)
        self.convert_result = QTextEdit()
        self.convert_result.setReadOnly(True)
        layout.addWidget(self.convert_result, 4, 0, 1, 2)
        layout.setRowStretch(4, 1)
    
    def calc_concentration_convert(self):
        try:
            w = float(self.wt_percent.text())
            d = float(self.density.text())
            M = float(self.molar_mass_convert.text())
            c = (w * d * 10) / M
            self.convert_result.setText(f"摩尔浓度 = (质量分数 × 密度 × 10) / 摩尔质量\n= ({w} × {d} × 10) / {M} = {c:.4f} mol/L")
        except:
            self.convert_result.setText("输入错误")
    
    def init_yield_calc(self, parent):
        layout = QGridLayout(parent)
        layout.addWidget(QLabel("实际产量 (g):"), 0, 0)
        self.actual_yield = QLineEdit()
        layout.addWidget(self.actual_yield, 0, 1)
        layout.addWidget(QLabel("理论产量 (g):"), 1, 0)
        self.theoretical_yield = QLineEdit()
        layout.addWidget(self.theoretical_yield, 1, 1)
        btn = QPushButton("计算产率")
        btn.setStyleSheet("background-color: lightblue;")
        btn.clicked.connect(self.calc_yield)
        layout.addWidget(btn, 2, 0, 1, 2)
        self.yield_result = QTextEdit()
        self.yield_result.setReadOnly(True)
        layout.addWidget(self.yield_result, 3, 0, 1, 2)
        layout.setRowStretch(3, 1)
    
    def calc_yield(self):
        try:
            actual = float(self.actual_yield.text())
            theoretical = float(self.theoretical_yield.text())
            percent = (actual / theoretical) * 100
            self.yield_result.setText(f"产率 = (实际产量 / 理论产量) × 100% = ({actual}/{theoretical})×100% = {percent:.2f}%")
        except:
            self.yield_result.setText("输入错误")
    
    # -------------------- 实用功能页面 --------------------
    def init_utils_page(self):
        layout = QVBoxLayout(self.utils_page)
        title = QLabel("实用功能")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setStyleSheet("color: blue;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # 使用QTabWidget组织实用功能
        self.utils_tabs = QTabWidget()
        layout.addWidget(self.utils_tabs)
        
        # pH计算器
        ph_page = QWidget()
        self.init_ph_calculator(ph_page)
        self.utils_tabs.addTab(ph_page, "pH计算器")
        
        # 气体定律
        gas_page = QWidget()
        self.init_gas_law(gas_page)
        self.utils_tabs.addTab(gas_page, "气体定律")
        
        # 热化学
        thermo_page = QWidget()
        self.init_thermochemistry(thermo_page)
        self.utils_tabs.addTab(thermo_page, "热化学计算")
        
        # 氧化还原
        redox_page = QWidget()
        self.init_redox(redox_page)
        self.utils_tabs.addTab(redox_page, "氧化还原分析")
        
        # 有机化学
        organic_page = QWidget()
        self.init_organic(organic_page)
        self.utils_tabs.addTab(organic_page, "有机化学工具")
        
        # 溶解度
        sol_page = QWidget()
        self.init_solubility(sol_page)
        self.utils_tabs.addTab(sol_page, "溶解度查询")
        
        # 缓冲溶液
        buffer_page = QWidget()
        self.init_buffer(buffer_page)
        self.utils_tabs.addTab(buffer_page, "缓冲溶液计算")
        
        # 酸碱滴定
        titration_page = QWidget()
        self.init_titration(titration_page)
        self.utils_tabs.addTab(titration_page, "酸碱滴定计算")
        
        # 光谱分析
        spec_page = QWidget()
        self.init_spectroscopy(spec_page)
        self.utils_tabs.addTab(spec_page, "光谱分析")
        
        # 化学动力学
        kin_page = QWidget()
        self.init_kinetics(kin_page)
        self.utils_tabs.addTab(kin_page, "化学动力学")
        
        # 电化学
        electro_page = QWidget()
        self.init_electrochem(electro_page)
        self.utils_tabs.addTab(electro_page, "电化学（能斯特方程）")
        
        # 化学平衡
        equil_page = QWidget()
        self.init_equilibrium(equil_page)
        self.utils_tabs.addTab(equil_page, "化学平衡计算")
        
        # 热力学
        thermo2_page = QWidget()
        self.init_thermodynamics(thermo2_page)
        self.utils_tabs.addTab(thermo2_page, "热力学计算（ΔG, ΔH, ΔS）")
        
        # 气体分压
        partial_page = QWidget()
        self.init_partial_pressure(partial_page)
        self.utils_tabs.addTab(partial_page, "气体分压计算")
        
        # 核化学
        nuclear_page = QWidget()
        self.init_nuclear(nuclear_page)
        self.utils_tabs.addTab(nuclear_page, "核化学计算（半衰期）")
        
        # 溶液配制
        prep_page = QWidget()
        self.init_solution_prep(prep_page)
        self.utils_tabs.addTab(prep_page, "溶液配制计算")
    
    # ---------- pH计算器 ----------
    def init_ph_calculator(self, parent):
        layout = QVBoxLayout(parent)
        # 强酸强碱
        group1 = QGroupBox("强酸/强碱")
        glayout = QHBoxLayout(group1)
        glayout.addWidget(QLabel("浓度 (mol/L):"))
        self.ph_conc = QLineEdit()
        glayout.addWidget(self.ph_conc)
        glayout.addWidget(QLabel("类型:"))
        self.ph_type = QComboBox()
        self.ph_type.addItems(["强酸", "强碱"])
        glayout.addWidget(self.ph_type)
        btn1 = QPushButton("计算pH")
        btn1.clicked.connect(self.calc_ph)
        glayout.addWidget(btn1)
        layout.addWidget(group1)
        
        group2 = QGroupBox("弱酸/弱碱")
        glayout2 = QHBoxLayout(group2)
        glayout2.addWidget(QLabel("浓度 (mol/L):"))
        self.weak_conc = QLineEdit()
        glayout2.addWidget(self.weak_conc)
        glayout2.addWidget(QLabel("Ka/Kb:"))
        self.ka_kb = QLineEdit()
        glayout2.addWidget(self.ka_kb)
        glayout2.addWidget(QLabel("类型:"))
        self.weak_type = QComboBox()
        self.weak_type.addItems(["弱酸", "弱碱"])
        glayout2.addWidget(self.weak_type)
        btn2 = QPushButton("计算pH")
        btn2.clicked.connect(self.calc_weak_ph)
        glayout2.addWidget(btn2)
        layout.addWidget(group2)
        
        self.ph_result = QTextEdit()
        self.ph_result.setReadOnly(True)
        layout.addWidget(self.ph_result)
    
    def calc_ph(self):
        try:
            conc = float(self.ph_conc.text())
            if self.ph_type.currentText() == "强酸":
                ph = -log10(conc)
                self.ph_result.setText(f"[H⁺] = {conc} mol/L\npH = {ph:.2f}")
            else:
                poh = -log10(conc)
                ph = 14 - poh
                self.ph_result.setText(f"[OH⁻] = {conc} mol/L\npOH = {poh:.2f}\npH = {ph:.2f}")
        except:
            self.ph_result.setText("输入错误")
    
    def calc_weak_ph(self):
        try:
            conc = float(self.weak_conc.text())
            ka = float(self.ka_kb.text())
            if self.weak_type.currentText() == "弱酸":
                h_conc = (ka * conc) ** 0.5
                ph = -log10(h_conc)
                self.ph_result.setText(f"[H⁺] = √(Ka×C) = {h_conc:.2e} mol/L\npH = {ph:.2f}")
            else:
                oh_conc = (ka * conc) ** 0.5
                poh = -log10(oh_conc)
                ph = 14 - poh
                self.ph_result.setText(f"[OH⁻] = √(Kb×C) = {oh_conc:.2e} mol/L\npOH = {poh:.2f}\npH = {ph:.2f}")
        except:
            self.ph_result.setText("输入错误")
    
    # ---------- 气体定律 ----------
    def init_gas_law(self, parent):
        layout = QGridLayout(parent)
        labels = ["压力 P (atm):", "体积 V (L):", "物质的量 n (mol):", "温度 T (K):"]
        self.gas_entries = {}
        for i, label in enumerate(labels):
            layout.addWidget(QLabel(label), i, 0)
            entry = QLineEdit()
            self.gas_entries[label.split()[0]] = entry
            layout.addWidget(entry, i, 1)
        btn = QPushButton("计算")
        btn.clicked.connect(self.calc_gas_law)
        layout.addWidget(btn, 4, 0, 1, 2)
        self.gas_result = QTextEdit()
        self.gas_result.setReadOnly(True)
        layout.addWidget(self.gas_result, 5, 0, 1, 2)
        layout.setRowStretch(5, 1)
    
    def calc_gas_law(self):
        R = 0.0821
        try:
            P = self.gas_entries["P"].text()
            V = self.gas_entries["V"].text()
            n = self.gas_entries["n"].text()
            T = self.gas_entries["T"].text()
            if P and V and n:
                P, V, n = float(P), float(V), float(n)
                T = P * V / (n * R)
                self.gas_result.setText(f"温度 T = PV/(nR) = {T:.2f} K")
            elif P and V and T:
                P, V, T = float(P), float(V), float(T)
                n = P * V / (R * T)
                self.gas_result.setText(f"物质的量 n = PV/(RT) = {n:.4f} mol")
            elif P and n and T:
                P, n, T = float(P), float(n), float(T)
                V = n * R * T / P
                self.gas_result.setText(f"体积 V = nRT/P = {V:.2f} L")
            elif V and n and T:
                V, n, T = float(V), float(n), float(T)
                P = n * R * T / V
                self.gas_result.setText(f"压力 P = nRT/V = {P:.2f} atm")
            else:
                self.gas_result.setText("请输入至少三个变量")
        except:
            self.gas_result.setText("输入错误")
    
    # ---------- 热化学计算 ----------
    def init_thermochemistry(self, parent):
        layout = QVBoxLayout(parent)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        # 热量计算
        heat_page = QWidget()
        heat_layout = QGridLayout(heat_page)
        heat_layout.addWidget(QLabel("质量 m (g):"), 0, 0)
        self.heat_mass = QLineEdit()
        heat_layout.addWidget(self.heat_mass, 0, 1)
        heat_layout.addWidget(QLabel("比热容 c (J/g·K):"), 1, 0)
        self.heat_c = QLineEdit()
        heat_layout.addWidget(self.heat_c, 1, 1)
        heat_layout.addWidget(QLabel("温度变化 ΔT (K):"), 2, 0)
        self.heat_dt = QLineEdit()
        heat_layout.addWidget(self.heat_dt, 2, 1)
        btn_heat = QPushButton("计算热量")
        btn_heat.clicked.connect(self.calc_heat)
        heat_layout.addWidget(btn_heat, 3, 0, 1, 2)
        self.heat_result = QTextEdit()
        heat_layout.addWidget(self.heat_result, 4, 0, 1, 2)
        tabs.addTab(heat_page, "热量计算")
        # 燃烧热
        comb_page = QWidget()
        comb_layout = QGridLayout(comb_page)
        comb_layout.addWidget(QLabel("燃烧热 ΔH (kJ/mol):"), 0, 0)
        self.dh_comb = QLineEdit()
        comb_layout.addWidget(self.dh_comb, 0, 1)
        comb_layout.addWidget(QLabel("物质的量 n (mol):"), 1, 0)
        self.n_comb = QLineEdit()
        comb_layout.addWidget(self.n_comb, 1, 1)
        btn_comb = QPushButton("计算放热")
        btn_comb.clicked.connect(self.calc_combustion)
        comb_layout.addWidget(btn_comb, 2, 0, 1, 2)
        self.comb_result = QTextEdit()
        comb_layout.addWidget(self.comb_result, 3, 0, 1, 2)
        tabs.addTab(comb_page, "燃烧热")
    
    def calc_heat(self):
        try:
            m = float(self.heat_mass.text())
            c = float(self.heat_c.text())
            dt = float(self.heat_dt.text())
            q = m * c * dt
            self.heat_result.setText(f"Q = m·c·ΔT = {m} × {c} × {dt} = {q:.2f} J")
        except:
            self.heat_result.setText("输入错误")
    
    def calc_combustion(self):
        try:
            dh = float(self.dh_comb.text())
            n = float(self.n_comb.text())
            q = dh * n
            self.comb_result.setText(f"Q = ΔH × n = {dh} × {n} = {q:.2f} kJ")
        except:
            self.comb_result.setText("输入错误")
    
    # ---------- 氧化还原分析 ----------
    def init_redox(self, parent):
        layout = QVBoxLayout(parent)
        layout.addWidget(QLabel("输入化合物（如 H2O, Fe2O3）:"))
        self.redox_input = QLineEdit()
        layout.addWidget(self.redox_input)
        btn = QPushButton("计算氧化数")
        btn.clicked.connect(self.calc_oxidation)
        layout.addWidget(btn)
        self.redox_result = QTextEdit()
        self.redox_result.setReadOnly(True)
        layout.addWidget(self.redox_result)
        # 常见氧化剂还原剂
        info = QLabel("常见氧化剂: KMnO₄, K₂Cr₂O₇, H₂O₂, HNO₃, O₂\n常见还原剂: Fe²⁺, Zn, H₂, CO, SO₂")
        info.setWordWrap(True)
        layout.addWidget(info)
    
    def calc_oxidation(self):
        formula = self.redox_input.text().strip()
        if not formula:
            return
        counts = ChemicalFormulaParser.parse_formula(formula)
        text = f"化合物: {formula}\n\n元素氧化数:\n"
        for elem, cnt in counts.items():
            valence = ValenceData.get_valence(elem)
            text += f"{elem}: {valence[0] if valence else 0} (常见)\n"
        self.redox_result.setText(text)
    
    # ---------- 有机化学工具 ----------
    def init_organic(self, parent):
        layout = QVBoxLayout(parent)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        # 官能团识别
        func_page = QWidget()
        func_layout = QVBoxLayout(func_page)
        func_layout.addWidget(QLabel("输入有机物名称:"))
        self.org_name = QLineEdit()
        func_layout.addWidget(self.org_name)
        btn_func = QPushButton("识别")
        btn_func.clicked.connect(self.identify_functional)
        func_layout.addWidget(btn_func)
        self.func_result = QTextEdit()
        self.func_result.setReadOnly(True)
        func_layout.addWidget(self.func_result)
        tabs.addTab(func_page, "官能团识别")
        # 同分异构体
        isomer_page = QWidget()
        isomer_layout = QVBoxLayout(isomer_page)
        isomer_layout.addWidget(QLabel("分子式 (如 C5H12):"))
        self.isomer_formula = QLineEdit()
        isomer_layout.addWidget(self.isomer_formula)
        btn_iso = QPushButton("计算异构体数")
        btn_iso.clicked.connect(self.calc_isomers)
        isomer_layout.addWidget(btn_iso)
        self.isomer_result = QTextEdit()
        self.isomer_result.setReadOnly(True)
        isomer_layout.addWidget(self.isomer_result)
        tabs.addTab(isomer_page, "同分异构体")
    
    def identify_functional(self):
        name = self.org_name.text().lower()
        functional_groups = {
            "醇": ["醇", "乙醇", "甲醇", "丙醇"], "醛": ["醛", "乙醛", "甲醛"],
            "酮": ["酮", "丙酮"], "羧酸": ["酸", "乙酸", "甲酸"], "酯": ["酯", "乙酸乙酯"],
            "醚": ["醚", "乙醚"], "胺": ["胺", "甲胺"], "烯烃": ["烯", "乙烯", "丙烯"],
            "炔烃": ["炔", "乙炔"], "芳香烃": ["苯", "甲苯", "二甲苯"]
        }
        found = []
        for group, keywords in functional_groups.items():
            for kw in keywords:
                if kw in name:
                    found.append(group)
                    break
        if found:
            self.func_result.setText(f"化合物: {name}\n\n可能含有的官能团: {', '.join(set(found))}")
        else:
            self.func_result.setText("未识别出常见官能团")
    
    def calc_isomers(self):
        formula = self.isomer_formula.text().strip()
        isomers = {"C5H12": 3, "C6H14": 5, "C7H16": 9, "C8H18": 18, "C4H10": 2, "C3H8": 1, "C2H6": 1}
        if formula in isomers:
            self.isomer_result.setText(f"分子式 {formula} 的同分异构体数目: {isomers[formula]} 种")
        else:
            self.isomer_result.setText("暂不支持该分子式\n常见烷烃异构体数:\nC₄H₁₀: 2, C₅H₁₂: 3, C₆H₁₄: 5, C₇H₁₆: 9")
    
    # ---------- 溶解度查询 ----------
    def init_solubility(self, parent):
        layout = QVBoxLayout(parent)
        self.sol_tree = QTextEdit()
        self.sol_tree.setReadOnly(True)
        data = "物质\t溶解度 (g/100g水, 20°C)\n"
        common = [("NaCl", 36.0), ("KCl", 34.0), ("KNO3", 31.6), ("NH4Cl", 37.2),
                  ("Ca(OH)2", 0.173), ("AgNO3", 216), ("CuSO4", 20.7), ("NaOH", 109)]
        for sub, sol in common:
            data += f"{sub}\t{sol}\n"
        self.sol_tree.setText(data)
        layout.addWidget(self.sol_tree)
        rules = QLabel("溶解度规则:\n• 碱金属盐大多可溶\n• 硝酸盐全部可溶\n• 氯化物、溴化物、碘化物除Ag⁺、Pb²⁺外可溶\n• 硫酸盐除Ba²⁺、Pb²⁺、Ca²⁺外可溶\n• 碳酸盐、磷酸盐大多不溶")
        rules.setWordWrap(True)
        layout.addWidget(rules)
    
    # ---------- 缓冲溶液计算 ----------
    def init_buffer(self, parent):
        layout = QGridLayout(parent)
        layout.addWidget(QLabel("pKa:"), 0, 0)
        self.pka = QLineEdit()
        layout.addWidget(self.pka, 0, 1)
        layout.addWidget(QLabel("[A⁻] (mol/L):"), 1, 0)
        self.base_conc = QLineEdit()
        layout.addWidget(self.base_conc, 1, 1)
        layout.addWidget(QLabel("[HA] (mol/L):"), 2, 0)
        self.acid_conc = QLineEdit()
        layout.addWidget(self.acid_conc, 2, 1)
        btn = QPushButton("计算pH")
        btn.clicked.connect(self.calc_buffer_ph)
        layout.addWidget(btn, 3, 0, 1, 2)
        self.buffer_result = QTextEdit()
        self.buffer_result.setReadOnly(True)
        layout.addWidget(self.buffer_result, 4, 0, 1, 2)
        layout.setRowStretch(4, 1)
    
    def calc_buffer_ph(self):
        try:
            pka = float(self.pka.text())
            base = float(self.base_conc.text())
            acid = float(self.acid_conc.text())
            ph = pka + log10(base / acid)
            self.buffer_result.setText(f"pH = pKa + log([A⁻]/[HA]) = {pka} + log({base}/{acid}) = {ph:.2f}")
        except:
            self.buffer_result.setText("输入错误")
    
    # ---------- 酸碱滴定计算 ----------
    def init_titration(self, parent):
        layout = QGridLayout(parent)
        layout.addWidget(QLabel("酸浓度 (mol/L):"), 0, 0)
        self.acid_conc_tit = QLineEdit()
        layout.addWidget(self.acid_conc_tit, 0, 1)
        layout.addWidget(QLabel("酸体积 (L):"), 1, 0)
        self.acid_vol_tit = QLineEdit()
        layout.addWidget(self.acid_vol_tit, 1, 1)
        layout.addWidget(QLabel("碱浓度 (mol/L):"), 2, 0)
        self.base_conc_tit = QLineEdit()
        layout.addWidget(self.base_conc_tit, 2, 1)
        btn = QPushButton("计算碱体积")
        btn.clicked.connect(self.calc_titration)
        layout.addWidget(btn, 3, 0, 1, 2)
        self.titration_result = QTextEdit()
        self.titration_result.setReadOnly(True)
        layout.addWidget(self.titration_result, 4, 0, 1, 2)
        layout.setRowStretch(4, 1)
    
    def calc_titration(self):
        try:
            ca = float(self.acid_conc_tit.text())
            va = float(self.acid_vol_tit.text())
            cb = float(self.base_conc_tit.text())
            vb = ca * va / cb
            self.titration_result.setText(f"CaVa = CbVb\n{ca} × {va} = {cb} × Vb\nVb = {vb:.4f} L = {vb*1000:.2f} mL")
        except:
            self.titration_result.setText("输入错误")
    
    # ---------- 光谱分析 ----------
    def init_spectroscopy(self, parent):
        layout = QVBoxLayout(parent)
        layout.addWidget(QLabel("波长 λ (nm):"))
        self.wavelength = QLineEdit()
        layout.addWidget(self.wavelength)
        btn = QPushButton("转换")
        btn.clicked.connect(self.convert_wavelength)
        layout.addWidget(btn)
        self.wave_result = QTextEdit()
        self.wave_result.setReadOnly(True)
        layout.addWidget(self.wave_result)
        colors = [("紫", "400-450"), ("蓝", "450-500"), ("青", "500-550"),
                  ("绿", "550-580"), ("黄", "580-600"), ("橙", "600-650"), ("红", "650-750")]
        for color, wl in colors:
            layout.addWidget(QLabel(f"{color}: {wl} nm"))
    
    def convert_wavelength(self):
        try:
            lam = float(self.wavelength.text()) * 1e-9
            c = 3e8
            h = 6.626e-34
            energy = h * c / lam
            self.wave_result.setText(f"波长: {self.wavelength.text()} nm\n能量: {energy:.2e} J\n能量: {energy/1.602e-19:.2f} eV")
        except:
            self.wave_result.setText("输入错误")
    
    # ---------- 化学动力学 ----------
    def init_kinetics(self, parent):
        layout = QGridLayout(parent)
        layout.addWidget(QLabel("活化能 Ea (J/mol):"), 0, 0)
        self.ea = QLineEdit()
        layout.addWidget(self.ea, 0, 1)
        layout.addWidget(QLabel("温度 T (K):"), 1, 0)
        self.temp_kin = QLineEdit()
        layout.addWidget(self.temp_kin, 1, 1)
        layout.addWidget(QLabel("指前因子 A:"), 2, 0)
        self.a_factor = QLineEdit()
        layout.addWidget(self.a_factor, 2, 1)
        btn = QPushButton("计算速率常数")
        btn.clicked.connect(self.calc_rate_constant)
        layout.addWidget(btn, 3, 0, 1, 2)
        self.kinetics_result = QTextEdit()
        self.kinetics_result.setReadOnly(True)
        layout.addWidget(self.kinetics_result, 4, 0, 1, 2)
        # 半衰期
        layout.addWidget(QLabel("速率常数 k (s⁻¹):"), 5, 0)
        self.k_half = QLineEdit()
        layout.addWidget(self.k_half, 5, 1)
        btn_half = QPushButton("计算半衰期")
        btn_half.clicked.connect(self.calc_half_life)
        layout.addWidget(btn_half, 6, 0, 1, 2)
        self.half_result = QLabel()
        layout.addWidget(self.half_result, 7, 0, 1, 2)
        layout.setRowStretch(4, 1)
    
    def calc_rate_constant(self):
        try:
            ea = float(self.ea.text())
            T = float(self.temp_kin.text())
            A = float(self.a_factor.text())
            R = 8.314
            k = A * np.exp(-ea / (R * T))
            self.kinetics_result.setText(f"k = A·exp(-Ea/RT) = {k:.2e} s⁻¹")
        except:
            self.kinetics_result.setText("输入错误")
    
    def calc_half_life(self):
        try:
            k = float(self.k_half.text())
            t_half = np.log(2) / k
            self.half_result.setText(f"t₁/₂ = {t_half:.2f} s")
        except:
            self.half_result.setText("输入错误")
    
    # ---------- 电化学 ----------
    def init_electrochem(self, parent):
        layout = QGridLayout(parent)
        layout.addWidget(QLabel("标准电势 E° (V):"), 0, 0)
        self.e0 = QLineEdit()
        layout.addWidget(self.e0, 0, 1)
        layout.addWidget(QLabel("温度 T (K):"), 1, 0)
        self.temp_nernst = QLineEdit()
        layout.addWidget(self.temp_nernst, 1, 1)
        layout.addWidget(QLabel("电子转移数 n:"), 2, 0)
        self.n_electron = QLineEdit()
        layout.addWidget(self.n_electron, 2, 1)
        layout.addWidget(QLabel("反应商 Q:"), 3, 0)
        self.q_value = QLineEdit()
        layout.addWidget(self.q_value, 3, 1)
        btn = QPushButton("计算电极电势")
        btn.clicked.connect(self.calc_nernst)
        layout.addWidget(btn, 4, 0, 1, 2)
        self.nernst_result = QTextEdit()
        self.nernst_result.setReadOnly(True)
        layout.addWidget(self.nernst_result, 5, 0, 1, 2)
        layout.setRowStretch(5, 1)
    
    def calc_nernst(self):
        try:
            e0 = float(self.e0.text())
            T = float(self.temp_nernst.text())
            n = float(self.n_electron.text())
            Q = float(self.q_value.text())
            R = 8.314
            F = 96485
            E = e0 - (R * T / (n * F)) * np.log(Q)
            self.nernst_result.setText(f"E = E° - (RT/nF) lnQ = {E:.4f} V")
        except:
            self.nernst_result.setText("输入错误")
    
    # ---------- 化学平衡 ----------
    def init_equilibrium(self, parent):
        layout = QGridLayout(parent)
        layout.addWidget(QLabel("温度 T (K):"), 0, 0)
        self.temp_eq = QLineEdit()
        layout.addWidget(self.temp_eq, 0, 1)
        layout.addWidget(QLabel("平衡常数 K:"), 1, 0)
        self.k_eq = QLineEdit()
        layout.addWidget(self.k_eq, 1, 1)
        btn = QPushButton("计算 ΔG°")
        btn.clicked.connect(self.calc_deltaG)
        layout.addWidget(btn, 2, 0, 1, 2)
        self.eq_result = QTextEdit()
        self.eq_result.setReadOnly(True)
        layout.addWidget(self.eq_result, 3, 0, 1, 2)
        layout.setRowStretch(3, 1)
    
    def calc_deltaG(self):
        try:
            T = float(self.temp_eq.text())
            K = float(self.k_eq.text())
            R = 8.314
            dG = -R * T * np.log(K)
            self.eq_result.setText(f"ΔG° = -RT lnK = {dG:.2f} J/mol = {dG/1000:.2f} kJ/mol")
        except:
            self.eq_result.setText("输入错误")
    
    # ---------- 热力学计算 ----------
    def init_thermodynamics(self, parent):
        layout = QGridLayout(parent)
        layout.addWidget(QLabel("ΔH (kJ/mol):"), 0, 0)
        self.dh_thermo = QLineEdit()
        layout.addWidget(self.dh_thermo, 0, 1)
        layout.addWidget(QLabel("ΔS (J/(mol·K)):"), 1, 0)
        self.ds_thermo = QLineEdit()
        layout.addWidget(self.ds_thermo, 1, 1)
        layout.addWidget(QLabel("温度 T (K):"), 2, 0)
        self.temp_thermo = QLineEdit()
        layout.addWidget(self.temp_thermo, 2, 1)
        btn = QPushButton("计算 ΔG")
        btn.clicked.connect(self.calc_gibbs)
        layout.addWidget(btn, 3, 0, 1, 2)
        self.thermo_result = QTextEdit()
        self.thermo_result.setReadOnly(True)
        layout.addWidget(self.thermo_result, 4, 0, 1, 2)
        layout.setRowStretch(4, 1)
    
    def calc_gibbs(self):
        try:
            H = float(self.dh_thermo.text()) * 1000
            S = float(self.ds_thermo.text())
            T = float(self.temp_thermo.text())
            G = H - T * S
            self.thermo_result.setText(f"ΔG = ΔH - TΔS = {H/1000:.2f} kJ - {T} × {S:.2f} J/K = {G/1000:.2f} kJ/mol")
        except:
            self.thermo_result.setText("输入错误")
    
    # ---------- 气体分压 ----------
    def init_partial_pressure(self, parent):
        layout = QGridLayout(parent)
        layout.addWidget(QLabel("总压 (atm):"), 0, 0)
        self.total_p = QLineEdit()
        layout.addWidget(self.total_p, 0, 1)
        layout.addWidget(QLabel("组分1摩尔分数:"), 1, 0)
        self.mole_frac1 = QLineEdit()
        layout.addWidget(self.mole_frac1, 1, 1)
        layout.addWidget(QLabel("组分2摩尔分数:"), 2, 0)
        self.mole_frac2 = QLineEdit()
        layout.addWidget(self.mole_frac2, 2, 1)
        btn = QPushButton("计算分压")
        btn.clicked.connect(self.calc_partial_pressure)
        layout.addWidget(btn, 3, 0, 1, 2)
        self.partial_result = QTextEdit()
        self.partial_result.setReadOnly(True)
        layout.addWidget(self.partial_result, 4, 0, 1, 2)
        layout.setRowStretch(4, 1)
    
    def calc_partial_pressure(self):
        try:
            P = float(self.total_p.text())
            x1 = float(self.mole_frac1.text()) if self.mole_frac1.text() else 0
            x2 = float(self.mole_frac2.text()) if self.mole_frac2.text() else 0
            p1 = P * x1
            p2 = P * x2
            self.partial_result.setText(f"组分1分压: {p1:.4f} atm\n组分2分压: {p2:.4f} atm\n总和: {p1+p2:.4f} atm")
        except:
            self.partial_result.setText("输入错误")
    
    # ---------- 核化学 ----------
    def init_nuclear(self, parent):
        layout = QGridLayout(parent)
        layout.addWidget(QLabel("半衰期 t₁/₂ (s):"), 0, 0)
        self.half_life = QLineEdit()
        layout.addWidget(self.half_life, 0, 1)
        layout.addWidget(QLabel("初始原子数 N₀:"), 1, 0)
        self.n0 = QLineEdit()
        layout.addWidget(self.n0, 1, 1)
        layout.addWidget(QLabel("经过时间 t (s):"), 2, 0)
        self.time_nuclear = QLineEdit()
        layout.addWidget(self.time_nuclear, 2, 1)
        btn = QPushButton("计算剩余原子数")
        btn.clicked.connect(self.calc_nuclear)
        layout.addWidget(btn, 3, 0, 1, 2)
        self.nuclear_result = QTextEdit()
        self.nuclear_result.setReadOnly(True)
        layout.addWidget(self.nuclear_result, 4, 0, 1, 2)
        layout.setRowStretch(4, 1)
    
    def calc_nuclear(self):
        try:
            t12 = float(self.half_life.text())
            N0 = float(self.n0.text())
            t = float(self.time_nuclear.text())
            lam = np.log(2) / t12
            N = N0 * np.exp(-lam * t)
            self.nuclear_result.setText(f"衰变常数 λ = {lam:.4e} s⁻¹\n剩余原子数 N = {N:.2f}")
        except:
            self.nuclear_result.setText("输入错误")
    
    # ---------- 溶液配制 ----------
    def init_solution_prep(self, parent):
        layout = QGridLayout(parent)
        layout.addWidget(QLabel("目标浓度 C (mol/L):"), 0, 0)
        self.target_c = QLineEdit()
        layout.addWidget(self.target_c, 0, 1)
        layout.addWidget(QLabel("目标体积 V (L):"), 1, 0)
        self.target_v = QLineEdit()
        layout.addWidget(self.target_v, 1, 1)
        layout.addWidget(QLabel("溶质摩尔质量 M (g/mol):"), 2, 0)
        self.solute_m = QLineEdit()
        layout.addWidget(self.solute_m, 2, 1)
        btn = QPushButton("计算所需溶质质量")
        btn.clicked.connect(self.calc_solution_prep)
        layout.addWidget(btn, 3, 0, 1, 2)
        self.prep_result = QTextEdit()
        self.prep_result.setReadOnly(True)
        layout.addWidget(self.prep_result, 4, 0, 1, 2)
        layout.setRowStretch(4, 1)
    
    def calc_solution_prep(self):
        try:
            C = float(self.target_c.text())
            V = float(self.target_v.text())
            M = float(self.solute_m.text())
            mass = C * V * M
            self.prep_result.setText(f"所需溶质质量 = C × V × M = {C} × {V} × {M} = {mass:.4f} g")
        except:
            self.prep_result.setText("输入错误")
    
    # ---------- 关于和帮助页面 ----------
    def init_about_page(self):
        layout = QVBoxLayout(self.about_page)
        text = QTextEdit()
        text.setReadOnly(True)
        about_text = """化学工具箱 v2.1

版本: 2.1
更新日期: 2025年5月8日

本版本使用PyQt5进行界面美化，所有功能与2.0保持一致。

主要功能：
- 化学方程式配平（支持离子方程式）
- 元素周期表（118种元素，含电负性）
- 计算功能（摩尔质量、浓度、稀释、比例、元素百分比、经验式、浓度换算、产率）
- 实用功能（pH、气体定律、热化学、氧化还原、有机化学、溶解度、缓冲溶液、滴定、光谱、动力学、电化学、平衡、热力学、分压、核化学、溶液配制）

开发者: 化学爱好者
开源协议: MIT License

感谢使用！"""
        text.setText(about_text)
        layout.addWidget(text)
    
    def init_help_page(self):
        layout = QVBoxLayout(self.help_page)
        text = QTextEdit()
        text.setReadOnly(True)
        help_text = """化学工具箱 v2.1 帮助

快速入门：
1. 点击工具栏按钮选择功能
2. 在输入框中输入数据
3. 点击相应的计算按钮

离子方程式格式：
- 阳离子：* 表示，如 H* 表示 H⁺，Ca** 表示 Ca²⁺
- 阴离子：^ 表示，如 HCO3^ 表示 HCO₃⁻，SO4^^ 表示 SO₄²⁻
- 示例：HCO3^+H*=CO2+H2O

提示：
- 氯的相对原子质量为35.5
- 温度使用开尔文(K)单位
- 浓度单位使用mol/L

所有计算均支持实时输入，请确保数据有效。"""
        text.setText(help_text)
        layout.addWidget(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChemistryToolbox()
    window.show()
    sys.exit(app.exec_())