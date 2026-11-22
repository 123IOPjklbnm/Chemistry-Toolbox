# -*- coding: utf-8 -*-
# 化学工具箱 v5.0
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog, colorchooser, simpledialog
import tkinter.font as tkfont
import re
import json
import sys
import subprocess
from collections import defaultdict
import numpy as np
from math import gcd, log10, sin, cos, tan, log, sqrt, pow
import datetime
import webbrowser
import os
import importlib.util
import time
import threading
import queue
import inspect

try:
    import openpyxl
    from openpyxl.styles import Font as XLFont, PatternFill as XLFill, Alignment as XLAlignment
    from openpyxl.chart import BarChart, LineChart, PieChart, Reference
    from openpyxl.chart.marker import DataPoint
    from openpyxl.chart.series import SeriesLabel
    from openpyxl.utils.datetime import from_excel
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False
    XLFont = None
    XLFill = None
    XLAlignment = None
    SeriesLabel = None

try:
    import xlrd
    HAS_XLRD = True
except ImportError:
    HAS_XLRD = False


# ==================== 主题配色 ====================
MODERN_COLORS = {
    'primary':        '#0F6CBD',
    'primary_hover':  '#1976D2',
    'primary_active': '#0A4A8A',
    'primary_light':  '#E3F2FD',
    'success':        '#107C10',
    'danger':         '#C42B1C',
    'warning':        '#E6A700',
    'bg':             '#F3F3F3',
    'surface':        '#FFFFFF',
    'sidebar':        '#1E1E2E',
    'sidebar_hover':  '#2A2A3E',
    'sidebar_text':   '#CDD6F4',
    'sidebar_text_dim': '#8A8AA0',
    'text':           '#1F1F1F',
    'text_light':     '#616161',
    'text_muted':     '#8A8A8A',
    'border':         '#E0E0E0',
    'hover_bg':       '#F5F5F5',
    'logo_green':     '#8BC34A',
    'logo_blue':      '#00A8F3',
    'excel_sel':      '#D9E8F5',
    'excel_sel_border':'#217346',
    'excel_fill_preview': '#888888',
    'card_bg':        '#FAFBFC',
    'card_hover':     '#F0F4F9',
}

DEFAULT_FONT = ("Microsoft YaHei", 10)
TITLE_FONT = ("Microsoft YaHei", 12, "bold")
H1_FONT = ("Microsoft YaHei", 16, "bold")
MONO_FONT = ("Consolas", 11)

# 内置的文本填充序列
TEXT_SEQUENCES = [
    ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"],
    ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"],
    ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
    ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"],
    ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"],
    ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"],
]

# 图表配色
CHART_COLORS = [
    '#0F6CBD', '#FF8C00', '#107C10', '#E6A700', '#8A2BE2', 
    '#00BFFF', '#FF1493', '#FFD700', '#32CD32', '#8B4513'
]

# ==================== 中文编程模板 ====================
CODE_TEMPLATE = '''注释：化学工具箱 5.0 中文编程示例
打印 ("你好，化学工具箱")

注释：获取输入示例
打印 ("请输入你的名字：")
获取输入() 赋值给 名字
打印 ("你好，" + 名字 + "！")

注释：类型转换示例
打印 ("请输入一个整数或小数：")
获取输入() 赋值给 输入串
变成整数(输入串) 赋值给 整数
打印 ("你输入的内容被转为整数的结果是：" + 变成字符串(整数))
打印 ("它的平方是：" + 变成字符串(整数 * 整数))

变成小数(输入串) 赋值给 小数
打印 ("转为小数的 2 倍是：" + 变成字符串(小数 * 2))

导入 时间 模块
打印 ("开始倒计时...")
使用 时间 模块的 睡眠 功能（1）
打印 ("1秒后...")
使用 时间 模块的 睡眠 功能（时间2）
打印 ("又过了2秒...")

当前时间() 赋值给 现在
格式化时间(现在) 赋值给 结果
打印 ("当前时间是：" + 结果)

定义函数 名为 求平方，参数为 数 的函数：
    数 * 数 赋值给 平方值
    返回 平方值

打印 (求平方(5))
打印 (求平方(2 + 3))
'''

_HIGHLIGHT_KEYWORDS = [
    '赋值给', '定义函数', '否则如果', '的范围内', '的函数',
    '参数为', '注释', '打印', '执行', '如果', '否则',
    '名为', '返回', '步长', '当',
    '导入', '模块', '作为', '的名称', '使用', '模块的', '功能',
    '获取输入', '变成整数', '变成小数', '变成字符串',
]


# ==================== 圆角按钮 ====================
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None,
                 width=140, height=42, radius=8,
                 bg=None, fg='#FFFFFF', hover_bg=None,
                 font=None, parent_bg=None,
                 outline='', align='center', **kwargs):
        if parent_bg is None:
            try:
                parent_bg = parent.cget('bg')
            except Exception:
                parent_bg = MODERN_COLORS['bg']
        kwargs.pop('anchor', None)
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bd=0, bg=parent_bg, **kwargs)
        self._text = text
        self._command = command
        self._radius = radius
        self._bg_color = bg or MODERN_COLORS['primary']
        self._fg_color = fg
        self._hover_bg = hover_bg or self._lighten(self._bg_color, 0.18)
        self._font = font or DEFAULT_FONT
        self._btn_w = width
        self._btn_h = height
        self._outline = outline
        self._align = align
        self._state = 'normal'
        self._draw(hover=False)
        self.configure(cursor='hand2')
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
               x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
               x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.create_polygon(pts, smooth=True, **kw)

    def _draw(self, hover):
        self.delete('all')
        if self._state == 'disabled':
            bg = MODERN_COLORS['border']
            fg = MODERN_COLORS['text_muted']
        else:
            bg = self._hover_bg if hover else self._bg_color
            fg = self._fg_color
        self._round_rect(1, 1, self._btn_w - 1, self._btn_h - 1,
                         self._radius, fill=bg, outline=self._outline)
        if self._align == 'left':
            self.create_text(18, self._btn_h / 2, text=self._text,
                             fill=fg, font=self._font, anchor='w')
        else:
            self.create_text(self._btn_w / 2, self._btn_h / 2,
                             text=self._text, fill=fg, font=self._font)

    @staticmethod
    def _lighten(hex_color, factor=0.2):
        hex_color = hex_color.lstrip('#')
        try:
            r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        except Exception:
            return hex_color
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f'#{r:02x}{g:02x}{b:02x}'

    def _on_click(self, _e):
        if self._state == 'disabled':
            return
        if self._command:
            self._command()

    def _on_enter(self, _e):
        if self._state == 'disabled':
            return
        self._draw(hover=True)

    def _on_leave(self, _e):
        if self._state == 'disabled':
            return
        self._draw(hover=False)

    def set_text(self, text):
        self._text = text
        self._draw(hover=False)

    def set_state(self, state):
        self._state = state
        self.configure(cursor='arrow' if state == 'disabled' else 'hand2')
        self._draw(hover=False)


# ==================== 现代输入框 ====================
class ModernEntry(tk.Frame):
    def __init__(self, parent, width=30, font=None, parent_bg=None, **kwargs):
        if parent_bg is None:
            try:
                parent_bg = parent.cget('bg')
            except Exception:
                parent_bg = MODERN_COLORS['surface']
        super().__init__(parent, bg=parent_bg, highlightthickness=0, bd=0)
        self._border = tk.Frame(self, bg=MODERN_COLORS['border'],
                                highlightthickness=0, bd=0)
        self._border.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.entry = tk.Entry(self._border, font=font or DEFAULT_FONT,
                              relief=tk.FLAT, bd=0,
                              bg=MODERN_COLORS['surface'],
                              fg=MODERN_COLORS['text'],
                              insertbackground=MODERN_COLORS['primary'],
                              highlightthickness=0, width=width, **kwargs)
        self.entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=7)
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)

    def _on_focus_in(self, _e):
        self._border.config(bg=MODERN_COLORS['primary'])

    def _on_focus_out(self, _e):
        self._border.config(bg=MODERN_COLORS['border'])

    def get(self):
        return self.entry.get()

    def delete(self, *a):
        return self.entry.delete(*a)

    def insert(self, *a):
        return self.entry.insert(*a)

    def bind(self, *a, **kw):
        return self.entry.bind(*a, **kw)

    def config(self, **kw):
        if 'state' in kw:
            self.entry.config(state=kw.pop('state'))
        if kw:
            self.entry.config(**kw)


# ==================== 像素 Logo ====================
def draw_pixel_logo(parent, bg_color, pixel=5):
    C = ["01110", "10000", "10000", "10000", "01110"]
    T = ["11111", "00100", "00100", "00100", "00100"]
    B = ["11110", "10001", "11110", "10001", "11110"]
    width = 17 * pixel
    height = 5 * pixel
    canvas = tk.Canvas(parent, bg=bg_color, highlightthickness=0, bd=0,
                       width=width, height=height)
    canvas.pack()

    def draw(pat, x0, color):
        for r, row in enumerate(pat):
            for c, ch in enumerate(row):
                if ch == '1':
                    x1 = x0 + c * pixel
                    y1 = r * pixel
                    canvas.create_rectangle(x1, y1, x1 + pixel, y1 + pixel,
                                            fill=color, outline='')

    draw(C, 0, MODERN_COLORS['logo_green'])
    draw(T, 6 * pixel, MODERN_COLORS['logo_green'])
    draw(B, 12 * pixel, MODERN_COLORS['logo_blue'])
    return canvas


# ==================== ttk 主题 ====================
def configure_ttk_theme(root):
    try:
        style = ttk.Style(root)
        if 'clam' in style.theme_names():
            style.theme_use('clam')
    except Exception:
        return
    try:
        style.configure('TNotebook', background=MODERN_COLORS['surface'],
                        borderwidth=0, tabmargins=[2, 8, 2, 0])
        style.configure('TNotebook.Tab', background=MODERN_COLORS['bg'],
                        foreground=MODERN_COLORS['text_light'],
                        padding=[12, 6], font=DEFAULT_FONT, borderwidth=0)
        style.map('TNotebook.Tab',
                  background=[('selected', MODERN_COLORS['surface']),
                              ('active', MODERN_COLORS['hover_bg'])],
                  foreground=[('selected', MODERN_COLORS['primary']),
                              ('active', MODERN_COLORS['text'])])
    except Exception:
        pass


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


# ==================== 相对原子质量 ====================
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


# ==================== 化学式解析 ====================
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
                    bracket_content = formula_part[bracket_start + 1:i - 1]
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
        if len(counts) == 1:
            element = list(counts.keys())[0]
            return {element: 0}
        element_valence = {}

        def get_en(e):
            en = {'F': 4.0, 'O': 3.5, 'Cl': 3.2, 'N': 3.0, 'Br': 3.0,
                  'S': 2.6, 'C': 2.6, 'P': 2.2, 'H': 2.2, 'B': 2.0}
            return en.get(e, 2.5)

        elements = list(counts.keys())
        elements.sort(key=get_en, reverse=True)
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
        match = re.search(r'\^(\d+)([+-])$', compound)
        if match:
            num = int(match.group(1))
            sign = match.group(2)
            charge = num if sign == '+' else -num
            formula = compound[:match.start()]
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
                i = 0
                n = len(side)
                current = ""
                while i < n:
                    c = side[i]
                    if c == '+':
                        if re.search(r'\^\d+$', current):
                            current += c
                            i += 1
                        else:
                            if current:
                                f, ch = EquationBalancer.parse_compound_with_charge(current)
                                compounds.append((f, ch))
                            current = ""
                            i += 1
                    else:
                        current += c
                        i += 1
                if current:
                    f, ch = EquationBalancer.parse_compound_with_charge(current)
                    compounds.append((f, ch))
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
                charge_row = [c for _, c in left_comp_data] + [-c for _, c in right_comp_data]
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
                        formatted += f"^{charge}+"
                    elif charge < 0:
                        formatted += f"^{abs(charge)}-"
                    left_parts.append(formatted)

                right_parts = []
                for i, (formula, charge) in enumerate(right_compounds):
                    coeff = best_solution[n_left + i] if (n_left + i) < len(best_solution) else 1
                    formatted = f"{coeff if coeff > 1 else ''}{formula}"
                    if charge > 0:
                        formatted += f"^{charge}+"
                    elif charge < 0:
                        formatted += f"^{abs(charge)}-"
                    right_parts.append(formatted)

                balanced_eq = f"{' + '.join(left_parts)} = {' + '.join(right_parts)}"
                valence_info = {}
                for idx, (formula, _) in enumerate(left_compounds):
                    valence_info[f'L{idx}'] = ChemicalFormulaParser.calculate_oxidation_states(formula)
                for idx, (formula, _) in enumerate(right_compounds):
                    valence_info[f'R{idx}'] = ChemicalFormulaParser.calculate_oxidation_states(formula)
                return balanced_eq, valence_info

            return "错误：无法配平该方程式，请检查输入格式", {}
        except Exception as e:
            return f"配平失败: {str(e)}", {}


# ==================== 元素数据 ====================
class ExtendedPeriodicTable:
    electron_config = {
        "H": "1", "He": "2", "Li": "2,1", "Be": "2,2", "B": "2,3", "C": "2,4", "N": "2,5", "O": "2,6", "F": "2,7", "Ne": "2,8",
        "Na": "2,8,1", "Mg": "2,8,2", "Al": "2,8,3", "Si": "2,8,4", "P": "2,8,5", "S": "2,8,6", "Cl": "2,8,7", "Ar": "2,8,8",
        "K": "2,8,8,1", "Ca": "2,8,8,2", "Sc": "2,8,9,2", "Ti": "2,8,10,2", "V": "2,8,11,2",
        "Cr": "2,8,13,1", "Mn": "2,8,13,2", "Fe": "2,8,14,2", "Co": "2,8,15,2", "Ni": "2,8,16,2",
        "Cu": "2,8,18,1", "Zn": "2,8,18,2", "Ga": "2,8,18,3", "Ge": "2,8,18,4", "As": "2,8,18,5",
        "Se": "2,8,18,6", "Br": "2,8,18,7", "Kr": "2,8,18,8", "Rb": "2,8,18,8,1", "Sr": "2,8,18,8,2",
        "Y": "2,8,18,9,2", "Zr": "2,8,18,10,2", "Nb": "2,8,18,12,1", "Mo": "2,8,18,13,1",
        "Tc": "2,8,18,13,2", "Ru": "2,8,18,15,1", "Rh": "2,8,18,16,1", "Pd": "2,8,18,18",
        "Ag": "2,8,18,18,1", "Cd": "2,8,18,18,2", "In": "2,8,18,18,3", "Sn": "2,8,18,18,4",
        "Sb": "2,8,18,18,5", "Te": "2,8,18,18,6", "I": "2,8,18,18,7", "Xe": "2,8,18,18,8",
        "Cs": "2,8,18,18,8,1", "Ba": "2,8,18,18,8,2", "La": "2,8,18,18,9,2",
        "Ce": "2,8,18,19,9,2", "Pr": "2,8,18,21,8,2", "Nd": "2,8,18,22,8,2",
        "Pm": "2,8,18,23,8,2", "Sm": "2,8,18,24,8,2", "Eu": "2,8,18,25,8,2",
        "Gd": "2,8,18,25,9,2", "Tb": "2,8,18,27,8,2", "Dy": "2,8,18,28,8,2",
        "Ho": "2,8,18,29,8,2", "Er": "2,8,18,30,8,2", "Tm": "2,8,18,31,8,2",
        "Yb": "2,8,18,32,8,2", "Lu": "2,8,18,32,9,2", "Hf": "2,8,18,32,10,2",
        "Ta": "2,8,18,32,11,2", "W": "2,8,18,32,12,2", "Re": "2,8,18,32,13,2",
        "Os": "2,8,18,32,14,2", "Ir": "2,8,18,32,15,2", "Pt": "2,8,18,32,17,1",
        "Au": "2,8,18,32,18,1", "Hg": "2,8,18,32,18,2", "Tl": "2,8,18,32,18,3",
        "Pb": "2,8,18,32,18,4", "Bi": "2,8,18,32,18,5", "Po": "2,8,18,32,18,6",
        "At": "2,8,18,32,18,7", "Rn": "2,8,18,32,18,8", "Fr": "2,8,18,32,18,8,1",
        "Ra": "2,8,18,32,18,8,2", "Ac": "2,8,18,32,18,9,2", "Th": "2,8,18,32,18,10,2",
        "Pa": "2,8,18,32,20,9,2", "U": "2,8,18,32,21,9,2", "Np": "2,8,18,32,22,9,2",
        "Pu": "2,8,18,32,24,8,2", "Am": "2,8,18,32,25,8,2",
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
    _ELEMENTS_RAW = [
        ("H","氢",1,1.008,1,1,"1s¹","最轻的元素"),("He","氦",2,4.0026,18,1,"1s²","稀有气体"),
        ("Li","锂",3,6.94,1,2,"[He] 2s¹","最轻的金属"),("Be","铍",4,9.0122,2,2,"[He] 2s²","轻金属，有毒"),
        ("B","硼",5,10.81,13,2,"[He] 2s² 2p¹","类金属"),("C","碳",6,12.011,14,2,"[He] 2s² 2p²","生命的基础"),
        ("N","氮",7,14.007,15,2,"[He] 2s² 2p³","大气主要成分"),("O","氧",8,15.999,16,2,"[He] 2s² 2p⁴","生命必需"),
        ("F","氟",9,18.998,17,2,"[He] 2s² 2p⁵","最活泼的非金属"),("Ne","氖",10,20.18,18,2,"[He] 2s² 2p⁶","稀有气体"),
        ("Na","钠",11,22.99,1,3,"[Ne] 3s¹","碱金属"),("Mg","镁",12,24.305,2,3,"[Ne] 3s²","轻金属"),
        ("Al","铝",13,26.982,13,3,"[Ne] 3s² 3p¹","含量最丰富的金属"),("Si","硅",14,28.086,14,3,"[Ne] 3s² 3p²","半导体材料"),
        ("P","磷",15,30.974,15,3,"[Ne] 3s² 3p³","白磷易燃"),("S","硫",16,32.06,16,3,"[Ne] 3s² 3p⁴","黄色固体"),
        ("Cl","氯",17,35.45,17,3,"[Ne] 3s² 3p⁵","黄绿色气体"),("Ar","氩",18,39.95,18,3,"[Ne] 3s² 3p⁶","稀有气体"),
        ("K","钾",19,39.098,1,4,"[Ar] 4s¹","活泼金属"),("Ca","钙",20,40.078,2,4,"[Ar] 4s²","骨骼主要成分"),
        ("Sc","钪",21,44.956,3,4,"[Ar] 3d¹ 4s²","稀土元素"),("Ti","钛",22,47.867,4,4,"[Ar] 3d² 4s²","高强度轻金属"),
        ("V","钒",23,50.942,5,4,"[Ar] 3d³ 4s²","钢铁添加剂"),("Cr","铬",24,51.996,6,4,"[Ar] 3d⁵ 4s¹","不锈钢成分"),
        ("Mn","锰",25,54.938,7,4,"[Ar] 3d⁵ 4s²","钢铁重要元素"),("Fe","铁",26,55.845,8,4,"[Ar] 3d⁶ 4s²","最常用的金属"),
        ("Co","钴",27,58.933,9,4,"[Ar] 3d⁷ 4s²","磁性材料"),("Ni","镍",28,58.693,10,4,"[Ar] 3d⁸ 4s²","不锈钢成分"),
        ("Cu","铜",29,63.546,11,4,"[Ar] 3d¹⁰ 4s¹","导电性好"),("Zn","锌",30,65.38,12,4,"[Ar] 3d¹⁰ 4s²","防腐镀层"),
        ("Ga","镓",31,69.723,13,4,"[Ar] 3d¹⁰ 4s² 4p¹","低熔点金属"),("Ge","锗",32,72.63,14,4,"[Ar] 3d¹⁰ 4s² 4p²","半导体材料"),
        ("As","砷",33,74.922,15,4,"[Ar] 3d¹⁰ 4s² 4p³","有毒类金属"),("Se","硒",34,78.96,16,4,"[Ar] 3d¹⁰ 4s² 4p⁴","光导材料"),
        ("Br","溴",35,79.904,17,4,"[Ar] 3d¹⁰ 4s² 4p⁵","红棕色液体"),("Kr","氪",36,83.798,18,4,"[Ar] 3d¹⁰ 4s² 4p⁶","稀有气体"),
        ("Rb","铷",37,85.468,1,5,"[Kr] 5s¹","活泼碱金属"),("Sr","锶",38,87.62,2,5,"[Kr] 5s²","用于烟花"),
        ("Y","钇",39,88.906,3,5,"[Kr] 4d¹ 5s²","稀土元素"),("Zr","锆",40,91.224,4,5,"[Kr] 4d² 5s²","耐腐蚀金属"),
        ("Nb","铌",41,92.906,5,5,"[Kr] 4d⁴ 5s¹","超导材料"),("Mo","钼",42,95.95,6,5,"[Kr] 4d⁵ 5s¹","钢铁添加剂"),
        ("Tc","锝",43,98,7,5,"[Kr] 4d⁵ 5s²","放射性元素"),("Ru","钌",44,101.07,8,5,"[Kr] 4d⁷ 5s¹","铂族金属"),
        ("Rh","铑",45,102.91,9,5,"[Kr] 4d⁸ 5s¹","催化剂"),("Pd","钯",46,106.42,10,5,"[Kr] 4d¹⁰","催化剂"),
        ("Ag","银",47,107.87,11,5,"[Kr] 4d¹⁰ 5s¹","导电性最佳"),("Cd","镉",48,112.41,12,5,"[Kr] 4d¹⁰ 5s²","有毒重金属"),
        ("In","铟",49,114.82,13,5,"[Kr] 4d¹⁰ 5s² 5p¹","用于液晶屏"),("Sn","锡",50,118.71,14,5,"[Kr] 4d¹⁰ 5s² 5p²","青铜成分"),
        ("Sb","锑",51,121.76,15,5,"[Kr] 4d¹⁰ 5s² 5p³","阻燃剂"),("Te","碲",52,127.6,16,5,"[Kr] 4d¹⁰ 5s² 5p⁴","半导体材料"),
        ("I","碘",53,126.90,17,5,"[Kr] 4d¹⁰ 5s² 5p⁵","消毒剂"),("Xe","氙",54,131.29,18,5,"[Kr] 4d¹⁰ 5s² 5p⁶","稀有气体"),
        ("Cs","铯",55,132.91,1,6,"[Xe] 6s¹","最活泼金属"),("Ba","钡",56,137.33,2,6,"[Xe] 6s²","用于X光造影"),
        ("La","镧",57,138.91,3,6,"[Xe] 5d¹ 6s²","稀土元素"),("Ce","铈",58,140.12,3,6,"[Xe] 4f¹ 5d¹ 6s²","稀土元素"),
        ("Pr","镨",59,140.91,3,6,"[Xe] 4f³ 6s²","稀土元素"),("Nd","钕",60,144.24,3,6,"[Xe] 4f⁴ 6s²","用于永磁体"),
        ("Pm","钷",61,145,3,6,"[Xe] 4f⁵ 6s²","放射性稀土"),("Sm","钐",62,150.36,3,6,"[Xe] 4f⁶ 6s²","稀土元素"),
        ("Eu","铕",63,151.96,3,6,"[Xe] 4f⁷ 6s²","用于荧光粉"),("Gd","钆",64,157.25,3,6,"[Xe] 4f⁷ 5d¹ 6s²","核反应堆控制棒"),
        ("Tb","铽",65,158.93,3,6,"[Xe] 4f⁹ 6s²","稀土元素"),("Dy","镝",66,162.50,3,6,"[Xe] 4f¹⁰ 6s²","稀土元素"),
        ("Ho","钬",67,164.93,3,6,"[Xe] 4f¹¹ 6s²","稀土元素"),("Er","铒",68,167.26,3,6,"[Xe] 4f¹² 6s²","稀土元素"),
        ("Tm","铥",69,168.93,3,6,"[Xe] 4f¹³ 6s²","稀土元素"),("Yb","镱",70,173.05,3,6,"[Xe] 4f¹⁴ 6s²","稀土元素"),
        ("Lu","镥",71,174.97,3,6,"[Xe] 4f¹⁴ 5d¹ 6s²","稀土元素"),("Hf","铪",72,178.49,4,6,"[Xe] 4f¹⁴ 5d² 6s²","耐热合金"),
        ("Ta","钽",73,180.95,5,6,"[Xe] 4f¹⁴ 5d³ 6s²","耐腐蚀金属"),("W","钨",74,183.84,6,6,"[Xe] 4f¹⁴ 5d⁴ 6s²","熔点最高"),
        ("Re","铼",75,186.21,7,6,"[Xe] 4f¹⁴ 5d⁵ 6s²","高熔点金属"),("Os","锇",76,190.23,8,6,"[Xe] 4f¹⁴ 5d⁶ 6s²","密度最大"),
        ("Ir","铱",77,192.22,9,6,"[Xe] 4f¹⁴ 5d⁷ 6s²","耐腐蚀"),("Pt","铂",78,195.08,10,6,"[Xe] 4f¹⁴ 5d⁹ 6s¹","贵金属"),
        ("Au","金",79,196.97,11,6,"[Xe] 4f¹⁴ 5d¹⁰ 6s¹","延展性好"),("Hg","汞",80,200.59,12,6,"[Xe] 4f¹⁴ 5d¹⁰ 6s²","液态金属"),
        ("Tl","铊",81,204.38,13,6,"[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p¹","剧毒"),("Pb","铅",82,207.2,14,6,"[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p²","重金属"),
        ("Bi","铋",83,208.98,15,6,"[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p³","低熔点金属"),("Po","钋",84,209,16,6,"[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁴","放射性"),
        ("At","砹",85,210,17,6,"[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁵","放射性"),("Rn","氡",86,222,18,6,"[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁶","放射性气体"),
        ("Fr","钫",87,223,1,7,"[Rn] 7s¹","放射性碱金属"),("Ra","镭",88,226,2,7,"[Rn] 7s²","放射性"),
        ("Ac","锕",89,227,3,7,"[Rn] 6d¹ 7s²","放射性"),("Th","钍",90,232.04,3,7,"[Rn] 6d² 7s²","核燃料"),
        ("Pa","镤",91,231.04,3,7,"[Rn] 5f² 6d¹ 7s²","放射性"),("U","铀",92,238.03,3,7,"[Rn] 5f³ 6d¹ 7s²","核燃料"),
        ("Np","镎",93,237,3,7,"[Rn] 5f⁴ 6d¹ 7s²","放射性"),("Pu","钚",94,244,3,7,"[Rn] 5f⁶ 7s²","核武器原料"),
        ("Am","镅",95,243,3,7,"[Rn] 5f⁷ 7s²","烟雾探测器"),("Cm","锔",96,247,3,7,"[Rn] 5f⁷ 6d¹ 7s²","放射性"),
        ("Bk","锫",97,247,3,7,"[Rn] 5f⁹ 7s²","人工合成"),("Cf","锎",98,251,3,7,"[Rn] 5f¹⁰ 7s²","中子源"),
        ("Es","锿",99,252,3,7,"[Rn] 5f¹¹ 7s²","人工合成"),("Fm","镄",100,257,3,7,"[Rn] 5f¹² 7s²","人工合成"),
        ("Md","钔",101,258,3,7,"[Rn] 5f¹³ 7s²","人工合成"),("No","锘",102,259,3,7,"[Rn] 5f¹⁴ 7s²","人工合成"),
        ("Lr","铹",103,262,3,7,"[Rn] 5f¹⁴ 6d¹ 7s²","人工合成"),("Rf","𬬻",104,267,4,7,"[Rn] 5f¹⁴ 6d² 7s²","人工合成"),
        ("Db","𬭊",105,268,5,7,"[Rn] 5f¹⁴ 6d³ 7s²","人工合成"),("Sg","𬭳",106,269,6,7,"[Rn] 5f¹⁴ 6d⁴ 7s²","人工合成"),
        ("Bh","𬭛",107,270,7,7,"[Rn] 5f¹⁴ 6d⁵ 7s²","人工合成"),("Hs","𬭶",108,269,8,7,"[Rn] 5f¹⁴ 6d⁶ 7s²","人工合成"),
        ("Mt","鿏",109,278,9,7,"[Rn] 5f¹⁴ 6d⁷ 7s²","人工合成"),("Ds","𫟼",110,281,10,7,"[Rn] 5f¹⁴ 6d⁸ 7s²","人工合成"),
        ("Rg","𬬭",111,282,11,7,"[Rn] 5f¹⁴ 6d⁹ 7s²","人工合成"),("Cn","鎶",112,285,12,7,"[Rn] 5f¹⁴ 6d¹⁰ 7s²","人工合成"),
        ("Nh","鉨",113,286,13,7,"[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p¹","人工合成"),("Fl","𫓧",114,289,14,7,"[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p²","人工合成"),
        ("Mc","镆",115,290,15,7,"[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p³","人工合成"),("Lv","𫟷",116,293,16,7,"[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁴","人工合成"),
        ("Ts","鿬",117,294,17,7,"[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁵","人工合成"),("Og","气奥",118,294,18,7,"[Rn] 5f¹⁴ 6d¹⁰ 7s² 7p⁶","人工合成"),
    ]
    elements_data = {
        sym: {"name": name, "atomic": atomic, "mass": mass,
              "group": group, "period": period,
              "config": config, "desc": desc}
        for (sym, name, atomic, mass, group, period, config, desc) in _ELEMENTS_RAW
    }


# ==================== 中文编程：基础工具 ====================
class InterpreterError(Exception):
    def __init__(self, msg, line=1, col=1):
        self.msg = msg
        self.line = line
        self.col = col
        super().__init__(msg)


def _find_outside_string(s, target):
    in_str = False
    i = 0
    n = len(s)
    tl = len(target)
    while i <= n - tl:
        if s[i] == '"':
            in_str = not in_str
            i += 1
            continue
        if not in_str and s[i:i + tl] == target:
            return i
        i += 1
    return -1


def _is_number_str(s):
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def _to_str(v):
    if isinstance(v, bool):
        return "正确" if v else "错误"
    if isinstance(v, float):
        r = round(v, 9)
        if r == int(r):
            return str(int(r))
        return str(r)
    return str(v)


def _num(v):
    if isinstance(v, bool):
        return 1 if v else 0
    if isinstance(v, (int, float)):
        return v
    raise ValueError("不是数字")


_FULLWIDTH_MAP = {
    '（': '(', '）': ')',
    '，': ',', '；': ';', '、': ',',
    '“': '"', '”': '"', '‘': "'", '’': "'",
    '％': '%',
    '＝': '=', '＜': '<', '＞': '>',
}


def _normalize_fullwidth(s):
    out = []
    in_str = False
    for ch in s:
        if in_str:
            out.append(ch)
            if ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            continue
        out.append(_FULLWIDTH_MAP.get(ch, ch))
    return ''.join(out)


def _preprocess_code(code):
    result = []
    for i, raw in enumerate(code.split('\n'), 1):
        raw = _normalize_fullwidth(raw).rstrip()
        comment_idx = raw.find('注释:')
        if comment_idx == -1:
            comment_idx = raw.find('注释：')
        code_part = raw[:comment_idx] if comment_idx != -1 else raw
        indent_width = 0
        content_start = 0
        for j, c in enumerate(code_part):
            if c == ' ':
                indent_width += 1
            elif c == '\t':
                indent_width += 4
            else:
                content_start = j
                break
        else:
            content_start = len(code_part)
        content = code_part[content_start:].rstrip()
        col = content_start + 1 if content else 1
        result.append({'line_num': i, 'indent': indent_width,
                       'content': content, 'col': col})
    return result


# ==================== 中文编程：AST 解析 ====================
class _ASTParser:
    def __init__(self, lines):
        self.lines = lines
        self.pos = 0

    def parse(self):
        stmts = self._parse_block(-1)
        if self.pos < len(self.lines):
            line = self.lines[self.pos]
            if line['content']:
                raise InterpreterError("无法解释", line['line_num'], line['col'])
        return stmts

    def _parse_block(self, parent_indent):
        stmts = []
        base_indent = None
        while self.pos < len(self.lines):
            line = self.lines[self.pos]
            if not line['content']:
                self.pos += 1
                continue
            if line['indent'] <= parent_indent:
                break
            if base_indent is None:
                base_indent = line['indent']
            elif line['indent'] < base_indent:
                break
            elif line['indent'] > base_indent:
                raise InterpreterError("意外的缩进", line['line_num'], line['col'])
            self.pos += 1
            stmt = self._parse_line(line)
            if stmt is not None:
                stmts.append(stmt)
        return stmts

    def _parse_line(self, line):
        content = line['content']
        line_num = line['line_num']
        col = line['col']

        m = re.match(r'^导入\s+([^\s]+)\s+模块\s*$', content)
        if m:
            return {'kind': 'import', 'line': line_num, 'col': col,
                    'module': m.group(1), 'alias': m.group(1)}

        m = re.match(r'^导入\s+([^\s]+)\s+作为\s+([^\s]+)\s+的名称\s*$', content)
        if m:
            return {'kind': 'import', 'line': line_num, 'col': col,
                    'module': m.group(2), 'alias': m.group(1)}

        m = re.match(r'^使用\s+([^\s]+)\s+模块的\s+([^\s]+)\s+功能\s*\((.*)\)\s*$', content)
        if m:
            return {'kind': 'use_module', 'line': line_num, 'col': col,
                    'alias': m.group(1), 'func': m.group(2), 'args': m.group(3).strip()}

        m = re.match(r'^定义函数\s*名为\s*([^\s，,：:]+)(?:\s*[，,]\s*参数为\s*([^：:]*?))?\s*的函数\s*[：:]\s*$', content)
        if m:
            name = m.group(1).strip()
            params_str = (m.group(2) or '').strip()
            params = [p for p in re.split(r'[，,、\s]+', params_str) if p]
            body = self._parse_block(line['indent'])
            if not body:
                raise InterpreterError("函数体为空", line_num, col)
            return {'kind': 'funcdef', 'line': line_num, 'col': col,
                    'name': name, 'params': params, 'body': body}

        m = re.match(r'^如果\s*(.+?)\s*时\s*[，,]\s*执行\s*[：:]\s*$', content)
        if m:
            return self._parse_if(line, m.group(1).strip())

        if re.match(r'^否则如果\s*(.+?)\s*时\s*[，,]\s*执行\s*[：:]\s*$', content):
            raise InterpreterError("意外的 否则如果", line_num, col)
        if re.match(r'^否则\s*[：:]\s*$', content):
            raise InterpreterError("意外的 否则", line_num, col)

        m = re.match(r'^返回\s*(.*)$', content)
        if m:
            return {'kind': 'return', 'line': line_num, 'col': col,
                    'expr': m.group(1).strip()}

        m = re.match(r'^当\s*(.+?)\s*时\s*[，,]\s*执行\s*[：:]\s*$', content)
        if m:
            cond = m.group(1).strip()
            body = self._parse_block(line['indent'])
            if not body:
                raise InterpreterError("循环体为空", line_num, col)
            return {'kind': 'while', 'line': line_num, 'col': col,
                    'cond': cond, 'body': body}

        m = re.match(
            r'^在\s*(\S+)\s*的\s*(.+?)\s*到\s*(.+?)\s*的范围内\s*[，,]\s*以\s*(.+?)\s*的步长执行\s*[：:]\s*$',
            content)
        if m:
            var_name = m.group(1).strip()
            start = m.group(2).strip()
            end = m.group(3).strip()
            step = m.group(4).strip()
            if not re.match(r'^[\u4e00-\u9fa5a-zA-Z_\d]+$', var_name):
                raise InterpreterError("无法解释", line_num, col)
            if var_name in ('正确', '错误'):
                raise InterpreterError("不能使用保留字作为变量名", line_num, col)
            body = self._parse_block(line['indent'])
            if not body:
                raise InterpreterError("循环体为空", line_num, col)
            return {'kind': 'for', 'line': line_num, 'col': col,
                    'var': var_name, 'start': start, 'end': end,
                    'step': step, 'body': body}

        m = re.match(r'^打印\s*\((.*)\)\s*$', content)
        if m:
            return {'kind': 'print', 'line': line_num, 'col': col,
                    'expr': m.group(1).strip()}

        idx = _find_outside_string(content, '赋值给')
        if idx != -1:
            expr = content[:idx].strip()
            var_name = content[idx + 3:].strip()
            if not expr or not var_name:
                raise InterpreterError("无法解释", line_num, col)
            if not re.match(r'^[\u4e00-\u9fa5a-zA-Z_\d]+$', var_name):
                raise InterpreterError("无法解释", line_num, col)
            if var_name in ('正确', '错误'):
                raise InterpreterError("不能使用保留字作为变量名", line_num, col)
            return {'kind': 'assign', 'line': line_num, 'col': col,
                    'expr': expr, 'var': var_name}

        return {'kind': 'expr', 'line': line_num, 'col': col, 'expr': content}

    def _parse_if(self, line, cond):
        branches = []
        body = self._parse_block(line['indent'])
        if not body:
            raise InterpreterError("条件分支体为空", line['line_num'], line['col'])
        branches.append((cond, body))
        else_body = None
        while self.pos < len(self.lines):
            nxt = self.lines[self.pos]
            if not nxt['content']:
                break
            if nxt['indent'] != line['indent']:
                break
            c = nxt['content']
            m2 = re.match(r'^否则如果\s*(.+?)\s*时\s*[，,]\s*执行\s*[：:]\s*$', c)
            if m2:
                self.pos += 1
                b = self._parse_block(nxt['indent'])
                if not b:
                    raise InterpreterError("条件分支体为空", nxt['line_num'], nxt['col'])
                branches.append((m2.group(1).strip(), b))
                continue
            m3 = re.match(r'^否则\s*[：:]\s*$', c)
            if m3:
                self.pos += 1
                b = self._parse_block(nxt['indent'])
                if not b:
                    raise InterpreterError("否则分支体为空", nxt['line_num'], nxt['col'])
                else_body = b
            break
        return {'kind': 'if', 'line': line['line_num'], 'col': line['col'],
                'branches': branches, 'else': else_body}


# ==================== 中文编程：表达式解析 ====================
class _ExprParser:
    def __init__(self, tokens, interp, line, col):
        self.tokens = tokens
        self.pos = 0
        self.interp = interp
        self.line = line
        self.col = col

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        t = self.peek()
        self.pos += 1
        return t

    def error(self, msg="无法解释"):
        raise InterpreterError(msg, self.line, self.col)

    def parse(self):
        v = self.parse_comparison()
        if self.peek() is not None:
            self.error()
        return v

    def parse_comparison(self):
        left = self.parse_additive()
        while True:
            op = self.peek()
            if op in ('>', '<', '>=', '<=', '==', '!='):
                self.advance()
                right = self.parse_additive()
                try:
                    if op == '>':
                        left = left > right
                    elif op == '<':
                        left = left < right
                    elif op == '>=':
                        left = left >= right
                    elif op == '<=':
                        left = left <= right
                    elif op == '==':
                        left = left == right
                    else:
                        left = left != right
                except Exception:
                    self.error("无法比较")
            else:
                break
        return left

    def parse_additive(self):
        left = self.parse_term()
        while self.peek() in ('+', '-'):
            op = self.advance()
            right = self.parse_term()
            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    left = _to_str(left) + _to_str(right)
                else:
                    try:
                        left = _num(left) + _num(right)
                    except Exception:
                        self.error("无法进行加法运算")
            else:
                try:
                    left = _num(left) - _num(right)
                except Exception:
                    self.error("无法进行减法运算")
        return left

    def parse_term(self):
        left = self.parse_unary()
        while self.peek() in ('*', '/', '%'):
            op = self.advance()
            right = self.parse_unary()
            try:
                a = _num(left)
                b = _num(right)
                if op == '*':
                    left = a * b
                elif op == '/':
                    if b == 0:
                        raise InterpreterError("0为除数", self.line, self.col)
                    left = a / b
                else:
                    if b == 0:
                        raise InterpreterError("0为除数", self.line, self.col)
                    left = a % b
            except InterpreterError:
                raise
            except Exception:
                self.error("无法进行运算")
        return left

    def parse_unary(self):
        op = self.peek()
        if op == '-':
            self.advance()
            try:
                return -_num(self.parse_unary())
            except Exception:
                self.error()
        if op == '+':
            self.advance()
            return self.parse_unary()
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()
        if tok is None:
            self.error()
        if tok == '(':
            self.advance()
            v = self.parse_comparison()
            if self.peek() != ')':
                self.error()
            self.advance()
            return v
        if len(tok) >= 2 and tok.startswith('"') and tok.endswith('"'):
            self.advance()
            return tok[1:-1]
        if _is_number_str(tok) and not re.match(r'^[\u4e00-\u9fa5]', tok):
            self.advance()
            try:
                if '.' in tok:
                    return float(tok)
                return int(tok)
            except Exception:
                self.error()
        if re.match(r'^[\u4e00-\u9fa5a-zA-Z_\d]+$', tok):
            self.advance()
            if self.peek() == '(':
                self.advance()
                args = []
                if self.peek() != ')':
                    args.append(self.parse_comparison())
                    while self.peek() == ',':
                        self.advance()
                        args.append(self.parse_comparison())
                if self.peek() != ')':
                    self.error()
                self.advance()
                return self.interp._call_function(tok, args, self.line, self.col)
            if tok == '正确':
                return True
            if tok == '错误':
                return False
            if tok in self.interp.variables:
                return self.interp.variables[tok]
            self.error(f"未定义的变量: {tok}")
        self.error()


# ==================== 中文编程：解释器 ====================
class ChineseInterpreter:
    def __init__(self, print_callback=None, input_callback=None):
        self.variables = {}
        self.functions = {}
        self.modules = {}
        self._print_cb = print_callback
        self._input_cb = input_callback
        self.builtins = {
            '当前时间': lambda: time.time(),
            '格式化时间': lambda ts=None: time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(ts if ts is not None else time.time())),
            '睡眠': lambda s=0: time.sleep(s),
            '延迟': lambda s=0: time.sleep(s),
            '获取输入': self._builtin_input,
            '变成整数': self._builtin_to_int,
            '变成小数': self._builtin_to_float,
            '变成字符串': self._builtin_to_str,
        }
        self._outputs = []
        self._return_flag = False
        self._return_value = None
        self._current_line = 1
        self._current_col = 1
        self._call_depth = 0
        self._max_depth = 200

    def _builtin_input(self, prompt=""):
        if self._input_cb:
            return self._input_cb(str(prompt))
        return ""

    def _builtin_to_int(self, v):
        if isinstance(v, bool):
            return 1 if v else 0
        if isinstance(v, int):
            return v
        try:
            if isinstance(v, str):
                v = v.strip()
            return int(float(v))
        except Exception:
            raise ValueError(f"无法将 {v!r} 转换为整数")

    def _builtin_to_float(self, v):
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        try:
            if isinstance(v, str):
                v = v.strip()
            return float(v)
        except Exception:
            raise ValueError(f"无法将 {v!r} 转换为小数")

    def _builtin_to_str(self, v):
        return _to_str(v)

    def _emit(self, text):
        if self._print_cb:
            self._print_cb(text)
        else:
            self._outputs.append(text)

    def execute(self, code):
        self.variables = {}
        self.functions = {}
        self.modules = {}
        self._outputs = []
        self._return_flag = False
        self._return_value = None
        self._call_depth = 0
        try:
            lines = _preprocess_code(code)
            parser = _ASTParser(lines)
            ast = parser.parse()
            self._exec_block(ast)
            return '\n'.join(self._outputs) if self._outputs else ""
        except InterpreterError as e:
            self._emit(f"第{e.line}行第{e.col}列，{e.msg}")
            return '\n'.join(self._outputs)
        except Exception:
            self._emit(
                f"第{self._current_line}行第{self._current_col}列，无法解释")
            return '\n'.join(self._outputs)

    def _exec_block(self, stmts):
        for stmt in stmts:
            self._exec_stmt(stmt)
            if self._return_flag:
                return

    def _exec_stmt(self, stmt):
        self._current_line = stmt['line']
        self._current_col = stmt['col']
        kind = stmt['kind']

        if kind == 'print':
            val = self._eval(stmt['expr'], stmt['line'], stmt['col'])
            self._emit(self._format_value(val))

        elif kind == 'assign':
            val = self._eval(stmt['expr'], stmt['line'], stmt['col'])
            self.variables[stmt['var']] = val

        elif kind == 'expr':
            val = self._eval(stmt['expr'], stmt['line'], stmt['col'])
            self._emit(self._format_value(val))

        elif kind == 'import':
            mod = stmt['module']
            alias = stmt['alias']
            if mod == '时间':
                self.modules[alias] = 'time'
            else:
                raise InterpreterError(f"不支持的模块: {mod}", stmt['line'], stmt['col'])

        elif kind == 'use_module':
            alias = stmt['alias']
            func = stmt['func']
            args_str = stmt['args']

            if alias not in self.modules:
                raise InterpreterError(f"未导入模块: {alias}", stmt['line'], stmt['col'])

            mod = self.modules[alias]
            if mod == 'time':
                args = []
                if args_str:
                    args_str = re.sub(r'^时间(?=\d)', '', args_str)
                    arg_parts = self._split_args(args_str, stmt['line'], stmt['col'])
                    for p in arg_parts:
                        args.append(self._eval(p, stmt['line'], stmt['col']))

                try:
                    if func in ('睡眠', '延迟'):
                        time.sleep(args[0] if args else 0)
                    elif func in ('当前时间', '时间'):
                        return time.time()
                    elif func in ('格式化时间', '日期'):
                        ts = args[0] if args else time.time()
                        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
                    else:
                        raise InterpreterError(f"时间模块未知的功能: {func}", stmt['line'], stmt['col'])
                except Exception as e:
                    if isinstance(e, InterpreterError):
                        raise
                    raise InterpreterError(f"执行时间模块功能失败: {e}", stmt['line'], stmt['col'])
            else:
                raise InterpreterError(f"未知模块: {mod}", stmt['line'], stmt['col'])

        elif kind == 'funcdef':
            self.functions[stmt['name']] = (stmt['params'], stmt['body'])

        elif kind == 'return':
            if stmt['expr']:
                self._return_value = self._eval(stmt['expr'], stmt['line'], stmt['col'])
            else:
                self._return_value = None
            self._return_flag = True

        elif kind == 'if':
            for cond, body in stmt['branches']:
                if self._eval_cond(cond, stmt['line'], stmt['col']):
                    self._exec_block(body)
                    return
            if stmt['else']:
                self._exec_block(stmt['else'])

        elif kind == 'while':
            guard = 0
            while True:
                guard += 1
                if guard > 1000000:
                    raise InterpreterError("循环次数过多（疑似死循环）",
                                           stmt['line'], stmt['col'])
                cond = self._eval_cond(stmt['cond'], stmt['line'], stmt['col'])
                if not cond:
                    break
                self._exec_block(stmt['body'])
                if self._return_flag:
                    return

        elif kind == 'for':
            var = stmt['var']
            start = self._eval(stmt['start'], stmt['line'], stmt['col'])
            end = self._eval(stmt['end'], stmt['line'], stmt['col'])
            step = self._eval(stmt['step'], stmt['line'], stmt['col'])

            if not isinstance(start, (int, float)) or isinstance(start, bool):
                raise InterpreterError("区间起点必须是数字", stmt['line'], stmt['col'])
            if not isinstance(end, (int, float)) or isinstance(end, bool):
                raise InterpreterError("区间终点必须是数字", stmt['line'], stmt['col'])
            if not isinstance(step, (int, float)) or isinstance(step, bool):
                raise InterpreterError("步长必须是数字", stmt['line'], stmt['col'])
            if step == 0:
                raise InterpreterError("步长不能为0", stmt['line'], stmt['col'])

            values = []
            if (isinstance(start, int) and isinstance(end, int)
                    and isinstance(step, int)):
                if (end - start) * step > 0:
                    values = list(range(start, end, step))
            else:
                cur = start
                if step > 0:
                    while cur < end - 1e-9:
                        values.append(cur)
                        cur += step
                        if len(values) > 1000000:
                            raise InterpreterError("循环次数过多", stmt['line'], stmt['col'])
                else:
                    while cur > end + 1e-9:
                        values.append(cur)
                        cur += step
                        if len(values) > 1000000:
                            raise InterpreterError("循环次数过多", stmt['line'], stmt['col'])

            for v in values:
                self.variables[var] = v
                self._exec_block(stmt['body'])
                if self._return_flag:
                    return

    def _split_args(self, s, line, col):
        parts = []
        current = ""
        in_str = False
        depth = 0
        for c in s:
            if c == '"':
                in_str = not in_str
                current += c
            elif not in_str and c == '(':
                depth += 1
                current += c
            elif not in_str and c == ')':
                depth -= 1
                current += c
            elif not in_str and depth == 0 and c == ',':
                parts.append(current.strip())
                current = ""
            else:
                current += c
        if current.strip():
            parts.append(current.strip())
        return parts

    def _call_function(self, name, args, line_num, col):
        if name in self.builtins:
            try:
                return self.builtins[name](*args)
            except InterpreterError:
                raise
            except TypeError:
                raise InterpreterError(
                    f"函数 {name} 参数数量不正确", line_num, col)
            except Exception as e:
                raise InterpreterError(
                    f"执行内置函数失败: {e}", line_num, col)
        if name not in self.functions:
            raise InterpreterError(f"未定义的函数: {name}", line_num, col)
        params, body = self.functions[name]
        if len(params) != len(args):
            raise InterpreterError(
                f"函数 {name} 需要 {len(params)} 个参数，实际传入 {len(args)} 个",
                line_num, col)
        if self._call_depth >= self._max_depth:
            raise InterpreterError("函数调用层级过深", line_num, col)
        self._call_depth += 1
        saved_vars = dict(self.variables)
        saved_flag = self._return_flag
        saved_val = self._return_value
        try:
            for p, a in zip(params, args):
                self.variables[p] = a
            self._return_flag = False
            self._return_value = None
            self._exec_block(body)
            return self._return_value
        finally:
            self.variables = saved_vars
            self._return_flag = saved_flag
            self._return_value = saved_val
            self._call_depth -= 1

    def _format_value(self, val):
        return _to_str(val)

    def _eval_cond(self, expr, line_num, col):
        val = self._eval(expr, line_num, col)
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, str):
            if val == "正确":
                return True
            if val == "错误":
                return False
            return bool(val)
        return bool(val)

    def _eval(self, expr, line_num, col):
        expr = expr.strip()
        if not expr:
            raise InterpreterError("空表达式", line_num, col)
        tokens = self._tokenize(expr, line_num, col)
        return _ExprParser(tokens, self, line_num, col).parse()

    def _tokenize(self, expr, line_num, col):
        tokens = []
        i = 0
        n = len(expr)
        while i < n:
            c = expr[i]
            if c.isspace():
                i += 1
                continue
            if c == '"':
                j = i + 1
                while j < n and expr[j] != '"':
                    j += 1
                if j >= n:
                    raise InterpreterError("字符串未闭合", line_num, col)
                tokens.append(expr[i:j + 1])
                i = j + 1
            elif c in '+-*/%()':
                tokens.append(c)
                i += 1
            elif c in '<>':
                if i + 1 < n and expr[i + 1] == '=':
                    tokens.append(c + '=')
                    i += 2
                else:
                    tokens.append(c)
                    i += 1
            elif c == '=':
                if i + 1 < n and expr[i + 1] == '=':
                    tokens.append('==')
                    i += 2
                else:
                    tokens.append('=')
                    i += 1
            elif c == '!' and i + 1 < n and expr[i + 1] == '=':
                tokens.append('!=')
                i += 2
            elif c == ',':
                tokens.append(',')
                i += 1
            elif c.isdigit() or c == '.':
                num = ''
                while i < n and (expr[i].isdigit() or expr[i] == '.'):
                    num += expr[i]
                    i += 1
                tokens.append(num)
            elif c == '_' or c.isalpha() or '\u4e00' <= c <= '\u9fa5':
                word = ''
                while i < n and (expr[i] == '_' or expr[i].isalnum()
                                 or '\u4e00' <= expr[i] <= '\u9fa5'):
                    word += expr[i]
                    i += 1
                tokens.append(word)
            else:
                tokens.append(c)
                i += 1
        return tokens


# ==================== 插件基类 ====================
class PluginBase:
    name = "未命名插件"
    version = "1.0"
    description = ""
    author = ""

    def __init__(self, app):
        self.app = app

    def get_menu_name(self):
        return self.name

    def run(self):
        messagebox.showinfo(self.name, "该插件尚未实现功能。")

    def register_menus(self):
        return []

    def register_shortcuts(self):
        return {}

    def on_balance(self, equation):
        return None

    def on_calculate(self, kind, params):
        return None

    def on_startup(self):
        pass

    def on_shutdown(self):
        pass


# ==================== 主程序 ====================
class ChemistryToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title("化学工具箱 v5.0")
        self.root.geometry("1280x850")
        self.root.minsize(1100, 700)
        try:
            self.root.configure(bg=MODERN_COLORS['bg'])
        except Exception:
            pass

        configure_ttk_theme(root)

        self.default_font = DEFAULT_FONT
        self.title_font = TITLE_FONT
        self.h1_font = H1_FONT
        self.ChemicalFormulaParser = ChemicalFormulaParser
        self.AtomicMass = AtomicMass
        self.ValenceData = ValenceData
        self.EquationBalancer = EquationBalancer
        self.ExtendedPeriodicTable = ExtendedPeriodicTable

        self.plugins = []
        self.sidebar_buttons = {}

        # CTB 表格底层数据结构
        self.table_rows = 20
        self.table_cols = 10
        self.table_row_height = 26
        self.table_col_width = 100
        self.table_cells = {}
        self.table_charts = []
        self.merged_cells = [] # 记录合并区域 (min_r, min_c, max_r, max_c)
        
        # 交互状态
        self.selection_start = None
        self.selection_end = None
        self.selected_cells = set()
        self.editing_cell = None
        self.floating_entry = None
        self._original_text = ""
        self._ignore_focus_out = False
        
        # 填充柄状态
        self.is_dragging_handle = False
        self.drag_target_cell = None
        
        # 图表交互状态
        self.selected_chart = None
        self.resizing_chart = None
        self.chart_drag_start = None
        self.chart_orig_pos = None
        self.chart_orig_size = None
        
        # 公式交互状态
        self.active_editor = None
        self.formula_drag_start = None
        self.formula_insert_pos = None
        self.formula_insert_len = 0
        
        # 公式计算结果缓存
        self.cell_cache = {}
        self.display_cache = {}
        
        # UI 变量
        self.table_row_h_var = None
        self.table_col_w_var = None
        self.table_font_var = None
        self.table_size_var = None
        self.table_bold_var = None
        self.table_align_var = None
        self.table_fg_color = None
        self.table_bg_color = None
        self.table_dtype_var = None
        self.formula_bar_var = None
        self.cell_ref_var = None
        
        # 设置变量
        self.enable_iteration_var = tk.BooleanVar(value=False)
        self.max_iter_var = tk.StringVar(value="100")
        self.tolerance_var = tk.StringVar(value="0.001")

        self._hl_job = None
        self._hl_lock = False

        self._interp_running = False
        self._interp_queue = None
        self._current_input_holder = None
        self._current_input_event = None
        self.run_btn = None
        self.exec_result = None
        self.input_frame = None
        self.input_label = None
        self.input_entry = None
        self.prog_notebook = None

        self._active_wheel_canvas = None

        self.create_menubar()

        self.root_container = tk.Frame(root, bg=MODERN_COLORS['bg'])
        self.root_container.pack(fill=tk.BOTH, expand=True)

        self.sidebar = tk.Frame(self.root_container, bg=MODERN_COLORS['sidebar'],
                                width=210)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        self.create_sidebar()

        self.content_container = tk.Frame(self.root_container, bg=MODERN_COLORS['bg'])
        self.content_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.topbar = tk.Frame(self.content_container, bg=MODERN_COLORS['bg'], height=40)
        self.topbar.pack(side=tk.TOP, fill=tk.X, padx=20, pady=(15, 0))
        self.topbar.pack_propagate(False)
        self.page_title = tk.Label(self.topbar, text="配平",
                                   font=H1_FONT, fg=MODERN_COLORS['text'],
                                   bg=MODERN_COLORS['bg'])
        self.page_title.pack(side=tk.LEFT)

        self.card_frame = tk.Frame(self.content_container,
                                   bg=MODERN_COLORS['surface'],
                                   highlightbackground=MODERN_COLORS['border'],
                                   highlightthickness=1, bd=0)
        self.card_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 10))

        self.content_frame = tk.Frame(self.card_frame, bg=MODERN_COLORS['surface'])
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        self.status_frame = tk.Frame(root, bg=MODERN_COLORS['sidebar'])
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tk.Label(self.status_frame, text="就绪",
                                     font=("Microsoft YaHei", 9),
                                     bd=0, anchor=tk.W,
                                     bg=MODERN_COLORS['sidebar'],
                                     fg=MODERN_COLORS['sidebar_text'],
                                     padx=16, pady=6)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.root.bind_all("<MouseWheel>", self._on_global_wheel)
        self.root.bind_all("<Button-4>", self._on_global_wheel)
        self.root.bind_all("<Button-5>", self._on_global_wheel)

        self.load_plugins()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.show_balance()

    # ---------- 全局滚轮 ----------
    def _on_global_wheel(self, event):
        canvas = getattr(self, '_active_wheel_canvas', None)
        if canvas is None:
            return
        try:
            if not canvas.winfo_exists():
                self._active_wheel_canvas = None
                return
        except Exception:
            self._active_wheel_canvas = None
            return
        try:
            delta = getattr(event, 'delta', 0) or 0
            num = getattr(event, 'num', 0) or 0
            if delta != 0:
                canvas.yview_scroll(int(-delta / 120), "units")
            elif num == 4:
                canvas.yview_scroll(-3, "units")
            elif num == 5:
                canvas.yview_scroll(3, "units")
        except Exception:
            pass

    def open_plugin_folder(self):
        plugin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")
        os.makedirs(plugin_dir, exist_ok=True)
        try:
            if sys.platform == "win32":
                os.startfile(plugin_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", plugin_dir])
            else:
                subprocess.Popen(["xdg-open", plugin_dir])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {e}")

    # ---------- 菜单 ----------
    def create_menubar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        self.file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=self.file_menu)
        self.file_menu.add_command(label="导出结果", command=self.export_result)
        self.file_menu.add_command(label="打开插件文件夹", command=self.open_plugin_folder)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="退出", command=self._on_close)
        self.tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=self.tools_menu)
        self.tools_menu.add_command(label="单位换算", command=self.show_unit_converter)
        self.tools_menu.add_command(label="实验记录", command=self.show_lab_notebook)
        self.help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=self.help_menu)
        self.help_menu.add_command(label="使用教程", command=self.show_help)
        self.help_menu.add_command(label="插件开发文档", command=self.show_plugin_docs)
        self.help_menu.add_command(label="中文编程开发文档", command=self.show_lang_docs)
        self.help_menu.add_command(label="关于", command=self.show_about)

    def create_sidebar(self):
        logo_area = tk.Frame(self.sidebar, bg=MODERN_COLORS['sidebar'])
        logo_area.pack(fill=tk.X, pady=(22, 4))
        draw_pixel_logo(logo_area, MODERN_COLORS['sidebar'], pixel=4)
        tk.Label(logo_area, text="化学工具箱",
                 font=("Microsoft YaHei", 12, "bold"),
                 fg='#FFFFFF', bg=MODERN_COLORS['sidebar']).pack(pady=(10, 0))
        tk.Label(logo_area, text="v5.0",
                 font=("Microsoft YaHei", 8),
                 fg=MODERN_COLORS['sidebar_text_dim'],
                 bg=MODERN_COLORS['sidebar']).pack(pady=(2, 0))

        sep = tk.Frame(self.sidebar, bg='#2E2E42', height=1)
        sep.pack(fill=tk.X, padx=18, pady=(20, 14))

        items = [
            ("配平",       self.show_balance),
            ("元素周期表", self.show_periodic),
            ("计算",       self.show_calculator_menu),
            ("实用功能",   self.show_utility_hub),
            ("编程",       self.show_programming),
        ]
        for text, cmd in items:
            btn = RoundedButton(self.sidebar, text=text, command=cmd,
                                width=178, height=42, radius=8,
                                bg=MODERN_COLORS['sidebar'],
                                fg=MODERN_COLORS['sidebar_text'],
                                hover_bg=MODERN_COLORS['sidebar_hover'],
                                font=("Microsoft YaHei", 11),
                                parent_bg=MODERN_COLORS['sidebar'],
                                align='left')
            btn.pack(pady=3, padx=14, fill=tk.X)
            self.sidebar_buttons[text] = btn

        bottom_sep = tk.Frame(self.sidebar, bg='#2E2E42', height=1)
        bottom_sep.pack(fill=tk.X, padx=18, pady=(24, 14))
        for text, cmd in [("帮助", self.show_help), ("关于", self.show_about)]:
            btn = RoundedButton(self.sidebar, text=text, command=cmd,
                                width=178, height=38, radius=8,
                                bg=MODERN_COLORS['sidebar'],
                                fg=MODERN_COLORS['sidebar_text_dim'],
                                hover_bg=MODERN_COLORS['sidebar_hover'],
                                font=("Microsoft YaHei", 10),
                                parent_bg=MODERN_COLORS['sidebar'],
                                align='left')
            btn.pack(pady=2, padx=14, fill=tk.X)
            self.sidebar_buttons[text] = btn

    # ---------- 插件 ----------
    def load_plugins(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        plugin_dir = os.path.join(base_dir, "plugins")
        try:
            os.makedirs(plugin_dir, exist_ok=True)
        except Exception:
            pass
        try:
            existing = [f for f in os.listdir(plugin_dir)
                        if f.endswith('.py') and not f.startswith('_')]
            if not existing:
                with open(os.path.join(plugin_dir, 'example_plugin.py'),
                          'w', encoding='utf-8') as f:
                    f.write(_EXAMPLE_PLUGIN)
        except Exception:
            pass
        try:
            for file in sorted(os.listdir(plugin_dir)):
                if not file.endswith(".py") or file.startswith("_"):
                    continue
                try:
                    spec = importlib.util.spec_from_file_location(
                        file[:-3], os.path.join(plugin_dir, file))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, "Plugin"):
                        plugin_instance = module.Plugin(self)
                        self.plugins.append(plugin_instance)
                except Exception as e:
                    print(f"加载插件 {file} 失败: {e}")
        except Exception:
            pass
        for p in self.plugins:
            try:
                if hasattr(p, 'on_startup'):
                    p.on_startup()
            except Exception as e:
                print(f"插件启动失败: {e}")
        self._apply_plugin_menus()
        self._apply_plugin_shortcuts()

    def _apply_plugin_menus(self):
        menu_map = {'工具': self.tools_menu, '文件': self.file_menu, '帮助': self.help_menu}
        for p in self.plugins:
            try:
                items = p.register_menus() if hasattr(p, 'register_menus') else []
            except Exception:
                items = []
            for item in items or []:
                try:
                    menu_name, label, cb = item
                except Exception:
                    continue
                menu = menu_map.get(menu_name)
                if menu is not None:
                    try:
                        menu.add_command(label=label, command=cb)
                    except Exception:
                        pass

    def _apply_plugin_shortcuts(self):
        for p in self.plugins:
            try:
                shortcuts = p.register_shortcuts() if hasattr(p, 'register_shortcuts') else {}
            except Exception:
                shortcuts = {}
            for key, cb in (shortcuts or {}).items():
                try:
                    self.root.bind(key, lambda e, c=cb: c())
                except Exception:
                    pass

    def _on_close(self):
        self._interp_running = False
        if self._current_input_event is not None:
            try:
                self._current_input_event.set()
            except Exception:
                pass
        for p in self.plugins:
            try:
                if hasattr(p, 'on_shutdown'):
                    p.on_shutdown()
            except Exception:
                pass
        try:
            self.root.destroy()
        except Exception:
            pass

    # ---------- 通用 ----------
    def clear_content(self):
        self._active_wheel_canvas = None
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def update_status(self, message):
        try:
            self.status_label.config(text=message)
            self.root.update_idletasks()
        except Exception:
            pass

    def _set_page_title(self, text):
        try:
            self.page_title.config(text=text)
        except Exception:
            pass

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

    # ==================== 实用功能 Hub ====================
    def show_utility_hub(self):
        self.clear_content()
        self._set_page_title("实用功能")
        self.update_status("选择一个工具开始使用（支持鼠标滚轮）")
        bg = MODERN_COLORS['surface']

        tk.Label(self.content_frame, text="实用工具", font=H1_FONT,
                 fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 4))
        tk.Label(self.content_frame, text="选择一个工具开始使用",
                 font=self.default_font, fg=MODERN_COLORS['text_muted'],
                 bg=bg).pack(pady=(0, 10))

        canvas = tk.Canvas(self.content_frame, bg=bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient=tk.VERTICAL,
                                 command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=bg)
        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        groups = [
            ("溶液与酸碱", [
                ("pH 计算器", "强酸 / 强碱 / 弱酸 / 弱碱 pH 计算", self.show_ph_calculator),
                ("缓冲溶液", "Henderson-Hasselbalch 方程计算缓冲液 pH", self.show_buffer),
                ("酸碱滴定", "根据酸/碱浓度计算滴定所需体积", self.show_titration),
                ("溶液配制", "计算配制目标浓度溶液所需溶质质量", self.show_solution_prep),
            ]),
            ("气体与热力学", [
                ("气体定律", "理想气体状态方程 PV = nRT 求解任意变量", self.show_gas_law),
                ("分压计算", "道尔顿分压定律 P_total = ΣP_i", self.show_partial_pressure),
                ("热化学", "热量 Q = mcΔT 与燃烧热计算", self.show_thermochemistry),
                ("热力学", "吉布斯自由能 ΔG = ΔH - TΔS", self.show_thermodynamics),
            ]),
            ("反应与平衡", [
                ("氧化还原分析", "计算化合物中各元素的氧化数", self.show_redox),
                ("化学平衡", "由平衡常数与温度计算 ΔG°", self.show_equilibrium),
                ("化学动力学", "阿伦尼乌斯方程与半衰期计算", self.show_kinetics),
                ("电化学", "能斯特方程 E = E° - (RT/nF) lnQ", self.show_electrochem),
            ]),
            ("专题工具", [
                ("有机化学工具", "官能团识别与同分异构体数目", self.show_organic),
                ("光谱分析", "波长-能量转换与可见光颜色对照", self.show_spectroscopy),
                ("核化学", "放射性衰变与半衰期计算", self.show_nuclear),
                ("溶解度查询", "常见物质的溶解度数据", self.show_solubility),
            ]),
            ("测试功能", [
                ("CTB 表格", "类似 Excel 的表格制作工具，支持公式与智能格式", self.show_ctb_table),
                ("PyInstaller 打包", "将 Python 脚本或中文编程打包为 EXE", self.show_pyinstaller_tool),
            ]),
        ]

        for group_name, items in groups:
            # 美化分组标题：左侧添加竖线，加大间距
            group_frame = tk.Frame(scroll_frame, bg=bg)
            group_frame.pack(fill=tk.X, padx=8, pady=(18, 8))
            tk.Frame(group_frame, bg=MODERN_COLORS['primary'], width=4, height=16).pack(side=tk.LEFT)
            tk.Label(group_frame, text=group_name,
                     font=("Microsoft YaHei", 12, "bold"),
                     fg=MODERN_COLORS['text'], bg=bg).pack(side=tk.LEFT, padx=8)

            grid = tk.Frame(scroll_frame, bg=bg)
            grid.pack(fill=tk.X, padx=8, pady=(0, 4))
            grid.grid_columnconfigure(0, weight=1)
            grid.grid_columnconfigure(1, weight=1)
            for i, (title, desc, cmd) in enumerate(items):
                card = self._make_utility_card(grid, title, desc, cmd, bg)
                card.grid(row=i // 2, column=i % 2, padx=6, pady=6, sticky="nsew")

        if self.plugins:
            group_frame = tk.Frame(scroll_frame, bg=bg)
            group_frame.pack(fill=tk.X, padx=8, pady=(18, 8))
            tk.Frame(group_frame, bg=MODERN_COLORS['success'], width=4, height=16).pack(side=tk.LEFT)
            tk.Label(group_frame, text="插件功能",
                     font=("Microsoft YaHei", 12, "bold"),
                     fg=MODERN_COLORS['text'], bg=bg).pack(side=tk.LEFT, padx=8)
            
            grid = tk.Frame(scroll_frame, bg=bg)
            grid.pack(fill=tk.X, padx=8, pady=(0, 4))
            grid.grid_columnconfigure(0, weight=1)
            grid.grid_columnconfigure(1, weight=1)
            for i, plugin in enumerate(self.plugins):
                try:
                    name = plugin.get_menu_name()
                except Exception:
                    name = "插件"
                desc = getattr(plugin, 'description', '') or "自定义插件功能"
                card = self._make_utility_card(grid, name, desc, plugin.run, bg)
                card.grid(row=i // 2, column=i % 2, padx=6, pady=6, sticky="nsew")

        self._active_wheel_canvas = canvas

    def _make_utility_card(self, parent, title, desc, command, bg):
        outer = tk.Frame(parent, bg=MODERN_COLORS['border'], highlightthickness=0, bd=0)
        inner = tk.Frame(outer, bg=MODERN_COLORS['card_bg'], highlightthickness=0, bd=0)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        title_lbl = tk.Label(inner, text=title,
                             font=("Microsoft YaHei", 11, "bold"),
                             fg=MODERN_COLORS['text'], bg=MODERN_COLORS['card_bg'], anchor=tk.W)
        title_lbl.pack(fill=tk.X, padx=16, pady=(14, 4))
        
        desc_lbl = tk.Label(inner, text=desc,
                            font=("Microsoft YaHei", 9),
                            fg=MODERN_COLORS['text_light'],
                            bg=MODERN_COLORS['card_bg'], anchor=tk.W, justify=tk.LEFT,
                            wraplength=280)
        desc_lbl.pack(fill=tk.X, padx=16, pady=(0, 14))

        def on_enter(_e):
            try:
                inner.config(bg=MODERN_COLORS['card_hover'])
                title_lbl.config(bg=MODERN_COLORS['card_hover'], fg=MODERN_COLORS['primary'])
                desc_lbl.config(bg=MODERN_COLORS['card_hover'], fg=MODERN_COLORS['text'])
                outer.config(bg=MODERN_COLORS['primary'])
            except Exception:
                pass

        def on_leave(_e):
            try:
                inner.config(bg=MODERN_COLORS['card_bg'])
                title_lbl.config(bg=MODERN_COLORS['card_bg'], fg=MODERN_COLORS['text'])
                desc_lbl.config(bg=MODERN_COLORS['card_bg'], fg=MODERN_COLORS['text_light'])
                outer.config(bg=MODERN_COLORS['border'])
            except Exception:
                pass

        def on_click(_e):
            try:
                command()
            except Exception as e:
                messagebox.showerror("错误", str(e))

        for widget in (outer, inner, title_lbl, desc_lbl):
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.bind('<Button-1>', on_click)
            try:
                widget.configure(cursor='hand2')
            except Exception:
                pass
        return outer

    # ==================== 计算菜单 ====================
    def show_calculator_menu(self):
        self.clear_content()
        self._set_page_title("化学计算")
        self.update_status("计算功能")
        bg = MODERN_COLORS['surface']
        tk.Label(self.content_frame, text="化学计算工具", font=self.title_font,
                 fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 10))
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        tabs = [
            ("摩尔质量", self.create_molar_calc),
            ("浓度计算", self.create_concentration_calc),
            ("稀释计算", self.create_dilution_calc),
            ("比例求解", self.create_ratio_calc),
            ("元素百分比", self.create_percent_composition_calc),
            ("经验式确定", self.create_empirical_formula_calc),
            ("浓度换算", self.create_concentration_convert_calc),
            ("产率计算", self.create_yield_calc),
        ]
        for name, builder in tabs:
            f = tk.Frame(notebook, bg=bg)
            notebook.add(f, text=name)
            builder(f)

    def create_molar_calc(self, parent):
        bg = MODERN_COLORS['surface']
        tk.Label(parent, text="输入化学式:", font=self.default_font,
                 bg=bg, fg=MODERN_COLORS['text']).pack(pady=(12, 6))
        self.molar_entry = ModernEntry(parent, width=40)
        self.molar_entry.pack(pady=5)
        self.molar_entry.bind('<Return>', lambda e: self.calc_molar_mass())
        RoundedButton(parent, text="计算", command=self.calc_molar_mass,
                      width=140, height=40).pack(pady=12)
        self.molar_result = tk.Text(parent, height=10, font=self.default_font,
                                    relief=tk.FLAT, bd=0,
                                    bg=MODERN_COLORS['bg'], fg=MODERN_COLORS['text'],
                                    padx=12, pady=10)
        self.molar_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def calc_molar_mass(self):
        formula = self.molar_entry.get().strip()
        if not formula:
            return
        mass, detail = ChemicalFormulaParser.calculate_molar_mass(formula)
        self.molar_result.delete(1.0, tk.END)
        if mass > 0:
            self.molar_result.insert(tk.END,
                f"化学式: {formula}\n相对分子质量: {mass}\n\n计算过程:\n{detail}")
        else:
            self.molar_result.insert(tk.END, detail)

    def create_concentration_calc(self, parent):
        bg = MODERN_COLORS['surface']
        tk.Label(parent, text="溶质质量 (g):", bg=bg).grid(row=0, column=0, padx=8, pady=8, sticky=tk.W)
        self.solute_mass = ModernEntry(parent, width=15)
        self.solute_mass.grid(row=0, column=1, padx=8, pady=8, sticky=tk.EW)
        tk.Label(parent, text="溶液体积 (L):", bg=bg).grid(row=1, column=0, padx=8, pady=8, sticky=tk.W)
        self.solution_vol = ModernEntry(parent, width=15)
        self.solution_vol.grid(row=1, column=1, padx=8, pady=8, sticky=tk.EW)
        tk.Label(parent, text="摩尔质量 (g/mol):", bg=bg).grid(row=2, column=0, padx=8, pady=8, sticky=tk.W)
        self.molar_mass_conc = ModernEntry(parent, width=15)
        self.molar_mass_conc.grid(row=2, column=1, padx=8, pady=8, sticky=tk.EW)
        RoundedButton(parent, text="计算浓度", command=self.calc_concentration,
                      width=140, height=40).grid(row=3, column=0, columnspan=2, pady=12)
        self.conc_result = tk.Text(parent, height=8, font=self.default_font,
                                   relief=tk.FLAT, bd=0,
                                   bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.conc_result.grid(row=4, column=0, columnspan=2, padx=12, pady=12, sticky="nsew")
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
            self.conc_result.insert(tk.END,
                f"溶质的量: {moles:.4f} mol\n溶液体积: {volume} L\n物质的量浓度: {concentration:.4f} mol/L")
        except Exception:
            self.conc_result.delete(1.0, tk.END)
            self.conc_result.insert(tk.END, "输入错误，请检查")

    def create_dilution_calc(self, parent):
        bg = MODERN_COLORS['surface']
        tk.Label(parent, text="初始浓度 (mol/L):", bg=bg).grid(row=0, column=0, padx=8, pady=8, sticky=tk.W)
        self.c1_entry = ModernEntry(parent, width=15)
        self.c1_entry.grid(row=0, column=1, padx=8, pady=8, sticky=tk.EW)
        tk.Label(parent, text="初始体积 (L):", bg=bg).grid(row=1, column=0, padx=8, pady=8, sticky=tk.W)
        self.v1_entry = ModernEntry(parent, width=15)
        self.v1_entry.grid(row=1, column=1, padx=8, pady=8, sticky=tk.EW)
        tk.Label(parent, text="最终体积 (L):", bg=bg).grid(row=2, column=0, padx=8, pady=8, sticky=tk.W)
        self.v2_entry = ModernEntry(parent, width=15)
        self.v2_entry.grid(row=2, column=1, padx=8, pady=8, sticky=tk.EW)
        RoundedButton(parent, text="计算最终浓度", command=self.calc_dilution,
                      width=160, height=40).grid(row=3, column=0, columnspan=2, pady=12)
        self.dilute_result = tk.Text(parent, height=6, font=self.default_font,
                                     relief=tk.FLAT, bd=0,
                                     bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.dilute_result.grid(row=4, column=0, columnspan=2, padx=12, pady=12, sticky="nsew")
        parent.grid_columnconfigure(1, weight=1)

    def calc_dilution(self):
        try:
            c1 = float(self.c1_entry.get())
            v1 = float(self.v1_entry.get())
            v2 = float(self.v2_entry.get())
            c2 = c1 * v1 / v2
            self.dilute_result.delete(1.0, tk.END)
            self.dilute_result.insert(tk.END,
                f"C1V1 = C2V2\n{c1} × {v1} = C2 × {v2}\nC2 = {c2:.4f} mol/L")
        except Exception:
            self.dilute_result.delete(1.0, tk.END)
            self.dilute_result.insert(tk.END, "输入错误")

    def create_ratio_calc(self, parent):
        bg = MODERN_COLORS['surface']
        tk.Label(parent, text="比例求解", font=self.title_font,
                 fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(12, 8))
        info_frame = tk.LabelFrame(parent, text="使用说明", font=self.default_font,
                                   bg=bg, fg=MODERN_COLORS['text_light'],
                                   bd=1, relief=tk.SOLID)
        info_frame.pack(fill=tk.X, padx=30, pady=8)
        tk.Label(info_frame,
                 text="格式1: a / b = c / x  ->  求解 x = (b × c) / a\n"
                      "格式2: a / b = x / d  ->  求解 x = (a × d) / b",
                 font=self.default_font, justify=tk.LEFT, bg=bg).pack(pady=8, padx=12)
        type_frame = tk.Frame(parent, bg=bg)
        type_frame.pack(pady=8)
        self.ratio_type = tk.StringVar(value="type1")
        tk.Radiobutton(type_frame, text="a / b = c / x", variable=self.ratio_type,
                       value="type1", command=self.update_ratio_inputs,
                       font=self.default_font, bg=bg,
                       activebackground=bg, selectcolor=bg).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(type_frame, text="a / b = x / d", variable=self.ratio_type,
                       value="type2", command=self.update_ratio_inputs,
                       font=self.default_font, bg=bg,
                       activebackground=bg, selectcolor=bg).pack(side=tk.LEFT, padx=10)
        self.ratio_input_frame = tk.Frame(parent, bg=bg)
        self.ratio_input_frame.pack(pady=10)
        self.ratio_entries = {}
        self.update_ratio_inputs()
        RoundedButton(parent, text="计算 x", command=self.calc_ratio,
                      width=140, height=40).pack(pady=10)
        result_frame = tk.LabelFrame(parent, text="计算结果", font=self.default_font,
                                     bg=bg, fg=MODERN_COLORS['text_light'],
                                     bd=1, relief=tk.SOLID)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=8)
        self.ratio_result = tk.Text(result_frame, height=6, font=MONO_FONT,
                                    relief=tk.FLAT, bd=0,
                                    bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.ratio_result.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def update_ratio_inputs(self):
        for widget in self.ratio_input_frame.winfo_children():
            widget.destroy()
        bg = MODERN_COLORS['surface']
        if self.ratio_type.get() == "type1":
            labels = ["a =", "b =", "c =", "x = ?"]
            self.ratio_vars = ["a", "b", "c"]
        else:
            labels = ["a =", "b =", "d =", "x = ?"]
            self.ratio_vars = ["a", "b", "d"]
        for i, label in enumerate(labels):
            tk.Label(self.ratio_input_frame, text=label, font=self.default_font,
                     bg=bg).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            entry = ModernEntry(self.ratio_input_frame, width=15)
            entry.grid(row=i, column=1, padx=10, pady=5)
            if i < 3:
                self.ratio_entries[self.ratio_vars[i]] = entry
            else:
                entry.entry.config(state='disabled', bg='#F0F0F0')
                self.ratio_entries["x_display"] = entry

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
                self.ratio_result.insert(tk.END,
                    f"比例式: {a} / {b} = {c} / x\n\n解: x = (b × c) / a = ({b}×{c})/{a} = {x:.6g}")
                self.ratio_entries["x_display"].entry.config(state='normal')
                self.ratio_entries["x_display"].delete(0, tk.END)
                self.ratio_entries["x_display"].insert(0, f"{x:.6g}")
                self.ratio_entries["x_display"].entry.config(state='disabled')
            else:
                a = float(self.ratio_entries["a"].get())
                b = float(self.ratio_entries["b"].get())
                d = float(self.ratio_entries["d"].get())
                if b == 0:
                    raise ValueError("分母 b 不能为0")
                x = (a * d) / b
                self.ratio_result.delete(1.0, tk.END)
                self.ratio_result.insert(tk.END,
                    f"比例式: {a} / {b} = x / {d}\n\n解: x = (a × d) / b = ({a}×{d})/{b} = {x:.6g}")
                self.ratio_entries["x_display"].entry.config(state='normal')
                self.ratio_entries["x_display"].delete(0, tk.END)
                self.ratio_entries["x_display"].insert(0, f"{x:.6g}")
                self.ratio_entries["x_display"].entry.config(state='disabled')
        except Exception as e:
            self.ratio_result.delete(1.0, tk.END)
            self.ratio_result.insert(tk.END, f"错误：{str(e)}")

    def create_percent_composition_calc(self, parent):
        bg = MODERN_COLORS['surface']
        tk.Label(parent, text="输入化学式:", font=self.default_font, bg=bg).pack(pady=(12, 6))
        self.percent_formula = ModernEntry(parent, width=40)
        self.percent_formula.pack(pady=5)
        RoundedButton(parent, text="计算元素百分比", command=self.calc_percent_composition,
                      width=180, height=40).pack(pady=12)
        self.percent_result = tk.Text(parent, height=12, font=self.default_font,
                                      relief=tk.FLAT, bd=0,
                                      bg=MODERN_COLORS['bg'], padx=12, pady=10)
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
        self.percent_result.insert(tk.END,
            f"化学式: {formula}\n摩尔质量: {total_mass:.4f} g/mol\n\n各元素质量分数:\n")
        for element in sorted(percent.keys()):
            self.percent_result.insert(tk.END, f"{element}: {percent[element]:.2f}%\n")

    def create_empirical_formula_calc(self, parent):
        bg = MODERN_COLORS['surface']
        tk.Label(parent, text="输入元素质量或百分比（格式：元素 数值，每行一个）",
                 font=self.default_font, bg=bg).pack(pady=(12, 6))
        self.empirical_text = tk.Text(parent, height=8, width=50, relief=tk.FLAT, bd=1,
                                      highlightbackground=MODERN_COLORS['border'],
                                      highlightcolor=MODERN_COLORS['primary'],
                                      highlightthickness=1,
                                      bg=MODERN_COLORS['surface'],
                                      fg=MODERN_COLORS['text'], padx=10, pady=8)
        self.empirical_text.pack(pady=5)
        tk.Label(parent, text="例如:\nC 40\nH 6.7\nO 53.3",
                 font=self.default_font, fg=MODERN_COLORS['text_muted'],
                 bg=bg).pack()
        RoundedButton(parent, text="确定经验式", command=self.calc_empirical_formula,
                      width=160, height=40).pack(pady=12)
        self.empirical_result = tk.Text(parent, height=5, font=self.default_font,
                                        relief=tk.FLAT, bd=0,
                                        bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.empirical_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def calc_empirical_formula(self):
        data = self.empirical_text.get(1.0, tk.END).strip()
        if not data:
            return
        masses = {}
        for line in data.split('\n'):
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
            except Exception:
                self.empirical_result.delete(1.0, tk.END)
                self.empirical_result.insert(tk.END, "数值无效")
                return
            masses[elem] = val
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
        for factor in range(1, 20):
            int_ratios = {elem: round(ratios[elem] * factor) for elem in ratios}
            if all(abs(ratios[elem] * factor - int_ratios[elem]) < 0.01 for elem in ratios):
                formula = "".join(
                    f"{elem}{int_ratios[elem] if int_ratios[elem] > 1 else ''}"
                    for elem in sorted(int_ratios.keys()))
                self.empirical_result.delete(1.0, tk.END)
                self.empirical_result.insert(tk.END, f"经验式: {formula}")
                return
        self.empirical_result.delete(1.0, tk.END)
        self.empirical_result.insert(tk.END, "无法确定整数比")

    def create_concentration_convert_calc(self, parent):
        bg = MODERN_COLORS['surface']
        tk.Label(parent, text="质量分数 (%):", bg=bg).grid(row=0, column=0, padx=8, pady=8, sticky=tk.W)
        self.wt_percent = ModernEntry(parent, width=15)
        self.wt_percent.grid(row=0, column=1, padx=8, pady=8, sticky=tk.EW)
        tk.Label(parent, text="溶液密度 (g/mL):", bg=bg).grid(row=1, column=0, padx=8, pady=8, sticky=tk.W)
        self.density = ModernEntry(parent, width=15)
        self.density.grid(row=1, column=1, padx=8, pady=8, sticky=tk.EW)
        tk.Label(parent, text="溶质摩尔质量 (g/mol):", bg=bg).grid(row=2, column=0, padx=8, pady=8, sticky=tk.W)
        self.molar_mass_convert = ModernEntry(parent, width=15)
        self.molar_mass_convert.grid(row=2, column=1, padx=8, pady=8, sticky=tk.EW)
        RoundedButton(parent, text="计算摩尔浓度", command=self.calc_concentration_convert,
                      width=160, height=40).grid(row=3, column=0, columnspan=2, pady=12)
        self.convert_result = tk.Text(parent, height=6, font=self.default_font,
                                      relief=tk.FLAT, bd=0,
                                      bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.convert_result.grid(row=4, column=0, columnspan=2, padx=12, pady=12, sticky="nsew")
        parent.grid_columnconfigure(1, weight=1)

    def calc_concentration_convert(self):
        try:
            w = float(self.wt_percent.get())
            d = float(self.density.get())
            M = float(self.molar_mass_convert.get())
            c = (w * d * 10) / M
            self.convert_result.delete(1.0, tk.END)
            self.convert_result.insert(tk.END,
                f"摩尔浓度 = (质量分数 × 密度 × 10) / 摩尔质量\n= ({w} × {d} × 10) / {M} = {c:.4f} mol/L")
        except Exception:
            self.convert_result.delete(1.0, tk.END)
            self.convert_result.insert(tk.END, "输入错误")

    def create_yield_calc(self, parent):
        bg = MODERN_COLORS['surface']
        tk.Label(parent, text="实际产量 (g):", bg=bg).grid(row=0, column=0, padx=8, pady=8, sticky=tk.W)
        self.actual_yield = ModernEntry(parent, width=15)
        self.actual_yield.grid(row=0, column=1, padx=8, pady=8, sticky=tk.EW)
        tk.Label(parent, text="理论产量 (g):", bg=bg).grid(row=1, column=0, padx=8, pady=8, sticky=tk.W)
        self.theoretical_yield = ModernEntry(parent, width=15)
        self.theoretical_yield.grid(row=1, column=1, padx=8, pady=8, sticky=tk.EW)
        RoundedButton(parent, text="计算产率", command=self.calc_yield,
                      width=140, height=40).grid(row=2, column=0, columnspan=2, pady=12)
        self.yield_result = tk.Text(parent, height=5, font=self.default_font,
                                    relief=tk.FLAT, bd=0,
                                    bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.yield_result.grid(row=3, column=0, columnspan=2, padx=12, pady=12, sticky="nsew")
        parent.grid_columnconfigure(1, weight=1)

    def calc_yield(self):
        try:
            actual = float(self.actual_yield.get())
            theoretical = float(self.theoretical_yield.get())
            percent = (actual / theoretical) * 100
            self.yield_result.delete(1.0, tk.END)
            self.yield_result.insert(tk.END,
                f"产率 = (实际产量 / 理论产量) × 100% = ({actual}/{theoretical})×100% = {percent:.2f}%")
        except Exception:
            self.yield_result.delete(1.0, tk.END)
            self.yield_result.insert(tk.END, "输入错误")

    # ==================== 配平页 ====================
    def show_balance(self):
        self.clear_content()
        self._set_page_title("配平")
        self.update_status("配平模式 - 离子用 ^数字+ 或 ^数字- 表示")
        bg = MODERN_COLORS['surface']

        tk.Label(self.content_frame, text="化学方程式配平",
                 font=H1_FONT, fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 4))
        tk.Label(self.content_frame,
                 text="输入化学方程式，自动配平并标注化合价",
                 font=self.default_font, fg=MODERN_COLORS['text_muted'],
                 bg=bg).pack(pady=(0, 12))

        help_frame = tk.Frame(self.content_frame, bg=MODERN_COLORS['primary_light'])
        help_frame.pack(fill=tk.X, padx=40, pady=(0, 12), ipady=6)
        tk.Label(help_frame, text="支持格式:",
                 font=("Microsoft YaHei", 9, "bold"),
                 fg=MODERN_COLORS['primary'],
                 bg=MODERN_COLORS['primary_light']).pack(side=tk.LEFT, padx=(12, 4))
        tk.Label(help_frame,
                 text="H2+O2=H2O   |   Fe2O3+CO=Fe+CO2   |   H^1++CO3^2-=HCO3^1-",
                 font=MONO_FONT, fg=MODERN_COLORS['primary'],
                 bg=MODERN_COLORS['primary_light']).pack(side=tk.LEFT, padx=4)

        input_frame = tk.Frame(self.content_frame, bg=bg)
        input_frame.pack(pady=(0, 16))
        tk.Label(input_frame, text="方程式:", font=self.default_font, bg=bg).pack(side=tk.LEFT, padx=(0, 8))
        self.equation_entry = ModernEntry(input_frame, width=60, font=MONO_FONT)
        self.equation_entry.pack(side=tk.LEFT, padx=(0, 8))
        self.equation_entry.bind('<Return>', lambda e: self.do_balance())
        RoundedButton(input_frame, text="配平", command=self.do_balance,
                      width=100, height=42).pack(side=tk.LEFT)

        result_frame = tk.Frame(self.content_frame, bg=MODERN_COLORS['bg'],
                                highlightbackground=MODERN_COLORS['border'],
                                highlightthickness=1)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=8)
        tk.Label(result_frame, text="配平结果",
                 font=("Microsoft YaHei", 10, "bold"),
                 fg=MODERN_COLORS['text_light'],
                 bg=MODERN_COLORS['bg']).pack(anchor=tk.W, padx=14, pady=(10, 0))
        self.result_text = tk.Text(result_frame, height=12,
                                   font=("Consolas", 12), wrap=tk.WORD,
                                   relief=tk.FLAT, bd=0,
                                   bg=MODERN_COLORS['bg'],
                                   fg=MODERN_COLORS['text'],
                                   padx=14, pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.result_text.tag_configure("blue_coeff",
                                       foreground=MODERN_COLORS['primary'],
                                       font=("Consolas", 12, "bold"))
        self.result_text.tag_configure("green_valence",
                                       foreground=MODERN_COLORS['success'],
                                       font=("Consolas", 10))
        self.result_text.tag_configure("red_valence",
                                       foreground=MODERN_COLORS['danger'],
                                       font=("Consolas", 10))
        self.result_text.tag_configure("normal",
                                       foreground=MODERN_COLORS['text'],
                                       font=("Consolas", 12))

        example_frame = tk.Frame(self.content_frame, bg=bg)
        example_frame.pack(pady=(8, 0))
        tk.Label(example_frame, text="快速示例:", bg=bg,
                 fg=MODERN_COLORS['text_light']).pack(side=tk.LEFT, padx=(0, 6))
        examples = [
            ("H2+O2=H2O", "氢气燃烧"),
            ("Fe2O3+CO=Fe+CO2", "炼铁"),
            ("Cu+AgNO3=Cu(NO3)2+Ag", "置换"),
            ("H^1++CO3^2-=HCO3^1-", "碳酸根"),
            ("H^1++OH^1-=H2O", "中和"),
        ]
        for eq, desc in examples:
            RoundedButton(example_frame, text=desc,
                          command=lambda e=eq: self.load_example(e),
                          width=100, height=32, radius=6,
                          bg=MODERN_COLORS['primary_light'],
                          fg=MODERN_COLORS['primary'],
                          hover_bg='#D0E4F7',
                          font=("Microsoft YaHei", 9)).pack(side=tk.LEFT, padx=3)

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
        result = None
        valence_data = {}
        for p in self.plugins:
            try:
                if hasattr(p, 'on_balance'):
                    r = p.on_balance(equation)
                    if r is not None:
                        result, valence_data = r
                        break
            except Exception:
                continue
        if result is None:
            result, valence_data = EquationBalancer.balance(equation)
        self.result_text.delete(1.0, tk.END)
        if result.startswith("错误") or result.startswith("配平失败"):
            self.result_text.insert(tk.END, result, "normal")
            self.update_status("配平失败")
            return
        self.result_text.insert(tk.END, "配平结果:\n\n", "normal")
        try:
            left, right = result.split(" = ")
            left_parts = left.split(" + ")
            right_parts = right.split(" + ")
            superscript_map = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

            def format_part(part):
                charge_match = re.search(r'\^(\d+)([+-])$', part)
                if charge_match:
                    num = int(charge_match.group(1))
                    sign = charge_match.group(2)
                    if num == 1:
                        charge_str = '⁺' if sign == '+' else '⁻'
                    else:
                        num_sup = str(num).translate(superscript_map)
                        charge_str = num_sup + ('⁺' if sign == '+' else '⁻')
                    part_clean = part[:charge_match.start()]
                else:
                    charge_str = ""
                    part_clean = part
                coeff_match = re.match(r'^(\d+)(.*)$', part_clean)
                if coeff_match:
                    coeff = coeff_match.group(1)
                    formula = coeff_match.group(2)
                else:
                    coeff = ""
                    formula = part_clean
                return coeff, self.format_subscript(formula), charge_str

            for i, part in enumerate(left_parts):
                coeff, formula, charge = format_part(part)
                if coeff:
                    self.result_text.insert(tk.END, coeff, "blue_coeff")
                self.result_text.insert(tk.END, formula, "normal")
                if charge:
                    self.result_text.insert(tk.END, charge, "normal")
                if i < len(left_parts) - 1:
                    self.result_text.insert(tk.END, " + ", "normal")
            self.result_text.insert(tk.END, " = ", "normal")
            for i, part in enumerate(right_parts):
                coeff, formula, charge = format_part(part)
                if coeff:
                    self.result_text.insert(tk.END, coeff, "blue_coeff")
                self.result_text.insert(tk.END, formula, "normal")
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

    # ==================== 元素周期表 ====================
    def show_periodic(self):
        self.clear_content()
        self._set_page_title("元素周期表")
        self.update_status("元素周期表 - 点击元素查看详细信息（支持鼠标滚轮）")
        bg = MODERN_COLORS['surface']
        tk.Label(self.content_frame, text="元素周期表",
                 font=H1_FONT, fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 4))
        tk.Label(self.content_frame, text="点击任意元素查看详细信息",
                 font=self.default_font, fg=MODERN_COLORS['text_muted'],
                 bg=bg).pack(pady=(0, 8))

        canvas = tk.Canvas(self.content_frame, bg=bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=bg)
        scrollable.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        rows_data = [
            ["H", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "He"],
            ["Li", "Be", "", "", "", "", "", "", "", "", "", "", "B", "C", "N", "O", "F", "Ne"],
            ["Na", "Mg", "", "", "", "", "", "", "", "", "", "", "Al", "Si", "P", "S", "Cl", "Ar"],
            ["K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr"],
            ["Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe"],
            ["Cs", "Ba", "La", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn"],
            ["Fr", "Ra", "Ac", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og"],
        ]

        def make_element_button(parent_w, symbol, data, bg_color, w=6, h=3):
            fr = tk.Frame(parent_w, bg=bg_color,
                          highlightbackground=MODERN_COLORS['border'],
                          highlightthickness=1, cursor='hand2')
            fr.configure(width=w * 12, height=h * 20)
            fr.pack_propagate(False)
            lbl = tk.Label(fr, text=symbol, font=("Microsoft YaHei", 11, "bold"),
                           bg=bg_color, fg=MODERN_COLORS['text'])
            lbl.pack(pady=(6, 0))
            lbl2 = tk.Label(fr, text=str(data['atomic']),
                            font=("Microsoft YaHei", 8),
                            bg=bg_color, fg=MODERN_COLORS['text_light'])
            lbl2.pack()
            for widget in (fr, lbl, lbl2):
                widget.bind('<Button-1>', lambda e, s=symbol: self.show_element_info(s))
            return fr

        for r, row in enumerate(rows_data):
            for c, symbol in enumerate(row):
                if symbol and symbol in ExtendedPeriodicTable.elements_data:
                    data = ExtendedPeriodicTable.elements_data[symbol]
                    if data["group"] == 1:
                        color = "#FFE0E0"
                    elif data["group"] == 2:
                        color = "#E0FFE0"
                    elif 3 <= data["group"] <= 12:
                        color = "#E0E7FF"
                    else:
                        color = "#FFF8DC"
                    fr = make_element_button(scrollable, symbol, data, color)
                    fr.grid(row=r, column=c, padx=1, pady=1)

        lanthanides = ["Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"]
        actinides = ["Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr"]
        lf = tk.Frame(scrollable, bg=bg)
        lf.grid(row=len(rows_data), column=0, columnspan=18, pady=(12, 4), sticky=tk.W)
        tk.Label(lf, text="镧系:", font=self.default_font, bg=bg,
                 fg=MODERN_COLORS['text_light']).pack(side=tk.LEFT, padx=8)
        for symbol in lanthanides:
            if symbol in ExtendedPeriodicTable.elements_data:
                data = ExtendedPeriodicTable.elements_data[symbol]
                fr = make_element_button(lf, symbol, data, "#FFF8DC", w=4, h=1)
                fr.pack(side=tk.LEFT, padx=1)

        af = tk.Frame(scrollable, bg=bg)
        af.grid(row=len(rows_data) + 1, column=0, columnspan=18, pady=4, sticky=tk.W)
        tk.Label(af, text="锕系:", font=self.default_font, bg=bg,
                 fg=MODERN_COLORS['text_light']).pack(side=tk.LEFT, padx=8)
        for symbol in actinides:
            if symbol in ExtendedPeriodicTable.elements_data:
                data = ExtendedPeriodicTable.elements_data[symbol]
                fr = make_element_button(af, symbol, data, "#FFE8C0", w=4, h=1)
                fr.pack(side=tk.LEFT, padx=1)

        self._active_wheel_canvas = canvas

    def show_element_info(self, symbol):
        data = ExtendedPeriodicTable.elements_data.get(symbol)
        if data:
            electron_layers = ExtendedPeriodicTable.electron_config.get(symbol, "未知")
            en = ExtendedPeriodicTable.electronegativity.get(symbol, "未知")
            info = (f"元素: {symbol}\n名称: {data['name']}\n原子序数: {data['atomic']}\n"
                    f"原子量: {data['mass']}\n电负性: {en}\n族: {data['group']}\n"
                    f"周期: {data['period']}\n电子排布: {data['config']}\n"
                    f"电子层: {electron_layers}\n简介: {data['desc']}")
            messagebox.showinfo("元素信息", info)
        else:
            messagebox.showinfo("元素信息", f"未找到 {symbol} 的详细信息")

    # ==================== 实用功能页（各计算器） ====================
    def show_ph_calculator(self):
        self.clear_content()
        self._set_page_title("pH 计算器")
        self.update_status("pH 计算器")
        bg = MODERN_COLORS['surface']
        tk.Label(self.content_frame, text="pH 值计算", font=H1_FONT,
                 fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 10))
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        f1 = tk.Frame(notebook, bg=bg)
        notebook.add(f1, text="强酸/强碱")
        tk.Label(f1, text="浓度 (mol/L):", bg=bg).pack(pady=(20, 6))
        self.ph_conc = ModernEntry(f1, width=20)
        self.ph_conc.pack(pady=5)
        tk.Label(f1, text="类型:", bg=bg).pack(pady=(10, 6))
        self.ph_type = ttk.Combobox(f1, values=["强酸", "强碱"], width=15)
        self.ph_type.pack(pady=5)
        self.ph_type.set("强酸")
        RoundedButton(f1, text="计算 pH", command=self.calc_ph,
                      width=140, height=40).pack(pady=14)
        self.ph_result = tk.Text(f1, height=5, width=50, relief=tk.FLAT, bd=0,
                                 bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.ph_result.pack(pady=10)

        f2 = tk.Frame(notebook, bg=bg)
        notebook.add(f2, text="弱酸/弱碱")
        tk.Label(f2, text="浓度 (mol/L):", bg=bg).pack(pady=(20, 6))
        self.weak_conc = ModernEntry(f2, width=20)
        self.weak_conc.pack(pady=5)
        tk.Label(f2, text="Ka/Kb:", bg=bg).pack(pady=(10, 6))
        self.ka_kb = ModernEntry(f2, width=20)
        self.ka_kb.pack(pady=5)
        tk.Label(f2, text="类型:", bg=bg).pack(pady=(10, 6))
        self.weak_type = ttk.Combobox(f2, values=["弱酸", "弱碱"], width=15)
        self.weak_type.pack(pady=5)
        self.weak_type.set("弱酸")
        RoundedButton(f2, text="计算 pH", command=self.calc_weak_ph,
                      width=140, height=40).pack(pady=14)
        self.weak_result = tk.Text(f2, height=5, width=50, relief=tk.FLAT, bd=0,
                                   bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.weak_result.pack(pady=10)

    def calc_ph(self):
        try:
            conc = float(self.ph_conc.get())
            if conc <= 0:
                raise ValueError
            if self.ph_type.get() == "强酸":
                ph = -log10(conc)
                self.ph_result.delete(1.0, tk.END)
                self.ph_result.insert(tk.END, f"[H+] = {conc} mol/L\npH = {ph:.2f}")
            else:
                poh = -log10(conc)
                ph = 14 - poh
                self.ph_result.delete(1.0, tk.END)
                self.ph_result.insert(tk.END, f"[OH-] = {conc} mol/L\npOH = {poh:.2f}\npH = {ph:.2f}")
        except Exception:
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
                self.weak_result.insert(tk.END,
                    f"[H+] = sqrt(Ka*C) = sqrt({ka}*{conc}) = {h_conc:.2e} mol/L\npH = {ph:.2f}")
            else:
                oh_conc = (ka * conc) ** 0.5
                poh = -log10(oh_conc)
                ph = 14 - poh
                self.weak_result.delete(1.0, tk.END)
                self.weak_result.insert(tk.END,
                    f"[OH-] = sqrt(Kb*C) = sqrt({ka}*{conc}) = {oh_conc:.2e} mol/L\npOH = {poh:.2f}\npH = {ph:.2f}")
        except Exception:
            self.weak_result.delete(1.0, tk.END)
            self.weak_result.insert(tk.END, "输入错误")

    def show_gas_law(self):
        self.clear_content()
        self._set_page_title("气体定律")
        self.update_status("理想气体状态方程")
        bg = MODERN_COLORS['surface']
        tk.Label(self.content_frame, text="理想气体状态方程",
                 font=H1_FONT, fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 4))
        tk.Label(self.content_frame, text="PV = nRT",
                 font=("Microsoft YaHei", 13), fg=MODERN_COLORS['text_light'],
                 bg=bg).pack(pady=(0, 14))
        input_frame = tk.Frame(self.content_frame, bg=bg)
        input_frame.pack(pady=10)
        for i, (label, attr) in enumerate([
            ("压力 P (atm):", 'pressure'),
            ("体积 V (L):", 'volume'),
            ("物质的量 n (mol):", 'moles'),
            ("温度 T (K):", 'temperature'),
        ]):
            tk.Label(input_frame, text=label, bg=bg).grid(row=i, column=0, padx=8, pady=8, sticky=tk.W)
            e = ModernEntry(input_frame, width=15)
            e.grid(row=i, column=1, padx=8, pady=8, sticky=tk.EW)
            setattr(self, attr, e)
        RoundedButton(input_frame, text="计算", command=self.calc_gas_law,
                      width=140, height=40).grid(row=4, column=0, columnspan=2, pady=14)
        self.gas_result = tk.Text(self.content_frame, height=10, font=self.default_font,
                                  relief=tk.FLAT, bd=0,
                                  bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.gas_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

    def calc_gas_law(self):
        R = 0.0821
        try:
            P_s = self.pressure.get().strip()
            V_s = self.volume.get().strip()
            n_s = self.moles.get().strip()
            T_s = self.temperature.get().strip()
            if P_s and V_s and n_s:
                P, V, n = float(P_s), float(V_s), float(n_s)
                T = P * V / (n * R)
                self.gas_result.delete(1.0, tk.END)
                self.gas_result.insert(tk.END,
                    f"温度 T = PV/(nR) = {P:.2f}*{V:.2f}/({n:.2f}*{R:.4f}) = {T:.2f} K")
            elif P_s and V_s and T_s:
                P, V, T = float(P_s), float(V_s), float(T_s)
                n = P * V / (R * T)
                self.gas_result.delete(1.0, tk.END)
                self.gas_result.insert(tk.END,
                    f"物质的量 n = PV/(RT) = {P:.2f}*{V:.2f}/({R:.4f}*{T:.2f}) = {n:.4f} mol")
            elif P_s and n_s and T_s:
                P, n, T = float(P_s), float(n_s), float(T_s)
                V = n * R * T / P
                self.gas_result.delete(1.0, tk.END)
                self.gas_result.insert(tk.END,
                    f"体积 V = nRT/P = {n:.2f}*{R:.4f}*{T:.2f}/{P:.2f} = {V:.2f} L")
            elif V_s and n_s and T_s:
                V, n, T = float(V_s), float(n_s), float(T_s)
                P = n * R * T / V
                self.gas_result.delete(1.0, tk.END)
                self.gas_result.insert(tk.END,
                    f"压力 P = nRT/V = {n:.2f}*{R:.4f}*{T:.2f}/{V:.2f} = {P:.2f} atm")
            else:
                self.gas_result.delete(1.0, tk.END)
                self.gas_result.insert(tk.END, "请输入至少三个变量")
        except Exception:
            self.gas_result.delete(1.0, tk.END)
            self.gas_result.insert(tk.END, "输入错误")

    def show_thermochemistry(self):
        self.clear_content()
        self._set_page_title("热化学计算")
        self.update_status("热化学计算")
        bg = MODERN_COLORS['surface']
        tk.Label(self.content_frame, text="热化学计算", font=H1_FONT,
                 fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 10))
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        hf = tk.Frame(notebook, bg=bg)
        notebook.add(hf, text="热量计算")
        for i, (label, attr) in enumerate([
            ("质量 m (g):", 'heat_mass'),
            ("比热容 c (J/g*K):", 'heat_c'),
            ("温度变化 dT (K):", 'heat_dt'),
        ]):
            tk.Label(hf, text=label, bg=bg).grid(row=i, column=0, padx=8, pady=8, sticky=tk.W)
            e = ModernEntry(hf, width=15)
            e.grid(row=i, column=1, padx=8, pady=8, sticky=tk.EW)
            setattr(self, attr, e)
        RoundedButton(hf, text="计算热量", command=self.calc_heat,
                      width=140, height=40).grid(row=3, column=0, columnspan=2, pady=12)
        self.heat_result = tk.Text(hf, height=5, relief=tk.FLAT, bd=0,
                                   bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.heat_result.grid(row=4, column=0, columnspan=2, padx=12, pady=12, sticky="nsew")
        hf.grid_columnconfigure(1, weight=1)

        cf = tk.Frame(notebook, bg=bg)
        notebook.add(cf, text="燃烧热")
        for i, (label, attr) in enumerate([
            ("燃烧热 dH (kJ/mol):", 'dh_comb'),
            ("物质的量 n (mol):", 'n_comb'),
        ]):
            tk.Label(cf, text=label, bg=bg).grid(row=i, column=0, padx=8, pady=8, sticky=tk.W)
            e = ModernEntry(cf, width=15)
            e.grid(row=i, column=1, padx=8, pady=8, sticky=tk.EW)
            setattr(self, attr, e)
        RoundedButton(cf, text="计算放热", command=self.calc_combustion,
                      width=140, height=40).grid(row=2, column=0, columnspan=2, pady=12)
        self.comb_result = tk.Text(cf, height=5, relief=tk.FLAT, bd=0,
                                   bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.comb_result.grid(row=3, column=0, columnspan=2, padx=12, pady=12, sticky="nsew")
        cf.grid_columnconfigure(1, weight=1)

    def calc_heat(self):
        try:
            m, c, dt = (float(self.heat_mass.get()), float(self.heat_c.get()),
                        float(self.heat_dt.get()))
            q = m * c * dt
            self.heat_result.delete(1.0, tk.END)
            self.heat_result.insert(tk.END,
                f"Q = m*c*dT\nQ = {m} * {c} * {dt}\nQ = {q:.2f} J")
        except Exception:
            self.heat_result.delete(1.0, tk.END)
            self.heat_result.insert(tk.END, "输入错误")

    def calc_combustion(self):
        try:
            dh, n = float(self.dh_comb.get()), float(self.n_comb.get())
            q = dh * n
            self.comb_result.delete(1.0, tk.END)
            self.comb_result.insert(tk.END, f"Q = dH * n\nQ = {dh} * {n}\nQ = {q:.2f} kJ")
        except Exception:
            self.comb_result.delete(1.0, tk.END)
            self.comb_result.insert(tk.END, "输入错误")

    def show_redox(self):
        self.clear_content()
        self._set_page_title("氧化还原分析")
        self.update_status("氧化还原反应")
        bg = MODERN_COLORS['surface']
        tk.Label(self.content_frame, text="氧化数计算",
                 font=H1_FONT, fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 10))
        tk.Label(self.content_frame, text="输入化合物（如 H2O, Fe2O3）:",
                 bg=bg).pack(pady=6)
        self.redox_formula = ModernEntry(self.content_frame, width=30, font=MONO_FONT)
        self.redox_formula.pack(pady=6)
        RoundedButton(self.content_frame, text="计算氧化数",
                      command=self.calc_oxidation,
                      width=160, height=40).pack(pady=12)
        self.redox_result = tk.Text(self.content_frame, height=10, font=self.default_font,
                                    relief=tk.FLAT, bd=0,
                                    bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.redox_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        common_frame = tk.Frame(self.content_frame, bg=MODERN_COLORS['primary_light'])
        common_frame.pack(fill=tk.X, padx=20, pady=10, ipady=8)
        tk.Label(common_frame, text="常见氧化剂/还原剂",
                 font=("Microsoft YaHei", 10, "bold"),
                 fg=MODERN_COLORS['primary'],
                 bg=MODERN_COLORS['primary_light']).pack(anchor=tk.W, padx=12, pady=(0, 4))
        tk.Label(common_frame,
                 text="氧化剂: KMnO4, K2Cr2O7, H2O2, HNO3, O2\n还原剂: Fe2+, Zn, H2, CO, SO2",
                 font=self.default_font,
                 bg=MODERN_COLORS['primary_light'], justify=tk.LEFT).pack(anchor=tk.W, padx=12)

    def calc_oxidation(self):
        formula = self.redox_formula.get().strip()
        if not formula:
            return
        counts = ChemicalFormulaParser.parse_formula(formula)
        self.redox_result.delete(1.0, tk.END)
        self.redox_result.insert(tk.END, f"化合物: {formula}\n\n元素氧化数:\n")
        states = ChemicalFormulaParser.calculate_oxidation_states(formula)
        for element in counts.keys():
            v = states.get(element, 0)
            self.redox_result.insert(tk.END, f"{element}: {v:+d}\n")

    def show_organic(self):
        self.clear_content()
        self._set_page_title("有机化学工具")
        self.update_status("有机化学工具")
        bg = MODERN_COLORS['surface']
        tk.Label(self.content_frame, text="有机化合物信息", font=H1_FONT,
                 fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 10))
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        ff = tk.Frame(notebook, bg=bg)
        notebook.add(ff, text="官能团识别")
        tk.Label(ff, text="输入有机物名称:", bg=bg).pack(pady=(20, 6))
        self.org_name = ModernEntry(ff, width=40)
        self.org_name.pack(pady=5)
        RoundedButton(ff, text="识别", command=self.identify_functional,
                      width=120, height=40).pack(pady=10)
        self.func_result = tk.Text(ff, height=10, relief=tk.FLAT, bd=0,
                                   bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.func_result.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        isf = tk.Frame(notebook, bg=bg)
        notebook.add(isf, text="同分异构体")
        tk.Label(isf, text="分子式 (如 C5H12):", bg=bg).pack(pady=(20, 6))
        self.isomer_formula = ModernEntry(isf, width=20)
        self.isomer_formula.pack(pady=5)
        RoundedButton(isf, text="计算异构体数", command=self.calc_isomers,
                      width=160, height=40).pack(pady=10)
        self.isomer_result = tk.Text(isf, height=10, relief=tk.FLAT, bd=0,
                                     bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.isomer_result.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

    def identify_functional(self):
        name = self.org_name.get().lower()
        self.func_result.delete(1.0, tk.END)
        functional_groups = {
            "醇": ["醇", "乙醇", "甲醇", "丙醇"], "醛": ["醛", "乙醛", "甲醛"],
            "酮": ["酮", "丙酮"], "羧酸": ["酸", "乙酸", "甲酸"],
            "酯": ["酯", "乙酸乙酯"], "醚": ["醚", "乙醚"],
            "胺": ["胺", "甲胺"], "烯烃": ["烯", "乙烯", "丙烯"],
            "炔烃": ["炔", "乙炔"], "芳香烃": ["苯", "甲苯", "二甲苯"]
        }
        found = []
        for group, keywords in functional_groups.items():
            for keyword in keywords:
                if keyword in name:
                    found.append(group)
                    break
        if found:
            self.func_result.insert(tk.END,
                f"化合物: {name}\n\n可能含有的官能团: {', '.join(set(found))}")
        else:
            self.func_result.insert(tk.END, "未识别出常见官能团")

    def calc_isomers(self):
        formula = self.isomer_formula.get().strip()
        self.isomer_result.delete(1.0, tk.END)
        isomers = {"C5H12": 3, "C6H14": 5, "C7H16": 9, "C8H18": 18,
                   "C4H10": 2, "C3H8": 1, "C2H6": 1}
        if formula in isomers:
            self.isomer_result.insert(tk.END,
                f"分子式 {formula} 的同分异构体数目: {isomers[formula]} 种")
        else:
            self.isomer_result.insert(tk.END,
                "暂不支持该分子式\n常见烷烃异构体数:\nC4H10: 2, C5H12: 3, C6H14: 5, C7H16: 9")

    def show_solubility(self):
        self.clear_content()
        self._set_page_title("溶解度查询")
        self.update_status("溶解度查询")
        bg = MODERN_COLORS['surface']
        tk.Label(self.content_frame, text="物质溶解度查询", font=H1_FONT,
                 fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 10))
        common = [("NaCl", 36.0), ("KCl", 34.0), ("KNO3", 31.6), ("NH4Cl", 37.2),
                  ("Ca(OH)2", 0.173), ("AgNO3", 216), ("CuSO4", 20.7), ("NaOH", 109)]
        tree = ttk.Treeview(self.content_frame, columns=("物质", "溶解度"),
                            show="headings", height=10)
        tree.heading("物质", text="物质")
        tree.heading("溶解度", text="溶解度 (g/100g水, 20°C)")
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)
        for substance, solubility in common:
            tree.insert("", tk.END, values=(substance, solubility))
        tk.Label(self.content_frame,
                 text="溶解度规则:\n"
                      "  碱金属盐大多可溶\n"
                      "  硝酸盐全部可溶\n"
                      "  氯化物、溴化物、碘化物除 Ag+、Pb2+ 外可溶\n"
                      "  硫酸盐除 Ba2+、Pb2+、Ca2+ 外可溶\n"
                      "  碳酸盐、磷酸盐大多不溶",
                 font=self.default_font, justify=tk.LEFT, bg=bg,
                 fg=MODERN_COLORS['text_light']).pack(pady=10, anchor=tk.W, padx=20)

    def show_buffer(self):
        self.clear_content()
        self._set_page_title("缓冲溶液计算")
        self.update_status("缓冲溶液计算")
        bg = MODERN_COLORS['surface']
        tk.Label(self.content_frame, text="缓冲溶液 pH 计算",
                 font=H1_FONT, fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 4))
        tk.Label(self.content_frame, text="Henderson-Hasselbalch 方程",
                 font=self.default_font, fg=MODERN_COLORS['text_muted'],
                 bg=bg).pack(pady=(0, 12))
        frame = tk.Frame(self.content_frame, bg=bg)
        frame.pack(pady=10)
        for i, (label, attr) in enumerate([
            ("pKa:", 'pka_entry'),
            ("[A-] (mol/L):", 'base_conc'),
            ("[HA] (mol/L):", 'acid_conc'),
        ]):
            tk.Label(frame, text=label, bg=bg).grid(row=i, column=0, padx=8, pady=8, sticky=tk.W)
            e = ModernEntry(frame, width=15)
            e.grid(row=i, column=1, padx=8, pady=8, sticky=tk.EW)
            setattr(self, attr, e)
        RoundedButton(frame, text="计算 pH", command=self.calc_buffer_ph,
                      width=140, height=40).grid(row=3, column=0, columnspan=2, pady=12)
        self.buffer_result = tk.Text(self.content_frame, height=8, font=self.default_font,
                                     relief=tk.FLAT, bd=0,
                                     bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.buffer_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def calc_buffer_ph(self):
        try:
            pka = float(self.pka_entry.get())
            base = float(self.base_conc.get())
            acid = float(self.acid_conc.get())
            ph = pka + log10(base / acid)
            self.buffer_result.delete(1.0, tk.END)
            self.buffer_result.insert(tk.END,
                f"pH = pKa + log([A-]/[HA])\npH = {pka} + log({base}/{acid})\n"
                f"pH = {pka} + {log10(base/acid):.2f}\npH = {ph:.2f}")
        except Exception:
            self.buffer_result.delete(1.0, tk.END)
            self.buffer_result.insert(tk.END, "输入错误")

    def show_titration(self):
        self.clear_content()
        self._set_page_title("酸碱滴定计算")
        self.update_status("酸碱滴定计算")
        bg = MODERN_COLORS['surface']
        tk.Label(self.content_frame, text="酸碱滴定计算", font=H1_FONT,
                 fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 12))
        frame = tk.Frame(self.content_frame, bg=bg)
        frame.pack(pady=10)
        for i, (label, attr) in enumerate([
            ("酸浓度 (mol/L):", 'acid_conc_tit'),
            ("酸体积 (L):", 'acid_vol_tit'),
            ("碱浓度 (mol/L):", 'base_conc_tit'),
        ]):
            tk.Label(frame, text=label, bg=bg).grid(row=i, column=0, padx=8, pady=8, sticky=tk.W)
            e = ModernEntry(frame, width=15)
            e.grid(row=i, column=1, padx=8, pady=8, sticky=tk.EW)
            setattr(self, attr, e)
        RoundedButton(frame, text="计算碱体积", command=self.calc_titration,
                      width=160, height=40).grid(row=3, column=0, columnspan=2, pady=12)
        self.titration_result = tk.Text(self.content_frame, height=8, font=self.default_font,
                                        relief=tk.FLAT, bd=0,
                                        bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.titration_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def calc_titration(self):
        try:
            ca, va, cb = (float(self.acid_conc_tit.get()),
                          float(self.acid_vol_tit.get()),
                          float(self.base_conc_tit.get()))
            vb = ca * va / cb
            self.titration_result.delete(1.0, tk.END)
            self.titration_result.insert(tk.END,
                f"CaVa = CbVb\n{ca} * {va} = {cb} * Vb\nVb = {vb:.4f} L = {vb*1000:.2f} mL")
        except Exception:
            self.titration_result.delete(1.0, tk.END)
            self.titration_result.insert(tk.END, "输入错误")

    def show_spectroscopy(self):
        self.clear_content()
        self._set_page_title("光谱分析")
        self.update_status("光谱分析")
        bg = MODERN_COLORS['surface']
        tk.Label(self.content_frame, text="光谱分析工具", font=H1_FONT,
                 fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 10))
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        wf = tk.Frame(notebook, bg=bg)
        notebook.add(wf, text="波长-能量转换")
        tk.Label(wf, text="波长 (nm):", bg=bg).pack(pady=(20, 6))
        self.wavelength = ModernEntry(wf, width=20)
        self.wavelength.pack(pady=5)
        RoundedButton(wf, text="转换", command=self.convert_wavelength,
                      width=120, height=40).pack(pady=10)
        self.wave_result = tk.Text(wf, height=5, relief=tk.FLAT, bd=0,
                                   bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.wave_result.pack(pady=10)

        cf = tk.Frame(notebook, bg=bg)
        notebook.add(cf, text="颜色与波长")
        colors = [("紫", "400-450"), ("蓝", "450-500"), ("青", "500-550"),
                  ("绿", "550-580"), ("黄", "580-600"), ("橙", "600-650"),
                  ("红", "650-750")]
        for color, wavelength in colors:
            tk.Label(cf, text=f"{color}: {wavelength} nm", font=self.default_font,
                     bg=bg).pack(pady=3)

    def convert_wavelength(self):
        try:
            lam = float(self.wavelength.get()) * 1e-9
            c = 3e8
            h = 6.626e-34
            energy = h * c / lam
            self.wave_result.delete(1.0, tk.END)
            self.wave_result.insert(tk.END,
                f"波长: {self.wavelength.get()} nm\n能量: {energy:.2e} J\n"
                f"能量: {energy/1.602e-19:.2f} eV")
        except Exception:
            self.wave_result.delete(1.0, tk.END)
            self.wave_result.insert(tk.END, "输入错误")

    def show_kinetics(self):
        self.clear_content()
        self._set_page_title("化学动力学")
        self.update_status("化学动力学")
        bg = MODERN_COLORS['surface']
        tk.Label(self.content_frame, text="阿伦尼乌斯方程", font=H1_FONT,
                 fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 12))
        frame = tk.Frame(self.content_frame, bg=bg)
        frame.pack(pady=10)
        for i, (label, attr) in enumerate([
            ("活化能 Ea (J/mol):", 'ea_entry'),
            ("温度 T (K):", 'temp_kin'),
            ("指前因子 A:", 'a_factor'),
        ]):
            tk.Label(frame, text=label, bg=bg).grid(row=i, column=0, padx=8, pady=8, sticky=tk.W)
            e = ModernEntry(frame, width=15)
            e.grid(row=i, column=1, padx=8, pady=8, sticky=tk.EW)
            setattr(self, attr, e)
        RoundedButton(frame, text="计算速率常数",
                      command=self.calc_rate_constant,
                      width=160, height=40).grid(row=3, column=0, columnspan=2, pady=12)
        self.kinetics_result = tk.Text(self.content_frame, height=8, font=self.default_font,
                                       relief=tk.FLAT, bd=0,
                                       bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.kinetics_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        half_frame = tk.Frame(self.content_frame, bg=MODERN_COLORS['primary_light'])
        half_frame.pack(fill=tk.X, padx=20, pady=10, ipady=8)
        tk.Label(half_frame, text="半衰期:",
                 font=("Microsoft YaHei", 10, "bold"),
                 bg=MODERN_COLORS['primary_light'],
                 fg=MODERN_COLORS['primary']).pack(side=tk.LEFT, padx=12)
        tk.Label(half_frame, text="速率常数 k (1/s):",
                 bg=MODERN_COLORS['primary_light']).pack(side=tk.LEFT, padx=6)
        self.k_half = ModernEntry(half_frame, width=12)
        self.k_half.pack(side=tk.LEFT, padx=6)
        RoundedButton(half_frame, text="计算半衰期",
                      command=self.calc_half_life,
                      width=140, height=36, radius=6).pack(side=tk.LEFT, padx=8)
        self.half_result = tk.Label(half_frame, text="", font=self.default_font,
                                    bg=MODERN_COLORS['primary_light'],
                                    fg=MODERN_COLORS['primary'])
        self.half_result.pack(side=tk.LEFT, padx=10)

    def calc_rate_constant(self):
        try:
            ea, T, A = (float(self.ea_entry.get()),
                        float(self.temp_kin.get()),
                        float(self.a_factor.get()))
            R = 8.314
            k = A * np.exp(-ea / (R * T))
            self.kinetics_result.delete(1.0, tk.END)
            self.kinetics_result.insert(tk.END,
                f"k = A*exp(-Ea/RT)\nk = {A:.2e} * exp(-{ea:.2e}/{R:.3f}*{T:.2f})\n"
                f"k = {k:.2e} 1/s")
        except Exception:
            self.kinetics_result.delete(1.0, tk.END)
            self.kinetics_result.insert(tk.END, "输入错误")

    def calc_half_life(self):
        try:
            k = float(self.k_half.get())
            t_half = np.log(2) / k
            self.half_result.config(text=f"t1/2 = {t_half:.2f} s")
        except Exception:
            self.half_result.config(text="输入错误")

    def show_electrochem(self):
        self.clear_content()
        self._set_page_title("能斯特方程")
        tk.Label(self.content_frame, text="能斯特方程",
                 font=H1_FONT, fg=MODERN_COLORS['primary'],
                 bg=MODERN_COLORS['surface']).pack(pady=(0, 4))
        tk.Label(self.content_frame, text="E = E0 - (RT/nF) lnQ",
                 font=self.default_font, fg=MODERN_COLORS['text_muted'],
                 bg=MODERN_COLORS['surface']).pack(pady=(0, 12))
        frame = tk.Frame(self.content_frame, bg=MODERN_COLORS['surface'])
        frame.pack(pady=10)
        for i, (label, attr) in enumerate([
            ("标准电势 E0 (V):", 'e0_entry'),
            ("温度 T (K):", 'temp_nernst'),
            ("电子转移数 n:", 'n_electron'),
            ("反应商 Q:", 'q_value'),
        ]):
            tk.Label(frame, text=label, bg=MODERN_COLORS['surface']).grid(
                row=i, column=0, padx=8, pady=8, sticky=tk.W)
            e = ModernEntry(frame, width=15)
            e.grid(row=i, column=1, padx=8, pady=8, sticky=tk.EW)
            setattr(self, attr, e)
        RoundedButton(frame, text="计算电极电势", command=self.calc_nernst,
                      width=160, height=40).grid(row=4, column=0, columnspan=2, pady=12)
        self.nernst_result = tk.Text(self.content_frame, height=8,
                                     relief=tk.FLAT, bd=0,
                                     bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.nernst_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def calc_nernst(self):
        try:
            e0 = float(self.e0_entry.get())
            T = float(self.temp_nernst.get())
            n = float(self.n_electron.get())
            Q = float(self.q_value.get())
            R = 8.314
            F = 96485
            E = e0 - (R * T / (n * F)) * np.log(Q)
            self.nernst_result.delete(1.0, tk.END)
            self.nernst_result.insert(tk.END,
                f"E = E0 - (RT/nF) lnQ\n= {e0} - ({R}*{T}/{n}/{F}) ln({Q})\n= {E:.4f} V")
        except Exception:
            self.nernst_result.delete(1.0, tk.END)
            self.nernst_result.insert(tk.END, "输入错误")

    def show_equilibrium(self):
        self.clear_content()
        self._set_page_title("化学平衡计算")
        tk.Label(self.content_frame, text="化学平衡",
                 font=H1_FONT, fg=MODERN_COLORS['primary'],
                 bg=MODERN_COLORS['surface']).pack(pady=(0, 4))
        tk.Label(self.content_frame, text="dG0 = -RT lnK",
                 font=self.default_font, fg=MODERN_COLORS['text_muted'],
                 bg=MODERN_COLORS['surface']).pack(pady=(0, 12))
        frame = tk.Frame(self.content_frame, bg=MODERN_COLORS['surface'])
        frame.pack(pady=10)
        for i, (label, attr) in enumerate([
            ("温度 T (K):", 'temp_eq'),
            ("平衡常数 K:", 'k_eq'),
        ]):
            tk.Label(frame, text=label, bg=MODERN_COLORS['surface']).grid(
                row=i, column=0, padx=8, pady=8, sticky=tk.W)
            e = ModernEntry(frame, width=15)
            e.grid(row=i, column=1, padx=8, pady=8, sticky=tk.EW)
            setattr(self, attr, e)
        RoundedButton(frame, text="计算 dG0", command=self.calc_deltaG,
                      width=140, height=40).grid(row=2, column=0, columnspan=2, pady=12)
        self.eq_result = tk.Text(self.content_frame, height=8, relief=tk.FLAT, bd=0,
                                 bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.eq_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def calc_deltaG(self):
        try:
            T = float(self.temp_eq.get())
            K = float(self.k_eq.get())
            R = 8.314
            dG = -R * T * np.log(K)
            self.eq_result.delete(1.0, tk.END)
            self.eq_result.insert(tk.END,
                f"dG0 = -RT lnK\n= -{R} * {T} * ln({K})\n"
                f"= {dG:.2f} J/mol = {dG/1000:.2f} kJ/mol")
        except Exception:
            self.eq_result.delete(1.0, tk.END)
            self.eq_result.insert(tk.END, "输入错误")

    def show_thermodynamics(self):
        self.clear_content()
        self._set_page_title("热力学计算")
        tk.Label(self.content_frame, text="吉布斯自由能",
                 font=H1_FONT, fg=MODERN_COLORS['primary'],
                 bg=MODERN_COLORS['surface']).pack(pady=(0, 4))
        tk.Label(self.content_frame, text="dG = dH - T*dS",
                 font=self.default_font, fg=MODERN_COLORS['text_muted'],
                 bg=MODERN_COLORS['surface']).pack(pady=(0, 12))
        frame = tk.Frame(self.content_frame, bg=MODERN_COLORS['surface'])
        frame.pack(pady=10)
        for i, (label, attr) in enumerate([
            ("dH (kJ/mol):", 'dh'),
            ("dS (J/(mol*K)):", 'ds'),
            ("温度 T (K):", 'temp_thermo'),
        ]):
            tk.Label(frame, text=label, bg=MODERN_COLORS['surface']).grid(
                row=i, column=0, padx=8, pady=8, sticky=tk.W)
            e = ModernEntry(frame, width=15)
            e.grid(row=i, column=1, padx=8, pady=8, sticky=tk.EW)
            setattr(self, attr, e)
        RoundedButton(frame, text="计算 dG", command=self.calc_gibbs,
                      width=140, height=40).grid(row=3, column=0, columnspan=2, pady=12)
        self.thermo_result = tk.Text(self.content_frame, height=8, relief=tk.FLAT, bd=0,
                                     bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.thermo_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def calc_gibbs(self):
        try:
            H = float(self.dh.get()) * 1000
            S = float(self.ds.get())
            T = float(self.temp_thermo.get())
            G = H - T * S
            self.thermo_result.delete(1.0, tk.END)
            self.thermo_result.insert(tk.END,
                f"dG = dH - T*dS\n= {H/1000:.2f} kJ - {T} * {S:.2f} J/K\n= {G/1000:.2f} kJ/mol")
        except Exception:
            self.thermo_result.delete(1.0, tk.END)
            self.thermo_result.insert(tk.END, "输入错误")

    def show_partial_pressure(self):
        self.clear_content()
        self._set_page_title("气体分压计算")
        tk.Label(self.content_frame, text="道尔顿分压定律",
                 font=H1_FONT, fg=MODERN_COLORS['primary'],
                 bg=MODERN_COLORS['surface']).pack(pady=(0, 4))
        tk.Label(self.content_frame, text="P_total = sum(P_i)",
                 font=self.default_font, fg=MODERN_COLORS['text_muted'],
                 bg=MODERN_COLORS['surface']).pack(pady=(0, 12))
        frame = tk.Frame(self.content_frame, bg=MODERN_COLORS['surface'])
        frame.pack(pady=10)
        for i, (label, attr) in enumerate([
            ("总压 (atm):", 'total_p'),
            ("组分1摩尔分数:", 'mole_frac1'),
            ("组分2摩尔分数:", 'mole_frac2'),
        ]):
            tk.Label(frame, text=label, bg=MODERN_COLORS['surface']).grid(
                row=i, column=0, padx=8, pady=8, sticky=tk.W)
            e = ModernEntry(frame, width=15)
            e.grid(row=i, column=1, padx=8, pady=8, sticky=tk.EW)
            setattr(self, attr, e)
        RoundedButton(frame, text="计算分压", command=self.calc_partial_pressure,
                      width=140, height=40).grid(row=3, column=0, columnspan=2, pady=12)
        self.partial_result = tk.Text(self.content_frame, height=8, relief=tk.FLAT, bd=0,
                                      bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.partial_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def calc_partial_pressure(self):
        try:
            P = float(self.total_p.get())
            x1 = float(self.mole_frac1.get()) if self.mole_frac1.get() else 0
            x2 = float(self.mole_frac2.get()) if self.mole_frac2.get() else 0
            p1, p2 = P * x1, P * x2
            self.partial_result.delete(1.0, tk.END)
            self.partial_result.insert(tk.END,
                f"组分1分压: {p1:.4f} atm\n组分2分压: {p2:.4f} atm\n总和: {p1+p2:.4f} atm")
        except Exception:
            self.partial_result.delete(1.0, tk.END)
            self.partial_result.insert(tk.END, "输入错误")

    def show_nuclear(self):
        self.clear_content()
        self._set_page_title("核化学计算")
        tk.Label(self.content_frame, text="放射性衰变",
                 font=H1_FONT, fg=MODERN_COLORS['primary'],
                 bg=MODERN_COLORS['surface']).pack(pady=(0, 4))
        tk.Label(self.content_frame, text="N = N0 * exp(-lambda*t)",
                 font=self.default_font, fg=MODERN_COLORS['text_muted'],
                 bg=MODERN_COLORS['surface']).pack(pady=(0, 12))
        frame = tk.Frame(self.content_frame, bg=MODERN_COLORS['surface'])
        frame.pack(pady=10)
        for i, (label, attr) in enumerate([
            ("半衰期 t1/2 (s):", 'half_life'),
            ("初始原子数 N0:", 'n0'),
            ("经过时间 t (s):", 'time_nuclear'),
        ]):
            tk.Label(frame, text=label, bg=MODERN_COLORS['surface']).grid(
                row=i, column=0, padx=8, pady=8, sticky=tk.W)
            e = ModernEntry(frame, width=15)
            e.grid(row=i, column=1, padx=8, pady=8, sticky=tk.EW)
            setattr(self, attr, e)
        RoundedButton(frame, text="计算剩余原子数", command=self.calc_nuclear,
                      width=180, height=40).grid(row=3, column=0, columnspan=2, pady=12)
        self.nuclear_result = tk.Text(self.content_frame, height=8, relief=tk.FLAT, bd=0,
                                      bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.nuclear_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def calc_nuclear(self):
        try:
            t12 = float(self.half_life.get())
            N0 = float(self.n0.get())
            t = float(self.time_nuclear.get())
            lam = np.log(2) / t12
            N = N0 * np.exp(-lam * t)
            self.nuclear_result.delete(1.0, tk.END)
            self.nuclear_result.insert(tk.END,
                f"衰变常数 lambda = ln2 / t1/2 = {lam:.4e} 1/s\n"
                f"剩余原子数 N = N0 * exp(-lambda*t) = {N0} * exp(-{lam:.4e}*{t}) = {N:.2f}")
        except Exception:
            self.nuclear_result.delete(1.0, tk.END)
            self.nuclear_result.insert(tk.END, "输入错误")

    def show_solution_prep(self):
        self.clear_content()
        self._set_page_title("溶液配制计算")
        tk.Label(self.content_frame, text="溶液配制计算",
                 font=H1_FONT, fg=MODERN_COLORS['primary'],
                 bg=MODERN_COLORS['surface']).pack(pady=(0, 12))
        frame = tk.Frame(self.content_frame, bg=MODERN_COLORS['surface'])
        frame.pack(pady=10)
        for i, (label, attr) in enumerate([
            ("目标浓度 C (mol/L):", 'target_c'),
            ("目标体积 V (L):", 'target_v'),
            ("溶质摩尔质量 M (g/mol):", 'solute_m'),
        ]):
            tk.Label(frame, text=label, bg=MODERN_COLORS['surface']).grid(
                row=i, column=0, padx=8, pady=8, sticky=tk.W)
            e = ModernEntry(frame, width=15)
            e.grid(row=i, column=1, padx=8, pady=8, sticky=tk.EW)
            setattr(self, attr, e)
        RoundedButton(frame, text="计算所需溶质质量",
                      command=self.calc_solution_prep,
                      width=180, height=40).grid(row=3, column=0, columnspan=2, pady=12)
        self.prep_result = tk.Text(self.content_frame, height=6, relief=tk.FLAT, bd=0,
                                   bg=MODERN_COLORS['bg'], padx=12, pady=10)
        self.prep_result.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def calc_solution_prep(self):
        try:
            C = float(self.target_c.get())
            V = float(self.target_v.get())
            M = float(self.solute_m.get())
            mass = C * V * M
            self.prep_result.delete(1.0, tk.END)
            self.prep_result.insert(tk.END,
                f"所需溶质质量 = C * V * M = {C} * {V} * {M} = {mass:.4f} g")
        except Exception:
            self.prep_result.delete(1.0, tk.END)
            self.prep_result.insert(tk.END, "输入错误")

    # ==================== 公式计算引擎 ====================
    def _col_to_idx(self, col_str):
        c = 0
        for char in col_str:
            c = c * 26 + (ord(char) - ord('A') + 1)
        return c - 1

    def _parse_cell_ref(self, ref):
        m = re.match(r'([A-Z]+)([0-9]+)', ref)
        if not m:
            return -1, -1
        c = self._col_to_idx(m.group(1))
        r = int(m.group(2)) - 1
        return r, c

    def _flatten(self, args):
        res = []
        for x in args:
            if isinstance(x, (list, tuple)):
                res.extend(x)
            else:
                res.append(x)
        return res

    def _eval_range(self, r1, c1, r2, c2, stack, current_cache, old_cache):
        min_r, max_r = min(r1, r2), max(r1, r2)
        min_c, max_c = min(c1, c2), max(c1, c2)
        vals = []
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                vals.append(self._get_cell_value(r, c, stack, current_cache, old_cache))
        return vals

    def _eval_formula(self, formula, stack, current_cache, old_cache):
        expr = formula[1:] # 去掉 '='
        
        def range_repl(m):
            r1, c1 = self._parse_cell_ref(m.group(1) + m.group(2))
            r2, c2 = self._parse_cell_ref(m.group(3) + m.group(4))
            if r1 == -1 or r2 == -1:
                return "None"
            return str(self._eval_range(r1, c1, r2, c2, stack, current_cache, old_cache))
            
        expr = re.sub(r'\b([A-Z]+)([0-9]+):([A-Z]+)([0-9]+)\b', range_repl, expr)
        
        def cell_repl(m):
            r, c = self._parse_cell_ref(m.group(1) + m.group(2))
            if r == -1:
                return "None"
            val = self._get_cell_value(r, c, stack, current_cache, old_cache)
            if val == "":
                val = 0
            return repr(val)
            
        expr = re.sub(r'\b([A-Z]+)([0-9]+)\b', cell_repl, expr)
        
        # 支持全角符号
        expr = expr.replace('（', '(').replace('）', ')').replace('，', ',').replace('＋', '+').replace('－', '-').replace('＊', '*').replace('／', '/')
        
        env = {
            'SUM': lambda *args: sum([x for x in self._flatten(args) if isinstance(x, (int, float))]),
            'AVERAGE': lambda *args: sum([x for x in self._flatten(args) if isinstance(x, (int, float))]) / len([x for x in self._flatten(args) if isinstance(x, (int, float))]) if len([x for x in self._flatten(args) if isinstance(x, (int, float))]) > 0 else 0,
            'MAX': lambda *args: max([x for x in self._flatten(args) if isinstance(x, (int, float))]) if len([x for x in self._flatten(args) if isinstance(x, (int, float))]) > 0 else 0,
            'MIN': lambda *args: min([x for x in self._flatten(args) if isinstance(x, (int, float))]) if len([x for x in self._flatten(args) if isinstance(x, (int, float))]) > 0 else 0,
            'COUNT': lambda *args: len([x for x in self._flatten(args) if isinstance(x, (int, float))]),
            'IF': lambda cond, t, f: t if cond else f,
            'ABS': abs, 'ROUND': round,
            'SIN': sin, 'COS': cos, 'TAN': tan, 'LOG': log,
            'SQRT': sqrt, 'POWER': pow
        }
        
        return eval(expr, {"__builtins__": None}, env)

    def _get_cell_value(self, r, c, stack, current_cache, old_cache):
        if (r, c) in stack:
            if hasattr(self, 'enable_iteration_var') and self.enable_iteration_var and self.enable_iteration_var.get():
                return old_cache.get((r, c), 0)
            else:
                return "#CIRC!"
        
        if (r, c) in current_cache:
            return current_cache[(r, c)]
            
        stack.add((r, c))
        try:
            text = str(self.table_cells.get((r, c), {}).get('text', '')).strip()
            if not text:
                val = 0
            elif text.startswith('='):
                try:
                    val = self._eval_formula(text, stack, current_cache, old_cache)
                    if isinstance(val, float) and val.is_integer():
                        val = int(val)
                except Exception:
                    val = "#ERR!"
            else:
                try:
                    val = float(text)
                    if val.is_integer():
                        val = int(val)
                except ValueError:
                    val = text
            
            current_cache[(r, c)] = val
            return val
        finally:
            stack.remove((r, c))

    def evaluate_all_cells(self):
        old_cache = self.cell_cache
        self.cell_cache = {}
        
        enable_iter = self.enable_iteration_var.get() if hasattr(self, 'enable_iteration_var') and self.enable_iteration_var else False
        
        if enable_iter:
            try:
                max_iter = int(self.max_iter_var.get())
                tol = float(self.tolerance_var.get())
            except:
                max_iter = 100
                tol = 0.001
                
            for _ in range(max_iter):
                current_cache = {}
                max_diff = 0
                for r in range(self.table_rows):
                    for c in range(self.table_cols):
                        val = self._get_cell_value(r, c, set(), current_cache, old_cache)
                        old_val = old_cache.get((r, c), 0)
                        if isinstance(val, (int, float)) and isinstance(old_val, (int, float)):
                            max_diff = max(max_diff, abs(val - old_val))
                self.cell_cache = current_cache
                old_cache = current_cache
                if max_diff < tol:
                    break
        else:
            for r in range(self.table_rows):
                for c in range(self.table_cols):
                    self._get_cell_value(r, c, set(), self.cell_cache, old_cache)
                    
        self.display_cache = {}
        for r in range(self.table_rows):
            for c in range(self.table_cols):
                raw_text = str(self.table_cells.get((r, c), {}).get('text', ''))
                if raw_text == '':
                    self.display_cache[(r, c)] = ''
                    continue
                
                val = self.cell_cache.get((r, c), '')
                if isinstance(val, float):
                    if val.is_integer():
                        val = int(val)
                    else:
                        val = float(f"{val:.6g}")
                self.display_cache[(r, c)] = str(val)

    # ==================== 填充柄算法 ====================
    def _translate_formula(self, formula, dr, dc):
        """平移公式中的相对引用"""
        if not formula.startswith('='):
            return formula
            
        def repl(m):
            col_str = m.group(1)
            row_str = m.group(2)
            
            if col_str in ('SUM', 'AVERAGE', 'MAX', 'MIN', 'COUNT', 'IF', 'ABS', 'ROUND', 'SIN', 'COS', 'TAN', 'LOG', 'SQRT', 'POWER'):
                return m.group(0)
                
            c = self._col_to_idx(col_str)
            r = int(row_str) - 1
            
            new_r = r + dr
            new_c = c + dc
            
            if new_r < 0 or new_c < 0:
                return "#REF!"
                
            return f"{self._col_label(new_c)}{new_r + 1}"
            
        return re.sub(r'\b([A-Z]+)([0-9]+)\b', repl, formula)

    def _match_seq(self, text):
        for seq in TEXT_SEQUENCES:
            if text in seq:
                return seq, seq.index(text)
        return None, -1

    def _fill_cells(self, start_cell, end_cell, target_cell):
        min_r, max_r = min(start_cell[0], end_cell[0]), max(start_cell[0], end_cell[0])
        min_c, max_c = min(start_cell[1], end_cell[1]), max(start_cell[1], end_cell[1])
        
        src_h = max_r - min_r + 1
        src_w = max_c - min_c + 1
        
        tgt_r, tgt_c = target_cell
        
        if tgt_r > max_r: # 向下填充
            dest_min_r = max_r + 1
            dest_max_r = tgt_r
            dest_min_c = min_c
            dest_max_c = max_c
            
            for r in range(dest_min_r, dest_max_r + 1):
                for c in range(dest_min_c, dest_max_c + 1):
                    src_r = min_r + (r - min_r) % src_h
                    src_c = min_c + (c - min_c) % src_w
                    
                    src_data = self.table_cells.get((src_r, src_c), {})
                    src_text = str(src_data.get('text', ''))
                    
                    new_text = src_text
                    if src_text.startswith('='):
                        dr = r - src_r
                        new_text = self._translate_formula(src_text, dr, 0)
                    elif _is_number_str(src_text) and src_h > 1:
                        try:
                            top_val = float(self.table_cells.get((min_r, src_c), {}).get('text', 0))
                            bot_val = float(self.table_cells.get((max_r, src_c), {}).get('text', 0))
                            step = (bot_val - top_val) / (src_h - 1) if src_h > 1 else 0
                            new_val = bot_val + step * (r - max_r)
                            new_text = _to_str(new_val)
                        except:
                            pass
                    else:
                        # 文本序列判断
                        col_texts = []
                        for rr in range(min_r, max_r + 1):
                            col_texts.append(str(self.table_cells.get((rr, src_c), {}).get('text', '')))
                        seq = None
                        idxs = []
                        for txt in col_texts:
                            s, i = self._match_seq(txt)
                            if s:
                                seq = s
                                idxs.append(i)
                            else:
                                break
                        if len(idxs) == len(col_texts) and seq:
                            if len(idxs) == 1:
                                step = 1
                            else:
                                step = idxs[-1] - idxs[-2]
                                if step <= 0: step += len(seq)
                            offset = r - max_r
                            new_idx = (idxs[-1] + step * offset) % len(seq)
                            new_text = seq[new_idx]
                            
                    self.table_cells.setdefault((r, c), {})['text'] = new_text
                    
        elif tgt_r < min_r: # 向上填充
            dest_min_r = tgt_r
            dest_max_r = min_r - 1
            dest_min_c = min_c
            dest_max_c = max_c
            
            for r in range(dest_min_r, dest_max_r + 1):
                for c in range(dest_min_c, dest_max_c + 1):
                    src_r = max_r - (max_r - r) % src_h
                    src_c = min_c + (c - min_c) % src_w
                    
                    src_data = self.table_cells.get((src_r, src_c), {})
                    src_text = str(src_data.get('text', ''))
                    
                    new_text = src_text
                    if src_text.startswith('='):
                        dr = r - src_r
                        new_text = self._translate_formula(src_text, dr, 0)
                    elif _is_number_str(src_text) and src_h > 1:
                        try:
                            top_val = float(self.table_cells.get((min_r, src_c), {}).get('text', 0))
                            bot_val = float(self.table_cells.get((max_r, src_c), {}).get('text', 0))
                            step = (bot_val - top_val) / (src_h - 1) if src_h > 1 else 0
                            new_val = top_val - step * (min_r - r)
                            new_text = _to_str(new_val)
                        except:
                            pass
                    else:
                        col_texts = []
                        for rr in range(min_r, max_r + 1):
                            col_texts.append(str(self.table_cells.get((rr, src_c), {}).get('text', '')))
                        seq = None
                        idxs = []
                        for txt in col_texts:
                            s, i = self._match_seq(txt)
                            if s:
                                seq = s
                                idxs.append(i)
                            else:
                                break
                        if len(idxs) == len(col_texts) and seq:
                            if len(idxs) == 1:
                                step = 1
                            else:
                                step = idxs[1] - idxs[0]
                                if step <= 0: step += len(seq)
                            offset = r - min_r
                            new_idx = (idxs[0] + step * offset) % len(seq)
                            new_text = seq[new_idx]
                            
                    self.table_cells.setdefault((r, c), {})['text'] = new_text
                    
        elif tgt_c > max_c: # 向右填充
            dest_min_r = min_r
            dest_max_r = max_r
            dest_min_c = max_c + 1
            dest_max_c = tgt_c
            
            for r in range(dest_min_r, dest_max_r + 1):
                for c in range(dest_min_c, dest_max_c + 1):
                    src_r = min_r + (r - min_r) % src_h
                    src_c = min_c + (c - min_c) % src_w
                    
                    src_data = self.table_cells.get((src_r, src_c), {})
                    src_text = str(src_data.get('text', ''))
                    
                    new_text = src_text
                    if src_text.startswith('='):
                        dc = c - src_c
                        new_text = self._translate_formula(src_text, 0, dc)
                    elif _is_number_str(src_text) and src_w > 1:
                        try:
                            left_val = float(self.table_cells.get((src_r, min_c), {}).get('text', 0))
                            right_val = float(self.table_cells.get((src_r, max_c), {}).get('text', 0))
                            step = (right_val - left_val) / (src_w - 1) if src_w > 1 else 0
                            new_val = right_val + step * (c - max_c)
                            new_text = _to_str(new_val)
                        except:
                            pass
                    else:
                        row_texts = []
                        for cc in range(min_c, max_c + 1):
                            row_texts.append(str(self.table_cells.get((src_r, cc), {}).get('text', '')))
                        seq = None
                        idxs = []
                        for txt in row_texts:
                            s, i = self._match_seq(txt)
                            if s:
                                seq = s
                                idxs.append(i)
                            else:
                                break
                        if len(idxs) == len(row_texts) and seq:
                            if len(idxs) == 1:
                                step = 1
                            else:
                                step = idxs[-1] - idxs[-2]
                                if step <= 0: step += len(seq)
                            offset = c - max_c
                            new_idx = (idxs[-1] + step * offset) % len(seq)
                            new_text = seq[new_idx]
                            
                    self.table_cells.setdefault((r, c), {})['text'] = new_text
                    
        elif tgt_c < min_c: # 向左填充
            dest_min_r = min_r
            dest_max_r = max_r
            dest_min_c = tgt_c
            dest_max_c = min_c - 1
            
            for r in range(dest_min_r, dest_max_r + 1):
                for c in range(dest_min_c, dest_max_c + 1):
                    src_r = min_r + (r - min_r) % src_h
                    src_c = max_c - (max_c - c) % src_w
                    
                    src_data = self.table_cells.get((src_r, src_c), {})
                    src_text = str(src_data.get('text', ''))
                    
                    new_text = src_text
                    if src_text.startswith('='):
                        dc = c - src_c
                        new_text = self._translate_formula(src_text, 0, dc)
                    elif _is_number_str(src_text) and src_w > 1:
                        try:
                            left_val = float(self.table_cells.get((src_r, min_c), {}).get('text', 0))
                            right_val = float(self.table_cells.get((src_r, max_c), {}).get('text', 0))
                            step = (right_val - left_val) / (src_w - 1) if src_w > 1 else 0
                            new_val = left_val - step * (min_c - c)
                            new_text = _to_str(new_val)
                        except:
                            pass
                    else:
                        row_texts = []
                        for cc in range(min_c, max_c + 1):
                            row_texts.append(str(self.table_cells.get((src_r, cc), {}).get('text', '')))
                        seq = None
                        idxs = []
                        for txt in row_texts:
                            s, i = self._match_seq(txt)
                            if s:
                                seq = s
                                idxs.append(i)
                            else:
                                break
                        if len(idxs) == len(row_texts) and seq:
                            if len(idxs) == 1:
                                step = 1
                            else:
                                step = idxs[1] - idxs[0]
                                if step <= 0: step += len(seq)
                            offset = c - min_c
                            new_idx = (idxs[0] + step * offset) % len(seq)
                            new_text = seq[new_idx]
                            
                    self.table_cells.setdefault((r, c), {})['text'] = new_text

    # ==================== CTB 表格 ====================
    def show_ctb_table(self):
        self.clear_content()
        self._set_page_title("CTB 表格")
        self.update_status("CTB 表格 - 支持公式与图表 (v5.0)")
        bg = MODERN_COLORS['surface']

        header_frame = tk.Frame(self.content_frame, bg=bg)
        header_frame.pack(fill=tk.X, pady=(0, 4))
        tk.Label(header_frame, text="CTB 表格", font=H1_FONT,
                 fg=MODERN_COLORS['primary'], bg=bg).pack(side=tk.LEFT)
        tk.Label(header_frame, text=" 类似 Excel 的表格制作工具",
                 font=self.default_font, fg=MODERN_COLORS['text_muted'],
                 bg=bg).pack(side=tk.LEFT, pady=(8, 0))

        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.X, padx=2, pady=(0, 4))

        file_tab = tk.Frame(notebook, bg=bg)
        notebook.add(file_tab, text="文件")
        self._build_table_file_tab(file_tab)

        fmt_tab = tk.Frame(notebook, bg=bg)
        notebook.add(fmt_tab, text="格式")
        self._build_table_format_tab(fmt_tab)

        func_tab = tk.Frame(notebook, bg=bg)
        notebook.add(func_tab, text="公式")
        self._build_table_formula_tab(func_tab)

        chart_tab = tk.Frame(notebook, bg=bg)
        notebook.add(chart_tab, text="插入图表")
        self._build_table_chart_tab(chart_tab)

        set_tab = tk.Frame(notebook, bg=bg)
        notebook.add(set_tab, text="设置")
        self._build_table_settings_tab(set_tab)

        # 公式栏区域 (紧凑设计)
        formula_bar_frame = tk.Frame(self.content_frame, bg=bg)
        formula_bar_frame.pack(fill=tk.X, padx=2, pady=(2, 2))
        
        self.cell_ref_var = tk.StringVar(value="A1")
        name_box = tk.Entry(formula_bar_frame, textvariable=self.cell_ref_var, width=8,
                            font=("Consolas", 10), relief=tk.FLAT, bd=1,
                            bg="#F9F9F9", justify=tk.CENTER, state='readonly')
        name_box.pack(side=tk.LEFT, padx=(0, 4))

        tk.Label(formula_bar_frame, text="fx", font=("Times New Roman", 12, "italic"),
                 fg=MODERN_COLORS['text_muted'], bg=bg).pack(side=tk.LEFT, padx=4)

        self.formula_bar_var = tk.StringVar()
        self.formula_entry = tk.Entry(formula_bar_frame, textvariable=self.formula_bar_var,
                                      font=("Microsoft YaHei", 10), relief=tk.SOLID, bd=1)
        self.formula_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=2)
        self.formula_entry.bind('<Return>', self._on_formula_bar_enter)
        self.formula_entry.bind('<FocusIn>', lambda e: setattr(self, 'active_editor', 'bar'))

        # 表格画布区域
        grid_outer = tk.Frame(self.content_frame, bg=MODERN_COLORS['border'])
        grid_outer.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Canvas 需要 takefocus=True 才能接收键盘事件
        self.table_canvas = tk.Canvas(grid_outer, bg=MODERN_COLORS['surface'], highlightthickness=0, takefocus=True)
        vbar = tk.Scrollbar(grid_outer, orient=tk.VERTICAL, command=self.table_canvas.yview)
        hbar = tk.Scrollbar(grid_outer, orient=tk.HORIZONTAL, command=self.table_canvas.xview)

        self.table_canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        self.table_canvas.grid(row=0, column=0, sticky='nsew')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='ew')
        grid_outer.grid_rowconfigure(0, weight=1)
        grid_outer.grid_columnconfigure(0, weight=1)

        # Canvas 事件绑定
        self.table_canvas.bind("<Button-1>", self._on_canvas_click)
        self.table_canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.table_canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.table_canvas.bind("<Double-Button-1>", self._on_canvas_double_click)
        self.table_canvas.bind("<Configure>", lambda e: self._draw_table())
        self.table_canvas.bind("<Key>", self._on_canvas_key)
        # 绑定独立的滚轮事件
        self.table_canvas.bind("<MouseWheel>", self._on_table_wheel)
        self.table_canvas.bind("<Button-4>", self._on_table_wheel_linux)
        self.table_canvas.bind("<Button-5>", self._on_table_wheel_linux)
        
        # 右键菜单绑定 (用于图表设置)
        self.table_canvas.bind("<Button-3>", self._on_canvas_right_click)

        # 初始化图表列表和合并区域
        self.table_charts = []
        self.merged_cells = []
        self.selected_chart = None

        self.evaluate_all_cells()
        self._draw_table()

    def _on_table_wheel(self, event):
        if event.state & 0x0001: # Shift键按下
            self.table_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            self.table_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
    def _on_table_wheel_linux(self, event):
        if event.num == 4:
            self.table_canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.table_canvas.yview_scroll(3, "units")

    def _on_canvas_right_click(self, event):
        x = self.table_canvas.canvasx(event.x)
        y = self.table_canvas.canvasy(event.y)
        
        # 检测是否点中了图表
        for chart in self.table_charts:
            cx, cy, cw, ch = chart['x'], chart['y'], chart['w'], chart['h']
            if cx <= x <= cx + cw and cy <= y <= cy + ch:
                self._show_chart_context_menu(event, chart)
                return

    def _show_chart_context_menu(self, event, chart):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="编辑标题", command=lambda: self._edit_chart_title(chart))
        menu.add_command(label="编辑图例", command=lambda: self._edit_chart_legend(chart))
        menu.add_command(label="更改颜色", command=lambda: self._change_chart_color(chart))
        menu.add_separator()
        menu.add_command(label="删除图表", command=lambda: self._delete_chart(chart))
        menu.post(event.x_root, event.y_root)

    def _edit_chart_title(self, chart):
        new_title = simpledialog.askstring("编辑图表", "请输入图表标题:", initialvalue=chart.get('title', '数据图表'))
        if new_title is not None:
            chart['title'] = new_title
            self._draw_table()

    def _edit_chart_legend(self, chart):
        c_type = chart['type']
        if c_type == 'pie':
            # 饼图：编辑分类标签
            data = self._get_chart_data(chart)
            if not data:
                messagebox.showwarning("提示", "当前图表没有数据。")
                return
                
            current_cats = chart.get('categories', [d[0] for d in data])
            if len(current_cats) != len(data):
                current_cats = [d[0] for d in data]
                
            legend_str = simpledialog.askstring("编辑图例", "请输入分类名称（用英文逗号分隔）:", initialvalue=",".join(current_cats))
            if legend_str is not None:
                new_cats = [s.strip() for s in legend_str.split(',')]
                if len(new_cats) == len(data):
                    chart['categories'] = new_cats
                    self._draw_table()
                else:
                    messagebox.showwarning("提示", f"图例数量（{len(new_cats)}）与数据点数量（{len(data)}）不匹配。")
        else:
            # 柱状图/折线图：编辑系列图例名称
            new_legend = simpledialog.askstring("编辑图例", "请输入数据系列名称（Y轴指标）:", initialvalue=chart.get('legend_name', '数值'))
            if new_legend is not None:
                chart['legend_name'] = new_legend
                self._draw_table()

    def _change_chart_color(self, chart):
        color = colorchooser.askcolor(title="选择图表主色调")[1]
        if color:
            chart['colors'] = [color] * 20 # 存储一组颜色
            self._draw_table()

    def _delete_chart(self, chart):
        if chart in self.table_charts:
            self.table_charts.remove(chart)
            self.selected_chart = None
            self._draw_table()

    def _get_chart_data(self, chart):
        min_r, max_r = chart['min_r'], chart['max_r']
        min_c, max_c = chart['min_c'], chart['max_c']
        
        # 智能判断表头行（只在除了第一列之外的数据列中寻找）
        has_header_row = False
        if max_r > min_r and max_c > min_c:
            first_row_has_text_in_num_cols = False
            second_row_has_num = False
            for c in range(min_c + 1, max_c + 1):
                v1 = self.cell_cache.get((min_r, c), '')
                v2 = self.cell_cache.get((min_r + 1, c), '')
                if isinstance(v1, str) and v1.strip() != '':
                    first_row_has_text_in_num_cols = True
                if isinstance(v2, (int, float)):
                    second_row_has_num = True
            if first_row_has_text_in_num_cols and second_row_has_num:
                has_header_row = True

        start_r = min_r + 1 if has_header_row else min_r
        
        # 寻找数值列（Y轴）
        y_cols = []
        for c in range(min_c, max_c + 1):
            has_num = False
            for r in range(start_r, max_r + 1):
                v = self.cell_cache.get((r, c), '')
                if isinstance(v, (int, float)):
                    has_num = True
                    break
            if has_num:
                y_cols.append(c)
                
        if not y_cols:
            return []
            
        # 确定 X 轴（分类）
        x_col = min_c
        if x_col in y_cols:
            x_col = None
            
        # 默认取第一个数值列作为 Y 轴
        y_col = y_cols[0]
        
        data = []
        for r in range(start_r, max_r + 1):
            if x_col is not None:
                cat = self.display_cache.get((r, x_col), '').strip()
                if not cat:
                    cat = str(r - start_r + 1)
            else:
                cat = str(r - start_r + 1)
                
            val = self.cell_cache.get((r, y_col), '')
            if isinstance(val, (int, float)):
                data.append((cat, val))
                
        # 如果有表头，自动更新图例名
        if has_header_row and x_col is not None and y_col is not None:
            header_val = self.display_cache.get((min_r, y_col), '')
            if header_val and not _is_number_str(header_val):
                chart['legend_name'] = header_val
                
        return data

    def _on_formula_bar_enter(self, event=None):
        if not self.selected_cells:
            return
        r, c = sorted(self.selected_cells)[0]
        self.table_cells.setdefault((r, c), {})['text'] = self.formula_bar_var.get()
        self.evaluate_all_cells()
        self._draw_table()
        self.table_canvas.focus_set()

    def _build_table_file_tab(self, parent):
        bg = MODERN_COLORS['surface']
        row1 = tk.Frame(parent, bg=bg)
        row1.pack(fill=tk.X, padx=4, pady=(4, 2))
        tk.Label(row1, text="导入:", bg=bg, font=self.default_font).pack(side=tk.LEFT, padx=(0, 4))
        RoundedButton(row1, text="导入 .ctbt", command=self.import_ctbt_table,
                      width=110, height=24, radius=4,
                      bg=MODERN_COLORS['primary_light'],
                      fg=MODERN_COLORS['primary'],
                      hover_bg='#D0E4F7').pack(side=tk.LEFT, padx=2)
        RoundedButton(row1, text="导入 Excel", command=self.import_excel_table,
                      width=110, height=24, radius=4,
                      bg=MODERN_COLORS['primary_light'],
                      fg=MODERN_COLORS['primary'],
                      hover_bg='#D0E4F7').pack(side=tk.LEFT, padx=2)

        row2 = tk.Frame(parent, bg=bg)
        row2.pack(fill=tk.X, padx=4, pady=2)
        tk.Label(row2, text="导出:", bg=bg, font=self.default_font).pack(side=tk.LEFT, padx=(0, 4))
        RoundedButton(row2, text="导出 .ctbt", command=self.export_ctbt_table,
                      width=110, height=24, radius=4).pack(side=tk.LEFT, padx=2)
        RoundedButton(row2, text="导出 Excel", command=self.export_excel_table,
                      width=110, height=24, radius=4).pack(side=tk.LEFT, padx=2)

        row3 = tk.Frame(parent, bg=bg)
        row3.pack(fill=tk.X, padx=4, pady=(2, 6))
        RoundedButton(row3, text="清空表格", command=self.clear_table,
                      width=110, height=24, radius=4,
                      bg=MODERN_COLORS['danger']).pack(side=tk.LEFT, padx=2)
        RoundedButton(row3, text="增加行", command=lambda: self._add_table_row(1),
                      width=90, height=24, radius=4).pack(side=tk.LEFT, padx=2)
        RoundedButton(row3, text="增加列", command=lambda: self._add_table_col(1),
                      width=90, height=24, radius=4).pack(side=tk.LEFT, padx=2)

    def _build_table_format_tab(self, parent):
        bg = MODERN_COLORS['surface']

        row1 = tk.Frame(parent, bg=bg)
        row1.pack(fill=tk.X, padx=4, pady=(4, 2))
        tk.Label(row1, text="行高:", bg=bg, font=self.default_font).pack(side=tk.LEFT, padx=(0, 2))
        self.table_row_h_var = tk.StringVar(value=str(self.table_row_height))
        tk.Spinbox(row1, from_=14, to=200, textvariable=self.table_row_h_var,
                   width=5).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(row1, text="列宽:", bg=bg, font=self.default_font).pack(side=tk.LEFT, padx=(0, 2))
        self.table_col_w_var = tk.StringVar(value=str(self.table_col_width))
        tk.Spinbox(row1, from_=30, to=800, textvariable=self.table_col_w_var,
                   width=5).pack(side=tk.LEFT, padx=(0, 8))
        RoundedButton(row1, text="应用尺寸", command=self._apply_table_size,
                      width=90, height=24, radius=4).pack(side=tk.LEFT, padx=2)

        row2 = tk.Frame(parent, bg=bg)
        row2.pack(fill=tk.X, padx=4, pady=2)
        tk.Label(row2, text="字体:", bg=bg, font=self.default_font).pack(side=tk.LEFT, padx=(0, 2))
        self.table_font_var = tk.StringVar(value="Microsoft YaHei")
        ttk.Combobox(row2, textvariable=self.table_font_var, width=14,
                     values=["Microsoft YaHei", "SimSun", "SimHei", "KaiTi",
                             "FangSong", "Consolas", "Courier New",
                             "Arial", "Times New Roman"]).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(row2, text="字号:", bg=bg, font=self.default_font).pack(side=tk.LEFT, padx=(0, 2))
        self.table_size_var = tk.StringVar(value="10")
        tk.Spinbox(row2, from_=6, to=72, textvariable=self.table_size_var,
                   width=4).pack(side=tk.LEFT, padx=(0, 6))
        self.table_bold_var = tk.BooleanVar(value=False)
        tk.Checkbutton(row2, text="加粗", variable=self.table_bold_var,
                       bg=bg, activebackground=bg, selectcolor=bg).pack(side=tk.LEFT, padx=(0, 6))
        RoundedButton(row2, text="应用字体", command=self._apply_table_format,
                      width=90, height=24, radius=4).pack(side=tk.LEFT, padx=2)

        row3 = tk.Frame(parent, bg=bg)
        row3.pack(fill=tk.X, padx=4, pady=(2, 6))
        tk.Label(row3, text="字体颜色:", bg=bg, font=self.default_font).pack(side=tk.LEFT, padx=(0, 2))
        self.table_fg_btn = RoundedButton(row3, text="选择", command=self._choose_fg_color,
                                          width=60, height=24, radius=4, bg="#E0E0E0", fg="#333333")
        self.table_fg_btn.pack(side=tk.LEFT, padx=(0, 4))
        tk.Label(row3, text="背景颜色:", bg=bg, font=self.default_font).pack(side=tk.LEFT, padx=(0, 2))
        self.table_bg_btn = RoundedButton(row3, text="选择", command=self._choose_bg_color,
                                          width=60, height=24, radius=4, bg="#E0E0E0", fg="#333333")
        self.table_bg_btn.pack(side=tk.LEFT, padx=(0, 4))
        RoundedButton(row3, text="清除颜色", command=self._clear_table_colors,
                      width=90, height=24, radius=4,
                      bg=MODERN_COLORS['danger']).pack(side=tk.LEFT, padx=2)

        row4 = tk.Frame(parent, bg=bg)
        row4.pack(fill=tk.X, padx=4, pady=2)
        tk.Label(row4, text="数据类型:", bg=bg, font=self.default_font).pack(side=tk.LEFT, padx=(0, 2))
        self.table_dtype_var = tk.StringVar(value="auto")
        ttk.Combobox(row4, textvariable=self.table_dtype_var, width=10, state="readonly",
                     values=["auto", "number", "text"]).pack(side=tk.LEFT, padx=(0, 6))
        
        tk.Label(row4, text="对齐方式:", bg=bg, font=self.default_font).pack(side=tk.LEFT, padx=(8, 2))
        self.table_align_var = tk.StringVar(value="auto")
        ttk.Combobox(row4, textvariable=self.table_align_var, width=8, state="readonly",
                     values=["auto", "left", "center", "right"]).pack(side=tk.LEFT, padx=(0, 6))

        RoundedButton(row4, text="应用格式", command=self._apply_table_format,
                      width=90, height=24, radius=4,
                      bg=MODERN_COLORS['success']).pack(side=tk.LEFT, padx=2)
        
        # 合并单元格功能
        row5 = tk.Frame(parent, bg=bg)
        row5.pack(fill=tk.X, padx=4, pady=(2, 6))
        RoundedButton(row5, text="合并居中", command=lambda: self._merge_cells(True),
                      width=90, height=24, radius=4).pack(side=tk.LEFT, padx=2)
        RoundedButton(row5, text="只合并不居中", command=lambda: self._merge_cells(False),
                      width=110, height=24, radius=4).pack(side=tk.LEFT, padx=2)
        RoundedButton(row5, text="取消合并", command=self._unmerge_cells,
                      width=90, height=24, radius=4,
                      bg=MODERN_COLORS['danger']).pack(side=tk.LEFT, padx=2)
        
        tk.Label(parent,
                 text="提示：auto 将根据内容智能判断（文本左对齐带绿角，数字右对齐）。\n"
                      "可在表格内拖拽鼠标框选多个单元格，再统一应用格式。",
                 bg=bg, font=("Microsoft YaHei", 9),
                 fg=MODERN_COLORS['text_muted'], justify=tk.LEFT).pack(side=tk.LEFT, padx=4, pady=4)

    def _merge_cells(self, center=True):
        if not self.selected_cells or len(self.selected_cells) < 2:
            messagebox.showinfo("提示", "请选择至少两个单元格进行合并。")
            return
            
        min_r = min(r for r, c in self.selected_cells)
        max_r = max(r for r, c in self.selected_cells)
        min_c = min(c for r, c in self.selected_cells)
        max_c = max(c for r, c in self.selected_cells)
        
        # 移除重叠的旧合并区
        new_merged = []
        for m in self.merged_cells:
            m_min_r, m_min_c, m_max_r, m_max_c = m
            # 如果不重叠，保留
            if m_max_r < min_r or m_min_r > max_r or m_max_c < min_c or m_min_c > max_c:
                new_merged.append(m)
        self.merged_cells = new_merged
        
        # 添加新合并区
        self.merged_cells.append((min_r, min_c, max_r, max_c))
        
        # 只有左上角保留文字，其他清空（防止后续绘制混淆）
        top_left_text = self.table_cells.get((min_r, min_c), {}).get('text', '')
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                if (r, c) != (min_r, min_c):
                    if (r, c) in self.table_cells:
                        self.table_cells[(r, c)]['text'] = ''
                        
        # 设置对齐方式
        if center:
            for r in range(min_r, max_r + 1):
                for c in range(min_c, max_c + 1):
                    d = self.table_cells.setdefault((r, c), {})
                    d['align'] = 'center'
        else:
            for r in range(min_r, max_r + 1):
                for c in range(min_c, max_c + 1):
                    d = self.table_cells.setdefault((r, c), {})
                    d['align'] = 'left'
                    
        self.evaluate_all_cells()
        self._draw_table()
        self.update_status("已合并单元格")

    def _unmerge_cells(self):
        if not self.selected_cells:
            messagebox.showinfo("提示", "请先选择要取消合并的区域。")
            return
            
        min_r = min(r for r, c in self.selected_cells)
        max_r = max(r for r, c in self.selected_cells)
        min_c = min(c for r, c in self.selected_cells)
        max_c = max(c for r, c in self.selected_cells)
        
        new_merged = []
        for m in self.merged_cells:
            m_min_r, m_min_c, m_max_r, m_max_c = m
            # 如果完全在选中区域内，则移除
            if m_min_r >= min_r and m_max_r <= max_r and m_min_c >= min_c and m_max_c <= max_c:
                continue
            new_merged.append(m)
            
        self.merged_cells = new_merged
        self._draw_table()
        self.update_status("已取消合并")

    def _choose_fg_color(self):
        color = colorchooser.askcolor(title="选择字体颜色")[1]
        if color:
            self.table_fg_color = color
            self.table_fg_btn.config(bg=color)
            self._apply_table_format()

    def _choose_bg_color(self):
        color = colorchooser.askcolor(title="选择背景颜色")[1]
        if color:
            self.table_bg_color = color
            self.table_bg_btn.config(bg=color)
            self._apply_table_format()

    def _clear_table_colors(self):
        self.table_fg_color = None
        self.table_bg_color = None
        self.table_fg_btn.config(bg="#E0E0E0")
        self.table_bg_btn.config(bg="#E0E0E0")
        self._apply_table_format()

    def _build_table_formula_tab(self, parent):
        bg = MODERN_COLORS['surface']
        tk.Label(parent, text="内置公式", bg=bg, font=self.default_font).pack(anchor=tk.W, padx=4, pady=(4, 2))
        
        funcs = [
            ("SUM", "求和", "=SUM(A1:A5)"),
            ("AVERAGE", "平均值", "=AVERAGE(A1:A5)"),
            ("MAX", "最大值", "=MAX(A1:A5)"),
            ("MIN", "最小值", "=MIN(A1:A5)"),
            ("COUNT", "计数", "=COUNT(A1:A5)"),
            ("IF", "条件", "=IF(A1>0, 1, 0)"),
            ("ABS", "绝对值", "=ABS(A1)"),
            ("ROUND", "四舍五入", "=ROUND(A1, 2)"),
            ("SIN", "正弦", "=SIN(A1)"),
            ("COS", "余弦", "=COS(A1)"),
            ("TAN", "正切", "=TAN(A1)"),
            ("LOG", "自然对数", "=LOG(A1)"),
            ("SQRT", "平方根", "=SQRT(A1)"),
            ("POWER", "幂", "=POWER(A1, 2)"),
        ]
        
        grid_frame = tk.Frame(parent, bg=bg)
        grid_frame.pack(fill=tk.X, padx=4, pady=4)
        
        for i, (func_name, desc, example) in enumerate(funcs):
            btn = RoundedButton(grid_frame, text=f"{func_name} ({desc})", 
                                command=lambda f=func_name: self._insert_formula_func(f),
                                width=130, height=24, radius=4,
                                bg=MODERN_COLORS['primary_light'],
                                fg=MODERN_COLORS['primary'],
                                hover_bg='#D0E4F7')
            btn.grid(row=i//4, column=i%4, padx=4, pady=4)

    def _build_table_chart_tab(self, parent):
        bg = MODERN_COLORS['surface']
        tk.Label(parent, text="插入内嵌图表（拖拽可移动，右下角调整大小，右键可自定义）", bg=bg, font=self.default_font).pack(anchor=tk.W, padx=4, pady=(4, 2))
        
        grid_frame = tk.Frame(parent, bg=bg)
        grid_frame.pack(fill=tk.X, padx=4, pady=4)
        
        RoundedButton(grid_frame, text="插入柱状图", command=lambda: self._generate_chart('bar'),
                      width=140, height=28, radius=6).grid(row=0, column=0, padx=6, pady=6)
        RoundedButton(grid_frame, text="插入折线图", command=lambda: self._generate_chart('line'),
                      width=140, height=28, radius=6).grid(row=0, column=1, padx=6, pady=6)
        RoundedButton(grid_frame, text="插入饼图", command=lambda: self._generate_chart('pie'),
                      width=140, height=28, radius=6).grid(row=0, column=2, padx=6, pady=6)
        
        tk.Label(parent,
                 text="提示：选中数据区域后点击插入。右键点击图表可编辑图例、颜色。\n"
                      "图表直接嵌入表格中，导出 .ctbt 时会一起保存。",
                 bg=bg, font=("Microsoft YaHei", 9),
                 fg=MODERN_COLORS['text_muted'], justify=tk.LEFT).pack(side=tk.LEFT, padx=4, pady=4)

    def _insert_formula_func(self, func_name):
        text_to_insert = f"{func_name}()"
        if self.active_editor == 'floating' and self.floating_entry:
            self.floating_entry.insert(tk.INSERT, text_to_insert)
            self.floating_entry.focus_set()
            cursor_pos = self.floating_entry.index(tk.INSERT)
            self.floating_entry.icursor(cursor_pos - 1)
        elif self.active_editor == 'bar' and self.formula_entry:
            self.formula_entry.insert(tk.INSERT, text_to_insert)
            self.formula_entry.focus_set()
            cursor_pos = self.formula_entry.index(tk.INSERT)
            self.formula_entry.icursor(cursor_pos - 1)
        else:
            if self.selected_cells:
                r, c = sorted(self.selected_cells)[0]
                self._start_editing((r, c))
                self.floating_entry.delete(0, tk.END)
                self.floating_entry.insert(0, f"={text_to_insert}")
                self.active_editor = 'floating'
                self.floating_entry.focus_set()
                cursor_pos = self.floating_entry.index(tk.INSERT)
                self.floating_entry.icursor(cursor_pos - 1)

    def _generate_chart(self, chart_type):
        if self.selected_cells:
            min_r = min(r for r, c in self.selected_cells)
            max_r = max(r for r, c in self.selected_cells)
            min_c = min(c for r, c in self.selected_cells)
            max_c = max(c for r, c in self.selected_cells)
        else:
            min_r, min_c = 0, 0
            max_r, max_c = -1, -1
            for r in range(self.table_rows):
                for c in range(self.table_cols):
                    if self.table_cells.get((r, c), {}).get('text', '').strip() != '':
                        max_r = max(max_r, r)
                        max_c = max(max_c, c)
            if max_r == -1:
                messagebox.showwarning("提示", "表格为空，没有可用的数据生成图表。")
                return
                
        has_data = False
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                if self.display_cache.get((r, c)):
                    has_data = True
                    break
        if not has_data:
            messagebox.showwarning("提示", "选区内没有有效数据。")
            return

        new_chart = {
            'type': chart_type,
            'title': '数据图表',
            'x': 100, 'y': 100,
            'w': 400, 'h': 300,
            'min_r': min_r, 'max_r': max_r,
            'min_c': min_c, 'max_c': max_c,
            'legend_name': '数值', # 新增图例名称
            'categories': [], # 自定义图例
            'colors': []      # 自定义颜色
        }
        self.table_charts.append(new_chart)
        self.selected_chart = new_chart
        self._draw_table()
        self.update_status("图表已插入。可拖拽移动或右键编辑。")

    def _build_table_settings_tab(self, parent):
        bg = MODERN_COLORS['surface']
        
        tk.Label(parent, text="迭代计算设置（解决循环引用）", font=("Microsoft YaHei", 10, "bold"),
                 bg=bg, fg=MODERN_COLORS['text']).pack(anchor=tk.W, padx=4, pady=(8, 4))
                 
        tk.Label(parent, text="提示：若表格存在如 A1=A1+2 的公式，需开启迭代计算。",
                 font=("Microsoft YaHei", 9), bg=bg, fg=MODERN_COLORS['text_muted']).pack(anchor=tk.W, padx=4, pady=(0, 8))
                 
        row1 = tk.Frame(parent, bg=bg)
        row1.pack(fill=tk.X, padx=4, pady=4)
        self.enable_iteration_var = tk.BooleanVar(value=False)
        tk.Checkbutton(row1, text="允许迭代计算", variable=self.enable_iteration_var,
                       bg=bg, activebackground=bg, selectcolor=bg,
                       font=self.default_font).pack(side=tk.LEFT, padx=(0, 10))
        RoundedButton(row1, text="应用设置", command=self._apply_settings,
                      width=90, height=24, radius=4).pack(side=tk.LEFT)
                      
        row2 = tk.Frame(parent, bg=bg)
        row2.pack(fill=tk.X, padx=4, pady=4)
        tk.Label(row2, text="最大迭代次数:", bg=bg, font=self.default_font).pack(side=tk.LEFT)
        self.max_iter_var = tk.StringVar(value="100")
        tk.Entry(row2, textvariable=self.max_iter_var, width=8).pack(side=tk.LEFT, padx=(4, 10))
        
        tk.Label(row2, text="最大误差:", bg=bg, font=self.default_font).pack(side=tk.LEFT)
        self.tolerance_var = tk.StringVar(value="0.001")
        tk.Entry(row2, textvariable=self.tolerance_var, width=8).pack(side=tk.LEFT, padx=(4, 10))

    def _apply_settings(self):
        self.evaluate_all_cells()
        self._draw_table()
        self.update_status("已应用设置并重新计算")

    def _col_label(self, c):
        s = ""
        c += 1
        while c > 0:
            c, rem = divmod(c - 1, 26)
            s = chr(ord('A') + rem) + s
        return s

    def _draw_table(self):
        canvas = getattr(self, 'table_canvas', None)
        if not canvas:
            return
            
        canvas.delete("all")
        
        head_w = 45
        head_h = 24
        cw = self.table_col_width
        ch = self.table_row_height
        
        canvas.create_rectangle(0, 0, head_w, head_h, fill="#E0E0E0", outline="#B0B0B0")
        
        for c in range(self.table_cols):
            x1 = head_w + c * cw
            x2 = x1 + cw
            canvas.create_rectangle(x1, 0, x2, head_h, fill="#F0F0F0", outline="#D0D0D0")
            canvas.create_text(x1 + cw/2, head_h/2, text=self._col_label(c),
                               font=("Microsoft YaHei", 9, "bold"), fill="#555")
                               
        for r in range(self.table_rows):
            y1 = head_h + r * ch
            y2 = y1 + ch
            canvas.create_rectangle(0, y1, head_w, y2, fill="#F0F0F0", outline="#D0D0D0")
            canvas.create_text(head_w/2, y1 + ch/2, text=str(r+1),
                               font=("Microsoft YaHei", 9, "bold"), fill="#555")

        # 处理合并单元格的隐藏逻辑
        skip_cells = set()
        merge_map = {} # (r,c) -> (top, left, bottom, right, is_top_left)
        for m in self.merged_cells:
            top, left, bottom, right = m
            for r in range(top, bottom + 1):
                for c in range(left, right + 1):
                    if (r, c) != (top, left):
                        skip_cells.add((r, c))
                    merge_map[(r, c)] = (top, left, bottom, right, (r, c) == (top, left))

        for r in range(self.table_rows):
            for c in range(self.table_cols):
                if (r, c) in skip_cells:
                    continue

                x1 = head_w + c * cw
                y1 = head_h + r * ch
                
                # 默认宽高
                x2 = x1 + cw
                y2 = y1 + ch
                
                is_merged = False
                if (r, c) in merge_map:
                    top, left, bottom, right, is_top_left = merge_map[(r, c)]
                    if is_top_left:
                        x2 = head_w + (right + 1) * cw
                        y2 = head_h + (bottom + 1) * ch
                        is_merged = True
                
                d = self.table_cells.get((r, c), {})
                raw_text = str(d.get('text', ''))
                disp_text = str(self.display_cache.get((r, c), ''))
                val = self.cell_cache.get((r, c), '')
                
                # 修复：使用 or 兜底，避免空字符串导致的透明文字
                bg_color = d.get('bg') or MODERN_COLORS['surface']
                fg_color = d.get('fg') or MODERN_COLORS['text']
                
                dtype = d.get('dtype') or 'auto'
                align = d.get('align') or 'auto'
                
                is_number = False
                if dtype == 'number':
                    is_number = True
                elif dtype == 'auto':
                    is_number = isinstance(val, (int, float))
                            
                if align == 'auto':
                    anchor = 'e' if is_number else 'w'
                    text_x = x2 - 6 if is_number else x1 + 6
                elif align == 'left':
                    anchor = 'w'
                    text_x = x1 + 6
                elif align == 'center':
                    anchor = 'center'
                    text_x = x1 + (x2 - x1) / 2
                else:
                    anchor = 'e'
                    text_x = x2 - 6

                canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline="#E0E0E0")
                
                if self.editing_cell != (r, c) or is_merged:
                    if disp_text:
                        fam = d.get('font') or 'Microsoft YaHei'
                        size = d.get('size') or 10
                        bold = bool(d.get('bold', False))
                        f = tkfont.Font(family=fam, size=size, weight='bold' if bold else 'normal')
                        
                        # 合并单元格不截断文字
                        if not is_merged and len(disp_text) > 15:
                            disp_text = disp_text[:13] + "..."
                                
                        canvas.create_text(text_x, y1 + (y2 - y1)/2, text=disp_text,
                                           font=f, fill=fg_color, anchor=anchor)
                                           
                    if (dtype == 'text' or (dtype == 'auto' and disp_text and not is_number)) and not is_merged:
                        canvas.create_polygon(x1, y1, x1+8, y1, x1, y1+8, fill="#107C10", outline="")
        
        if self.selected_cells:
            min_r = min(r for r, c in self.selected_cells)
            max_r = max(r for r, c in self.selected_cells)
            min_c = min(c for r, c in self.selected_cells)
            max_c = max(c for r, c in self.selected_cells)
            
            # 选中高亮如果碰到合并单元格，可以扩展，这里做简单处理
            sel_x1 = head_w + min_c * cw
            sel_y1 = head_h + min_r * ch
            sel_x2 = head_w + (max_c + 1) * cw
            sel_y2 = head_h + (max_r + 1) * ch
            
            canvas.create_rectangle(sel_x1, sel_y1, sel_x2, sel_y2, fill=MODERN_COLORS['excel_sel'], outline="", stipple='gray50')
            canvas.create_rectangle(sel_x1, sel_y1, sel_x2, sel_y2, outline=MODERN_COLORS['excel_sel_border'], width=2)
            
            if self.selection_start:
                sr, sc = self.selection_start
                fx = head_w + (sc + 1) * cw
                fy = head_h + (sr + 1) * ch
                canvas.create_rectangle(fx-4, fy-4, fx+4, fy+4, fill=MODERN_COLORS['excel_sel_border'], outline="white")
                
            if self.is_dragging_handle and self.drag_target_cell:
                tr, tc = self.drag_target_cell
                
                if tr > max_r:
                    p_x1 = head_w + min_c * cw
                    p_y1 = head_h + (max_r + 1) * ch
                    p_x2 = head_w + (max_c + 1) * cw
                    p_y2 = head_h + (tr + 1) * ch
                elif tr < min_r:
                    p_x1 = head_w + min_c * cw
                    p_y1 = head_h + tr * ch
                    p_x2 = head_w + (max_c + 1) * cw
                    p_y2 = head_h + min_r * ch
                elif tc > max_c:
                    p_x1 = head_w + (max_c + 1) * cw
                    p_y1 = head_h + min_r * ch
                    p_x2 = head_w + (tc + 1) * cw
                    p_y2 = head_h + (max_r + 1) * ch
                elif tc < min_c:
                    p_x1 = head_w + tc * cw
                    p_y1 = head_h + min_r * ch
                    p_x2 = head_w + min_c * cw
                    p_y2 = head_h + (max_r + 1) * ch
                else:
                    p_x1, p_y1, p_x2, p_y2 = -1000, -1000, -1000, -1000
                
                if p_x1 != -1000:
                    canvas.create_rectangle(p_x1, p_y1, p_x2, p_y2, outline=MODERN_COLORS['excel_fill_preview'], width=1, dash=(4, 4))

        for chart in self.table_charts:
            try:
                self._draw_embedded_chart(chart)
            except Exception as e:
                # 容错：防止某个图表绘制失败导致整个表格卡死
                print(f"绘制图表错误: {e}")
                canvas.create_rectangle(chart['x'], chart['y'], chart['x']+chart['w'], chart['y']+chart['h'], outline="red", dash=(4,4))
                canvas.create_text(chart['x']+20, chart['y']+20, text="图表渲染失败", fill="red", anchor="nw")

        total_w = head_w + self.table_cols * cw
        total_h = head_h + self.table_rows * ch
        canvas.configure(scrollregion=(0, 0, total_w, total_h))

    def _draw_embedded_chart(self, chart):
        x, y = chart['x'], chart['y']
        w, h = chart['w'], chart['h']
        c_type = chart['type']
        title = chart.get('title', '数据图表')
        canvas = self.table_canvas

        border_color = MODERN_COLORS['primary'] if self.selected_chart == chart else "#CCCCCC"
        border_w = 2 if self.selected_chart == chart else 1

        canvas.create_rectangle(x, y, x+w, y+h, fill="#FFFFFF", outline=border_color, width=border_w)
        canvas.create_rectangle(x, y, x+w, y+25, fill="#F8F8F8", outline="#E0E0E0", width=1)
        canvas.create_text(x+10, y+12, text=title, anchor='w', font=("Microsoft YaHei", 9, "bold"), fill="#333")
        
        canvas.create_text(x+w-15, y+12, text="×", font=("Arial", 12, "bold"), fill="#FF4444", tags=("chart_close",))

        data = self._get_chart_data(chart)
        if not data:
            canvas.create_text(x+w/2, y+h/2, text="无有效数据", fill="#999", font=("Microsoft YaHei", 10))
            rx, ry = x+w, y+h
            canvas.create_rectangle(rx-8, ry-8, rx, ry, fill=MODERN_COLORS['primary'], outline="white", tags=("chart_resize",))
            return

        pad_left = 45
        pad_right = 20
        pad_top = 40
        pad_bottom = 40
        
        plot_w = w - pad_left - pad_right
        plot_h = h - pad_top - pad_bottom
        
        if plot_w < 20 or plot_h < 20:
            rx, ry = x+w, y+h
            canvas.create_rectangle(rx-8, ry-8, rx, ry, fill=MODERN_COLORS['primary'], outline="white", tags=("chart_resize",))
            return

        cats = chart.get('categories', [])
        if len(cats) != len(data):
            cats = [d[0] for d in data]

        colors = chart.get('colors', [])
        if len(colors) < 20:
            colors = CHART_COLORS

        legend_name = chart.get('legend_name', '数值')

        if c_type in ('bar', 'line'):
            max_val = max([v for _, v in data]) if data else 1
            min_val = min([v for _, v in data]) if data else 0

            # 扩展数值范围，留出上下边距
            if max_val == min_val:
                max_val += 1
                min_val -= 1
            else:
                diff = max_val - min_val
                max_val += diff * 0.1
                min_val -= diff * 0.1

            if max_val < 0: max_val = 0
            if min_val > 0: min_val = 0

            val_range = max_val - min_val
            if val_range == 0: val_range = 1

            # 计算0点所在的Y坐标
            zero_y = y + pad_top + plot_h - ((0 - min_val) / val_range) * plot_h

            # 画网格线和刻度
            for i in range(5):
                val = min_val + (val_range * i / 4)
                ty = y + pad_top + plot_h - ((val - min_val) / val_range) * plot_h
                canvas.create_line(x+pad_left-4, ty, x+pad_left, ty, fill="#CCC")
                canvas.create_text(x+pad_left-6, ty, text=f"{val:.4g}", anchor='e', font=("Arial", 8), fill="#777")
                canvas.create_line(x+pad_left, ty, x+pad_left+plot_w, ty, fill="#F0F0F0", dash=(2,2))

            canvas.create_line(x+pad_left, zero_y, x+pad_left+plot_w, zero_y, fill="#888", width=1.5)
            canvas.create_line(x+pad_left, y+pad_top, x+pad_left, y+pad_top+plot_h, fill="#CCC")

            n = len(data)
            step = plot_w / n

            if c_type == 'bar':
                bar_w = min(step * 0.6, 40)
                for i, (cat, val) in enumerate(data):
                    cx = x + pad_left + i * step + step/2
                    bar_h = (abs(val) / val_range) * plot_h

                    if val >= 0:
                        by1 = zero_y - bar_h
                        by2 = zero_y
                    else:
                        by1 = zero_y
                        by2 = zero_y + bar_h

                    color = colors[0]
                    canvas.create_rectangle(cx - bar_w/2, by1, cx + bar_w/2, by2, fill=color, outline="")

                    disp_cat = str(cats[i])
                    if len(disp_cat) > 6: disp_cat = disp_cat[:5] + "..."
                    canvas.create_text(cx, y+pad_top+plot_h+10, text=disp_cat, anchor='n', font=("Arial", 8), fill="#555")

                    ty_text = by1 - 5 if val >= 0 else by2 + 5
                    anchor_text = 's' if val >= 0 else 'n'
                    canvas.create_text(cx, ty_text, text=f"{val:.4g}", anchor=anchor_text, font=("Arial", 8, "bold"), fill="#333")

            elif c_type == 'line':
                points = []
                for i, (cat, val) in enumerate(data):
                    cx = x + pad_left + i * step + step/2
                    cy = y + pad_top + plot_h - ((val - min_val) / val_range) * plot_h
                    points.append((cx, cy))

                if len(points) > 1:
                    canvas.create_line([p for pt in points for p in pt], fill=colors[0], width=2, smooth=False)

                for i, (cx, cy) in enumerate(points):
                    canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill="#FFF", outline=colors[0], width=2)
                    disp_cat = str(cats[i])
                    if len(disp_cat) > 6: disp_cat = disp_cat[:5] + "..."
                    canvas.create_text(cx, y+pad_top+plot_h+10, text=disp_cat, anchor='n', font=("Arial", 8), fill="#555")

                    val = data[i][1]
                    ty_text = cy - 8 if val >= 0 else cy + 8
                    anchor_text = 's' if val >= 0 else 'n'
                    canvas.create_text(cx, ty_text, text=f"{val:.4g}", anchor=anchor_text, font=("Arial", 8), fill="#333")

            # 绘制图例
            leg_x = x + w - 90
            leg_y = y + 30
            canvas.create_rectangle(leg_x, leg_y, leg_x+12, leg_y+12, fill=colors[0], outline="")
            canvas.create_text(leg_x+18, leg_y+6, text=legend_name, anchor='w', font=("Microsoft YaHei", 8), fill="#333")

        elif c_type == 'pie':
            total = sum([abs(v) for _, v in data])
            if total <= 0:
                canvas.create_text(x+w/2, y+h/2, text="总和必须大于0", fill="#999", font=("Microsoft YaHei", 10))
            else:
                r = min(plot_w, plot_h) / 2.5
                cx = x + pad_left + plot_w/2 - 20
                cy = y + pad_top + plot_h/2
                
                start_angle = 90
                leg_x = x + w - 100
                leg_y = y + 40
                
                for i, (cat, val) in enumerate(data):
                    angle = (abs(val) / total) * 360
                    color = colors[i % len(colors)]
                    
                    canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=start_angle, extent=-angle, fill=color, outline="#FFF", width=1)
                    
                    if angle > 15:
                        mid_angle = start_angle - angle/2
                        import math
                        rad = -mid_angle * math.pi / 180
                        tx = cx + (r * 0.6) * math.cos(rad)
                        ty = cy + (r * 0.6) * math.sin(rad)
                        canvas.create_text(tx, ty, text=f"{(abs(val)/total)*100:.1f}%", fill="#FFF", font=("Arial", 8, "bold"))
                    
                    canvas.create_rectangle(leg_x, leg_y + i*20, leg_x+12, leg_y+12 + i*20, fill=color, outline="")
                    disp_cat = str(cats[i])
                    if len(disp_cat) > 8: disp_cat = disp_cat[:7] + "..."
                    canvas.create_text(leg_x+18, leg_y+6 + i*20, text=disp_cat, anchor='w', font=("Arial", 8), fill="#333")
                    
                    start_angle -= angle

        rx, ry = x+w, y+h
        canvas.create_rectangle(rx-8, ry-8, rx, ry, fill=MODERN_COLORS['primary'], outline="white", tags=("chart_resize",))

    def _get_cell_from_event(self, event):
        x = self.table_canvas.canvasx(event.x)
        y = self.table_canvas.canvasy(event.y)
        head_w = 45
        head_h = 24
        
        if x < head_w or y < head_h:
            return None
            
        c = int((x - head_w) // self.table_col_width)
        r = int((y - head_h) // self.table_row_height)
        
        if 0 <= r < self.table_rows and 0 <= c < self.table_cols:
            return (r, c)
        return None

    def _get_range_ref(self, start, end):
        r1, c1 = start
        r2, c2 = end
        min_r, max_r = min(r1, r2), max(r1, r2)
        min_c, max_c = min(c1, c2), max(c1, c2)
        col1 = self._col_label(min_c)
        col2 = self._col_label(max_c)
        row1 = min_r + 1
        row2 = max_r + 1
        return f"{col1}{row1}:{col2}{row2}" if (min_r != max_r or min_c != max_c) else f"{col1}{row1}"

    def _update_selection(self, start_cell, end_cell):
        if not start_cell or not end_cell:
            return
        r1, c1 = start_cell
        r2, c2 = end_cell
        min_r, max_r = min(r1, r2), max(r1, r2)
        min_c, max_c = min(c1, c2), max(c1, c2)
        
        self.selected_cells = set()
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                self.selected_cells.add((r, c))
                
        if len(self.selected_cells) == 1:
            r, c = start_cell
            self.cell_ref_var.set(f"{self._col_label(c)}{r+1}")
            self.formula_bar_var.set(self.table_cells.get((r, c), {}).get('text', ''))
        else:
            self.cell_ref_var.set(f"{min_r+1}R x {max_c-min_c+1}C")
            self.formula_bar_var.set("")

    def _on_canvas_click(self, event):
        x = self.table_canvas.canvasx(event.x)
        y = self.table_canvas.canvasy(event.y)
        
        self.selected_chart = None
        for chart in self.table_charts:
            cx, cy, cw, ch = chart['x'], chart['y'], chart['w'], chart['h']
            if cx <= x <= cx + cw and cy <= y <= cy + ch:
                if cx + cw - 25 <= x <= cx + cw - 5 and cy + 5 <= y <= cy + 25:
                    self.table_charts.remove(chart)
                    self._draw_table()
                    return
                if cx + cw - 10 <= x <= cx + cw and cy + ch - 10 <= y <= cy + ch:
                    self.resizing_chart = chart
                    self.chart_drag_start = (x, y)
                    self.chart_orig_size = (cw, ch)
                    self._draw_table()
                    return
                
                self.selected_chart = chart
                self.chart_drag_start = (x, y)
                self.chart_orig_pos = (cx, cy)
                self._draw_table()
                return

        if self.selected_cells and self.selection_start:
            max_r = max(r for r, c in self.selected_cells)
            max_c = max(c for r, c in self.selected_cells)
            
            head_w = 45
            head_h = 24
            fx = head_w + (max_c + 1) * self.table_col_width
            fy = head_h + (max_r + 1) * self.table_row_height
            
            if abs(x - fx) < 10 and abs(y - fy) < 10:
                self.is_dragging_handle = True
                self.drag_target_cell = (max_r, max_c)
                return

        cell = self._get_cell_from_event(event)
        if cell:
            r, c = cell
            
            is_editing_formula = False
            active_entry = None
            
            if self.active_editor == 'floating' and self.floating_entry and self.floating_entry.winfo_exists():
                if self.floating_entry.get().startswith('='):
                    is_editing_formula = True
                    active_entry = self.floating_entry
            elif self.active_editor == 'bar' and self.formula_entry and self.formula_entry.winfo_exists():
                if self.formula_entry.get().startswith('='):
                    is_editing_formula = True
                    active_entry = self.formula_entry
                    
            if is_editing_formula:
                ref = f"{self._col_label(c)}{r+1}"
                active_entry.insert(tk.INSERT, ref)
                self.formula_drag_start = cell
                self.formula_insert_pos = active_entry.index(tk.INSERT) - len(ref)
                self.formula_insert_len = len(ref)
                active_entry.focus_set()
                
                self._ignore_focus_out = True
                self.root.after(200, lambda: setattr(self, '_ignore_focus_out', False))
                return

            self.table_canvas.focus_set()
            self.selection_start = cell
            self.selection_end = cell
            self._update_selection(cell, cell)
            self._draw_table()
            self._hide_floating_entry()
        else:
            self.selection_start = None
            self.selection_end = None
            self.selected_cells = set()
            self._draw_table()
            self._hide_floating_entry()

    def _on_canvas_drag(self, event):
        x = self.table_canvas.canvasx(event.x)
        y = self.table_canvas.canvasy(event.y)
        
        if getattr(self, 'resizing_chart', None):
            dx = x - self.chart_drag_start[0]
            dy = y - self.chart_drag_start[1]
            self.resizing_chart['w'] = max(150, self.chart_orig_size[0] + dx)
            self.resizing_chart['h'] = max(100, self.chart_orig_size[1] + dy)
            self._draw_table()
            return
            
        if getattr(self, 'selected_chart', None) and getattr(self, 'chart_drag_start', None):
            dx = x - self.chart_drag_start[0]
            dy = y - self.chart_drag_start[1]
            self.selected_chart['x'] = self.chart_orig_pos[0] + dx
            self.selected_chart['y'] = self.chart_orig_pos[1] + dy
            self._draw_table()
            return

        cell = self._get_cell_from_event(event)
        
        if self.is_dragging_handle:
            if cell:
                if cell != self.drag_target_cell:
                    self.drag_target_cell = cell
                    self._draw_table()
            return
            
        if cell:
            if self.formula_drag_start:
                new_ref = self._get_range_ref(self.formula_drag_start, cell)
                
                active_entry = None
                if self.active_editor == 'floating' and self.floating_entry and self.floating_entry.winfo_exists():
                    active_entry = self.floating_entry
                elif self.active_editor == 'bar' and self.formula_entry and self.formula_entry.winfo_exists():
                    active_entry = self.formula_entry
                    
                if active_entry:
                    text = active_entry.get()
                    text = text[:self.formula_insert_pos] + new_ref + text[self.formula_insert_pos+self.formula_insert_len:]
                    active_entry.delete(0, tk.END)
                    active_entry.insert(0, text)
                    active_entry.icursor(self.formula_insert_pos + len(new_ref))
                    self.formula_insert_len = len(new_ref)
                    active_entry.focus_set()
                return
                
            if self.selection_start:
                if cell != self.selection_end:
                    self.selection_end = cell
                    self._update_selection(self.selection_start, self.selection_end)
                    self._draw_table()

    def _on_canvas_release(self, event):
        if getattr(self, 'resizing_chart', None):
            self.resizing_chart = None
            return
            
        if getattr(self, 'selected_chart', None):
            self.chart_drag_start = None
            return
            
        if self.is_dragging_handle:
            self.is_dragging_handle = False
            cell = self._get_cell_from_event(event)
            
            if cell and self.selection_start and self.selection_end:
                if cell not in self.selected_cells:
                    self._fill_cells(self.selection_start, self.selection_end, cell)
                    self.evaluate_all_cells()
                    
            self.drag_target_cell = None
            self._draw_table()

    def _on_canvas_double_click(self, event):
        cell = self._get_cell_from_event(event)
        if cell:
            # 如果是合并单元格，找到左上角
            for m in self.merged_cells:
                top, left, bottom, right = m
                if top <= cell[0] <= bottom and left <= cell[1] <= right:
                    cell = (top, left)
                    break
            self._start_editing(cell)

    def _on_canvas_key(self, event):
        if not self.selected_cells:
            return
            
        if self.editing_cell:
            return
            
        r, c = self.selection_start
        
        if event.keysym in ('Up', 'Down', 'Left', 'Right'):
            if event.keysym == 'Up': r = max(0, r - 1)
            elif event.keysym == 'Down': r = min(self.table_rows - 1, r + 1)
            elif event.keysym == 'Left': c = max(0, c - 1)
            elif event.keysym == 'Right': c = min(self.table_cols - 1, c + 1)
            
            new_cell = (r, c)
            self.selection_start = new_cell
            self.selection_end = new_cell
            self._update_selection(new_cell, new_cell)
            self._draw_table()
            self._scroll_to_cell(new_cell)
            return
            
        if event.keysym in ('Delete', 'BackSpace'):
            for cell in self.selected_cells:
                if cell in self.table_cells:
                    self.table_cells[cell]['text'] = ''
            self.evaluate_all_cells()
            self._draw_table()
            return
            
        if event.keysym == 'F2':
            self._start_editing((r, c))
            return
            
        if event.char and event.char.isprintable():
            self._start_editing((r, c))
            # 修复：event_generate 不支持 char 参数，直接使用 insert
            self.floating_entry.insert(tk.END, event.char)
            self.floating_entry.icursor(tk.END)
            return "break"

    def _scroll_to_cell(self, cell):
        r, c = cell
        head_w = 45
        head_h = 24
        cw = self.table_col_width
        ch = self.table_row_height
        
        x1 = head_w + c * cw
        y1 = head_h + r * ch
        x2 = x1 + cw
        y2 = y1 + ch
        
        canvas = self.table_canvas
        x_view = canvas.canvasx(0)
        y_view = canvas.canvasy(0)
        w_view = canvas.winfo_width()
        h_view = canvas.winfo_height()
        
        if x1 < x_view:
            canvas.xview_moveto(x1 / (head_w + self.table_cols * cw))
        elif x2 > x_view + w_view:
            canvas.xview_moveto((x2 - w_view) / (head_w + self.table_cols * cw))
            
        if y1 < y_view:
            canvas.yview_moveto(y1 / (head_h + self.table_rows * ch))
        elif y2 > y_view + h_view:
            canvas.yview_moveto((y2 - h_view) / (head_h + self.table_rows * ch))

    def _start_editing(self, cell, initial_text=""):
        r, c = cell
        self.editing_cell = cell
        self._draw_table()
        
        head_w = 45
        head_h = 24
        x = head_w + c * self.table_col_width
        y = head_h + r * self.table_row_height
        
        cx = self.table_canvas.canvasx(0)
        cy = self.table_canvas.canvasy(0)
        
        d = self.table_cells.get(cell, {})
        fam = d.get('font') or 'Microsoft YaHei'
        size = d.get('size') or 10
        bold = bool(d.get('bold', False))
        
        if self.floating_entry:
            self.floating_entry.destroy()
            
        self.floating_entry = tk.Entry(self.table_canvas, font=(fam, size, 'bold' if bold else 'normal'),
                                       relief=tk.SOLID, bd=1, bg="white", justify=tk.LEFT)
        
        if initial_text:
            self.floating_entry.insert(0, initial_text)
        else:
            text = d.get('text', '')
            self._original_text = text
            self.floating_entry.insert(0, text)
            self.floating_entry.select_range(0, tk.END)
        
        self.floating_entry.place(x=x - cx, y=y - cy, width=self.table_col_width, height=self.table_row_height)
        self.floating_entry.focus_set()
        self.active_editor = 'floating'
        
        self.floating_entry.bind('<Return>', lambda e: self._save_floating_entry(move=(1, 0)))
        self.floating_entry.bind('<Tab>', lambda e: self._save_floating_entry(move=(0, 1)))
        self.floating_entry.bind('<Escape>', self._cancel_editing)
        self.floating_entry.bind('<FocusOut>', self._on_floating_focus_out)

    def _on_floating_focus_out(self, event=None):
        if getattr(self, '_ignore_focus_out', False):
            return
        self._save_floating_entry()

    def _save_floating_entry(self, event=None, move=(0, 0)):
        if not self.floating_entry or not self.editing_cell:
            return
        r, c = self.editing_cell
        val = self.floating_entry.get()
        self.table_cells.setdefault((r, c), {})['text'] = val
        
        self.floating_entry.destroy()
        self.floating_entry = None
        self.editing_cell = None
        self.formula_drag_start = None
        
        if move != (0, 0):
            dr, dc = move
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.table_rows and 0 <= nc < self.table_cols:
                r, c = nr, nc
                
        self.selection_start = (r, c)
        self.selection_end = (r, c)
        self._update_selection((r, c), (r, c))
        self.evaluate_all_cells()
        self._draw_table()
        self.table_canvas.focus_set()
        self._scroll_to_cell((r, c))

    def _cancel_editing(self, event=None):
        if not self.floating_entry or not self.editing_cell:
            return
        r, c = self.editing_cell
        self.table_cells.setdefault((r, c), {})['text'] = self._original_text
        
        self.floating_entry.destroy()
        self.floating_entry = None
        self.editing_cell = None
        self.formula_drag_start = None
        
        self.selection_start = (r, c)
        self.selection_end = (r, c)
        self._update_selection((r, c), (r, c))
        self._draw_table()
        self.table_canvas.focus_set()
        
    def _hide_floating_entry(self):
        if self.floating_entry:
            self._save_floating_entry()

    def _apply_table_size(self):
        try:
            h = int(self.table_row_h_var.get())
            w = int(self.table_col_w_var.get())
        except Exception:
            messagebox.showwarning("提示", "行高/列宽必须是整数")
            return
        self.table_row_height = max(14, min(h, 200))
        self.table_col_width = max(30, min(w, 800))
        self._draw_table()
        self.update_status("已应用表格尺寸")

    def _apply_table_format(self):
        if not self.selected_cells:
            messagebox.showinfo("提示", "请先在表格中选择要应用格式的区域")
            return
            
        fam = (self.table_font_var.get() or '').strip() or "Microsoft YaHei"
        try:
            size = int(self.table_size_var.get())
        except Exception:
            size = 10
        size = max(6, min(size, 72))
        bold = self.table_bold_var.get()
        fg = self.table_fg_color
        cell_bg = self.table_bg_color
        dtype = self.table_dtype_var.get() if self.table_dtype_var else 'auto'
        align = self.table_align_var.get() if self.table_align_var else 'auto'

        for key in self.selected_cells:
            d = self.table_cells.setdefault(key, {})
            d['font'] = fam
            d['size'] = size
            d['bold'] = bold
            d['dtype'] = dtype
            d['align'] = align
            if fg is not None:
                d['fg'] = fg
            if cell_bg is not None:
                d['bg'] = cell_bg

        self._draw_table()
        self.update_status(f"已应用格式到 {len(self.selected_cells)} 个单元格")

    def _add_table_row(self, n=1):
        self.table_rows = min(self.table_rows + n, 300)
        self.evaluate_all_cells()
        self._draw_table()

    def _add_table_col(self, n=1):
        self.table_cols = min(self.table_cols + n, 50)
        self.evaluate_all_cells()
        self._draw_table()

    def clear_table(self):
        if not messagebox.askyesno("确认", "确定要清空表格吗？"):
            return
        self.table_cells = {}
        self.table_charts = []
        self.merged_cells = []
        self.cell_cache = {}
        self.display_cache = {}
        self._draw_table()
        self.update_status("表格已清空")

    def export_ctbt_table(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".ctbt",
            filetypes=[("CTB 表格", "*.ctbt"), ("所有文件", "*.*")])
        if not path:
            return
        try:
            cells = {}
            for (r, c), d in self.table_cells.items():
                # 修复：去掉复杂的判断，全量保存，以免纯数据（无格式修改）丢失
                cells[f"{r},{c}"] = {
                    'text': d.get('text', ''),
                    'font': d.get('font', 'Microsoft YaHei'),
                    'size': d.get('size', 10),
                    'bold': d.get('bold', False),
                    'fg': d.get('fg', ''),
                    'bg': d.get('bg', ''),
                    'dtype': d.get('dtype', 'auto'),
                    'align': d.get('align', 'auto'),
                }
            data = {
                'type': 'ctb-table',
                'version': '5.0',
                'rows': self.table_rows,
                'cols': self.table_cols,
                'row_height': self.table_row_height,
                'col_width': self.table_col_width,
                'cells': cells,
                'charts': self.table_charts,
                'merged_cells': self.merged_cells,
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.update_status(f"已导出: {path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")

    def import_ctbt_table(self):
        path = filedialog.askopenfilename(
            filetypes=[("CTB 表格", "*.ctbt"), ("所有文件", "*.*")])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('type') != 'ctb-table':
                messagebox.showerror("错误", "不是有效的 ctbt 表格文件")
                return
            self.table_rows = max(1, min(int(data.get('rows', 20)), 300))
            self.table_cols = max(1, min(int(data.get('cols', 10)), 50))
            self.table_row_height = max(14, min(int(data.get('row_height', 26)), 200))
            self.table_col_width = max(30, min(int(data.get('col_width', 100)), 800))
            self.table_cells = {}
            for key, val in (data.get('cells') or {}).items():
                try:
                    rs, cs = key.split(',')
                    r, c = int(rs), int(cs)
                    if 0 <= r < self.table_rows and 0 <= c < self.table_cols:
                        self.table_cells[(r, c)] = {
                            'text': str(val.get('text', '')),
                            'font': val.get('font', 'Microsoft YaHei'),
                            'size': int(val.get('size', 10)),
                            'bold': bool(val.get('bold', False)),
                            'fg': val.get('fg', ''),
                            'bg': val.get('bg', ''),
                            'dtype': val.get('dtype', 'auto'),
                            'align': val.get('align', 'auto'),
                        }
                except Exception:
                    continue
            self.table_charts = data.get('charts', [])
            self.merged_cells = [tuple(m) for m in data.get('merged_cells', [])]
            self.selected_chart = None
            self.evaluate_all_cells()
            self._draw_table()
            self.update_status(f"已导入: {path}")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {e}")

    def import_excel_table(self):
        if not HAS_OPENPYXL:
            messagebox.showerror("缺少依赖",
                "导入/导出 Excel 需要 openpyxl 库。\n请运行：pip install openpyxl")
            return
        path = filedialog.askopenfilename(
            filetypes=[("Excel 文件", "*.xlsx *.xlsm *.xls"), ("所有文件", "*.*")])
        if not path:
            return
        ext = os.path.splitext(path)[1].lower()
        if ext == '.xls':
            self._import_xls_file(path)
            return
        try:
            # 优先读取值，忽略图表等复杂对象
            try:
                wb = openpyxl.load_workbook(path, data_only=True)
            except Exception:
                wb = openpyxl.load_workbook(path, data_only=False)
                
            ws = wb.active
            
            # 寻找真实的最大行列，防止因为图表导致范围过大
            max_r = 1
            max_c = 1
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value is not None:
                        max_r = max(max_r, cell.row)
                        max_c = max(max_c, cell.column)
                        
            max_r = min(max_r, 300)
            max_c = min(max_c, 50)
            
            self.table_rows = max(20, max_r)
            self.table_cols = max(10, max_c)
            self.table_cells = {}
            
            for r in range(self.table_rows):
                for c in range(self.table_cols):
                    cell = ws.cell(row=r + 1, column=c + 1)
                    v = cell.value
                    if v is None:
                        continue
                        
                    fam = 'Microsoft YaHei'
                    size = 10
                    bold = False
                    fg = ''
                    bg = ''
                    try:
                        f_obj = cell.font
                        if f_obj is not None:
                            if f_obj.name:
                                fam = f_obj.name
                            if f_obj.size:
                                size = int(f_obj.size)
                            bold = bool(f_obj.b)
                            if f_obj.color and f_obj.color.rgb:
                                c_rgb = f_obj.color.rgb
                                # 防止读取到奇怪的 chart 对象报错
                                if isinstance(c_rgb, str):
                                    if len(c_rgb) == 8 and c_rgb != '00000000':
                                        fg = '#' + c_rgb[2:]
                    except Exception:
                        pass
                    try:
                        fill = cell.fill
                        if fill and fill.fill_type == 'solid' and fill.start_color and fill.start_color.rgb:
                            c_rgb = str(fill.start_color.rgb)
                            if len(c_rgb) == 8 and c_rgb != '00000000':
                                bg = '#' + c_rgb[2:]
                    except Exception:
                        pass
                    
                    # 防止白底白字导致看不见
                    if fg and bg and fg.upper() == bg.upper():
                        fg = ''
                        
                    dtype = 'auto'
                    if isinstance(v, (int, float)):
                        dtype = 'number'
                    else:
                        dtype = 'text'
                        
                    align = 'auto'
                    if cell.alignment and cell.alignment.horizontal:
                        align = cell.alignment.horizontal
                        
                    text = str(v)
                    
                    if isinstance(v, (int, float)) and not isinstance(v, bool):
                        # 修复：强制检查是否可能是日期
                        is_date_format = False
                        if v > 10000: # 粗估，大于1万基本是日期序列号
                            is_date_format = True
                        elif cell.is_date:
                            is_date_format = True
                        elif cell.number_format:
                            fmt = str(cell.number_format).lower()
                            if any(k in fmt for k in ('yy', 'mm', 'dd', 'm/d', 'd-m', 'h:', 'h m', 'am/pm', '上午', '下午', '年', '月', '日')):
                                is_date_format = True
                                
                        if is_date_format:
                            try:
                                from openpyxl.utils.datetime import from_excel
                                dt = from_excel(v, wb.epoch)
                                if dt.year > 1900:
                                    if dt.hour != 0 or dt.minute != 0 or dt.second != 0:
                                        text = dt.strftime("%Y-%m-%d %H:%M:%S")
                                    else:
                                        text = dt.strftime("%Y-%m-%d")
                                    dtype = 'text'
                            except Exception:
                                pass
                        else:
                            if v.is_integer():
                                text = str(int(v))
                            else:
                                text = str(v)
                    elif isinstance(v, datetime.datetime):
                        text = v.strftime("%Y-%m-%d %H:%M:%S")
                        dtype = 'text'
                    else:
                        text = str(v)
                        
                    self.table_cells[(r, c)] = {
                        'text': text,
                        'font': fam,
                        'size': size,
                        'bold': bold,
                        'fg': fg,
                        'bg': bg,
                        'dtype': dtype,
                        'align': align,
                    }
                    
            # 重建 Excel 图表
            self.table_charts = []
            try:
                charts = getattr(ws, '_charts', [])
                for ch in charts:
                    ch_type = 'bar'
                    if ch.__class__.__name__ == 'LineChart':
                        ch_type = 'line'
                    elif ch.__class__.__name__ == 'PieChart':
                        ch_type = 'pie'
                        
                    title = "导入图表"
                    if ch.title is not None:
                        try:
                            if hasattr(ch.title, 'tx') and ch.title.tx and ch.title.tx.rich:
                                title = ch.title.tx.rich.p[0].r[0].t
                        except:
                            pass
                    
                    # 提取图例名称
                    legend_name = "数值"
                    try:
                        if ch.series and len(ch.series) > 0:
                            s = ch.series[0]
                            if hasattr(s, 'tx') and s.tx:
                                if hasattr(s.tx, 'v') and s.tx.v:
                                    legend_name = str(s.tx.v)
                                elif hasattr(s.tx, 'strRef') and s.tx.strRef:
                                    ref = s.tx.strRef.f
                                    m = re.search(r'\$?([A-Z]+)\$?([0-9]+)', ref)
                                    if m:
                                        c = self._col_to_idx(m.group(1))
                                        r = int(m.group(2)) - 1
                                        if 0 <= r < self.table_rows and 0 <= c < self.table_cols:
                                            legend_name = self.display_cache.get((r, c), "数值")
                                            if not legend_name.strip():
                                                legend_name = "数值"
                    except Exception:
                        pass

                    min_r, max_r = 0, self.table_rows-1
                    min_c, max_c = 0, self.table_cols-1
                    
                    if ch.series:
                        s = ch.series[0]
                        if s.val and s.val.numRef and s.val.numRef.f:
                            ref = s.val.numRef.f
                            m = re.search(r'\$?([A-Z]+)\$?([0-9]+)(?::\$?([A-Z]+)\$?([0-9]+))?', ref)
                            if m:
                                c1 = self._col_to_idx(m.group(1))
                                r1 = int(m.group(2)) - 1
                                if m.group(3):
                                    c2 = self._col_to_idx(m.group(3))
                                    r2 = int(m.group(4)) - 1
                                else:
                                    c2, r2 = c1, r1
                                
                                min_r, max_r = min(r1, r2), max(r1, r2)
                                min_c, max_c = min(c1, c2), max(c1, c2)
                                
                                if s.cat:
                                    cat_ref = None
                                    if s.cat.strRef and s.cat.strRef.f:
                                        cat_ref = s.cat.strRef.f
                                    elif s.cat.numRef and s.cat.numRef.f:
                                        cat_ref = s.cat.numRef.f
                                        
                                    if cat_ref:
                                        cat_m = re.search(r'\$?([A-Z]+)\$?([0-9]+)(?::\$?([A-Z]+)\$?([0-9]+))?', cat_ref)
                                        if cat_m:
                                            cc1 = self._col_to_idx(cat_m.group(1))
                                            if cc1 < min_c:
                                                min_c = cc1
                                            if c2 < min_c:
                                                max_c = min_c
                                            
                    # 估计位置
                    x, y = 50, 50
                    try:
                        anchor = ch.anchor
                        if hasattr(anchor, '_from'):
                            x = self.table_col_width * anchor._from.col + 20
                            y = self.table_row_height * anchor._from.row + 20
                    except:
                        pass
                        
                    if max_r >= 0 and max_c >= 0:
                        new_chart = {
                            'type': ch_type,
                            'title': title,
                            'x': max(50, x), 'y': max(50, y),
                            'w': 400, 'h': 300,
                            'min_r': max(0, min_r), 'max_r': min(self.table_rows-1, max_r),
                            'min_c': max(0, min_c), 'max_c': min(self.table_cols-1, max_c),
                            'legend_name': legend_name,
                            'categories': [],
                            'colors': []
                        }
                        self.table_charts.append(new_chart)
            except Exception as ce:
                print(f"解析图表失败: {ce}")
                
            # 解析合并单元格
            self.merged_cells = []
            try:
                merged_ranges = ws.merged_cells.ranges
                for mr in merged_ranges:
                    # openpyxl 行列从 1 开始
                    self.merged_cells.append((mr.min_row - 1, mr.min_col - 1, mr.max_row - 1, mr.max_col - 1))
            except Exception as me:
                print(f"解析合并单元格失败: {me}")
                
            self.evaluate_all_cells()
            self._draw_table()
            self.update_status(f"已导入: {path}")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {e}")

    def _import_xls_file(self, path):
        if not HAS_XLRD:
            messagebox.showerror("缺少依赖",
                "导入 .xls 需要 xlrd 库。\n请运行：pip install xlrd\n"
                "或先将文件另存为 .xlsx 再导入。")
            return
        try:
            book = xlrd.open_workbook(path, formatting_info=True)
            sheet = book.sheet_by_index(0)
            self.table_rows = max(20, min(sheet.nrows, 200))
            self.table_cols = max(10, min(sheet.ncols, 50))
            self.table_cells = {}
            for r in range(self.table_rows):
                for c in range(self.table_cols):
                    if r >= sheet.nrows or c >= sheet.ncols:
                        continue
                    v = sheet.cell_value(r, c)
                    ctype = sheet.cell_type(r, c)
                    if v == '' or v is None:
                        continue
                        
                    dtype = 'auto'
                    if ctype == 2:
                        dtype = 'number'
                    else:
                        dtype = 'text'
                        
                    if isinstance(v, float) and v.is_integer():
                        v = int(v)
                    fam = 'Microsoft YaHei'
                    size = 10
                    bold = False
                    fg = ''
                    bg = ''
                    try:
                        xf_index = sheet.cell_xf_index(r, c)
                        xf = book.xf_list[xf_index]
                        font = book.font_list[xf.font_index]
                        if font.name:
                            fam = font.name
                        if font.height:
                            size = max(6, int(font.height / 20))
                        bold = bool(font.bold)
                    except Exception:
                        pass
                    self.table_cells[(r, c)] = {
                        'text': str(v),
                        'font': fam,
                        'size': size,
                        'bold': bold,
                        'fg': fg,
                        'bg': bg,
                        'dtype': dtype,
                        'align': 'auto',
                    }
            self.table_charts = []
            
            # 解析 xls 合并单元格（xlrd 格式）
            self.merged_cells = []
            try:
                # xlrd 需要 formatting_info=True 才能获取 merged_cells
                for rlo, rhi, clo, chi in sheet.merged_cells:
                    self.merged_cells.append((rlo, clo, rhi-1, chi-1))
            except Exception as e:
                print(f"xls 合并单元格读取失败: {e}")

            self.evaluate_all_cells()
            self._draw_table()
            self.update_status(f"已导入: {path}")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {e}")

    def export_excel_table(self):
        if not HAS_OPENPYXL:
            messagebox.showerror("缺少依赖",
                "导入/导出 Excel 需要 openpyxl 库。\n请运行：pip install openpyxl")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx")])
        if not path:
            return
        try:
            from openpyxl.utils import get_column_letter
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Sheet1"
            max_r = max((r for (r, _) in self.table_cells.keys()), default=-1)
            max_c = max((c for (_, c) in self.table_cells.keys()), default=-1)
            total_rows = max(self.table_rows, max_r + 1)
            total_cols = max(self.table_cols, max_c + 1)
            
            for r in range(total_rows):
                for c in range(total_cols):
                    d = self.table_cells.get((r, c))
                    if not d:
                        continue
                    text = d.get('text', '')
                    cell = ws.cell(row=r + 1, column=c + 1)
                    
                    dtype = d.get('dtype', 'auto')
                    align = d.get('align', 'auto')
                    is_number = False
                    
                    if dtype == 'number':
                        is_number = True
                    elif dtype == 'auto':
                        t_stripped = text.strip()
                        if t_stripped:
                            try:
                                float(t_stripped)
                                if not (t_stripped.startswith('0') and len(t_stripped) > 1 and '.' not in t_stripped):
                                    is_number = True
                            except ValueError:
                                pass
                    
                    if text != '':
                        if text.startswith('='):
                            cell.value = text
                        elif is_number:
                            try:
                                val = float(text)
                                if val.is_integer():
                                    val = int(val)
                                cell.value = val
                            except Exception:
                                cell.value = text
                                cell.number_format = '@'
                        else:
                            cell.value = text
                            cell.number_format = '@'

                    fam = (d.get('font') or 'Microsoft YaHei').strip() or 'Microsoft YaHei'
                    try:
                        size = int(d.get('size', 10))
                    except Exception:
                        size = 10
                    size = max(1, min(size, 409))
                    bold = bool(d.get('bold', False))

                    fg = d.get('fg')
                    xl_fg = "FF" + fg[1:] if fg and fg.startswith('#') else None

                    try:
                        cell.font = XLFont(name=fam, size=size, bold=bold, color=xl_fg)
                    except Exception:
                        try:
                            cell.font = XLFont(size=size, bold=bold, color=xl_fg)
                        except Exception:
                            pass

                    bg = d.get('bg')
                    if bg and bg.startswith('#'):
                        xl_bg = "FF" + bg[1:]
                        try:
                            cell.fill = XLFill(start_color=xl_bg, end_color=xl_bg, fill_type="solid")
                        except Exception:
                            pass
                            
                    if align == 'auto':
                        xl_align = 'right' if is_number else 'left'
                    else:
                        xl_align = align
                        
                    if XLAlignment:
                        cell.alignment = XLAlignment(horizontal=xl_align)

            # 导出合并单元格
            for m in self.merged_cells:
                top, left, bottom, right = m
                try:
                    ws.merge_cells(start_row=top+1, start_column=left+1, end_row=bottom+1, end_column=right+1)
                except Exception as e:
                    print(f"合并导出失败: {e}")

            for c in range(total_cols):
                try:
                    ws.column_dimensions[get_column_letter(c + 1)].width = \
                        max(6, self.table_col_width / 7.0)
                except Exception:
                    pass

            # 导出图表
            for idx, chart in enumerate(self.table_charts):
                try:
                    c_type = chart['type']
                    if c_type == 'bar':
                        e_chart = BarChart()
                        e_chart.type = "col" # 柱状图
                        e_chart.style = 10 # 样式
                        e_chart.title = chart.get('title', '数据图表')
                        e_chart.y_axis.title = '数值'
                        e_chart.x_axis.title = '分类'
                    elif c_type == 'line':
                        e_chart = LineChart()
                        e_chart.title = chart.get('title', '数据图表')
                    elif c_type == 'pie':
                        e_chart = PieChart()
                        e_chart.title = chart.get('title', '数据图表')
                    else:
                        continue
                        
                    e_chart.title = chart.get('title', '数据图表')
                    
                    min_r, max_r = chart['min_r'], chart['max_r']
                    min_c, max_c = chart['min_c'], chart['max_c']
                    
                    # 重新识别表头和数据范围
                    has_header_row = False
                    if max_r > min_r and max_c >= min_c:
                        first_row_has_text_in_num_cols = False
                        second_row_has_num = False
                        for c in range(min_c + 1, max_c + 1):
                            v1 = self.cell_cache.get((min_r, c), '')
                            v2 = self.cell_cache.get((min_r + 1, c), '')
                            if isinstance(v1, str) and v1.strip() != '':
                                first_row_has_text_in_num_cols = True
                            if isinstance(v2, (int, float)):
                                second_row_has_num = True
                        if first_row_has_text_in_num_cols and second_row_has_num:
                            has_header_row = True

                    # 数据列（Y轴）
                    y_cols = []
                    for c in range(min_c, max_c + 1):
                        has_num = False
                        for r in range(min_r, max_r + 1):
                            if has_header_row and r == min_r:
                                continue
                            v = self.cell_cache.get((r, c), '')
                            if isinstance(v, (int, float)):
                                has_num = True
                                break
                        if has_num:
                            y_cols.append(c)
                            
                    if not y_cols:
                        continue 
                        
                    x_col = min_c
                    if x_col in y_cols:
                        x_col = None
                        
                    start_r = min_r + 1 if has_header_row else min_r
                    
                    from openpyxl.chart.series import SeriesLabel
                    
                    for i, c_idx in enumerate(y_cols):
                        data_ref = Reference(ws, min_col=c_idx+1, min_row=start_r+1, max_row=max_r+1)
                        
                        series_name = chart.get('legend_name', '数值')
                        if has_header_row:
                            header_val = self.cell_cache.get((min_r, c_idx), '')
                            if header_val and isinstance(header_val, str):
                                series_name = header_val
                                
                        if len(y_cols) > 1 and not has_header_row:
                            series_name = f"{series_name}{i+1}"
                            
                        e_chart.add_data(data_ref, titles_from_data=False)
                        
                        if len(e_chart.series) > i:
                            s = e_chart.series[i]
                            s.tx = SeriesLabel(v=series_name)
                            
                            # 设置颜色
                            chart_colors = chart.get('colors', [])
                            if not chart_colors:
                                chart_colors = CHART_COLORS
                            color_hex = chart_colors[i % len(chart_colors)].replace('#', '')
                            
                            if c_type == 'bar':
                                s.graphicalProperties.solidFill = color_hex
                                s.graphicalProperties.line.solidFill = color_hex
                            elif c_type == 'line':
                                s.graphicalProperties.line.solidFill = color_hex
                                s.graphicalProperties.line.width = 20000

                    # 添加分类轴
                    if x_col is not None:
                        cats_ref = Reference(ws, min_col=x_col+1, min_row=start_r+1, max_row=max_r+1)
                        e_chart.set_categories(cats_ref)
                        
                    ws.add_chart(e_chart, f"{get_column_letter(total_cols + 2)}{idx * 15 + 2}")
                except Exception as e:
                    print(f"导出图表失败: {e}")

            wb.save(path)
            self.update_status(f"已导出: {path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")

    # ==================== PyInstaller 打包工具 ====================
    def show_pyinstaller_tool(self):
        self.clear_content()
        self._set_page_title("PyInstaller 打包")
        self.update_status("将 Python 脚本或中文编程打包为 EXE")
        bg = MODERN_COLORS['surface']

        # 顶部标题和说明
        tk.Label(self.content_frame, text="PyInstaller 打包工具",
                 font=H1_FONT, fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 4))
        tk.Label(self.content_frame, text="支持打包 .py / .ctb 脚本，无需编写命令行",
                 font=self.default_font, fg=MODERN_COLORS['text_muted'],
                 bg=bg).pack(pady=(0, 12))

        # 中间配置区域
        config_frame = tk.Frame(self.content_frame, bg=MODERN_COLORS['card_bg'],
                                highlightbackground=MODERN_COLORS['border'],
                                highlightthickness=1, padx=20, pady=20)
        config_frame.pack(fill=tk.X, pady=(0, 12))

        # 1. 脚本位置
        tk.Label(config_frame, text="脚本位置:", font=("Microsoft YaHei", 10, "bold"),
                 bg=MODERN_COLORS['card_bg']).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        script_frame = tk.Frame(config_frame, bg=MODERN_COLORS['card_bg'])
        script_frame.grid(row=0, column=1, columnspan=3, sticky=tk.EW, pady=5, padx=(10, 0))
        
        self.pkg_script_var = tk.StringVar()
        ModernEntry(script_frame, width=50, textvariable=self.pkg_script_var).pack(side=tk.LEFT, padx=(0, 8))
        RoundedButton(script_frame, text="浏览", width=80, height=34, radius=6,
                      command=self._browse_pkg_script).pack(side=tk.LEFT)

        # 2. 软件名称
        tk.Label(config_frame, text="软件名称:", font=("Microsoft YaHei", 10, "bold"),
                 bg=MODERN_COLORS['card_bg']).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pkg_name_var = tk.StringVar(value="my_app")
        ModernEntry(config_frame, width=30, textvariable=self.pkg_name_var).grid(
            row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # 3. 软件图标
        tk.Label(config_frame, text="软件图标:", font=("Microsoft YaHei", 10, "bold"),
                 bg=MODERN_COLORS['card_bg']).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        icon_frame = tk.Frame(config_frame, bg=MODERN_COLORS['card_bg'])
        icon_frame.grid(row=2, column=1, columnspan=3, sticky=tk.EW, pady=5, padx=(10, 0))
        
        self.pkg_icon_var = tk.StringVar()
        ModernEntry(icon_frame, width=50, textvariable=self.pkg_icon_var).pack(side=tk.LEFT, padx=(0, 8))
        RoundedButton(icon_frame, text="浏览 (可选)", width=100, height=34, radius=6,
                      command=self._browse_pkg_icon).pack(side=tk.LEFT)

        # 4. 选项
        options_frame = tk.Frame(config_frame, bg=MODERN_COLORS['card_bg'])
        options_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=10, padx=(0, 0))

        # 4.1 控制台/窗口
        console_frame = tk.Frame(options_frame, bg=MODERN_COLORS['card_bg'])
        console_frame.pack(side=tk.LEFT, padx=(0, 30))
        tk.Label(console_frame, text="控制台窗口:", font=("Microsoft YaHei", 10, "bold"),
                 bg=MODERN_COLORS['card_bg']).pack(anchor=tk.W)
        self.pkg_console_var = tk.StringVar(value="--console")
        tk.Radiobutton(console_frame, text="基于控制台", variable=self.pkg_console_var,
                       value="--console", bg=MODERN_COLORS['card_bg'], selectcolor=MODERN_COLORS['card_bg']).pack(anchor=tk.W)
        tk.Radiobutton(console_frame, text="基于窗口（隐藏控制台）", variable=self.pkg_console_var,
                       value="--windowed", bg=MODERN_COLORS['card_bg'], selectcolor=MODERN_COLORS['card_bg']).pack(anchor=tk.W)

        # 4.2 单文件/单目录
        file_frame = tk.Frame(options_frame, bg=MODERN_COLORS['card_bg'])
        file_frame.pack(side=tk.LEFT, padx=(0, 30))
        tk.Label(file_frame, text="单文件 (--onedir / --onefile):", font=("Microsoft YaHei", 10, "bold"),
                 bg=MODERN_COLORS['card_bg']).pack(anchor=tk.W)
        self.pkg_onefile_var = tk.StringVar(value="--onefile")
        tk.Radiobutton(file_frame, text="单目录", variable=self.pkg_onefile_var,
                       value="--onedir", bg=MODERN_COLORS['card_bg'], selectcolor=MODERN_COLORS['card_bg']).pack(anchor=tk.W)
        tk.Radiobutton(file_frame, text="单文件", variable=self.pkg_onefile_var,
                       value="--onefile", bg=MODERN_COLORS['card_bg'], selectcolor=MODERN_COLORS['card_bg']).pack(anchor=tk.W)

        # 5. 输出路径
        tk.Label(config_frame, text="输出路径:", font=("Microsoft YaHei", 10, "bold"),
                 bg=MODERN_COLORS['card_bg']).grid(row=4, column=0, sticky=tk.W, pady=5)
        
        out_frame = tk.Frame(config_frame, bg=MODERN_COLORS['card_bg'])
        out_frame.grid(row=4, column=1, columnspan=3, sticky=tk.EW, pady=5, padx=(10, 0))
        
        default_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        self.pkg_out_var = tk.StringVar(value=default_out)
        ModernEntry(out_frame, width=50, textvariable=self.pkg_out_var).pack(side=tk.LEFT, padx=(0, 8))
        RoundedButton(out_frame, text="浏览", width=80, height=34, radius=6,
                      command=self._browse_pkg_out).pack(side=tk.LEFT)

        config_frame.grid_columnconfigure(1, weight=1)

        # 6. 执行区域
        action_frame = tk.Frame(self.content_frame, bg=bg)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.pkg_btn = RoundedButton(action_frame, text="将 .PY 转换为 .EXE",
                                     command=self._run_pyinstaller,
                                     width=250, height=44, radius=8,
                                     bg=MODERN_COLORS['primary'])
        self.pkg_btn.pack()

        # 7. 日志输出
        log_frame = tk.Frame(self.content_frame, bg=MODERN_COLORS['border'])
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.pkg_log = scrolledtext.ScrolledText(log_frame, height=15,
                                                 font=("Consolas", 10),
                                                 state=tk.DISABLED,
                                                 relief=tk.FLAT, bd=0,
                                                 bg="#1E1E2E", fg="#CDD6F4",
                                                 padx=12, pady=10)
        self.pkg_log.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.pkg_log.tag_configure('error', foreground='#F38BA8')
        self.pkg_log.tag_configure('success', foreground='#A6E3A1')
        self.pkg_log.tag_configure('info', foreground='#89B4FA')
        
        # 底部状态
        self.pkg_status_label = tk.Label(self.content_frame, text="等待打包...",
                                         font=self.default_font, fg=MODERN_COLORS['text_muted'],
                                         bg=bg)
        self.pkg_status_label.pack(anchor=tk.W)

    def _append_pkg_log(self, text, tag=None):
        try:
            self.pkg_log.config(state=tk.NORMAL)
            if tag:
                self.pkg_log.insert(tk.END, text, tag)
            else:
                self.pkg_log.insert(tk.END, text)
            self.pkg_log.see(tk.END)
            self.pkg_log.config(state=tk.DISABLED)
        except Exception:
            pass

    def _browse_pkg_script(self):
        path = filedialog.askopenfilename(
            filetypes=[("Python/CTB 脚本", "*.py *.ctb"), ("所有文件", "*.*")])
        if path:
            self.pkg_script_var.set(path)
            name = os.path.splitext(os.path.basename(path))[0]
            if self.pkg_name_var.get() == "my_app":
                self.pkg_name_var.set(name)

    def _browse_pkg_icon(self):
        path = filedialog.askopenfilename(
            filetypes=[("图标文件", "*.ico"), ("所有文件", "*.*")])
        if path:
            self.pkg_icon_var.set(path)

    def _browse_pkg_out(self):
        path = filedialog.askdirectory()
        if path:
            self.pkg_out_var.set(path)

    def _run_pyinstaller(self):
        script_path = self.pkg_script_var.get().strip()
        if not script_path or not os.path.exists(script_path):
            messagebox.showerror("错误", "请选择有效的脚本文件！")
            return
            
        name = self.pkg_name_var.get().strip()
        if not name:
            messagebox.showerror("错误", "请输入软件名称！")
            return
            
        icon = self.pkg_icon_var.get().strip()
        console = self.pkg_console_var.get()
        onefile = self.pkg_onefile_var.get()
        out_path = self.pkg_out_var.get().strip()
        
        if not out_path:
            out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
            self.pkg_out_var.set(out_path)
            
        try:
            os.makedirs(out_path, exist_ok=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建输出目录: {e}")
            return

        # 构建命令
        cmd = ["pyinstaller", "-y", "--clean", "--noconfirm", console, onefile, "--name", name]
        if icon:
            cmd.extend(["--icon", icon])
            
        # 临时工作目录
        work_path = os.path.join(out_path, "build")
        spec_path = out_path
        cmd.extend(["--distpath", out_path, "--workpath", work_path, "--specpath", spec_path])
        
        if script_path.endswith('.ctb'):
            with open(script_path, 'r', encoding='utf-8') as f:
                code_content = f.read()

            temp_runner = os.path.join(out_path, "temp_ctb_runner.py")
            
            # 提取完整的核心依赖环境（包括 import 语句和全局变量）
            base_imports = """
import sys
import os
import time
import re
from collections import defaultdict

"""
            core_logic = inspect.getsource(InterpreterError) + "\n"
            core_logic += inspect.getsource(_find_outside_string) + "\n"
            core_logic += inspect.getsource(_is_number_str) + "\n"
            core_logic += inspect.getsource(_to_str) + "\n"
            core_logic += inspect.getsource(_num) + "\n"
            core_logic += "_FULLWIDTH_MAP = " + repr(_FULLWIDTH_MAP) + "\n"
            core_logic += inspect.getsource(_normalize_fullwidth) + "\n"
            core_logic += inspect.getsource(_preprocess_code) + "\n"
            core_logic += inspect.getsource(_ASTParser) + "\n"
            core_logic += inspect.getsource(_ExprParser) + "\n"
            core_logic += inspect.getsource(ChineseInterpreter) + "\n"

            if console == '--windowed':
                # 基于窗口运行：自带 Tkinter 界面
                runner_code = base_imports + """
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext

""" + core_logic + f"""

class GuiInterpreter(ChineseInterpreter):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.output_text = scrolledtext.ScrolledText(root, height=20, width=60, font=("Consolas", 12))
        self.output_text.pack(padx=10, pady=10)

    def _emit(self, text):
        self.output_text.insert(tk.END, text + "\\n")
        self.output_text.see(tk.END)
        self.root.update()

    def _builtin_input(self, prompt=""):
        return simpledialog.askstring("输入", prompt, parent=self.root) or ""

def main():
    root = tk.Tk()
    root.title("中文编程运行器")
    root.geometry("800x600")
    interp = GuiInterpreter(root)
    code = {repr(code_content)}
    interp.execute(code)
    # 执行结束后不关闭窗口，让用户能看结果
"""
            else:
                # 基于控制台运行：直接 print 和 input
                runner_code = base_imports + core_logic + f"""

def main():
    interp = ChineseInterpreter(print_callback=print, input_callback=input)
    code = {repr(code_content)}
    interp.execute(code)
    try:
        input("\\nPress Enter to exit...")
    except RuntimeError:
        pass
"""
            runner_code += """
if __name__ == "__main__":
    main()
"""
            with open(temp_runner, 'w', encoding='utf-8') as f:
                f.write(runner_code)
                
            cmd.append(temp_runner)
        else:
            cmd.append(script_path)

        self.pkg_btn.set_state('disabled')
        self.pkg_status_label.config(text="正在打包，请稍候...", fg=MODERN_COLORS['primary'])
        
        self.pkg_log.config(state=tk.NORMAL)
        self.pkg_log.delete(1.0, tk.END)
        self.pkg_log.config(state=tk.DISABLED)
        
        self._append_pkg_log(f"执行的命令:\n{' '.join(cmd)}\n\n", 'info')

        def run_task():
            try:
                # 启动子进程
                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                for line in process.stdout:
                    self.root.after(0, lambda l=line: self._append_pkg_log(l))
                    
                process.wait()
                
                if process.returncode == 0:
                    self.root.after(0, lambda: self._append_pkg_log("\n打包成功！", 'success'))
                    self.root.after(0, lambda: self.pkg_status_label.config(text=f"打包完成，输出目录: {out_path}", fg=MODERN_COLORS['success']))
                else:
                    self.root.after(0, lambda: self._append_pkg_log(f"\n打包失败，退出代码: {process.returncode}", 'error'))
                    self.root.after(0, lambda: self.pkg_status_label.config(text="打包失败", fg=MODERN_COLORS['danger']))
                    
            except FileNotFoundError:
                self.root.after(0, lambda: self._append_pkg_log("\n错误: 找不到 pyinstaller 命令。请确保已安装 pyinstaller。\n运行: pip install pyinstaller", 'error'))
                self.root.after(0, lambda: self.pkg_status_label.config(text="找不到 PyInstaller", fg=MODERN_COLORS['danger']))
            except Exception as e:
                self.root.after(0, lambda err=str(e): self._append_pkg_log(f"\n发生异常: {err}", 'error'))
                self.root.after(0, lambda: self.pkg_status_label.config(text="打包异常", fg=MODERN_COLORS['danger']))
            finally:
                self.root.after(0, lambda: self.pkg_btn.set_state('normal'))

        threading.Thread(target=run_task, daemon=True).start()

    # ==================== 编程页 ====================
    def show_programming(self):
        self.clear_content()
        self._set_page_title("中文编程")
        self.update_status("编程模式 - 5.0 新增：获取输入、变成整数、变成小数、变成字符串")
        bg = MODERN_COLORS['surface']
        tk.Label(self.content_frame, text="中文编程环境",
                 font=H1_FONT, fg=MODERN_COLORS['primary'], bg=bg).pack(pady=(0, 10))
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        self.prog_notebook = notebook

        prog_frame = tk.Frame(notebook, bg=bg)
        notebook.add(prog_frame, text="程序")

        btn_frame = tk.Frame(prog_frame, bg=bg)
        btn_frame.pack(fill=tk.X, pady=(6, 4))
        RoundedButton(btn_frame, text="导入", command=self.import_program,
                      width=90, height=34, radius=6,
                      bg=MODERN_COLORS['primary_light'],
                      fg=MODERN_COLORS['primary'],
                      hover_bg='#D0E4F7').pack(side=tk.LEFT, padx=4)
        RoundedButton(btn_frame, text="保存", command=self.save_program,
                      width=90, height=34, radius=6,
                      bg=MODERN_COLORS['primary_light'],
                      fg=MODERN_COLORS['primary'],
                      hover_bg='#D0E4F7').pack(side=tk.LEFT, padx=4)
        self.run_btn = RoundedButton(btn_frame, text="执行", command=self.execute_program,
                                     width=110, height=34, radius=6)
        self.run_btn.pack(side=tk.LEFT, padx=4)
        RoundedButton(btn_frame, text="插入模板", command=self.insert_template,
                      width=110, height=34, radius=6).pack(side=tk.LEFT, padx=4)

        editor_frame = tk.Frame(prog_frame, bg=MODERN_COLORS['border'])
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.code_editor = tk.Text(editor_frame, height=20,
                                   font=("Consolas", 11), wrap=tk.WORD,
                                   relief=tk.FLAT, bd=0,
                                   bg=MODERN_COLORS['surface'],
                                   fg=MODERN_COLORS['text'],
                                   insertbackground=MODERN_COLORS['primary'],
                                   padx=10, pady=8,
                                   undo=True)
        sb = tk.Scrollbar(editor_frame, orient=tk.VERTICAL,
                          command=self.code_editor.yview)
        self.code_editor.configure(yscrollcommand=sb.set)
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._setup_highlight()
        self._hl_job = None
        self._hl_lock = False
        self.code_editor.insert('1.0', CODE_TEMPLATE)
        self.code_editor.bind('<KeyRelease>', self._schedule_highlight)
        self.code_editor.bind('<<Paste>>', self._schedule_highlight)
        self.code_editor.bind('<<Cut>>', self._schedule_highlight)
        self.root.after(80, self._highlight_code)

        result_frame = tk.Frame(notebook, bg=bg)
        notebook.add(result_frame, text="执行结果")

        self.input_frame = tk.Frame(result_frame, bg=MODERN_COLORS['primary_light'])
        self.input_label = tk.Label(self.input_frame, text="输入:",
                                    bg=MODERN_COLORS['primary_light'],
                                    fg=MODERN_COLORS['primary'],
                                    font=("Microsoft YaHei", 10, "bold"))
        self.input_label.pack(side=tk.LEFT, padx=(10, 4), pady=6)
        self.input_entry = tk.Entry(self.input_frame, font=("Consolas", 11),
                                    relief=tk.FLAT, bd=0,
                                    bg=MODERN_COLORS['surface'],
                                    fg=MODERN_COLORS['text'],
                                    insertbackground=MODERN_COLORS['primary'],
                                    highlightthickness=1,
                                    highlightbackground=MODERN_COLORS['border'],
                                    highlightcolor=MODERN_COLORS['primary'])
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=6)
        tk.Label(self.input_frame, text="按 Enter 提交",
                 bg=MODERN_COLORS['primary_light'],
                 fg=MODERN_COLORS['text_light'],
                 font=("Microsoft YaHei", 9)).pack(side=tk.LEFT, padx=(4, 10))
        self.input_entry.bind('<Return>', lambda e: self._submit_input())
        self._input_submit_cb = None

        self.exec_result = tk.Text(result_frame, height=20,
                                   font=("Consolas", 11),
                                   state=tk.DISABLED,
                                   relief=tk.FLAT, bd=0,
                                   bg=MODERN_COLORS['bg'],
                                   fg=MODERN_COLORS['text'],
                                   padx=12, pady=10)
        self.exec_result.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.exec_result.tag_configure('input_prompt',
                                       foreground=MODERN_COLORS['primary'],
                                       font=("Consolas", 11, "bold"))
        self.exec_result.tag_configure('input_value',
                                       foreground=MODERN_COLORS['success'],
                                       font=("Consolas", 11))
        self.exec_result.tag_configure('error',
                                       foreground=MODERN_COLORS['danger'],
                                       font=("Consolas", 11, "bold"))

    def _setup_highlight(self):
        t = self.code_editor
        t.tag_configure('kw', foreground='#0050B3', font=("Consolas", 11, "bold"))
        t.tag_configure('str', foreground='#008000')
        t.tag_configure('num', foreground='#B85500')
        t.tag_configure('cmt', foreground='#808080', font=("Consolas", 11, "italic"))
        t.tag_configure('bi', foreground='#7B1FA2', font=("Consolas", 11, "bold"))

    def _schedule_highlight(self, _event=None):
        if self._hl_job:
            try:
                self.root.after_cancel(self._hl_job)
            except Exception:
                pass
        self._hl_job = self.root.after(120, self._highlight_code)

    def _highlight_code(self):
        if self._hl_lock:
            return
        try:
            widget = self.code_editor
        except AttributeError:
            return
        self._hl_lock = True
        try:
            content = widget.get('1.0', 'end-1c')
            for tag in ('kw', 'str', 'num', 'cmt', 'bi'):
                widget.tag_remove(tag, '1.0', 'end')
            if not content:
                return
            lines = content.split('\n')
            for i, line in enumerate(lines):
                ln = i + 1
                cidx = -1
                for marker in ('注释:', '注释：'):
                    p = line.find(marker)
                    if p != -1 and (cidx == -1 or p < cidx):
                        cidx = p
                code_part = line if cidx == -1 else line[:cidx]
                if cidx != -1:
                    widget.tag_add('cmt', f"{ln}.{cidx}", f"{ln}.{len(line)}")

                str_ranges = [(m.start(), m.end())
                              for m in re.finditer(r'"[^"\n]*"', code_part)]
                for s, e in str_ranges:
                    widget.tag_add('str', f"{ln}.{s}", f"{ln}.{e}")

                def in_str(pos):
                    for s, e in str_ranges:
                        if s <= pos < e:
                            return True
                    return False

                for m in re.finditer(r'(?<![\w.])\d+(?:\.\d+)?', code_part):
                    if not in_str(m.start()):
                        widget.tag_add('num', f"{ln}.{m.start()}", f"{ln}.{m.end()}")

                for kw in _HIGHLIGHT_KEYWORDS:
                    start = 0
                    while True:
                        p = code_part.find(kw, start)
                        if p == -1:
                            break
                        if not in_str(p):
                            widget.tag_add('kw', f"{ln}.{p}", f"{ln}.{p + len(kw)}")
                        start = p + len(kw)

                for kw in ('正确', '错误'):
                    start = 0
                    while True:
                        p = code_part.find(kw, start)
                        if p == -1:
                            break
                        if not in_str(p):
                            widget.tag_add('kw', f"{ln}.{p}", f"{ln}.{p + 2}")
                        start = p + 2

                for bi in ('获取输入', '变成整数', '变成小数', '变成字符串'):
                    start = 0
                    while True:
                        p = code_part.find(bi, start)
                        if p == -1:
                            break
                        if not in_str(p):
                            widget.tag_add('bi', f"{ln}.{p}", f"{ln}.{p + len(bi)}")
                        start = p + len(bi)
        except Exception:
            pass
        finally:
            self._hl_lock = False

    def import_program(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CTB文件", "*.ctb"), ("所有文件", "*.*")])
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.code_editor.delete(1.0, tk.END)
                self.code_editor.insert(tk.END, content)
                self.update_status(f"已导入: {filename}")
                self.root.after(80, self._highlight_code)
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")

    def save_program(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".ctb",
            filetypes=[("CTB文件", "*.ctb"), ("所有文件", "*.*")])
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.code_editor.get(1.0, tk.END))
                self.update_status(f"已保存: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")

    def insert_template(self):
        if messagebox.askyesno("确认", "插入模板会覆盖当前代码，是否继续？"):
            self.code_editor.delete(1.0, tk.END)
            self.code_editor.insert('1.0', CODE_TEMPLATE)
            self.root.after(80, self._highlight_code)

    def _append_result(self, text, tag=None):
        try:
            self.exec_result.config(state=tk.NORMAL)
            if tag:
                self.exec_result.insert(tk.END, text, tag)
            else:
                self.exec_result.insert(tk.END, text)
            self.exec_result.see(tk.END)
            self.exec_result.config(state=tk.DISABLED)
        except Exception:
            pass

    def _print_callback(self, text):
        self.root.after(0, lambda t=text: self._append_result(t + "\n"))

    def _show_input_bar(self, prompt=""):
        try:
            self.input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=6, pady=(0, 6))
            self.input_label.config(text=prompt if prompt else "输入:")
            self.input_entry.delete(0, tk.END)
            self.input_entry.focus_set()
        except Exception:
            pass

    def _hide_input_bar(self):
        try:
            self.input_frame.pack_forget()
        except Exception:
            pass

    def _submit_input(self):
        if self._current_input_holder is None or self._current_input_event is None:
            return
        val = self.input_entry.get()
        self._current_input_holder['value'] = val
        self._append_result(val + "\n", 'input_value')
        self._hide_input_bar()
        try:
            self._current_input_event.set()
        except Exception:
            pass

    def _input_callback(self, prompt=""):
        if not self._interp_running:
            return ""
        holder = {'value': ''}
        event = threading.Event()
        self._current_input_holder = holder
        self._current_input_event = event

        def ask_ui():
            try:
                if self.prog_notebook is not None:
                    self.prog_notebook.select(1)
            except Exception:
                pass
            self._append_result(prompt, 'input_prompt')
            self._show_input_bar(prompt)

        self.root.after(0, ask_ui)
        event.wait()
        self._current_input_holder = None
        self._current_input_event = None
        return holder.get('value', '')

    def _on_exec_finish(self):
        self._interp_running = False
        try:
            if self.run_btn is not None:
                self.run_btn.set_state('normal')
                self.run_btn.set_text("执行")
        except Exception:
            pass
        self._hide_input_bar()
        self.update_status("执行完成")

    def execute_program(self):
        if self._interp_running:
            messagebox.showinfo("提示", "程序正在执行中，请稍候……")
            return
        code = self.code_editor.get(1.0, tk.END)

        try:
            self.exec_result.config(state=tk.NORMAL)
            self.exec_result.delete(1.0, tk.END)
            self.exec_result.config(state=tk.DISABLED)
        except Exception:
            pass

        try:
            if self.prog_notebook is not None:
                self.prog_notebook.select(1)
        except Exception:
            pass

        self._interp_running = True
        try:
            if self.run_btn is not None:
                self.run_btn.set_state('disabled')
                self.run_btn.set_text("执行中…")
        except Exception:
            pass
        self.update_status("程序执行中...")

        interpreter = ChineseInterpreter(
            print_callback=self._print_callback,
            input_callback=self._input_callback
        )

        def run():
            try:
                interpreter.execute(code)
            except Exception as e:
                self.root.after(0, lambda err=str(e):
                                self._append_result(f"\n错误: {err}\n", 'error'))
            finally:
                self.root.after(0, self._on_exec_finish)

        t = threading.Thread(target=run, daemon=True)
        t.start()

    # ==================== 其他页 ====================
    def export_result(self):
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".txt")
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("化学工具箱 v5.0 计算结果\n")
                    f.write(f"导出时间: {datetime.datetime.now()}\n")
                messagebox.showinfo("成功", f"已保存到 {filename}")
        except Exception:
            messagebox.showerror("错误", "保存失败")

    def show_unit_converter(self):
        messagebox.showinfo("单位换算",
            "常用换算:\n1 mol/L = 1000 mmol/L\n1 atm = 101.325 kPa\n"
            "1 cal = 4.184 J\n0 C = 273.15 K")

    def show_lab_notebook(self):
        self.clear_content()
        self._set_page_title("实验记录本")
        tk.Label(self.content_frame, text="实验记录本", font=H1_FONT,
                 bg=MODERN_COLORS['surface'],
                 fg=MODERN_COLORS['primary']).pack(pady=(0, 10))
        text_area = scrolledtext.ScrolledText(self.content_frame, height=20,
                                              relief=tk.FLAT, bd=0,
                                              bg=MODERN_COLORS['bg'],
                                              padx=12, pady=10,
                                              font=self.default_font)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        text_area.insert(tk.END, f"实验日期: {datetime.datetime.now()}\n\n")

        def save():
            try:
                with filedialog.asksaveasfile(mode='w', defaultextension=".txt") as f:
                    if f:
                        f.write(text_area.get(1.0, tk.END))
                        messagebox.showinfo("成功", "已保存")
            except Exception:
                pass

        RoundedButton(self.content_frame, text="保存", command=save,
                      width=120, height=40).pack(pady=6)

    # ==================== 帮助 / 关于 / 插件文档 / 语言文档 ====================
    def show_help(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        help_dir = os.path.join(base_dir, "help")
        try:
            os.makedirs(help_dir, exist_ok=True)
        except Exception:
            pass
        help_file = os.path.join(help_dir, "help.html")

        html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>化学工具箱 v4.1 - 帮助与实验演示</title>
    <style>
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

        .page-panel { display: none; }
        .page-panel.active { display: block; }

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
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 12px;
            margin: 12px 0;
        }
        .feature-card {
            background: linear-gradient(135deg, #f8fbff, #eaf2ff);
            border: 1px solid #d6e6ff;
            border-radius: 8px;
            padding: 14px 16px;
        }
        .feature-card h3 {
            color: #1a5fb4;
            font-size: 15px;
            margin-bottom: 6px;
        }
        .feature-card p {
            color: #555;
            font-size: 13px;
            line-height: 1.6;
            margin: 0;
        }

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

    <nav class="top-nav">
        <div class="nav-inner">
            <div class="nav-title">化学工具箱 v4.1</div>
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="switchPage('help')">帮助文档</button>
                <button class="nav-tab" onclick="switchPage('experiment')">实验演示</button>
            </div>
        </div>
    </nav>

    <div id="help-page" class="page-panel active">
        <div class="help-body">
            <div class="help-container">
                <h1>化学工具箱 v4.1 帮助文档</h1>
                <p>欢迎使用化学工具箱！本软件集成了化学方程式配平、元素周期表、多种计算工具、
                实用功能、<strong>CTB 表格</strong>、中文编程环境以及可扩展的插件系统。</p>

                <h2>v4.1 更新亮点</h2>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h3>CTB 表格（新增）</h3>
                        <p>类 Excel 表格编辑器，支持 .ctbt / .xlsx / .xls 导入导出，
                        字体、字号、加粗在 Excel 中完整保留。</p>
                    </div>
                    <div class="feature-card">
                        <h3>中文编程增强</h3>
                        <p>新增 如果 / 否则如果 / 否则、定义函数 / 返回 语法，
                        并提供实时语法高亮。</p>
                    </div>
                    <div class="feature-card">
                        <h3>插件系统增强</h3>
                        <p>新增 PluginBase 基类，可注册菜单、快捷键，拦截配平与计算请求，
                        提供完整开发文档。</p>
                    </div>
                    <div class="feature-card">
                        <h3>体验优化</h3>
                        <p>实用功能与元素周期表支持鼠标滚轮平滑滚动，
                        帮助/关于界面焕新。</p>
                    </div>
                </div>

                <h2>主要功能</h2>
                <ul>
                    <li><strong>配平：</strong>支持化学方程式及离子方程式（用 <code>^1+</code> / <code>^2-</code> 表示电荷）。</li>
                    <li><strong>元素周期表：</strong>点击元素查看详细信息（原子量、电负性、电子排布等）。</li>
                    <li><strong>计算工具：</strong>摩尔质量、浓度、稀释、比例、元素百分比、经验式、浓度换算、产率。</li>
                    <li><strong>实用功能：</strong>pH、气体定律、热化学、氧化还原、有机、溶解度、缓冲溶液、滴定、光谱、动力学、电化学、平衡常数、热力学、分压、核化学、溶液配制。</li>
                    <li><strong>CTB 表格（测试功能）：</strong>表格制作、文件导入/导出、行高列宽与字体设置。</li>
                    <li><strong>中文编程：</strong>变量、算术、比较、循环、条件分支、函数定义与返回、语法高亮。</li>
                </ul>

                <h2>中文编程语法速查</h2>
                <ul>
                    <li><code>打印 (表达式)</code></li>
                    <li><code>表达式 赋值给 变量</code></li>
                    <li><code>当 条件 时，执行：</code>（缩进 4 空格）</li>
                    <li><code>在 变量 的 起 到 止 的范围内，以 步长 的步长执行：</code></li>
                    <li><code>如果 条件 时，执行：</code> / <code>否则如果 条件 时，执行：</code> / <code>否则：</code></li>
                    <li><code>定义函数 名为 函数名，参数为 参数1，参数2 的函数：</code></li>
                    <li><code>返回 表达式</code></li>
                    <li>布尔字面量：<code>正确</code> / <code>错误</code></li>
                    <li>注释：<code>注释：</code> 或 <code>注释:</code> 后面到行尾</li>
                </ul>

                <h2>插件系统</h2>
                <p>将自定义插件（<code>.py</code> 文件）放入程序目录下的 <code>plugins</code> 文件夹，
                程序启动时会自动加载，并挂载到"实用功能"页面最下方以及菜单/快捷键中。</p>
                <p>插件需提供名为 <code>Plugin</code> 的类，参数为 app 实例，可继承 <code>PluginBase</code>。</p>
                <p>详细 API 请参考"帮助 → 插件开发文档"。</p>

                <h2>使用提示及注意事项</h2>
                <ul>
                    <li>化学式区分大小写（如 Co 和 CO 不同）。</li>
                    <li>配平时，若无法配平请检查输入的化学方程式是否准确。</li>
                    <li>计算结果均为近似值，适用于教学和一般计算。</li>
                    <li>CTB 表格的 Excel 导入导出需要 <code>openpyxl</code>（.xls 需要 <code>xlrd</code>）。</li>
                    <li>请勿导入任何不信任的、来源不明的插件。</li>
                </ul>

                <div class="warning-box">
                    <strong>免责声明：</strong> 本软件中数据由 AI 收集，不保证准确，请仔细判断。
                    本软件数据由 AI 添加，部分功能由 AI 开发，所以本软件不保证任何数据以及功能计算出的结果准确，
                    也不保证结论正确，由本软件造成的任何问题，本软件开发者不承担任何责任。
                    "实验演示模块"是测试功能，不稳定，请谨慎使用。<br><br>
                    <strong>使用协议：</strong> 如果开始使用本软件，则认为已经同意上述说明。
                    若不同意，则应立即停止使用本软件。
                </div>

                <h2>版本信息</h2>
                <p>化学工具箱 v4.1，在 v4.0 基础上修复 CTB 表格 Excel 字体丢失、实用功能滚轮支持，
                并优化帮助与关于界面。</p>
                <div class="help-footer">© 化学爱好者 | 使用愉快！</div>
            </div>
        </div>
    </div>

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
        function switchPage(page) {
            document.querySelectorAll('.page-panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));

            if (page === 'help') {
                document.getElementById('help-page').classList.add('active');
                document.querySelectorAll('.nav-tab')[0].classList.add('active');
            } else {
                document.getElementById('experiment-page').classList.add('active');
                document.querySelectorAll('.nav-tab')[1].classList.add('active');
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

        window.addEventListener('load', () => {
            drawGrid();
            drawNucleus();
        });
    </script>
</body>
</html>
"""
        try:
            if os.path.exists(help_file):
                try:
                    os.remove(help_file)
                except Exception:
                    pass
            with open(help_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            webbrowser.open(help_file)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建或打开帮助文件：{e}")

    def show_about(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        about_dir = os.path.join(base_dir, "about")
        try:
            os.makedirs(about_dir, exist_ok=True)
        except Exception:
            pass
        about_file = os.path.join(about_dir, "about.html")

        html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>关于 - 化学工具箱 v5.0</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Microsoft YaHei', 'Segoe UI', system-ui, sans-serif; background: #f5f5f5; min-height: 100vh; }
.top-nav { background: linear-gradient(135deg, #1a5fb4, #0d3b8c); box-shadow: 0 2px 10px rgba(0,0,0,0.2); position: sticky; top: 0; z-index: 1000; }
.nav-inner { max-width: 1100px; margin: 0 auto; padding: 0 20px; display: flex; align-items: center; justify-content: space-between; }
.nav-title { color: #fff; font-size: 18px; font-weight: 600; padding: 14px 0; }
.about-body { padding: 40px 20px; }
.about-container { max-width: 820px; margin: auto; background: #fff; padding: 36px 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
.header-area { text-align: center; padding-bottom: 24px; border-bottom: 2px solid #eef3f9; }
.app-logo { width: 64px; height: 64px; border-radius: 16px; background: linear-gradient(135deg, #1a5fb4, #0d3b8c); display: inline-flex; align-items: center; justify-content: center; color: #fff; font-size: 32px; font-weight: bold; letter-spacing: -2px; box-shadow: 0 6px 18px rgba(26,95,180,0.35); margin-bottom: 14px; }
h1 { color: #1a3d6b; font-size: 26px; margin-bottom: 6px; }
.version { display: inline-block; background: #eaf2ff; color: #1a5fb4; padding: 3px 12px; border-radius: 999px; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.slogan { color: #7f8c8d; font-size: 14px; margin-top: 6px; }
h2 { color: #1a5fb4; font-size: 17px; margin: 26px 0 12px; padding-left: 10px; border-left: 3px solid #3584e4; }
p { line-height: 1.8; color: #333; font-size: 14px; margin-bottom: 10px; }
ul { line-height: 1.9; padding-left: 24px; color: #333; font-size: 14px; }
ul li { margin-bottom: 4px; }
.feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin: 8px 0; }
.feature-card { background: linear-gradient(135deg, #f8fbff, #eaf2ff); border: 1px solid #d6e6ff; border-radius: 10px; padding: 14px 16px; transition: all 0.25s; }
.feature-card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(26,95,180,0.12); }
.feature-card h3 { color: #1a5fb4; font-size: 14px; margin-bottom: 6px; }
.feature-card p { color: #555; font-size: 13px; line-height: 1.6; margin: 0; }
.info-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
.info-table th, .info-table td { border: 1px solid #e6eef8; padding: 9px 12px; text-align: left; font-size: 14px; }
.info-table th { background: #eaf2ff; color: #1a5fb4; font-weight: 600; width: 140px; }
.warning-box { background: #fff3cd; border-left: 4px solid #f0ad4e; padding: 12px 16px; margin: 14px 0; border-radius: 0 8px 8px 0; color: #856404; font-size: 13px; line-height: 1.7; }
.warning-box strong { color: #d9534f; }
.footer { margin-top: 32px; padding-top: 18px; border-top: 1px solid #eee; text-align: center; color: #888; font-size: 13px; }
</style>
</head>
<body>
<nav class="top-nav">
    <div class="nav-inner">
        <div class="nav-title">化学工具箱 v5.0</div>
    </div>
</nav>

<div class="about-body">
    <div class="about-container">
        <div class="header-area">
            <div class="app-logo">CTB</div>
            <h1>化学工具箱</h1>
            <div class="version">版本 5.0</div>
            <div class="slogan">集化学配平 · 计算 · 学习 · 编程 · 表格于一体的桌面工具</div>
        </div>

        <h2>v5.0 更新亮点</h2>
        <div class="feature-grid">
            <div class="feature-card">
                <h3>PyInstaller 打包工具</h3>
                <p>新增测试功能，类似 auto-py-to-exe，支持将 Python/CTB 脚本打包成 EXE，提供图标、单文件、窗口模式等配置。</p>
            </div>
            <div class="feature-card">
                <h3>CTB 表格体验优化</h3>
                <p>去除了说明选项卡，大幅压缩了顶部工具栏的高度，让主体表格拥有更大的显示空间，操作更加紧凑。</p>
            </div>
            <div class="feature-card">
                <h3>实用功能排版美化</h3>
                <p>重新设计了实用功能页的卡片样式，增加了分组竖线标识和卡片悬停反馈，视觉更加层次分明。</p>
            </div>
        </div>

        <h2>核心功能一览</h2>
        <ul>
            <li>化学方程式配平（支持离子方程式）</li>
            <li>交互式元素周期表（118 种元素）</li>
            <li>8 种化学计算工具</li>
            <li>16+ 种实用功能（含打包、表格等）</li>
            <li>CTB 表格（支持公式、框选、填充柄、内嵌图表、合并单元格）</li>
            <li>中文编程环境（含语法高亮、后台线程、标准输入）</li>
            <li>可扩展插件系统</li>
        </ul>

        <h2>技术信息</h2>
        <table class="info-table">
            <tr><th>开发语言</th><td>Python 3.10+</td></tr>
            <tr><th>GUI 框架</th><td>Tkinter / ttk（Fluent 现代风）</td></tr>
            <tr><th>数值计算</th><td>NumPy（配平引擎使用 lstsq 求解）</td></tr>
            <tr><th>并发模型</th><td>threading + tkinter.after（编程执行/打包）</td></tr>
            <tr><th>Excel 支持</th><td>openpyxl（.xlsx）/ xlrd（.xls）</td></tr>
            <tr><th>打包支持</th><td>PyInstaller</td></tr>
        </table>

        <div class="warning-box">
            <strong>免责声明：</strong> 本软件中数据由 AI 收集，不保证准确；
            部分功能由 AI 开发，不保证计算结果绝对准确。因使用本软件造成的任何问题，
            软件作者不承担任何责任。若不同意，请停止使用本软件。
        </div>

        <div class="footer">© 2026 化学工具箱 | 开源免费 | 感谢使用！</div>
    </div>
</div>
</body>
</html>"""
        try:
            if os.path.exists(about_file):
                try:
                    os.remove(about_file)
                except Exception:
                    pass
            with open(about_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            webbrowser.open(about_file)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建或打开关于文件：{e}")

    def show_plugin_docs(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        doc_dir = os.path.join(base_dir, "docs")
        try:
            os.makedirs(doc_dir, exist_ok=True)
        except Exception:
            pass
        doc_file = os.path.join(doc_dir, "plugin_dev.html")

        html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>插件开发文档 - 化学工具箱 v5.0</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Microsoft YaHei', system-ui, sans-serif; background:#f5f5f5; padding: 40px 20px; }
.wrap { max-width: 900px; margin: auto; background:#fff; padding: 32px; border-radius: 10px; box-shadow: 0 2px 14px rgba(0,0,0,.08); }
h1 { color:#1a3d6b; border-bottom:2px solid #3498db; padding-bottom:10px; margin-bottom:18px; }
h2 { color:#2980b9; margin:24px 0 10px; font-size:18px; }
p, li { line-height: 1.8; color:#333; }
ul, ol { padding-left: 24px; margin-bottom: 12px; }
pre { background:#1E1E2E; color:#CDD6F4; padding:16px; border-radius:8px; overflow-x:auto; font-family: Consolas, monospace; font-size: 13px; line-height: 1.55; margin: 10px 0; }
code { background:#f0f0f0; padding:2px 6px; border-radius:4px; font-family: Consolas, monospace; color:#c0392b; }
pre code { background: transparent; color: inherit; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; }
th, td { border: 1px solid #ddd; padding: 8px 10px; text-align: left; }
th { background: #E3F2FD; color:#0F6CBD; }
.note { background:#e7f3ff; border-left:4px solid #0F6CBD; padding:10px 14px; border-radius: 0 6px 6px 0; margin: 10px 0; color:#0A4A8A;}
</style>
</head>
<body>
<div class="wrap">
<h1>化学工具箱 v5.0 插件开发文档</h1>

<h2>1. 插件放置位置</h2>
<p>将你的 <code>.py</code> 文件放入主程序同目录下的 <code>plugins/</code> 文件夹即可。程序启动时会自动扫描并加载。</p>

<h2>2. 最小插件示例</h2>
<pre><code>from tkinter import messagebox

class Plugin:
    def __init__(self, app):
        self.app = app

    def get_menu_name(self):
        return "我的插件"

    def run(self):
        messagebox.showinfo("我的插件", "Hello!")</code></pre>

<h2>3. 继承 PluginBase 获得完整能力</h2>
<table>
<tr><th>方法</th><th>说明</th></tr>
<tr><td><code>get_menu_name()</code></td><td>显示在卡片上的名称</td></tr>
<tr><td><code>register_menus()</code></td><td>注册主菜单项</td></tr>
<tr><td><code>on_balance(equation)</code></td><td>拦截配平请求</td></tr>
</table>

<div class="note">
提示：v5.0 的中文编程执行在后台线程中运行，插件无需关心线程安全；
如果你的插件需要更新 UI，请使用 <code>self.app.root.after(0, callback)</code>。
</div>

</div>
</body>
</html>"""
        try:
            if os.path.exists(doc_file):
                try:
                    os.remove(doc_file)
                except Exception:
                    pass
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            webbrowser.open(doc_file)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建或打开文档：{e}")

    def show_lang_docs(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        doc_dir = os.path.join(base_dir, "docs")
        try:
            os.makedirs(doc_dir, exist_ok=True)
        except Exception:
            pass
        doc_file = os.path.join(doc_dir, "lang_dev.html")

        html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>中文编程开发文档 - 化学工具箱 v5.0</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Microsoft YaHei', system-ui, sans-serif; background:#f5f5f5; padding: 40px 20px; }
.wrap { max-width: 900px; margin: auto; background:#fff; padding: 32px; border-radius: 10px; box-shadow: 0 2px 14px rgba(0,0,0,.08); }
h1 { color:#1a3d6b; border-bottom:2px solid #3498db; padding-bottom:10px; margin-bottom:18px; }
h2 { color:#2980b9; margin:24px 0 10px; font-size:18px; border-left: 4px solid #3498db; padding-left: 10px; }
p, li { line-height: 1.8; color:#333; }
ul, ol { padding-left: 24px; margin-bottom: 12px; }
pre { background:#1E1E2E; color:#CDD6F4; padding:16px; border-radius:8px; overflow-x:auto; font-family: Consolas, monospace; font-size: 13px; line-height: 1.55; margin: 10px 0; }
code { background:#f0f0f0; padding:2px 6px; border-radius:4px; font-family: Consolas, monospace; color:#c0392b; }
pre code { background: transparent; color: inherit; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 14px; }
th, td { border: 1px solid #ddd; padding: 10px 12px; text-align: left; }
th { background: #E3F2FD; color:#0F6CBD; }
.note { background:#e7f3ff; border-left:4px solid #0F6CBD; padding:10px 14px; border-radius: 0 6px 6px 0; margin: 10px 0; color:#0A4A8A;}
.warning { background:#fff3cd; border-left:4px solid #f0ad4e; padding:10px 14px; border-radius: 0 6px 6px 0; margin: 10px 0; color:#856404;}
</style>
</head>
<body>
<div class="wrap">
<h1>中文编程语言开发文档</h1>
<p>欢迎使用化学工具箱内置的“中文编程环境”。这里提供了一个简单易学的编程语言，采用自然语言（中文）作为关键字，非常适合初学者、学生进行逻辑训练和化学计算。</p>

<h2>1. 基础语法</h2>
<p>程序由一行行代码组成，通过缩进（Tab 或 4个空格）来表示代码块。支持全角/半角符号混用。</p>

<h3>1.1 注释</h3>
<p>使用 <code>注释:</code> 或 <code>注释：</code>。后面的内容会被忽略。</p>
<pre><code>注释：这是一行注释
打印 ("Hello 化学工具箱")</code></pre>

<h3>1.2 输出与变量</h3>
<p>使用 <code>打印 (...)</code> 输出内容。使用 <code>表达式 赋值给 变量名</code> 进行赋值。</p>
<pre><code>打印 ("请输入你的年龄：")
获取输入() 赋值给 年龄字符串
变成整数(年龄字符串) 赋值给 年龄
年龄 + 1 赋值给 明年年龄
打印 ("明年你 " + 变成字符串(明年年龄) + " 岁了。")</code></pre>

<h2>2. 5.0 版本新增：交互与类型转换</h2>
<table>
    <tr><th>功能名称</th><th>语法示例</th><th>说明</th></tr>
    <tr><td><b>获取输入</b></td><td><code>获取输入()</code> 或 <code>获取输入("提示语")</code></td><td>阻塞等待用户在下方控制台输入内容，按回车后返回字符串。</td></tr>
    <tr><td><b>变成整数</b></td><td><code>变成整数(表达式)</code></td><td>将小数或字符串转为整数（自动截断小数部分）。</td></tr>
    <tr><td><b>变成小数</b></td><td><code>变成小数(表达式)</code></td><td>将整数或字符串转为小数（浮点数）。</td></tr>
    <tr><td><b>变成字符串</b></td><td><code>变成字符串(表达式)</code></td><td>将数字转换为字符串，以便与文字进行拼接。</td></tr>
</table>

<h2>3. 逻辑控制</h2>

<h3>3.1 条件判断</h3>
<pre><code>如果 分数 >= 60 时，执行：
    打印 ("及格了")
否则如果 分数 >= 50 时，执行：
    打印 ("补考")
否则：
    打印 ("不及格")</code></pre>

<h3>3.2 循环：当...时</h3>
<pre><code>1 赋值给 计数
当 计数 <= 5 时，执行：
    打印 (计数)
    计数 + 1 赋值给 计数</code></pre>

<h3>3.3 循环：范围遍历</h3>
<pre><code>注释：从 1 到 10，步长为 2
在 i 的 1 到 10 的范围内，以 2 的步长执行：
    打印 ("当前的 i 是：" + 变成字符串(i))</code></pre>

<h2>4. 函数定义</h2>
<p>使用 <code>定义函数</code> 可以封装重复的逻辑，并支持多参数和返回值。</p>
<pre><code>定义函数 名为 计算平均分，参数为 分数1, 分数2 的函数：
    (分数1 + 分数2) / 2 赋值给 平均分
    返回 平均分

打印 (计算平均分(80, 90))</code></pre>

<h2>5. 模块与扩展</h2>
<pre><code>导入 时间 模块
使用 时间 模块的 睡眠 功能 (1.5)
当前时间() 赋值给 现在
格式化时间(现在) 赋值给 结果
打印 ("当前时间是：" + 结果)</code></pre>

<h2>6. 运算符一览</h2>
<ul>
    <li><b>算术运算</b>： <code>+</code>（加/拼接）、<code>-</code>（减）、<code>*</code>（乘）、<code>/</code>（除）、<code>%</code>（取余）</li>
    <li><b>比较运算</b>： <code>></code>、<code><</code>、<code>>=</code>、<code><=</code>、<code>==</code>（等于）、<code>!=</code>（不等于）</li>
    <li><b>逻辑值</b>： <code>正确</code> (True)、<code>错误</code> (False)</li>
</ul>

</div>
</body>
</html>"""
        try:
            if os.path.exists(doc_file):
                try:
                    os.remove(doc_file)
                except Exception:
                    pass
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            webbrowser.open(doc_file)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建或打开文档：{e}")


# ==================== 示例插件内容 ====================
_EXAMPLE_PLUGIN = '''# -*- coding: utf-8 -*-
"""
示例插件 - 化学工具箱 v5.0
将此文件复制并修改即可开发自己的插件。
"""
from tkinter import messagebox


class Plugin:
    name = "示例插件"
    version = "1.0"
    description = "演示插件基础用法（可以删除本文件）"

    def __init__(self, app):
        self.app = app

    def get_menu_name(self):
        return self.name

    def run(self):
        messagebox.showinfo(
            "示例插件",
            "这是一个示例插件！\\n\\n"
            "参考 帮助 → 插件开发文档 了解如何编写自己的插件。"
        )

    def register_menus(self):
        return []

    def register_shortcuts(self):
        return {}

    def on_balance(self, equation):
        return None

    def on_startup(self):
        print("[示例插件] 已加载")

    def on_shutdown(self):
        print("[示例插件] 已卸载")
'''


if __name__ == "__main__":
    root = tk.Tk()
    app = ChemistryToolbox(root)
    root.mainloop()