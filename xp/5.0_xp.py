# -*- coding: utf-8 -*-
# 化学工具箱 v5.0
# 兼容 Python 3.4（Windows XP）及更高版本，不依赖 NumPy，仅使用标准库
# Excel 功能为可选项：Python 3.4 建议 openpyxl 2.4.9 / xlrd 1.2.0
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog, colorchooser, simpledialog
import tkinter.font as tkfont
import re
import json
import sys
import subprocess
from collections import defaultdict, OrderedDict
import math
try:
    from math import gcd
except ImportError:  # Python 3.4 没有 math.gcd
    from fractions import gcd
from math import log10, sin, cos, tan, log, sqrt, pow
import datetime
import webbrowser
import os
import importlib.util
import time
import threading
import queue
import inspect
import types

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
        return '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)

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
        # Python 3.4 的普通 dict 不保证插入顺序，这里用 OrderedDict
        counts = OrderedDict()

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
                    counts[element] = counts.get(element, 0) + count * multiplier
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
        return counts

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
                    return 0, '错误：未知元素 {0}'.format(element)
                contribution = mass * count
                total_mass += contribution
                if count == 1:
                    details.append('{0}({1})'.format(element, mass))
                else:
                    details.append('{0}{1}({2}×{3})'.format(element, count, mass, count))
            return total_mass, " + ".join(details) + ' = {0}'.format(total_mass)
        except Exception as e:
            return 0, '计算错误：{0}'.format(str(e))

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
        element_valence = OrderedDict()

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


# ==================== 纯 Python 线性代数（替代 NumPy） ====================
_FLOAT_EPS = 2.220446049250313e-16


def _svd_least_squares(A, b):
    """求 A x = b 的最小二乘最小范数解（单边 Jacobi SVD）。

    行为与 numpy.linalg.lstsq(A, b, rcond=None)[0] 一致，
    用于在完全不依赖 NumPy 的情况下求解配平方程组。
    A 为 m 行 n 列的二维列表，b 为长度 m 的列表，返回长度 n 的列表。
    """
    m = len(A)
    n = len(A[0]) if m else 0
    if m == 0 or n == 0:
        return [0.0] * n

    a = [[float(v) for v in row] for row in A]
    bv = [float(v) for v in b]
    # v 记录列变换，最终每列即一个右奇异向量
    v = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

    for _sweep in range(60):
        off = 0.0
        for p in range(n - 1):
            for q in range(p + 1, n):
                alpha = 0.0
                beta = 0.0
                gamma = 0.0
                for i in range(m):
                    ap = a[i][p]
                    aq = a[i][q]
                    alpha += ap * ap
                    beta += aq * aq
                    gamma += ap * aq
                if alpha == 0.0 or beta == 0.0:
                    continue
                denom = math.sqrt(alpha * beta)
                if denom == 0.0 or abs(gamma) <= 1e-16 * denom:
                    continue
                ratio = abs(gamma) / denom
                if ratio > off:
                    off = ratio
                zeta = (beta - alpha) / (2.0 * gamma)
                if zeta >= 0.0:
                    t = 1.0 / (zeta + math.sqrt(1.0 + zeta * zeta))
                else:
                    t = -1.0 / (-zeta + math.sqrt(1.0 + zeta * zeta))
                c = 1.0 / math.sqrt(1.0 + t * t)
                s = c * t
                for i in range(m):
                    ap = a[i][p]
                    aq = a[i][q]
                    a[i][p] = c * ap - s * aq
                    a[i][q] = s * ap + c * aq
                for i in range(n):
                    vp = v[i][p]
                    vq = v[i][q]
                    v[i][p] = c * vp - s * vq
                    v[i][q] = s * vp + c * vq
        if off < 1e-16:
            break

    sigma = []
    for j in range(n):
        s2 = 0.0
        for i in range(m):
            s2 += a[i][j] * a[i][j]
        sigma.append(math.sqrt(s2))

    smax = max(sigma) if sigma else 0.0
    tol = max(m, n) * _FLOAT_EPS * smax
    x = [0.0] * n
    for j in range(n):
        sj = sigma[j]
        if sj == 0.0 or sj <= tol:
            continue
        dot = 0.0
        for i in range(m):
            dot += a[i][j] * bv[i]
        coef = dot / (sj * sj)
        for i in range(n):
            x[i] += coef * v[i][j]
    return x


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
                A = [[float(v) for v in row] for row in A]
                b = [float(v) for v in b]

                if n_unknowns > 1:
                    A_reduced = [row[1:] for row in A]
                    b_reduced = [b[i] - A[i][0] * first_coeff for i in range(len(b))]
                    try:
                        solution = _svd_least_squares(A_reduced, b_reduced)
                        coeffs = [first_coeff] + list(solution)
                        valid = True
                        int_coeffs = []
                        for c in coeffs[:n_unknowns]:
                            if c < 0.01:
                                valid = False
                                break
                            ic = int(round(c))
                            if abs(ic - c) > 1e-3:
                                valid = False
                                break
                            int_coeffs.append(ic)
                        if valid and len(int_coeffs) == n_unknowns:
                            residual = []
                            for i in range(len(A)):
                                total = 0.0
                                for j in range(n_unknowns):
                                    total += A[i][j] * coeffs[j]
                                residual.append(abs(total - b[i]))
                            error = sum(residual)
                            if error < best_error:
                                best_error = error
                                best_solution = int_coeffs
                    except Exception:
                        continue
                elif n_unknowns == 1:
                    if abs(A[0][0] * first_coeff - b[0]) < 1e-5:
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
                    formatted = '{0}{1}'.format(coeff if coeff > 1 else '', formula)
                    if charge > 0:
                        formatted += '^{0}+'.format(charge)
                    elif charge < 0:
                        formatted += '^{0}-'.format(abs(charge))
                    left_parts.append(formatted)

                right_parts = []
                for i, (formula, charge) in enumerate(right_compounds):
                    coeff = best_solution[n_left + i] if (n_left + i) < len(best_solution) else 1
                    formatted = '{0}{1}'.format(coeff if coeff > 1 else '', formula)
                    if charge > 0:
                        formatted += '^{0}+'.format(charge)
                    elif charge < 0:
                        formatted += '^{0}-'.format(abs(charge))
                    right_parts.append(formatted)

                balanced_eq = '{0} = {1}'.format(' + '.join(left_parts), ' + '.join(right_parts))
                valence_info = OrderedDict()
                for idx, (formula, _) in enumerate(left_compounds):
                    valence_info['L{0}'.format(idx)] = ChemicalFormulaParser.calculate_oxidation_states(formula)
                for idx, (formula, _) in enumerate(right_compounds):
                    valence_info['R{0}'.format(idx)] = ChemicalFormulaParser.calculate_oxidation_states(formula)
                return balanced_eq, valence_info

            return "错误：无法配平该方程式，请检查输入格式", {}
        except Exception as e:
            return '配平失败: {0}'.format(str(e)), {}


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
            self.error('未定义的变量: {0}'.format(tok))
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
            raise ValueError('无法将 {0!r} 转换为整数'.format(v))

    def _builtin_to_float(self, v):
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        try:
            if isinstance(v, str):
                v = v.strip()
            return float(v)
        except Exception:
            raise ValueError('无法将 {0!r} 转换为小数'.format(v))

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
            self._emit('第{0}行第{1}列，{2}'.format(e.line, e.col, e.msg))
            return '\n'.join(self._outputs)
        except Exception:
            self._emit(
                '第{0}行第{1}列，无法解释'.format(self._current_line, self._current_col))
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
                raise InterpreterError('不支持的模块: {0}'.format(mod), stmt['line'], stmt['col'])

        elif kind == 'use_module':
            alias = stmt['alias']
            func = stmt['func']
            args_str = stmt['args']

            if alias not in self.modules:
                raise InterpreterError('未导入模块: {0}'.format(alias), stmt['line'], stmt['col'])

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
                        raise InterpreterError('时间模块未知的功能: {0}'.format(func), stmt['line'], stmt['col'])
                except Exception as e:
                    if isinstance(e, InterpreterError):
                        raise
                    raise InterpreterError('执行时间模块功能失败: {0}'.format(e), stmt['line'], stmt['col'])
            else:
                raise InterpreterError('未知模块: {0}'.format(mod), stmt['line'], stmt['col'])

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
                    '函数 {0} 参数数量不正确'.format(name), line_num, col)
            except Exception as e:
                raise InterpreterError(
                    '执行内置函数失败: {0}'.format(e), line_num, col)
        if name not in self.functions:
            raise InterpreterError('未定义的函数: {0}'.format(name), line_num, col)
        params, body = self.functions[name]
        if len(params) != len(args):
            raise InterpreterError(
                '函数 {0} 需要 {1} 个参数，实际传入 {2} 个'.format(name, len(params), len(args)),
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
            messagebox.showerror("错误", '无法打开文件夹: {0}'.format(e))

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
                    plugin_path = os.path.join(plugin_dir, file)
                    spec = importlib.util.spec_from_file_location(file[:-3], plugin_path)
                    if hasattr(importlib.util, 'module_from_spec'):
                        module = importlib.util.module_from_spec(spec)
                    else:  # Python 3.4 没有 module_from_spec
                        module = types.ModuleType(file[:-3])
                        module.__file__ = plugin_path
                        module.__loader__ = spec.loader
                    spec.loader.exec_module(module)
                    if hasattr(module, "Plugin"):
                        plugin_instance = module.Plugin(self)
                        self.plugins.append(plugin_instance)
                except Exception as e:
                    print('加载插件 {0} 失败: {1}'.format(file, e))
        except Exception:
            pass
        for p in self.plugins:
            try:
                if hasattr(p, 'on_startup'):
                    p.on_startup()
            except Exception as e:
                print('插件启动失败: {0}'.format(e))
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
                '化学式: {0}\n相对分子质量: {1}\n\n计算过程:\n{2}'.format(formula, mass, detail))
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
                '溶质的量: {0:.4f} mol\n溶液体积: {1} L\n物质的量浓度: {2:.4f} mol/L'.format(moles, volume, concentration))
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
                'C1V1 = C2V2\n{0} × {1} = C2 × {2}\nC2 = {3:.4f} mol/L'.format(c1, v1, v2, c2))
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
                    '比例式: {0} / {1} = {2} / x\n\n解: x = (b × c) / a = ({3}×{4})/{5} = {6:.6g}'.format(a, b, c, b, c, a, x))
                self.ratio_entries["x_display"].entry.config(state='normal')
                self.ratio_entries["x_display"].delete(0, tk.END)
                self.ratio_entries["x_display"].insert(0, '{0:.6g}'.format(x))
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
                    '比例式: {0} / {1} = x / {2}\n\n解: x = (a × d) / b = ({3}×{4})/{5} = {6:.6g}'.format(a, b, d, a, d, b, x))
                self.ratio_entries["x_display"].entry.config(state='normal')
                self.ratio_entries["x_display"].delete(0, tk.END)
                self.ratio_entries["x_display"].insert(0, '{0:.6g}'.format(x))
                self.ratio_entries["x_display"].entry.config(state='disabled')
        except Exception as e:
            self.ratio_result.delete(1.0, tk.END)
            self.ratio_result.insert(tk.END, '错误：{0}'.format(str(e)))

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
            '化学式: {0}\n摩尔质量: {1:.4f} g/mol\n\n各元素质量分数:\n'.format(formula, total_mass))
        for element in sorted(percent.keys()):
            self.percent_result.insert(tk.END, '{0}: {1:.2f}%\n'.format(element, percent[element]))

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
                self.empirical_result.insert(tk.END, '未知元素 {0}'.format(elem))
                return
            moles[elem] = mass / atomic
        min_mole = min(moles.values())
        ratios = {elem: mole / min_mole for elem, mole in moles.items()}
        for factor in range(1, 20):
            int_ratios = {elem: round(ratios[elem] * factor) for elem in ratios}
            if all(abs(ratios[elem] * factor - int_ratios[elem]) < 0.01 for elem in ratios):
                formula = "".join(
                    '{0}{1}'.format(elem, int_ratios[elem] if int_ratios[elem] > 1 else '')
                    for elem in sorted(int_ratios.keys()))
                self.empirical_result.delete(1.0, tk.END)
                self.empirical_result.insert(tk.END, '经验式: {0}'.format(formula))
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
                '摩尔浓度 = (质量分数 × 密度 × 10) / 摩尔质量\n= ({0} × {1} × 10) / {2} = {3:.4f} mol/L'.format(w, d, M, c))
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
                '产率 = (实际产量 / 理论产量) × 100% = ({0}/{1})×100% = {2:.2f}%'.format(actual, theoretical, percent))
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
                        self.result_text.insert(tk.END, '{0}: '.format(key), "normal")
                        for elem, valence in valences.items():
                            if valence > 0:
                                self.result_text.insert(tk.END, '{0}({1:+d}) '.format(elem, valence), "green_valence")
                            elif valence < 0:
                                self.result_text.insert(tk.END, '{0}({1}) '.format(elem, valence), "red_valence")
                            else:
                                self.result_text.insert(tk.END, '{0}(0) '.format(elem), "normal")
                        self.result_text.insert(tk.END, "\n", "normal")
            self.update_status("配平完成")
        except Exception as e:
            self.result_text.insert(tk.END, '显示错误: {0}'.format(str(e)), "normal")
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
            info = ('元素: {0}\n名称: {1}\n原子序数: {2}\n原子量: {3}\n电负性: {4}\n族: {5}\n周期: {6}\n电子排布: {7}\n电子层: {8}\n简介: {9}'.format(symbol, data['name'], data['atomic'], data['mass'], en, data['group'], data['period'], data['config'], electron_layers, data['desc']))
            messagebox.showinfo("元素信息", info)
        else:
            messagebox.showinfo("元素信息", '未找到 {0} 的详细信息'.format(symbol))

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
                self.ph_result.insert(tk.END, '[H+] = {0} mol/L\npH = {1:.2f}'.format(conc, ph))
            else:
                poh = -log10(conc)
                ph = 14 - poh
                self.ph_result.delete(1.0, tk.END)
                self.ph_result.insert(tk.END, '[OH-] = {0} mol/L\npOH = {1:.2f}\npH = {2:.2f}'.format(conc, poh, ph))
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
                    '[H+] = sqrt(Ka*C) = sqrt({0}*{1}) = {2:.2e} mol/L\npH = {3:.2f}'.format(ka, conc, h_conc, ph))
            else:
                oh_conc = (ka * conc) ** 0.5
                poh = -log10(oh_conc)
                ph = 14 - poh
                self.weak_result.delete(1.0, tk.END)
                self.weak_result.insert(tk.END,
                    '[OH-] = sqrt(Kb*C) = sqrt({0}*{1}) = {2:.2e} mol/L\npOH = {3:.2f}\npH = {4:.2f}'.format(ka, conc, oh_conc, poh, ph))
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
                    '温度 T = PV/(nR) = {0:.2f}*{1:.2f}/({2:.2f}*{3:.4f}) = {4:.2f} K'.format(P, V, n, R, T))
            elif P_s and V_s and T_s:
                P, V, T = float(P_s), float(V_s), float(T_s)
                n = P * V / (R * T)
                self.gas_result.delete(1.0, tk.END)
                self.gas_result.insert(tk.END,
                    '物质的量 n = PV/(RT) = {0:.2f}*{1:.2f}/({2:.4f}*{3:.2f}) = {4:.4f} mol'.format(P, V, R, T, n))
            elif P_s and n_s and T_s:
                P, n, T = float(P_s), float(n_s), float(T_s)
                V = n * R * T / P
                self.gas_result.delete(1.0, tk.END)
                self.gas_result.insert(tk.END,
                    '体积 V = nRT/P = {0:.2f}*{1:.4f}*{2:.2f}/{3:.2f} = {4:.2f} L'.format(n, R, T, P, V))
            elif V_s and n_s and T_s:
                V, n, T = float(V_s), float(n_s), float(T_s)
                P = n * R * T / V
                self.gas_result.delete(1.0, tk.END)
                self.gas_result.insert(tk.END,
                    '压力 P = nRT/V = {0:.2f}*{1:.4f}*{2:.2f}/{3:.2f} = {4:.2f} atm'.format(n, R, T, V, P))
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
                'Q = m*c*dT\nQ = {0} * {1} * {2}\nQ = {3:.2f} J'.format(m, c, dt, q))
        except Exception:
            self.heat_result.delete(1.0, tk.END)
            self.heat_result.insert(tk.END, "输入错误")

    def calc_combustion(self):
        try:
            dh, n = float(self.dh_comb.get()), float(self.n_comb.get())
            q = dh * n
            self.comb_result.delete(1.0, tk.END)
            self.comb_result.insert(tk.END, 'Q = dH * n\nQ = {0} * {1}\nQ = {2:.2f} kJ'.format(dh, n, q))
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
        self.redox_result.insert(tk.END, '化合物: {0}\n\n元素氧化数:\n'.format(formula))
        states = ChemicalFormulaParser.calculate_oxidation_states(formula)
        for element in counts.keys():
            v = states.get(element, 0)
            self.redox_result.insert(tk.END, '{0}: {1:+d}\n'.format(element, v))

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
                '化合物: {0}\n\n可能含有的官能团: {1}'.format(name, ', '.join(set(found))))
        else:
            self.func_result.insert(tk.END, "未识别出常见官能团")

    def calc_isomers(self):
        formula = self.isomer_formula.get().strip()
        self.isomer_result.delete(1.0, tk.END)
        isomers = {"C5H12": 3, "C6H14": 5, "C7H16": 9, "C8H18": 18,
                   "C4H10": 2, "C3H8": 1, "C2H6": 1}
        if formula in isomers:
            self.isomer_result.insert(tk.END,
                '分子式 {0} 的同分异构体数目: {1} 种'.format(formula, isomers[formula]))
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
                'pH = pKa + log([A-]/[HA])\npH = {0} + log({1}/{2})\npH = {3} + {4:.2f}\npH = {5:.2f}'.format(pka, base, acid, pka, log10(base/acid), ph))
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
                'CaVa = CbVb\n{0} * {1} = {2} * Vb\nVb = {3:.4f} L = {4:.2f} mL'.format(ca, va, cb, vb, vb*1000))
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
            tk.Label(cf, text='{0}: {1} nm'.format(color, wavelength), font=self.default_font,
                     bg=bg).pack(pady=3)

    def convert_wavelength(self):
        try:
            lam = float(self.wavelength.get()) * 1e-9
            c = 3e8
            h = 6.626e-34
            energy = h * c / lam
            self.wave_result.delete(1.0, tk.END)
            self.wave_result.insert(tk.END,
                '波长: {0} nm\n能量: {1:.2e} J\n能量: {2:.2f} eV'.format(self.wavelength.get(), energy, energy/1.602e-19))
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
            k = A * math.exp(-ea / (R * T))
            self.kinetics_result.delete(1.0, tk.END)
            self.kinetics_result.insert(tk.END,
                'k = A*exp(-Ea/RT)\nk = {0:.2e} * exp(-{1:.2e}/{2:.3f}*{3:.2f})\nk = {4:.2e} 1/s'.format(A, ea, R, T, k))
        except Exception:
            self.kinetics_result.delete(1.0, tk.END)
            self.kinetics_result.insert(tk.END, "输入错误")

    def calc_half_life(self):
        try:
            k = float(self.k_half.get())
            t_half = math.log(2) / k
            self.half_result.config(text='t1/2 = {0:.2f} s'.format(t_half))
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
            E = e0 - (R * T / (n * F)) * math.log(Q)
            self.nernst_result.delete(1.0, tk.END)
            self.nernst_result.insert(tk.END,
                'E = E0 - (RT/nF) lnQ\n= {0} - ({1}*{2}/{3}/{4}) ln({5})\n= {6:.4f} V'.format(e0, R, T, n, F, Q, E))
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
            dG = -R * T * math.log(K)
            self.eq_result.delete(1.0, tk.END)
            self.eq_result.insert(tk.END,
                'dG0 = -RT lnK\n= -{0} * {1} * ln({2})\n= {3:.2f} J/mol = {4:.2f} kJ/mol'.format(R, T, K, dG, dG/1000))
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
                'dG = dH - T*dS\n= {0:.2f} kJ - {1} * {2:.2f} J/K\n= {3:.2f} kJ/mol'.format(H/1000, T, S, G/1000))
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
                '组分1分压: {0:.4f} atm\n组分2分压: {1:.4f} atm\n总和: {2:.4f} atm'.format(p1, p2, p1+p2))
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
            lam = math.log(2) / t12
            N = N0 * math.exp(-lam * t)
            self.nuclear_result.delete(1.0, tk.END)
            self.nuclear_result.insert(tk.END,
                '衰变常数 lambda = ln2 / t1/2 = {0:.4e} 1/s\n剩余原子数 N = N0 * exp(-lambda*t) = {1} * exp(-{2:.4e}*{3}) = {4:.2f}'.format(lam, N0, lam, t, N))
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
                '所需溶质质量 = C * V * M = {0} * {1} * {2} = {3:.4f} g'.format(C, V, M, mass))
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
                        val = float('{0:.6g}'.format(val))
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
                
            return '{0}{1}'.format(self._col_label(new_c), new_r + 1)
            
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
                    messagebox.showwarning("提示", '图例数量（{0}）与数据点数量（{1}）不匹配。'.format(len(new_cats), len(data)))
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
            btn = RoundedButton(grid_frame, text='{0} ({1})'.format(func_name, desc), 
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
        text_to_insert = '{0}()'.format(func_name)
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
                self.floating_entry.insert(0, '={0}'.format(text_to_insert))
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
                print('绘制图表错误: {0}'.format(e))
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
                canvas.create_text(x+pad_left-6, ty, text='{0:.4g}'.format(val), anchor='e', font=("Arial", 8), fill="#777")
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
                    canvas.create_text(cx, ty_text, text='{0:.4g}'.format(val), anchor=anchor_text, font=("Arial", 8, "bold"), fill="#333")

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
                    canvas.create_text(cx, ty_text, text='{0:.4g}'.format(val), anchor=anchor_text, font=("Arial", 8), fill="#333")

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
                        canvas.create_text(tx, ty, text='{0:.1f}%'.format((abs(val)/total)*100), fill="#FFF", font=("Arial", 8, "bold"))
                    
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
        return '{0}{1}:{2}{3}'.format(col1, row1, col2, row2) if (min_r != max_r or min_c != max_c) else '{0}{1}'.format(col1, row1)

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
            self.cell_ref_var.set('{0}{1}'.format(self._col_label(c), r+1))
            self.formula_bar_var.set(self.table_cells.get((r, c), {}).get('text', ''))
        else:
            self.cell_ref_var.set('{0}R x {1}C'.format(min_r+1, max_c-min_c+1))
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
                ref = '{0}{1}'.format(self._col_label(c), r+1)
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
        self.update_status('已应用格式到 {0} 个单元格'.format(len(self.selected_cells)))

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
                cells['{0},{1}'.format(r, c)] = {
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
            self.update_status('已导出: {0}'.format(path))
        except Exception as e:
            messagebox.showerror("错误", '导出失败: {0}'.format(e))

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
            self.update_status('已导入: {0}'.format(path))
        except Exception as e:
            messagebox.showerror("错误", '导入失败: {0}'.format(e))

    def import_excel_table(self):
        if not HAS_OPENPYXL:
            messagebox.showerror("缺少依赖",
                "导入/导出 Excel 需要 openpyxl 库。\n请运行：pip install openpyxl\n（Python 3.4 请安装：pip install openpyxl==2.4.9）")
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
            from openpyxl.utils import column_index_from_string
            max_r = 1
            max_c = 1
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value is not None:
                        max_r = max(max_r, cell.row)
                        col = cell.column
                        # openpyxl 2.x 的 cell.column 是列字母，3.x 才是数字
                        if not isinstance(col, int):
                            col = column_index_from_string(col)
                        max_c = max(max_c, col)
                        
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
                            # openpyxl 2.x 整数单元格返回 int，3.x 可能返回 float
                            if float(v).is_integer():
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
                print('解析图表失败: {0}'.format(ce))
                
            # 解析合并单元格
            self.merged_cells = []
            try:
                merged = ws.merged_cells
                # openpyxl 3.x 返回带 ranges 的对象，2.x 直接是字符串集合
                merged_ranges = getattr(merged, 'ranges', merged)
                for mr in merged_ranges:
                    if hasattr(mr, 'min_row'):
                        # openpyxl 行列从 1 开始
                        self.merged_cells.append((mr.min_row - 1, mr.min_col - 1,
                                                  mr.max_row - 1, mr.max_col - 1))
                    else:
                        range_text = str(mr)
                        if ':' in range_text:
                            start, end = range_text.split(':', 1)
                            c1 = column_index_from_string(re.match(r'[A-Z]+', start).group(0))
                            r1 = int(re.search(r'\d+', start).group(0))
                            c2 = column_index_from_string(re.match(r'[A-Z]+', end).group(0))
                            r2 = int(re.search(r'\d+', end).group(0))
                            self.merged_cells.append((r1 - 1, c1 - 1, r2 - 1, c2 - 1))
            except Exception as me:
                print('解析合并单元格失败: {0}'.format(me))
                
            self.evaluate_all_cells()
            self._draw_table()
            self.update_status('已导入: {0}'.format(path))
        except Exception as e:
            messagebox.showerror("错误", '导入失败: {0}'.format(e))

    def _import_xls_file(self, path):
        if not HAS_XLRD:
            messagebox.showerror("缺少依赖",
                "导入 .xls 需要 xlrd 库。\n请运行：pip install xlrd\n（Python 3.4 请安装：pip install xlrd==1.2.0）\n"
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
                print('xls 合并单元格读取失败: {0}'.format(e))

            self.evaluate_all_cells()
            self._draw_table()
            self.update_status('已导入: {0}'.format(path))
        except Exception as e:
            messagebox.showerror("错误", '导入失败: {0}'.format(e))

    def export_excel_table(self):
        if not HAS_OPENPYXL:
            messagebox.showerror("缺少依赖",
                "导入/导出 Excel 需要 openpyxl 库。\n请运行：pip install openpyxl\n（Python 3.4 请安装：pip install openpyxl==2.4.9）")
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
                    print('合并导出失败: {0}'.format(e))

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
                            series_name = '{0}{1}'.format(series_name, i+1)
                            
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
                        
                    ws.add_chart(e_chart, '{0}{1}'.format(get_column_letter(total_cols + 2), idx * 15 + 2))
                except Exception as e:
                    print('导出图表失败: {0}'.format(e))

            wb.save(path)
            self.update_status('已导出: {0}'.format(path))
        except Exception as e:
            messagebox.showerror("错误", '导出失败: {0}'.format(e))

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
            messagebox.showerror("错误", '无法创建输出目录: {0}'.format(e))
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
from collections import defaultdict, OrderedDict

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

""" + core_logic + '\n\nclass GuiInterpreter(ChineseInterpreter):\n    def __init__(self, root):\n        super().__init__()\n        self.root = root\n        self.output_text = scrolledtext.ScrolledText(root, height=20, width=60, font=("Consolas", 12))\n        self.output_text.pack(padx=10, pady=10)\n\n    def _emit(self, text):\n        self.output_text.insert(tk.END, text + "\\n")\n        self.output_text.see(tk.END)\n        self.root.update()\n\n    def _builtin_input(self, prompt=""):\n        return simpledialog.askstring("输入", prompt, parent=self.root) or ""\n\ndef main():\n    root = tk.Tk()\n    root.title("中文编程运行器")\n    root.geometry("800x600")\n    interp = GuiInterpreter(root)\n    code = {0}\n    interp.execute(code)\n    # 执行结束后不关闭窗口，让用户能看结果\n'.format(repr(code_content))
            else:
                # 基于控制台运行：直接 print 和 input
                runner_code = base_imports + core_logic + '\n\ndef main():\n    interp = ChineseInterpreter(print_callback=print, input_callback=input)\n    code = {0}\n    interp.execute(code)\n    try:\n        input("\\nPress Enter to exit...")\n    except RuntimeError:\n        pass\n'.format(repr(code_content))
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
        
        self._append_pkg_log('执行的命令:\n{0}\n\n'.format(' '.join(cmd)), 'info')

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
                    universal_newlines=True,
                    bufsize=1,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000) if os.name == 'nt' else 0
                )
                
                for line in process.stdout:
                    self.root.after(0, lambda l=line: self._append_pkg_log(l))
                    
                process.wait()
                
                if process.returncode == 0:
                    self.root.after(0, lambda: self._append_pkg_log("\n打包成功！", 'success'))
                    self.root.after(0, lambda: self.pkg_status_label.config(text='打包完成，输出目录: {0}'.format(out_path), fg=MODERN_COLORS['success']))
                else:
                    self.root.after(0, lambda: self._append_pkg_log('\n打包失败，退出代码: {0}'.format(process.returncode), 'error'))
                    self.root.after(0, lambda: self.pkg_status_label.config(text="打包失败", fg=MODERN_COLORS['danger']))
                    
            except FileNotFoundError:
                self.root.after(0, lambda: self._append_pkg_log("\n错误: 找不到 pyinstaller 命令。请确保已安装 pyinstaller。\n运行: pip install pyinstaller", 'error'))
                self.root.after(0, lambda: self.pkg_status_label.config(text="找不到 PyInstaller", fg=MODERN_COLORS['danger']))
            except Exception as e:
                self.root.after(0, lambda err=str(e): self._append_pkg_log('\n发生异常: {0}'.format(err), 'error'))
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
                    widget.tag_add('cmt', '{0}.{1}'.format(ln, cidx), '{0}.{1}'.format(ln, len(line)))

                str_ranges = [(m.start(), m.end())
                              for m in re.finditer(r'"[^"\n]*"', code_part)]
                for s, e in str_ranges:
                    widget.tag_add('str', '{0}.{1}'.format(ln, s), '{0}.{1}'.format(ln, e))

                def in_str(pos):
                    for s, e in str_ranges:
                        if s <= pos < e:
                            return True
                    return False

                for m in re.finditer(r'(?<![\w.])\d+(?:\.\d+)?', code_part):
                    if not in_str(m.start()):
                        widget.tag_add('num', '{0}.{1}'.format(ln, m.start()), '{0}.{1}'.format(ln, m.end()))

                for kw in _HIGHLIGHT_KEYWORDS:
                    start = 0
                    while True:
                        p = code_part.find(kw, start)
                        if p == -1:
                            break
                        if not in_str(p):
                            widget.tag_add('kw', '{0}.{1}'.format(ln, p), '{0}.{1}'.format(ln, p + len(kw)))
                        start = p + len(kw)

                for kw in ('正确', '错误'):
                    start = 0
                    while True:
                        p = code_part.find(kw, start)
                        if p == -1:
                            break
                        if not in_str(p):
                            widget.tag_add('kw', '{0}.{1}'.format(ln, p), '{0}.{1}'.format(ln, p + 2))
                        start = p + 2

                for bi in ('获取输入', '变成整数', '变成小数', '变成字符串'):
                    start = 0
                    while True:
                        p = code_part.find(bi, start)
                        if p == -1:
                            break
                        if not in_str(p):
                            widget.tag_add('bi', '{0}.{1}'.format(ln, p), '{0}.{1}'.format(ln, p + len(bi)))
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
                self.update_status('已导入: {0}'.format(filename))
                self.root.after(80, self._highlight_code)
            except Exception as e:
                messagebox.showerror("错误", '导入失败: {0}'.format(str(e)))

    def save_program(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".ctb",
            filetypes=[("CTB文件", "*.ctb"), ("所有文件", "*.*")])
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.code_editor.get(1.0, tk.END))
                self.update_status('已保存: {0}'.format(filename))
            except Exception as e:
                messagebox.showerror("错误", '保存失败: {0}'.format(str(e)))

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
                                self._append_result('\n错误: {0}\n'.format(err), 'error'))
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
                    f.write('导出时间: {0}\n'.format(datetime.datetime.now()))
                messagebox.showinfo("成功", '已保存到 {0}'.format(filename))
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
        text_area.insert(tk.END, '实验日期: {0}\n\n'.format(datetime.datetime.now()))

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
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>化学工具箱 v5.0 - 帮助与实验演示</title>
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
        /* ===== v5.0 帮助文档：IE8 兼容样式（表格/块级布局，不用 flex、grid、sticky） ===== */
        body { font-family: Tahoma, "Microsoft YaHei", "宋体", SimSun, sans-serif; }
        table.navbar { width: 100%; border-collapse: collapse; background: #14539A; }
        table.navbar td.brand { color: #FFFFFF; font-size: 17px; font-weight: bold; padding: 12px 18px; }
        table.navbar td.brand span.sub { font-size: 12px; font-weight: normal; color: #BFD8F5; margin-left: 10px; }
        table.navbar td.tabs { text-align: right; padding: 8px 18px 8px 0; }
        button.navbtn { font-family: inherit; font-size: 14px; color: #E8F1FF; background: #1B6AC0; border: 1px solid #4E8FD6; padding: 6px 16px; margin-left: 6px; cursor: pointer; }
        button.navbtn.active { background: #FFFFFF; color: #14539A; font-weight: bold; border-color: #FFFFFF; }
        .help-container { width: 900px; margin: 0 auto; }
        h2.sec { font-size: 20px; color: #14539A; border-left: 6px solid #2F74C9; padding: 2px 0 2px 10px; margin: 34px 0 12px; line-height: 1.5; }
        h3.sub { font-size: 16px; color: #1B5FA8; margin: 22px 0 8px; }
        p.meta { color: #667788; font-size: 13px; margin-bottom: 16px; }
        div.toc { background: #F3F8FF; border: 1px solid #D6E4F5; padding: 12px 16px; margin: 0 0 10px; font-size: 14px; line-height: 2; }
        table.kv { width: 100%; border-collapse: collapse; margin: 6px 0 10px; font-size: 14px; }
        table.kv th { width: 110px; text-align: left; background: #EEF4FC; color: #14539A; border: 1px solid #DCE6F2; padding: 7px 10px; font-weight: bold; vertical-align: top; }
        table.kv td { border: 1px solid #DCE6F2; padding: 7px 10px; color: #333333; line-height: 1.75; }
        table.data { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 14px; }
        table.data th { background: #E3F2FD; color: #0F6CBD; border: 1px solid #CFE0F0; padding: 7px 9px; text-align: left; }
        table.data td { border: 1px solid #CFE0F0; padding: 7px 9px; line-height: 1.75; }
        div.note { background: #EAF4FF; border-left: 4px solid #0F6CBD; padding: 10px 14px; margin: 10px 0; font-size: 14px; line-height: 1.8; color: #0A4A8A; }
        div.warn { background: #FFF6E0; border-left: 4px solid #E0A100; padding: 10px 14px; margin: 10px 0; font-size: 14px; line-height: 1.8; color: #7A5200; }
        div.ie-warn { background: #FFF6E0; border: 1px solid #E0A100; color: #7A5200; padding: 12px 16px; margin: 0 0 14px; font-size: 14px; }
        span.tag { font-size: 12px; color: #FFFFFF; background: #2F74C9; padding: 1px 8px; margin-left: 8px; font-weight: normal; }
        pre.code { background: #1E1E2E; color: #CDD6F4; padding: 14px; font-family: Consolas, "Courier New", monospace; font-size: 13px; line-height: 1.7; margin: 8px 0; overflow-x: auto; }
        ul, ol { margin: 6px 0 12px 24px; }
        li { line-height: 1.85; font-size: 14px; color: #333333; }
        a { color: #0F6CBD; }
    </style>
</head>
<body>

    <table class="navbar" cellpadding="0" cellspacing="0" width="100%">
        <tr>
            <td class="brand">化学工具箱 v5.0<span class="sub">帮助与实验演示</span></td>
            <td class="tabs">
                <button class="navbtn active" type="button" onclick="switchPage('help', this)">帮助文档</button>
                <button class="navbtn" type="button" onclick="switchPage('experiment', this)">实验演示</button>
            </td>
        </tr>
    </table>

    <div id="help-page" class="page-panel active">
        <div class="help-body">
        <div class="help-container">
        <h1>化学工具箱 v5.0 帮助文档</h1>
        <p class="meta">适用版本：v5.0　|　运行环境：Windows XP SP3 及以上（Python 3.4 32 位）　|　文档更新：2026-11</p>

        <div class="toc">
            <b>目录</b><br>
            <a href="#s1">1　版本与总览</a> ·
            <a href="#s2">2　界面与操作</a> ·
            <a href="#s3">3　方程式配平</a> ·
            <a href="#s4">4　元素周期表</a> ·
            <a href="#s5">5　化学计算</a> ·
            <a href="#s6">6　实用功能</a> ·
            <a href="#s7">7　CTB 表格</a> ·
            <a href="#s8">8　中文编程</a> ·
            <a href="#s9">9　打包成 EXE</a> ·
            <a href="#s10">10　其他工具</a> ·
            <a href="#s11">11　插件系统</a> ·
            <a href="#s12">12　常见问题</a> ·
            <a href="#s13">13　协议与免责</a> ·
            <a href="#s14">14　版本历史</a>
        </div>

        <!-- ==================== 1 ==================== -->
        <h2 class="sec" id="s1">1　版本与总览</h2>
        <p>化学工具箱是一个单文件、零依赖的化学学习与办公辅助程序：主程序只有一个 <code>.py</code> 文件，
        内置元素数据、公式引擎、表格与中文编程解释器，不依赖 NumPy 等第三方库，可在 Windows XP SP3 + Python 3.4 上直接运行，
        也可以用 PyInstaller 打包成单文件 EXE 后在不装 Python 的机器上使用。</p>
        <table class="data">
            <tr><th style="width:120px">功能区</th><th style="width:230px">模块</th><th>一句话说明</th></tr>
            <tr><td rowspan="3">左侧主导航</td><td>配平</td><td>输入化学方程式（含离子式），自动求最小整数系数并标注元素化合价</td></tr>
            <tr><td>元素周期表</td><td>118 种元素的分组色块表，点击查看原子量、电负性、电子排布等 10 项资料</td></tr>
            <tr><td>计算 / 实用功能 / 编程</td><td>8 个常用化学计算 + 16 个专题工具 + 类 Excel 表格 + 中文编程环境</td></tr>
            <tr><td rowspan="2">底部</td><td>帮助</td><td>本页面（帮助文档 + 实验演示两个页签）</td></tr>
            <tr><td>关于</td><td>版本信息、功能亮点、运行环境与致谢</td></tr>
            <tr><td>菜单栏</td><td>文件 / 工具 / 帮助</td><td>导出结果、打开插件文件夹、单位换算、实验记录、各说明文档</td></tr>
        </table>
        <div class="note"><b>v5.0 相比 v4.1 的变化：</b>① 新增「PyInstaller 打包」工具，可在图形界面里把 <code>.py</code> 转成 EXE；
        ② CTB 表格顶部工具栏压缩为一行，宽屏/小屏都不再挤成两行；③ 实用功能首页按「溶液与酸碱 / 气体与热力学 / 反应与平衡 / 专题工具 / 测试功能」重新分组；
        ④ 中文编程新增 <code>获取输入</code>、<code>变成整数</code>、<code>变成小数</code>、<code>变成字符串</code> 四个内置函数，输入框与执行改在后台线程，界面不再卡死。</div>

        <!-- ==================== 2 ==================== -->
        <h2 class="sec" id="s2">2　界面与操作</h2>
        <h3 class="sub">2.1　窗口结构</h3>
        <table class="kv">
            <tr><th>左侧栏</th><td>自上而下：Logo 与版本号 → 配平 / 元素周期表 / 计算 / 实用功能 / 编程 五个按钮 → 分隔线 → 帮助 / 关于。当前页面所在的按钮会高亮。</td></tr>
            <tr><th>标题区</th><td>页面顶部显示当前模块名与副标题；滚动页面可用鼠标滚轮（鼠标停在内容区时滚动才生效）。</td></tr>
            <tr><th>内容区</th><td>各模块自己的控件区，切换页面时整块重建，不会残留上一页的控件。</td></tr>
            <tr><th>状态栏</th><td>窗口最下方一行文字，显示操作提示与结果摘要（例如「配平完成」「计算完成」）。</td></tr>
            <tr><th>菜单栏</th><td>「文件」：导出结果 / 打开插件文件夹 / 退出；「工具」：单位换算 / 实验记录；「帮助」：使用教程 / 插件开发文档 / 中文编程开发文档 / 关于。</td></tr>
        </table>
        <h3 class="sub">2.2　通用操作约定</h3>
        <ul>
            <li>计算类模块统一是「填参数 → 点按钮 → 下方或右侧出结果」，结果区只读，可选中复制。</li>
            <li>只有少数模块支持「留空 = 不知道」（气体定律、分压计算），其余模块要求每格都填；填错（如字母代替数字）多数在结果区显示「输入错误」，少数组件弹「错误」提示框，程序不会崩溃。</li>
            <li>所有弹窗标题都是「错误」「提示」「元素信息」这类固定字样，正文写明原因。</li>
            <li>窗口可按右上角关闭；关闭时会先停掉中文编程的执行线程、唤醒等待输入的对话框，并依次调用各插件的 <code>on_shutdown()</code>，然后退出（不会弹「是否保存」）。</li>
        </ul>

        <!-- ==================== 3 ==================== -->
        <h2 class="sec" id="s3">3　方程式配平</h2>
        <p><b>用途：</b>把未配平的化学方程式（分子式或离子式）补成最小整数系数，并逐元素显示化合价，方便检查电子转移。</p>
        <table class="kv">
            <tr><th>输入格式</th><td>反应物与生成物用 <code>=</code> 分隔，多种物质用 <code>+</code> 连接。例：<code>H2+O2=H2O</code>、<code>Fe2O3+CO=Fe+CO2</code>。</td></tr>
            <tr><th>离子写法</th><td>电荷写在元素或原子团后面，用 <code>^数字+</code> 或 <code>^数字-</code>，例如 <code>H^1+</code>、<code>CO3^2-</code>、<code>SO4^2-</code>。整个方程式例：<code>H^1++CO3^2-=HCO3^1-</code>。</td></tr>
            <tr><th>括号</th><td>支持圆括号与方括号嵌套并带下标，如 <code>Ca(OH)2</code>、<code>Al2(SO4)3</code>、<code>K4[Fe(CN)6]</code>。元素符号首字母大写、第二字母小写：<code>Co</code> 是钴，<code>CO</code> 会按 C 与 O 两个元素来算，两者结果完全不同，请按元素符号规范书写。</td></tr>
            <tr><th>求解方法</th><td>对每种元素列守恒方程（同时列电荷守恒），用内置的纯 Python 最小二乘 + SVD 解出系数向量，再按最小公倍数放大为整数，最后除以最大公约数得到最简比。不需要 NumPy。</td></tr>
            <tr><th>输出</th><td>配平后的方程式；下面逐元素列出化合价：正价绿色、负价红色、0 价灰色，系数为蓝色加粗。</td></tr>
            <tr><th>快速示例</th><td>界面提供 5 个按钮：氢气燃烧、炼铁、置换、碳酸根、中和，点一下直接填入输入框。</td></tr>
        </table>
        <p><b>示例（离子方程式）：</b></p>
        <pre class="code">输入：H^1++CO3^2-=HCO3^1-
输出：H^1+ + CO3^2- = HCO3^1-   （系数均为 1，电荷守恒：+1 + (-2) = -1）</pre>
        <div class="note">配平失败时先查三件事：① 元素符号大小写（<code>Co</code>/<code>CO</code>）；② 两边元素种类是否真的相同；③ 离子电荷写法有没有漏掉 <code>^</code>。插件可以通过 <code>on_balance(equation)</code> 优先拦截配平请求，返回 <code>(配平结果, 化合价字典)</code> 二元组即由插件给出结果。</div>

        <!-- ==================== 4 ==================== -->
        <h2 class="sec" id="s4">4　元素周期表</h2>
        <table class="kv">
            <tr><th>内容</th><td>118 种元素，按 7 个周期 + 镧系/锕系两行排列；按族别着色（第 1 族淡红、第 2 族淡绿、过渡金属淡蓝、其余淡黄，镧系/锕系单独配色）。</td></tr>
            <tr><th>操作</th><td>鼠标点击任一元素方块 → 弹出「元素信息」窗口；滚轮可平滑滚动整张表。</td></tr>
            <tr><th>信息字段</th><td>元素符号、中文名称、原子序数、原子量、电负性、族、周期、电子排布式、电子层分布、一句话简介（共 10 项）。</td></tr>
            <tr><th>数据缺失</th><td>个别超重元素没有电负性/电子层数据时显示「未知」，不影响其它字段。</td></tr>
        </table>

        <!-- ==================== 5 ==================== -->
        <h2 class="sec" id="s5">5　化学计算（8 个页签）</h2>
        <p>点左侧「计算」进入，界面为一排页签，每个页签独立计算、互不影响。以下逐项说明输入、公式与输出。</p>

        <h3 class="sub">5.1　摩尔质量</h3>
        <table class="kv">
            <tr><th>输入</th><td>化学式，如 <code>H2O</code>、<code>Ca(OH)2</code>、<code>CuSO4</code>、<code>K4[Fe(CN)6]</code>（支持圆括号/方括号嵌套与下标数字）。</td></tr>
            <tr><th>计算</th><td>解析化学式得到各元素原子个数，逐个乘以原子量后求和：M = Σ(n_i × A_i)。</td></tr>
            <tr><th>输出</th><td>相对分子质量（直接给出数值，不固定小数位）＋ 计算过程（按元素符号字母顺序展开），例如 <code>H2(1.008×2) + O1(16×1) = 18.016</code>。</td></tr>
            <tr><th>错误</th><td>含未知元素时结果区显示「错误：未知元素 X」；输入框为空时点按钮无反应。</td></tr>
        </table>

        <h3 class="sub">5.2　浓度计算</h3>
        <table class="kv">
            <tr><th>输入</th><td>溶质质量 m（g）、溶液体积 V（L）、摩尔质量 M（g/mol）。</td></tr>
            <tr><th>公式</th><td>n = m / M；c = n / V。</td></tr>
            <tr><th>输出</th><td>物质的量 n（mol）与物质的量浓度 c（mol/L），各保留 4 位小数。</td></tr>
            <tr><th>示例</th><td>m = 5.85 g、V = 1 L、M = 58.44 g/mol（NaCl）→ n = 0.1001 mol，c = 0.1001 mol/L。</td></tr>
        </table>

        <h3 class="sub">5.3　稀释计算</h3>
        <table class="kv">
            <tr><th>输入</th><td>稀释前浓度 C1（mol/L）、稀释前体积 V1（L）、稀释后体积 V2（L）。</td></tr>
            <tr><th>公式</th><td>稀释前后溶质物质的量不变：C1·V1 = C2·V2 → C2 = C1·V1 / V2。</td></tr>
            <tr><th>输出</th><td>稀释后浓度 C2（mol/L，4 位小数）＋ 代入过程。</td></tr>
        </table>

        <h3 class="sub">5.4　比例求解</h3>
        <table class="kv">
            <tr><th>输入</th><td>两种写法任选：<br>格式一 <code>a / b = c / x</code>（x 在右下）→ x = b·c / a；<br>格式二 <code>a / b = x / d</code>（x 在左上）→ x = a·d / b。</td></tr>
            <tr><th>输出</th><td>未知量 x，保留 6 位有效数字。</td></tr>
            <tr><th>注意</th><td>分母为 0 时给出「错误：分母 a 不能为0」（格式二为 b），不会崩溃。</td></tr>
        </table>

        <h3 class="sub">5.5　元素百分比（质量分数）</h3>
        <table class="kv">
            <tr><th>输入</th><td>化学式，如 <code>C6H12O6</code>、<code>(NH4)2SO4</code>。</td></tr>
            <tr><th>计算</th><td>先求摩尔质量 M，再对每个元素求 w% = n_i·A_i / M × 100%。</td></tr>
            <tr><th>输出</th><td>摩尔质量（4 位小数）＋ 每个元素的质量分数（2 位小数），按元素符号字母顺序列出。</td></tr>
        </table>

        <h3 class="sub">5.6　经验式确定</h3>
        <table class="kv">
            <tr><th>输入</th><td>每行一个元素，格式「元素 数值」，数值可以是质量分数（%）或质量（g），例如：<br><code>C 40</code><br><code>H 6.7</code><br><code>O 53.3</code></td></tr>
            <tr><th>计算</th><td>① 每个元素除以自身原子量得到摩尔数；② 全部除以最小摩尔数得到比值；③ 在 1～19 倍之间寻找能让所有比值接近整数的最小倍数（容差 0.01）；④ 乘以该倍数并四舍五入。</td></tr>
            <tr><th>输出</th><td>经验式（如 <code>CH2O</code>）；数值比例找不到整数比时报「无法确定整数比」。</td></tr>
            <tr><th>注意</th><td>数据误差过大（比值离整数超过容差）时结果可能不理想，建议用带小数的高精度数据。</td></tr>
        </table>

        <h3 class="sub">5.7　浓度换算（质量分数 ↔ 物质的量浓度）</h3>
        <table class="kv">
            <tr><th>输入</th><td>质量分数 w（%）、溶液密度 ρ（g/mL）、溶质摩尔质量 M（g/mol）。</td></tr>
            <tr><th>公式</th><td>取 1 L 溶液：质量 = 1000ρ g，其中溶质 = 1000ρ·w/100 g，故 c = (1000·ρ·w/100) / M = 10·ρ·w / M。</td></tr>
            <tr><th>输出</th><td>物质的量浓度 c（mol/L，4 位小数）。</td></tr>
            <tr><th>示例</th><td>w = 98%、ρ = 1.84 g/mL、M = 98 g/mol（浓硫酸）→ c = 18.4 mol/L。</td></tr>
        </table>

        <h3 class="sub">5.8　产率计算</h3>
        <table class="kv">
            <tr><th>输入</th><td>实际产量、理论产量（单位一致即可，g 或 mol）。</td></tr>
            <tr><th>公式</th><td>产率 = 实际产量 / 理论产量 × 100%。</td></tr>
            <tr><th>输出</th><td>百分产率（2 位小数）；理论产量为 0 时显示「输入错误」。</td></tr>
        </table>

        <!-- ==================== 6 ==================== -->
        <h2 class="sec" id="s6">6　实用功能（16 个专题工具）</h2>
        <p>点左侧「实用功能」进入卡片首页，按 5 个分组排列，点卡片即进入对应工具。每个工具都是「填参数 → 计算 → 出结果」的单页。</p>

        <h3 class="sub">6.1　pH 计算器 <span class="tag">溶液与酸碱</span></h3>
        <table class="kv">
            <tr><th>页签</th><td>两个页签：强酸/强碱、弱酸/弱碱；每个页签内用「类型」下拉框再选强酸/强碱或弱酸/弱碱。</td></tr>
            <tr><th>强酸强碱</th><td>输入浓度 C（mol/L）。强酸：pH = −lg C；强碱：pOH = −lg C，pH = 14 − pOH。</td></tr>
            <tr><th>弱酸弱碱</th><td>输入浓度 C 与电离常数（Ka 或 Kb）。弱酸：[H⁺] = √(Ka·C)，pH = −lg[H⁺]；弱碱：[OH⁻] = √(Kb·C)，pH = 14 + lg[OH⁻]。</td></tr>
            <tr><th>输出</th><td>强酸给 [H⁺] 与原值一样的浓度、pH；强碱给 [OH⁻]、pOH、pH（pH/pOH 均 2 位小数）；弱酸弱碱的离子浓度写成科学计数法（2 位小数）。</td></tr>
            <tr><th>示例</th><td>0.1 mol/L 醋酸（Ka = 1.8×10⁻⁵）→ [H⁺] ≈ 1.34×10⁻³，pH ≈ 2.87。</td></tr>
        </table>

        <h3 class="sub">6.2　缓冲溶液 <span class="tag">溶液与酸碱</span></h3>
        <table class="kv">
            <tr><th>输入</th><td>弱酸的 pKa、共轭碱浓度 [A⁻]、弱酸浓度 [HA]（mol/L）。</td></tr>
            <tr><th>公式</th><td>Henderson–Hasselbalch：pH = pKa + lg([A⁻]/[HA])。</td></tr>
            <tr><th>输出</th><td>缓冲液 pH（2 位小数）。</td></tr>
            <tr><th>提示</th><td>该公式假设体积不变、忽略活度系数；[A⁻]/[HA] 在 0.1～10 之间时估算最可靠。</td></tr>
        </table>

        <h3 class="sub">6.3　酸碱滴定 <span class="tag">溶液与酸碱</span></h3>
        <table class="kv">
            <tr><th>输入</th><td>酸浓度 Ca（mol/L）、酸体积 Va（L）、碱浓度 Cb（mol/L）。</td></tr>
            <tr><th>公式</th><td>按 1:1 计量：Ca·Va = Cb·Vb → Vb = Ca·Va / Cb。</td></tr>
            <tr><th>输出</th><td>所需碱体积 Vb（同时给出 L 与 mL 两种单位）。</td></tr>
            <tr><th>注意</th><td>只适用于一元强酸—一元强碱（或计量比 1:1）的情形；多元酸碱请先换算计量比。</td></tr>
        </table>

        <h3 class="sub">6.4　溶液配制 <span class="tag">溶液与酸碱</span></h3>
        <table class="kv">
            <tr><th>输入</th><td>目标浓度 C（mol/L）、目标体积 V（L）、溶质摩尔质量 M（g/mol）。</td></tr>
            <tr><th>公式</th><td>m = C·V·M。</td></tr>
            <tr><th>输出</th><td>需称取的溶质质量（g，4 位小数）。</td></tr>
        </table>

        <h3 class="sub">6.5　气体定律 <span class="tag">气体与热力学</span></h3>
        <table class="kv">
            <tr><th>输入</th><td>四个框：压强 P（atm）、体积 V（L）、物质的量 n（mol）、温度 T（K）。<b>留空一个</b>表示求它；<b>四个都填时会按「先算 T」处理</b>，你填的 T 被忽略。</td></tr>
            <tr><th>公式</th><td>PV = nRT，R = 0.0821 L·atm/(mol·K)；按「P+V+n → T、P+V+T → n、P+n+T → V、V+n+T → P」的顺序判断。</td></tr>
            <tr><th>输出</th><td>被求出的那个量（2 位小数，物质的量 n 为 4 位）＋ 代入过程。</td></tr>
            <tr><th>错误</th><td>少于三个有效变量时提示「请输入至少三个变量」；T 为 0 会除零，显示「输入错误」；其它非法输入同样显示「输入错误」。</td></tr>
        </table>

        <h3 class="sub">6.6　分压计算 <span class="tag">气体与热力学</span></h3>
        <table class="kv">
            <tr><th>输入</th><td>总压 P_total（atm）与组分 1、组分 2 的摩尔分数 x₁、x₂；某一项留空按 0 处理。</td></tr>
            <tr><th>公式</th><td>道尔顿分压定律：P_i = P_total × x_i；两个组分之和与总压对照即可自查。</td></tr>
            <tr><th>输出</th><td>两组分分压与分压之和（atm，均 4 位小数）。</td></tr>
        </table>

        <h3 class="sub">6.7　热化学 <span class="tag">气体与热力学</span></h3>
        <table class="kv">
            <tr><th>热量页</th><td>输入质量 m（g）、比热容 c（J/(g·K)）、温度变化 ΔT（K）→ Q = m·c·ΔT（J，2 位小数）。</td></tr>
            <tr><th>燃烧热页</th><td>输入摩尔燃烧焓 ΔH（kJ/mol）与物质的量 n（mol）→ Q = ΔH·n（kJ，2 位小数）。</td></tr>
            <tr><th>符号约定</th><td>ΔT 用「末温 − 初温」；ΔH 放热反应取负值（结果自带正负号）。输入非数字时显示「输入错误」。</td></tr>
        </table>

        <h3 class="sub">6.8　热力学 <span class="tag">气体与热力学</span></h3>
        <table class="kv">
            <tr><th>输入</th><td>焓变 ΔH（kJ/mol）、温度 T（K）、熵变 ΔS（J/(mol·K)）。</td></tr>
            <tr><th>公式</th><td>ΔG = ΔH − T·ΔS（内部把 ΔH 换算成 J 后计算，再换回 kJ）。</td></tr>
            <tr><th>输出</th><td>ΔG（kJ/mol，2 位小数）＋ 代入过程（内部先把 ΔH 从 kJ 换算成 J）。判断自发性请自行看 ΔG 的正负。</td></tr>
        </table>

        <h3 class="sub">6.9　氧化还原分析 <span class="tag">反应与平衡</span></h3>
        <table class="kv">
            <tr><th>输入</th><td>化合物化学式，如 <code>H2O</code>、<code>Fe2O3</code>、<code>KMnO4</code>、<code>H2SO4</code>。</td></tr>
            <tr><th>方法</th><td>按电负性由高到低分配常见价态，代数和必须为 0；若不为 0，再从多价态元素里挑选一个价态修正。单质（只含一种元素）直接记为 0 价。</td></tr>
            <tr><th>输出</th><td>逐元素氧化数（如 H +1、O −2、Fe +3）。</td></tr>
            <tr><th>附页</th><td>下方列出常见氧化剂（KMnO4、K2Cr2O7、H2O2、HNO3、O2）与常见还原剂（Fe2+、Zn、H2、CO、SO2）。</td></tr>
        </table>

        <h3 class="sub">6.10　化学平衡 <span class="tag">反应与平衡</span></h3>
        <table class="kv">
            <tr><th>输入</th><td>平衡常数 K、温度 T（K）。</td></tr>
            <tr><th>公式</th><td>ΔG° = −R·T·ln K，R = 8.314 J/(mol·K)。</td></tr>
            <tr><th>输出</th><td>标准吉布斯自由能变，同时给出 J/mol 与 kJ/mol（都保留 2 位小数），并列出代入过程。</td></tr>
            <tr><th>注意</th><td>K 必须大于 0；K ≤ 0 或输入非数字时显示「输入错误」。ln K 为负表示 ΔG° 为正（反应不利）。</td></tr>
        </table>

        <h3 class="sub">6.11　化学动力学 <span class="tag">反应与平衡</span></h3>
        <table class="kv">
            <tr><th>阿伦尼乌斯</th><td>输入活化能 Ea（<b>J/mol</b>）、温度 T（K）、指前因子 A → k = A·exp(−Ea/(R·T))，R = 8.314；输出 k（科学计数法，单位 1/s）与代入过程。</td></tr>
            <tr><th>半衰期</th><td>输入速率常数 k（1/s）→ t½ = ln2 / k，结果以<b>秒</b>显示。</td></tr>
            <tr><th>注意</th><td>Ea 的单位是 J/mol（不是 kJ/mol），直接代入；手头数据是 kJ/mol 时请先乘 1000。</td></tr>
        </table>

        <h3 class="sub">6.12　电化学（能斯特方程） <span class="tag">反应与平衡</span></h3>
        <table class="kv">
            <tr><th>输入</th><td>标准电极电势 E°（V）、温度 T（K）、转移电子数 n、反应商 Q。</td></tr>
            <tr><th>公式</th><td>E = E° − (R·T/(n·F))·ln Q，R = 8.314、F = 96485，T 由你输入（室温填 298.15）。</td></tr>
            <tr><th>输出</th><td>实际电极电势 E（V，4 位小数）＋ 代入过程。</td></tr>
        </table>

        <h3 class="sub">6.13　有机化学工具 <span class="tag">专题工具</span></h3>
        <table class="kv">
            <tr><th>官能团识别</th><td>输入有机物的<b>中文名称</b>（如 乙醇、乙酸乙酯、甲苯），按关键词表匹配：醇、醛、酮、羧酸、酯、醚、胺、烯烃、炔烃、芳香烃。输出「可能含有的官能团」。</td></tr>
            <tr><th>同分异构体</th><td>输入烷烃分子式，查内置表：C2H6=1、C3H8=1、C4H10=2、C5H12=3、C6H14=5、C7H16=9、C8H18=18。其它分子式会提示「暂不支持」。</td></tr>
            <tr><th>说明</th><td>这两项是教学速查，不做完整的结构式解析；识别结果是「可能含有的官能团」，供快速判断用。</td></tr>
        </table>

        <h3 class="sub">6.14　光谱分析 <span class="tag">专题工具</span></h3>
        <table class="kv">
            <tr><th>输入</th><td>波长 λ（nm），填在「波长-能量转换」页签。</td></tr>
            <tr><th>公式</th><td>E = h·c/λ，h = 6.626×10⁻³⁴ J·s、c = 3×10⁸ m/s；λ 先换算成米。电子伏特 eV = E / 1.602×10⁻¹⁹。</td></tr>
            <tr><th>输出</th><td>波长、能量（J，科学计数法）、能量（eV，2 位小数）；输入非数字显示「输入错误」。</td></tr>
            <tr><th>颜色对照</th><td>第二个页签「颜色与波长」是只读清单：紫 400–450、蓝 450–500、青 500–550、绿 550–580、黄 580–600、橙 600–650、红 650–750 nm。</td></tr>
        </table>

        <h3 class="sub">6.15　核化学 <span class="tag">专题工具</span></h3>
        <table class="kv">
            <tr><th>输入</th><td>半衰期 t½（s）、初始原子数 N0、经过时间 t（s）。</td></tr>
            <tr><th>公式</th><td>衰变常数 λ = ln2 / t½；剩余原子数 N = N0·exp(−λ·t)。</td></tr>
            <tr><th>输出</th><td>λ（1/s，科学计数法）与剩余原子数 N（2 位小数）。</td></tr>
        </table>

        <h3 class="sub">6.16　溶解度查询 <span class="tag">专题工具</span></h3>
        <table class="kv">
            <tr><th>数据表</th><td>20 ℃ 下每 100 g 水的溶解度（g）：NaCl 36.0、KCl 34.0、KNO3 31.6、NH4Cl 37.2、Ca(OH)2 0.173、AgNO3 216、CuSO4 20.7、NaOH 109。</td></tr>
            <tr><th>使用</th><td>表格是只读清单（不可排序、不可编辑）；下方固定显示 5 条溶解性规律：碱金属盐大多可溶 / 硝酸盐全部可溶 / 氯化物、溴化物、碘化物除 Ag⁺、Pb²⁺ 外可溶 / 硫酸盐除 Ba²⁺、Pb²⁺、Ca²⁺ 外可溶 / 碳酸盐、磷酸盐大多不溶。</td></tr>
        </table>

        <!-- ==================== 7 ==================== -->
        <h2 class="sec" id="s7">7　CTB 表格</h2>
        <p>入口：左侧「实用功能 → 测试功能 → CTB 表格」（菜单里没有这一项，只能从这里进）。它是一个轻量电子表格，支持公式、格式、合并与柱/折线/饼图，文件扩展名 <code>.ctbt</code>。</p>

        <h3 class="sub">7.1　基本操作</h3>
        <ul>
            <li>单击选中单元格，双击或直接敲字/F2 进入编辑；编辑框里 <code>Enter</code> 提交并下移一格、<code>Tab</code> 提交并右移一格、<code>Esc</code> 取消；选中状态按方向键移动、<code>Delete</code>/<code>Backspace</code> 清空内容。</li>
            <li>按住左键拖出矩形选区（不支持 Ctrl 多选）；选区右下角的小方块是填充柄，往下拖可复制到下方：选中两格以上数字时按等差递增，单格时原样复制，公式会自动平移引用。</li>
            <li>行高、列宽不能用鼠标拖表头改，只能在「格式」页签里改数值（行高 14–200、列宽 30–800），点「应用尺寸」生效；内容超出窗口时出现横竖滚动条。</li>
            <li>表格区域本身没有右键菜单；右键只在<b>点中图表</b>时弹出（编辑标题 / 编辑图例 / 更改颜色 / 删除图表）。</li>
            <li>顶部工具栏是 5 个页签，v5.0 已压缩为一行：<b>文件、格式、公式、插入图表、设置</b>。插入/删除行列在「文件」页签里（只有「增加行」「增加列」，没有删除行/列）。</li>
        </ul>

        <h3 class="sub">7.2　公式与函数</h3>
        <table class="kv">
            <tr><th>写法</th><td>以 <code>=</code> 开头即按公式处理，例如 <code>=A1+B1</code>、<code>=SUM(A1:B5)*2</code>、<code>=IF(C1&gt;60,"及格","不及格")</code>。不会写公式的单元格按数据类型自动判断为数字或文本。</td></tr>
            <tr><th>区域引用</th><td><code>A1:B5</code> 表示矩形区域；函数参数可用区域，例如 <code>=AVERAGE(B2:B10)</code>。</td></tr>
            <tr><th>函数</th><td>SUM 求和、AVERAGE 平均、MAX、MIN、COUNT 计数、IF 条件、ABS 绝对值、ROUND 四舍五入、SIN/COS/TAN 三角、LOG <b>自然对数（ln）</b>、SQRT 开方、POWER 乘方；共 14 个，没有 LOG10、SUMIF 之类。</td></tr>
            <tr><th>全角容错</th><td>公式里的全角括号（）、逗号，、加号＋、减号－、乘号＊、除号／会自动转成半角再解析；<b>全角等号和全角数字不转换</b>，等号必须用半角 <code>=</code>。</td></tr>
            <tr><th>错误值</th><td>除零、引用空单元格做非法运算等显示 <code>#ERR!</code>；检测到循环引用显示 <code>#CIRC!</code>。</td></tr>
            <tr><th>迭代计算</th><td>「格式 → 迭代计算」可开关：勾选「允许迭代计算」并填「最大迭代次数」（默认 100）与「最大误差」（默认 0.001），点「应用设置」后反复重算到误差小于该值或达次数上限，适合累加器之类场景；不勾选则一律报 <code>#CIRC!</code>。</td></tr>
        </table>

        <h3 class="sub">7.3　格式</h3>
        <table class="data">
            <tr><th style="width:130px">项目</th><th>可选值 / 说明</th></tr>
            <tr><td>行高 / 列宽</td><td>行高 14–200 像素，列宽 30–800 像素</td></tr>
            <tr><td>字体</td><td>Microsoft YaHei、SimSun（宋体）、SimHei（黑体）、KaiTi（楷体）、FangSong（仿宋）、Consolas、Courier New、Arial、Times New Roman</td></tr>
            <tr><td>字号 / 加粗</td><td>6–72 号；加粗开关</td></tr>
            <tr><td>颜色</td><td>字体色、背景色（调色板选取）</td></tr>
            <tr><td>数据类型</td><td>自动 / 数字 / 文本（「文本」会原样保存前导零、编号等）</td></tr>
            <tr><td>对齐</td><td>自动 / 左 / 中 / 右</td></tr>
            <tr><td>合并</td><td>合并居中、只合并不居中、取消合并</td></tr>
        </table>

        <h3 class="sub">7.4　图表</h3>
        <ul>
            <li>先框选数据区域（含表头更佳），再到「插入图表」页签点柱状图 / 折线图 / 饼图；图表浮在表格上方，拖图表本体可移动，拖右下角可缩放。</li>
            <li>图表右上角有个小方块，点它就是关闭（删除）该图表。</li>
            <li>右键<b>图表</b>弹出菜单：编辑标题、编辑图例（饼图为分类名称，柱/折线为系列名称）、更改颜色、删除图表。不能在这里切换图表类型，要换类型就删掉重插。</li>
            <li>图表的位置、尺寸、标题、图例、颜色随 <code>.ctbt</code> 一起保存，下次打开原样恢复。</li>
        </ul>

        <h3 class="sub">7.5　导入导出</h3>
        <table class="kv">
            <tr><th>导入</th><td><code>.ctbt</code>（本程序格式，保留格式/公式/合并/图表）与 Excel（<code>.xlsx</code>/<code>.xlsm</code> 走 openpyxl 并优先取值，<code>.xls</code> 走 xlrd；都只读当前活动工作表，最多 300 行 × 50 列，带格式不完整保留）。</td></tr>
            <tr><th>导出</th><td><code>.ctbt</code> 为完整保存；导出 Excel 时单元格里的公式会按原文写成 Excel 公式（交给 Excel 自己算，不是程序算好的数值），字体色、底色、对齐与行高列宽会尽量带上。</td></tr>
            <tr><th>依赖提示</th><td>Excel 导入导出依赖 openpyxl（XP + Python 3.4 请装 <code>openpyxl==2.4.9</code>）；缺失时点按钮会弹窗提示，改用 <code>.ctbt</code> 不受影响。</td></tr>
        </table>

        <!-- ==================== 8 ==================== -->
        <h2 class="sec" id="s8">8　中文编程</h2>
        <p>入口：左侧「编程」。界面为两页签——「程序」为编辑器（Consolas 字体、实时语法高亮），「执行结果」为输出与输入控制台。执行在后台线程进行，运行中界面仍可响应，「执行」按钮会变成「停止」。</p>

        <h3 class="sub">8.1　程序的基本结构</h3>
        <ul>
            <li>一行一条语句；用缩进表示代码块，缩进可以是 4 个空格或 1 个 Tab（Tab 按 4 空格计）。</li>
            <li>语句关键字全部是中文，但变量名可以用中文、英文、数字、下划线，不能叫「正确」「错误」。</li>
            <li>标点全角/半角通用：全角括号、逗号、冒号、加减乘除号、比较号会自动转半角；<b>字符串内部不转换</b>。</li>
            <li>字符串用半角双引号；单行注释用 <code>注释:</code> 或 <code>注释：</code>。</li>
        </ul>

        <h3 class="sub">8.2　输出与赋值</h3>
        <table class="kv">
            <tr><th>打印</th><td><code>打印 (表达式)</code> —— 输出一行，自动转成文本。</td></tr>
            <tr><th>赋值</th><td><code>表达式 赋值给 变量名</code> —— 例 <code>3 + 4 赋值给 答案</code>。</td></tr>
            <tr><th>取值</th><td>直接写变量名即可参与运算。</td></tr>
        </table>
        <pre class="code">打印 ("请输入你的年龄：")
获取输入() 赋值给 年龄字符串
变成整数(年龄字符串) 赋值给 年龄
年龄 + 1 赋值给 明年年龄
打印 ("明年你 " + 变成字符串(明年年龄) + " 岁了。")</pre>

        <h3 class="sub">8.3　条件判断</h3>
        <pre class="code">如果 分数 &gt;= 60 时，执行：
    打印 ("及格了")
否则如果 分数 &gt;= 50 时，执行：
    打印 ("补考")
否则：
    打印 ("不及格")</pre>

        <h3 class="sub">8.4　循环</h3>
        <p><b>当…时循环</b>（条件为真时反复执行）：</p>
        <pre class="code">5 赋值给 计数
当 计数 &lt;= 10 时，执行：
    打印 (计数)
    计数 + 1 赋值给 计数</pre>
        <p><b>范围循环</b>（计数循环，<b>终点不包含</b>）：</p>
        <pre class="code">注释：从 1 开始，每次加 2，直到小于 10
在 i 的 1 到 10 的范围内，以 2 的步长执行：
    打印 (i)</pre>
        <ul>
            <li>「以 X 的步长执行」这句话<b>必须写</b>，不能省略；步长可以是小数，也可以是负数（倒着数）。</li>
            <li>上例输出 1、3、5、7、9（不含 10）。想要包含终点，把终点写成 11 或改用「当」循环。</li>
            <li>起点/终点/步长都必须是数字；步长为 0 会报「步长不能为0」；单次循环超过 100 万次会报「循环次数过多（疑似死循环）」。</li>
        </ul>

        <h3 class="sub">8.5　函数</h3>
        <pre class="code">定义函数 名为 求平均值，参数为 甲, 乙 的函数：
    返回 (甲 + 乙) / 2

求平均值(80, 90) 赋值给 平均分
打印 ("平均分是 " + 变成字符串(平均分))</pre>
        <ul>
            <li>「参数为 …」可以整段省略，写成 <code>定义函数 名为 打招呼 的函数：</code>。</li>
            <li><code>返回</code> 后面可以不跟表达式（直接结束函数，相当于返回空值）；函数体为空会报错。</li>
            <li>函数必须先定义后调用；调用可以嵌套，但嵌套深度上限 200 层，超出报「调用层级过深」。</li>
        </ul>

        <h3 class="sub">8.6　导入模块</h3>
        <p>两种写法，注意「作为」两边的顺序是<b>先别名、后真模块名</b>：</p>
        <pre class="code">注释：写法一，直接用模块名
导入 时间 模块
使用 时间 模块的 睡眠 功能（2）

注释：写法二，起别名
导入 数学库 作为 math 的名称
使用 数学库 模块的 sqrt 功能(16) 赋值给 根
打印 (根)</pre>
        <ul>
            <li><code>导入 X 模块</code>：导入后可以用 <code>使用 X 模块的 函数 功能(参数)</code> 调用。</li>
            <li><code>导入 别名 作为 X 的名称</code>：真正的模块名写在「作为」后面，别名写在前面。</li>
            <li>可导入的是 Python 标准库（如 <code>math</code>、<code>time</code>、<code>random</code>）以及本机已安装的第三方库；模块名区分大小写。</li>
            <li>调用模块函数时请写全名（<code>sqrt</code>、<code>sleep</code>），中文名只在「使用…功能」这一句里作为语法关键字。</li>
        </ul>

        <h3 class="sub">8.7　内置函数</h3>
        <table class="data">
            <tr><th style="width:150px">函数</th><th style="width:200px">写法</th><th>说明</th></tr>
            <tr><td>当前时间</td><td><code>当前时间()</code></td><td>返回当前时间戳（秒，浮点数）。</td></tr>
            <tr><td>格式化时间</td><td><code>格式化时间()</code><br><code>格式化时间(时间戳)</code></td><td>返回「2026-11-22 10:30:00」这样的字符串；不传参数则取当前时间。</td></tr>
            <tr><td>睡眠 / 延迟</td><td><code>睡眠(秒)</code><br><code>延迟(秒)</code></td><td>暂停执行指定秒数，两个名字完全等价。</td></tr>
            <tr><td>获取输入</td><td><code>获取输入()</code><br><code>获取输入("提示语")</code></td><td>在「执行结果」页下方输入栏等待用户输入，按 <code>Enter</code> 提交后返回字符串（v5.0 新增）。</td></tr>
            <tr><td>变成整数</td><td><code>变成整数(表达式)</code></td><td>转成整数；字符串会先去空格再转，<code>"3.9"</code> 得到 3（截断小数），<code>正确/错误</code> 得到 1/0（v5.0 新增）。</td></tr>
            <tr><td>变成小数</td><td><code>变成小数(表达式)</code></td><td>转成浮点数，<code>正确/错误</code> 得到 1.0/0.0（v5.0 新增）。</td></tr>
            <tr><td>变成字符串</td><td><code>变成字符串(表达式)</code></td><td>转成文本，便于用 <code>+</code> 拼接输出（v5.0 新增）。</td></tr>
        </table>

        <h3 class="sub">8.8　运算符与字面量</h3>
        <table class="kv">
            <tr><th>算术</th><td><code>+</code> <code>-</code> <code>*</code> <code>/</code> <code>%</code>（取余）与括号 <code>()</code>；优先级与数学一致，括号优先。</td></tr>
            <tr><th>比较</th><td><code>&gt;</code> <code>&lt;</code> <code>&gt;=</code> <code>&lt;=</code> <code>==</code> <code>!=</code>，结果是 <code>正确</code> 或 <code>错误</code>。</td></tr>
            <tr><th>布尔字面量</th><td><code>正确</code>（真）、<code>错误</code>（假）；它们不能当变量名。</td></tr>
            <tr><th>字符串</th><td>用半角双引号，<code>"</code> 与 <code>"</code> 中间的内容原样保留；用 <code>+</code> 拼接，参与算术前要先 <code>变成整数</code>/<code>变成小数</code>。</td></tr>
            <tr><th>数字</th><td>整数与小数都支持；除法结果为小数；除数为 0 会报错。</td></tr>
        </table>

        <h3 class="sub">8.9　完整的示例程序</h3>
        <pre class="code">注释：猜数字（演示输入、循环、条件与函数）
打印 ("我想好了一个 1 到 100 之间的整数。")

定义函数 名为 太大了，参数为 猜测 的函数：
    打印 ("你猜的 " + 变成字符串(猜测) + " 太大了")

定义函数 名为 太小了，参数为 猜测 的函数：
    打印 ("你猜的 " + 变成字符串(猜测) + " 太小了")

30 赋值给 次数
42 赋值给 目标
50 赋值给 猜测
当 次数 &gt; 0 时，执行：
    打印 ("还剩 " + 变成字符串(次数) + " 次，你猜：")
    获取输入() 赋值给 输入串
    变成整数(输入串) 赋值给 猜测
    如果 猜测 &gt; 目标 时，执行：
        太大了(猜测)
    否则如果 猜测 &lt; 目标 时，执行：
        太小了(猜测)
    否则：
        打印 ("猜对了！")
        0 赋值给 次数
    次数 - 1 赋值给 次数</pre>
        <div class="note">这段程序演示了输入、循环、条件与函数四类语法，直接复制到「程序」页签即可运行。猜对后把 <code>次数</code> 置 0（再减 1 变成 −1），循环条件不再成立，程序自然结束。运行时请切到「执行结果」页，在下方输入栏输入数字并按 <code>Enter</code>；程序在等输入时界面不会卡死，可随时按「停止」。</div>

        <h3 class="sub">8.10　限制与排错</h3>
        <table class="data">
            <tr><th style="width:200px">现象</th><th>原因与处理</th></tr>
            <tr><td>报「无法解释」</td><td>该行不符合任何语句格式。检查关键字是否写全（「时，执行：」的逗号与冒号不能少）、变量名是否含空格或标点。</td></tr>
            <tr><td>报「未定义的变量」</td><td>变量名拼错，或使用前没有赋值；中文变量名区分全角/半角字符。</td></tr>
            <tr><td>报「缩进错误」</td><td>代码块必须整体缩进（4 空格或 1 个 Tab，不要混用空格与 Tab）。</td></tr>
            <tr><td>循环不结束</td><td>检查循环变量是否在循环体里被更新；死循环会被 100 万次上限拦住。</td></tr>
            <tr><td>获取输入没反应</td><td>请到「执行结果」页签，在底部输入栏输入并回车；编辑器页签里输入是无效的。</td></tr>
            <tr><td>中文标点</td><td>括号、逗号、冒号、运算符的全角写法会自动转换；<b>字符串内部不转换</b>，所以引号里要显示全角字符就照原样写。</td></tr>
        </table>

        <!-- ==================== 9 ==================== -->
        <h2 class="sec" id="s9">9　打包成 EXE（PyInstaller 工具）</h2>
        <p>入口：左侧「实用功能 → 测试功能 → PyInstaller 打包」。把本机上的 <code>.py</code>（或本程序的中文编程脚本 <code>.ctb</code>）交给 PyInstaller，产出可直接双击的 EXE，不需要手写命令行。</p>

        <h3 class="sub">9.1　表单字段</h3>
        <table class="data">
            <tr><th style="width:150px">字段</th><th>说明</th></tr>
            <tr><td>脚本位置</td><td>要打包的脚本，点「浏览」选择；支持 <code>.py</code> 与 <code>.ctb</code>。选完后若名称仍是默认值，会自动填成脚本文件名（不含扩展名）。</td></tr>
            <tr><td>软件名称</td><td>产出的 EXE 文件名，默认 <code>my_app</code>；不能为空。</td></tr>
            <tr><td>软件图标</td><td>可选，选择框默认只列 <code>.ico</code>（也可切到「所有文件」）；填非 ico 文件 PyInstaller 会报错。不填则用默认图标。</td></tr>
            <tr><td>控制台窗口</td><td><b>基于控制台</b>（<code>--console</code>，运行时会有一个黑窗口，能看到 print 与报错）；<b>基于窗口</b>（<code>--windowed</code>，隐藏控制台，适合纯 GUI 程序）。</td></tr>
            <tr><td>单文件</td><td><b>单文件</b>（<code>--onefile</code>，只产出一个 exe，启动时先解压到临时目录，启动慢 3–10 秒）；<b>单目录</b>（<code>--onedir</code>，产出一个文件夹，启动快，便于排查缺模块）。</td></tr>
            <tr><td>输出路径</td><td>默认是「主程序所在目录\\output」，可改；不存在的目录会自动创建。</td></tr>
            <tr><td>按钮 / 日志 / 状态栏</td><td>点「将 .PY 转换为 .EXE」开始；日志区实时显示 PyInstaller 输出（错误红色、成功绿色、信息蓝色），底部状态栏显示当前阶段。</td></tr>
        </table>

        <h3 class="sub">9.2　实际执行的命令</h3>
        <pre class="code">pyinstaller -y --clean --noconfirm --console|--windowed --onefile|--onedir
            --name 软件名称 [--icon 图标.ico]
            --distpath 输出目录 --workpath 输出目录\\build --specpath 输出目录
            脚本路径</pre>
        <p>打包 <code>.ctb</code> 时，工具会先在输出目录生成 <code>temp_ctb_runner.py</code>（把中文编程解释器与你的脚本代码拼在一起），再对这个 runner 打包；窗口模式会自带一个 Tkinter 运行界面。</p>

        <h3 class="sub">9.3　使用前提与已知限制</h3>
        <ul>
            <li>运行环境里必须能直接执行 <code>pyinstaller</code> 命令（已安装且加入 PATH）。没装或没加 PATH 时日志里会出现「'pyinstaller' 不是内部或外部命令」。</li>
            <li>产出的是<b>当前 Python 的位数</b>：用 32 位 Python 3.4 打包，才能在 32 位 Windows XP 上跑；用 64 位 Python 打包的 exe 在 XP 上无法运行。</li>
            <li>给 Windows XP 打包时，建议在 XP 本机打包（在 Win10 上打的包可能依赖 XP 没有的系统 DLL）。</li>
            <li>本工具没有暴露 <code>--noupx</code>、<code>--additional-hooks-dir</code> 这些参数。带 gevent 等特殊依赖的程序，请改用随迁移包提供的 <code>build_xp.bat</code>（其中已固定 <code>-F --noupx --clean --additional-hooks-dir=...</code>）。</li>
            <li>单文件 exe 首次启动较慢、体积约 9–10 MB（含 Tkinter）；部分杀毒软件会误报，需加白名单。</li>
            <li>打包成<b>单文件</b>后，程序在临时解压目录里运行，<code>plugins\\</code> 也在那里：外部插件读不到、运行中自动生成的模板也会随退出消失。要保留插件能力请选<b>单目录</b>模式。</li>
        </ul>

        <!-- ==================== 10 ==================== -->
        <h2 class="sec" id="s10">10　其他工具</h2>
        <h3 class="sub">10.1　单位换算（提示框）</h3>
        <table class="kv">
            <tr><th>入口</th><td>菜单「工具 → 单位换算」。</td></tr>
            <tr><th>形式</th><td>弹出一个信息框，列出 4 条常用换算：1 mol/L = 1000 mmol/L；1 atm = 101.325 kPa；1 cal = 4.184 J；0 ℃ = 273.15 K。<b>它不是交互式换算器</b>，只做速查提示。</td></tr>
        </table>

        <h3 class="sub">10.2　实验记录本</h3>
        <table class="kv">
            <tr><th>入口</th><td>菜单「工具 → 实验记录」。</td></tr>
            <tr><th>用法</th><td>一个可编辑的多行文本框，已预填「实验日期: 」；写完点保存，选择路径后存为 <code>.txt</code>（UTF-8）。</td></tr>
            <tr><th>注意</th><td>不会自动保存，关闭页面前请先保存；本程序不联网，记录只存在本地。</td></tr>
        </table>

        <h3 class="sub">10.3　导出结果</h3>
        <table class="kv">
            <tr><th>入口</th><td>菜单「文件 → 导出结果」。</td></tr>
            <tr><th>现状</th><td>弹出保存对话框，写出一个 <code>.txt</code>，内容为标题「化学工具箱 v5.0 计算结果」与导出时间。<b>当前版本尚未把页面上的具体计算明细写进文件</b>，需要留档时请直接选中结果区的文字复制。</td></tr>
        </table>

        <!-- ==================== 11 ==================== -->
        <h2 class="sec" id="s11">11　插件系统</h2>
        <h3 class="sub">11.1　加载规则</h3>
        <ul>
            <li>插件放在「主程序文件所在目录」下的 <code>plugins\\</code> 文件夹（菜单「文件 → 打开插件文件夹」可直接打开）。源码运行或打包成<b>单目录</b> exe 时，就是 exe 旁的 <code>plugins\\</code>；打包成<b>单文件</b>（<code>-F</code>）时不读外部插件，详见第 9 章。</li>
            <li>启动时扫描该目录下所有 <code>.py</code>（以下划线开头的文件会跳过）；目录里一个 <code>.py</code> 都没有时，会自动生成 <code>example_plugin.py</code> 作模板。</li>
            <li>每个插件文件里必须有名为 <code>Plugin</code> 的类；程序会用 <code>Plugin(app)</code> 实例化，<code>app</code> 即主窗口对象。</li>
            <li>加载失败的插件不会影响其它插件，失败原因打印在控制台（打包成 <code>--windowed</code> 时看不到，调试请用 <code>--console</code> 版）。</li>
            <li>插件以卡片形式出现在「实用功能」页最下方的「插件功能」组，同时可注册到菜单与快捷键。</li>
        </ul>

        <h3 class="sub">11.2　类的属性与方法</h3>
        <table class="data">
            <tr><th style="width:170px">成员</th><th style="width:250px">签名</th><th>作用</th></tr>
            <tr><td>name / version</td><td>字符串属性</td><td>插件名与版本，显示在卡片与菜单上。</td></tr>
            <tr><td>description / author</td><td>字符串属性</td><td>一句话说明（显示在卡片上）与作者。</td></tr>
            <tr><td>__init__</td><td><code>def __init__(self, app)</code></td><td>保存 <code>self.app = app</code>，可在这里做初始化。</td></tr>
            <tr><td>get_menu_name</td><td><code>def get_menu_name(self)</code></td><td>返回菜单显示名，默认返回 <code>name</code>。</td></tr>
            <tr><td>run</td><td><code>def run(self)</code></td><td>点击插件卡片时执行，插件的主功能写在这里。</td></tr>
            <tr><td>register_menus</td><td><code>def register_menus(self)</code></td><td>返回列表 <code>[(菜单名, 标签, 回调), ...]</code>；菜单名只能是 <code>"文件"</code>、<code>"工具"</code>、<code>"帮助"</code>。</td></tr>
            <tr><td>register_shortcuts</td><td><code>def register_shortcuts(self)</code></td><td>返回字典 <code>{"&lt;Control-k&gt;": 回调}</code>，键为 Tk 事件串，直接绑定到主窗口。</td></tr>
            <tr><td>on_balance</td><td><code>def on_balance(self, equation)</code></td><td>配平前的拦截钩子：<b>必须返回 <code>(配平结果, 化合价字典)</code> 二元组</b>才会被采用；返回 None 交给内置算法。化合价字典可为 <code>{}</code>，格式见 5 节。</td></tr>
            <tr><td>on_calculate</td><td><code>def on_calculate(self, kind, params)</code></td><td>计算类请求的预留钩子，默认返回 None（当前版本内置计算器不强制走此钩子）。</td></tr>
            <tr><td>on_startup / on_shutdown</td><td><code>def on_startup(self)</code><br><code>def on_shutdown(self)</code></td><td>加载完成后、关闭窗口前各调用一次，适合初始化资源与清理。</td></tr>
        </table>

        <h3 class="sub">11.3　最小示例</h3>
        <pre class="code"># -*- coding: utf-8 -*-
from tkinter import messagebox

class Plugin:
    name = "我的插件"
    version = "1.0"
    description = "点一下弹个提示"

    def __init__(self, app):
        self.app = app

    def run(self):
        messagebox.showinfo(self.name, "插件运行了！")

    def register_menus(self):
        return [("工具", "我的插件", self.run)]

    def register_shortcuts(self):
        return {"&lt;Control-p&gt;": self.run}</pre>
        <div class="note">插件写成普通类即可，<b>不需要</b>继承任何基类：程序只按 <code>hasattr</code> 检查并调用你实现了的方法，未实现的方法会被跳过。若要复用主程序里的 <code>PluginBase</code> 默认实现，可以在插件文件里用 <code>import sys; PluginBase = sys.modules['__main__'].PluginBase</code> 取得它（仅在主程序以脚本方式启动时有效，打包后可能取不到，所以推荐直接用普通类）。</div>
        <div class="warn"><b>线程注意：</b>v5.0 的中文编程在后台线程执行。插件若在回调里修改界面，请用 <code>self.app.root.after(0, 你的函数)</code> 投递到主线程，不要在后台线程直接操作控件。
        <br><b>安全：</b>插件是普通 Python 代码，拥有与本程序相同的权限，请勿加载来源不明的插件。</div>

        <!-- ==================== 12 ==================== -->
        <h2 class="sec" id="s12">12　常见问题</h2>
        <table class="data">
            <tr><th style="width:230px">问题</th><th>说明</th></tr>
            <tr><td>帮助页版本号是 v4.1？</td><td>旧版本文档没有跟着程序升级。本版已统一为 <b>v5.0</b>：标题、关于页、窗口标题、侧边栏一致。</td></tr>
            <tr><td>XP 上字体发虚/变成宋体？</td><td>XP 没有「微软雅黑」，程序会自动回退到 Tahoma / 宋体，属于正常现象。</td></tr>
            <tr><td>实验演示在 IE 里空白？</td><td>该页用 HTML5 Canvas 与较新 JavaScript，IE8 及更低版本不支持；请用 Firefox 或 IE9+ 打开，帮助文档本身在 IE8 下可正常阅读。</td></tr>
            <tr><td>配平结果不对？</td><td>先检查元素符号大小写、两边元素种类、离子电荷写法；复杂有机物或未定系数的反应可能无解。</td></tr>
            <tr><td><code>CuSO4·5H2O</code> 摩尔质量算错？</td><td>化学式解析不认识结晶水中间那个圆点，请分开算：<code>CuSO4</code> 加上 5×<code>H2O</code>。</td></tr>
            <tr><td>CTB 公式显示 <code>#CIRC!</code>？</td><td>存在循环引用。改公式打破循环，或在「格式 → 迭代计算」里勾选启用并设置「最大迭代次数」与「最大误差」，点「应用设置」。</td></tr>
            <tr><td>打包时提示 pyinstaller 不是内部命令？</td><td>PyInstaller 未安装或未加入 PATH。在 XP 上请先运行迁移包里的 <code>install_on_xp.bat</code>，并用 <code>start_gui.bat</code> 启动打包界面。</td></tr>
            <tr><td>打包出的 exe 在 XP 打不开？</td><td>多半是在 64 位 Python 下打包的。请用 32 位 Python 3.4 打包，并尽量在 XP 本机打包。</td></tr>
            <tr><td>中文编程「获取输入」没反应？</td><td>切到「执行结果」页签，在下方输入栏输入并回车。</td></tr>
            <tr><td>程序会联网吗？</td><td>不会。程序不发起任何网络请求，数据全部在本地；只有你手动点「帮助/关于」时用系统默认浏览器打开本地 HTML 文件。</td></tr>
        </table>

        <!-- ==================== 13 ==================== -->
        <h2 class="sec" id="s13">13　协议与免责</h2>
        <div class="warn">
            <b>免责声明：</b>本软件中的数据由 AI 收集整理，不保证准确；部分功能由 AI 开发，不保证计算结果与结论正确。
            本软件仅作教学与日常辅助用途，请勿用于医疗、安全、生产等关键决策。由使用本软件造成的任何问题，开发者不承担任何责任。
            「实验演示模块」属于测试功能，稳定性有限，请谨慎使用。<br><br>
            <b>使用协议：</b>开始使用本软件即视为已阅读并同意上述说明；若不同意，请立即停止使用。
        </div>

        <!-- ==================== 14 ==================== -->
        <h2 class="sec" id="s14">14　版本历史</h2>
        <table class="data">
            <tr><th style="width:90px">版本</th><th>主要变化</th></tr>
            <tr><td>v4.0</td><td>建立主框架：配平、元素周期表、计算工具、实用功能、中文编程、插件机制。</td></tr>
            <tr><td>v4.1</td><td>新增 CTB 表格（类 Excel，支持 .ctbt 与 Excel 导入导出、字体字号保留）；中文编程新增「如果 / 否则如果 / 否则」「定义函数 / 返回」与实时语法高亮；新增 PluginBase 基类（注册菜单、快捷键、拦截配平与计算）；实用功能与周期表支持鼠标滚轮；帮助与关于界面改版。</td></tr>
            <tr><td><b>v5.0</b></td><td>新增 PyInstaller 打包工具（图形界面把 .py/.ctb 转 EXE）；CTB 表格顶部工具栏压缩为一行；实用功能首页按 5 组重新排布；中文编程新增 <code>获取输入</code>、<code>变成整数</code>、<code>变成小数</code>、<code>变成字符串</code>，输入与执行改到后台线程；帮助文档重写为逐模块手册，并做 IE8 兼容处理。</td></tr>
        </table>
        <p style="color:#667; font-size:13px; margin-top:10px;">© 化学爱好者 · 使用愉快！</p>
        </div>
        </div>
    </div>

    <div id="experiment-page" class="page-panel">
        <!--[if lt IE 9]>
        <div class="ie-warn" style="margin:20px;">提示：本页的「实验演示」使用 HTML5 Canvas 与较新的 JavaScript，IE8 及更低版本无法运行。
        上面的「帮助文档」可以正常阅读；如需观看演示，请用 Firefox 或 IE9 及以上版本浏览器打开本页面。</div>
        <style type="text/css">#app { display: none; }</style>
        <![endif]-->
        <div class="experiment-body">
            <div id="app">
                <div class="exp-header">
                    <h1>卢瑟福α粒子散射实验模拟器</h1>
                    <p>运用计算机编程模拟原子结构 —— 核式模型与散射实验</p>
                </div>

                <div class="exp-tabs">
                    <div class="exp-tab active" onclick="switchExpTab('scattering', this)">α粒子散射实验</div>
                    <div class="exp-tab" onclick="switchExpTab('atomic', this)">核式原子结构模型</div>
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

    <script type="text/javascript">
    /* ===== 导航脚本（ES3 写法，IE8 可用；不改动实验演示的原有逻辑） ===== */
    function _setText(el, txt) {
        if (!el) return;
        if (typeof el.textContent !== 'undefined') { el.textContent = txt; }
        else { el.innerText = txt; }
    }
    function switchPage(page, btn) {
        var helpPage = document.getElementById('help-page');
        var expPage = document.getElementById('experiment-page');
        if (page === 'help') {
            if (helpPage) helpPage.style.display = 'block';
            if (expPage) expPage.style.display = 'none';
        } else {
            if (helpPage) helpPage.style.display = 'none';
            if (expPage) expPage.style.display = 'block';
        }
        var i, c, tabs = document.getElementsByTagName('button');
        for (i = 0; i < tabs.length; i++) {
            c = tabs[i].className || '';
            if (c.indexOf('navbtn') !== -1) { tabs[i].className = 'navbtn'; }
        }
        if (btn) btn.className = 'navbtn active';
        if (page !== 'help') {
            setTimeout(function () {
                try {
                    if (typeof electrons !== 'undefined' && electrons.length === 0
                        && typeof updateAtom === 'function') { updateAtom(); }
                    if (typeof animationRunning !== 'undefined' && !animationRunning
                        && typeof animateElectrons === 'function') {
                        animationRunning = true;
                        _setText(document.getElementById('animBtn'), '暂停');
                        animateElectrons();
                    }
                } catch (e) { }
            }, 100);
        }
    }
    function switchExpTab(tab, el) {
        var i, c, panels = ['scattering', 'atomic'];
        for (i = 0; i < panels.length; i++) {
            var p = document.getElementById(panels[i]);
            if (p) { p.style.display = (panels[i] === tab) ? 'block' : 'none'; }
        }
        var divs = document.getElementsByTagName('div');
        for (i = 0; i < divs.length; i++) {
            c = divs[i].className || '';
            if (c.indexOf('exp-tab') === 0) { divs[i].className = 'exp-tab'; }
        }
        if (el) el.className = 'exp-tab active';
        if (tab === 'atomic') {
            setTimeout(function () {
                try { if (typeof updateAtom === 'function') { updateAtom(); } } catch (e) { }
            }, 100);
        }
    }
    function updateValue(id, val) {
        _setText(document.getElementById(id), val);
    }
    </script>

    <script type="text/javascript">
    /* ===== 以下为实验演示核心（Canvas + ES6）：需要 Firefox 或 IE9 及以上 ===== */

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
            messagebox.showerror("错误", '无法创建或打开帮助文件：{0}'.format(e))

    def show_about(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        about_dir = os.path.join(base_dir, "about")
        try:
            os.makedirs(about_dir, exist_ok=True)
        except Exception:
            pass
        about_file = os.path.join(about_dir, "about.html")

        html_content = """<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>关于 - 化学工具箱 v5.0</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Microsoft YaHei', 'Segoe UI', system-ui, sans-serif; background: #f5f5f5; min-height: 100vh; }
.top-nav { background: #14539A; background: linear-gradient(135deg, #1a5fb4, #0d3b8c); box-shadow: 0 2px 10px rgba(0,0,0,0.2); position: sticky; top: 0; z-index: 1000; }
.nav-inner { max-width: 1100px; margin: 0 auto; padding: 0 20px; display: flex; align-items: center; justify-content: space-between; }
.nav-title { color: #fff; font-size: 18px; font-weight: 600; padding: 14px 0; }
.about-body { padding: 40px 20px; }
.about-container { max-width: 820px; margin: auto; background: #fff; padding: 36px 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
.header-area { text-align: center; padding-bottom: 24px; border-bottom: 2px solid #eef3f9; }
.app-logo { width: 64px; height: 64px; border-radius: 16px; background: #1a5fb4; background: linear-gradient(135deg, #1a5fb4, #0d3b8c); display: inline-flex; align-items: center; justify-content: center; color: #fff; font-size: 32px; font-weight: bold; letter-spacing: -2px; box-shadow: 0 6px 18px rgba(26,95,180,0.35); margin-bottom: 14px; }
h1 { color: #1a3d6b; font-size: 26px; margin-bottom: 6px; }
.version { display: inline-block; background: #eaf2ff; color: #1a5fb4; padding: 3px 12px; border-radius: 999px; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.slogan { color: #7f8c8d; font-size: 14px; margin-top: 6px; }
h2 { color: #1a5fb4; font-size: 17px; margin: 26px 0 12px; padding-left: 10px; border-left: 3px solid #3584e4; }
p { line-height: 1.8; color: #333; font-size: 14px; margin-bottom: 10px; }
ul { line-height: 1.9; padding-left: 24px; color: #333; font-size: 14px; }
ul li { margin-bottom: 4px; }
.feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin: 8px 0; }
.feature-card { background: #F3F8FF; background: linear-gradient(135deg, #f8fbff, #eaf2ff); border: 1px solid #d6e6ff; border-radius: 10px; padding: 14px 16px; transition: all 0.25s; }
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
<!--[if lt IE 9]>
<style type="text/css">
/* IE8 回退：不支持 flex / grid / inline-flex，改为块级布局，保证内容可读 */
.nav-inner { display: block; }
.app-logo { display: block; margin: 0 auto 14px; line-height: 64px; text-align: center; }
.feature-grid { display: block; }
.feature-card { margin-bottom: 10px; }
.version { display: inline; }
</style>
<![endif]-->
</head>
<body>
<div class="top-nav">
    <div class="nav-inner">
        <div class="nav-title">化学工具箱 v5.0</div>
    </div>
</div>

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
            <tr><th>开发语言</th><td>Python 3.4+（兼容 Windows XP）</td></tr>
            <tr><th>GUI 框架</th><td>Tkinter / ttk（Fluent 现代风）</td></tr>
            <tr><th>数值计算</th><td>纯 Python（内置 SVD 最小二乘配平，无需 NumPy）</td></tr>
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
            messagebox.showerror("错误", '无法创建或打开关于文件：{0}'.format(e))

    def show_plugin_docs(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        doc_dir = os.path.join(base_dir, "docs")
        try:
            os.makedirs(doc_dir, exist_ok=True)
        except Exception:
            pass
        doc_file = os.path.join(doc_dir, "plugin_dev.html")

        html_content = """<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>插件开发文档 - 化学工具箱 v5.0</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Tahoma, 'Microsoft YaHei', '宋体', sans-serif; background:#f5f5f5; padding: 40px 20px; }
.wrap { max-width: 900px; margin: auto; background:#fff; padding: 32px; border-radius: 10px; box-shadow: 0 2px 14px rgba(0,0,0,.08); }
h1 { color:#1a3d6b; border-bottom:2px solid #3498db; padding-bottom:10px; margin-bottom:18px; font-size: 24px; }
h2 { color:#2980b9; margin:24px 0 10px; font-size:18px; }
h3 { color:#1a5fb4; margin:16px 0 8px; font-size:15px; }
p, li { line-height: 1.8; color:#333; font-size: 14px; }
ul, ol { padding-left: 24px; margin-bottom: 12px; }
pre { background:#1E1E2E; color:#CDD6F4; padding:16px; border-radius:8px; overflow-x:auto; font-family: Consolas, monospace; font-size: 13px; line-height: 1.55; margin: 10px 0; }
code { background:#f0f0f0; padding:2px 6px; border-radius:4px; font-family: Consolas, monospace; color:#c0392b; }
pre code { background: transparent; color: inherit; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; }
th, td { border: 1px solid #ddd; padding: 8px 10px; text-align: left; font-size: 14px; line-height: 1.7; vertical-align: top; }
th { background: #E3F2FD; color:#0F6CBD; }
.note { background:#e7f3ff; border-left:4px solid #0F6CBD; padding:10px 14px; border-radius: 0 6px 6px 0; margin: 10px 0; color:#0A4A8A; }
.warning { background:#fff3cd; border-left:4px solid #f0ad4e; padding:10px 14px; margin: 10px 0; color:#856404; }
</style>
</head>
<body>
<div class="wrap">
<h1>化学工具箱 v5.0 插件开发文档</h1>
<p>插件就是一个放在 <code>plugins/</code> 里的普通 <code>.py</code> 文件。程序启动时扫描加载，把插件挂到「实用功能」页底部的「插件功能」组，同时可以注册到主菜单与快捷键。本文档按 v5.0 的加载器实现编写，写了方法签名、调用时机与可复制的示例。</p>

<h2>1. 放置与加载规则</h2>
<ul>
<li>位置：主程序同目录下的 <code>plugins/</code> 文件夹（菜单「文件 → 打开插件文件夹」可直接打开）。</li>
<li>扫描：加载目录下所有 <code>.py</code> 文件，跳过以 <code>_</code> 开头的文件；如果目录里一个 <code>.py</code> 都没有，程序会自动生成 <code>example_plugin.py</code> 作模板。</li>
<li>入口类必须叫 <code>Plugin</code>；程序用 <code>Plugin(app)</code> 实例化，<code>app</code> 是主窗口对象（<code>ChemistryToolbox</code>）。</li>
<li>单个插件出错只打印 <code>加载插件 xxx 失败: ...</code>，不影响其它插件与主程序；加载发生在启动时，运行中新增插件需重启程序。</li>
<li>插件不需要继承任何基类：程序用 <code>hasattr</code> 逐个检查你实现了哪些方法，未实现的直接跳过。</li>
</ul>

<h2>2. 最小可用插件</h2>
<pre><code># -*- coding: utf-8 -*-
from tkinter import messagebox

class Plugin:
    name = "我的插件"
    version = "1.0"
    description = "点一下弹个提示"       # 显示在实用功能页的插件卡片上
    author = "你的名字"

    def __init__(self, app):
        self.app = app

    def run(self):
        messagebox.showinfo(self.name, "插件运行了！")</code></pre>
<p>只实现 <code>run()</code> 就够用了：插件卡片会自动出现，点击即执行。</p>

<h2>3. 属性与方法全表</h2>
<table>
<tr><th style="width:170px">成员</th><th style="width:250px">签名</th><th>作用与调用时机</th></tr>
<tr><td>name<br>version</td><td>字符串类属性</td><td>插件名与版本号，用于卡片标题与菜单文字。</td></tr>
<tr><td>description<br>author</td><td>字符串类属性</td><td>一句话说明（显示在卡片上）与作者署名。</td></tr>
<tr><td>__init__</td><td><code>def __init__(self, app)</code></td><td>加载时调用一次；至少保存 <code>self.app = app</code>。</td></tr>
<tr><td>get_menu_name</td><td><code>def get_menu_name(self)</code></td><td>返回卡片显示名；不实现时默认用 <code>name</code>。</td></tr>
<tr><td>run</td><td><code>def run(self)</code></td><td>点击插件卡片时执行，插件主功能写在这里。</td></tr>
<tr><td>register_menus</td><td><code>def register_menus(self)</code></td><td>启动时调用，返回 <code>[(菜单名, 标签, 回调), ...]</code>；菜单名只能是 <code>"文件"</code>、<code>"工具"</code>、<code>"帮助"</code>。</td></tr>
<tr><td>register_shortcuts</td><td><code>def register_shortcuts(self)</code></td><td>启动时调用，返回 <code>{"Tk事件串": 回调}</code>，逐个绑定到主窗口。</td></tr>
<tr><td>on_balance</td><td><code>def on_balance(self, equation)</code></td><td>用户点「配平」时先调用；返回 <code>(配平结果, 化合价字典)</code> 二元组即采用插件结果，返回 None 交给内置算法。</td></tr>
<tr><td>on_calculate</td><td><code>def on_calculate(self, kind, params)</code></td><td>预留的计算钩子，当前内置计算器不强制调用，返回 None 即可。</td></tr>
<tr><td>on_startup</td><td><code>def on_startup(self)</code></td><td>所有插件加载完成后调用一次，适合建目录、读配置。</td></tr>
<tr><td>on_shutdown</td><td><code>def on_shutdown(self)</code></td><td>关闭窗口前调用一次，适合保存状态、释放资源。</td></tr>
</table>

<h2>4. 注册菜单与快捷键</h2>
<pre><code>    def register_menus(self):
        # 三项：菜单名、菜单项文字、点击后的回调
        return [("工具", "打开我的面板", self.run),
                ("帮助", "我的插件说明", self.show_help)]

    def register_shortcuts(self):
        # 键是 Tk 事件串：&lt;Control-p&gt; 表示 Ctrl+P，&lt;F5&gt; 表示 F5
        return {"&lt;Control-p&gt;": self.run}</code></pre>
<p>回调可以是任意无参函数（一般用 <code>self.方法名</code>）；快捷键绑定到主窗口，窗口获得焦点时生效。</p>

<h2>5. 拦截配平请求</h2>
<pre><code>    def on_balance(self, equation):
        if equation.replace(" ", "") == "H2+O2=H2O":
            # 必须返回二元组：(配平结果, 化合价字典)
            return ("2H2 + O2 = 2H2O    （由插件给出）", {})
        return None        # 返回 None：交回内置算法</code></pre>
<p>返回值必须是<b>二元组</b>：第一项是配平后的方程式字符串；第二项是化合价字典，用于在结果下方显示「化合价标注」，没有就写 <code>{}</code>。只返回一个字符串会因无法解包而被程序忽略（异常被吞掉，插件看起来「没生效」）。</p>
<p>化合价字典的格式是 <code>{化学式: {元素: 化合价整数}}</code>，例如：</p>
<pre><code>    {"H2": {"H": 1}, "O2": {"O": 0}, "H2O": {"H": 1, "O": -2}}</code></pre>

<h2>6. 线程与界面更新</h2>
<div class="note">插件回调默认运行在 Tk 主线程，可以直接操作控件。但如果你在自己的插件里开了后台线程（<code>threading.Thread</code>），或在中文编程执行期间被调用，<b>必须</b>用 <code>self.app.root.after(0, 你的函数)</code> 把界面更新投递回主线程；在后台线程直接改控件可能造成界面错乱甚至崩溃。</div>

<h2>7. 调试与分发</h2>
<ul>
<li>加载失败的详细原因只打印到控制台：用 <code>python 主程序.py</code> 运行，或用 <code>--console</code> 模式打包的 exe 才能看到；<code>--windowed</code> 打包后看不到控制台输出。</li>
<li>插件目录取的是「主程序文件所在目录 + plugins」。源码运行与 PyInstaller <b>单目录</b>模式（默认 <code>--onedir</code>）下就在 exe 旁边的 <code>plugins/</code>，放进去即生效；<b>单文件</b>模式（<code>--onefile</code>）解压到临时目录运行，<code>plugins/</code> 也在临时目录里，启动时自动生成的模板用不上、你预先放好的插件不会被读到。需要插件就别用 <code>-F</code>。</li>
<li>插件是普通 Python 代码，拥有与本程序相同的权限（可读写文件、联网），请勿加载来源不明的插件。</li>
<li>写完先做一次自检：<code>python -c "import 你的插件文件名"</code> 能过，再把文件放进 <code>plugins/</code>。</li>
</ul>

<div class="warning">安全提示：本程序不会校验插件内容，也不会限制插件权限。请只使用自己编写或信任的插件。</div>

<div class="note">相关文档：程序内的「帮助 → 使用教程」包含 16 个模块的完整说明，「帮助 → 中文编程开发文档」是中文编程语法手册。</div>

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
            messagebox.showerror("错误", '无法创建或打开文档：{0}'.format(e))

    def show_lang_docs(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        doc_dir = os.path.join(base_dir, "docs")
        try:
            os.makedirs(doc_dir, exist_ok=True)
        except Exception:
            pass
        doc_file = os.path.join(doc_dir, "lang_dev.html")

        html_content = """<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>中文编程开发文档 - 化学工具箱 v5.0</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Tahoma, 'Microsoft YaHei', '宋体', sans-serif; background:#f5f5f5; padding: 40px 20px; }
.wrap { max-width: 900px; margin: auto; background:#fff; padding: 32px; border-radius: 10px; box-shadow: 0 2px 14px rgba(0,0,0,.08); }
h1 { color:#1a3d6b; border-bottom:2px solid #3498db; padding-bottom:10px; margin-bottom:18px; font-size: 24px; }
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
<div class="note">
<b>书写规则：</b>一行一条语句；代码块整体缩进，用 4 个空格或 1 个 Tab（Tab 记作 4 空格，<b>不要空格与 Tab 混用</b>）；
变量名可用中文、英文、数字、下划线，但不能用保留字「正确」「错误」；行内 <code>注释:</code> 或 <code>注释：</code> 之后到行尾都会被忽略。
全角的括号、逗号、冒号、加减乘除与比较符会自动转成半角，<b>字符串引号内的内容不转换</b>。
</div>

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
当 计数 &lt;= 5 时，执行：
    打印 (计数)
    计数 + 1 赋值给 计数</code></pre>

<h3>3.3 循环：范围遍历</h3>
<pre><code>注释：从 1 开始，每次加 2，直到小于 10
在 i 的 1 到 10 的范围内，以 2 的步长执行：
    打印 ("当前的 i 是：" + 变成字符串(i))</code></pre>
<div class="note">
<b>三个要点：</b>① 终点<b>不包含</b>在循环内（上面输出 1、3、5、7、9，没有 10）；
② 「以 X 的步长执行」这句<b>不能省略</b>，步长可以是小数或负数（负数表示倒着数）；
③ 步长为 0 会报「步长不能为0」；循环次数超过 100 万次会报「循环次数过多（疑似死循环）」。
</div>

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
<p>可导入的是 Python 标准库（<code>math</code>、<code>time</code>、<code>random</code> 等）或本机已安装的第三方库，模块名区分大小写。要起别名时记住顺序：<b>别名在前、真正的模块名在后</b>。</p>
<pre><code>导入 数学库 作为 math 的名称
使用 数学库 模块的 sqrt 功能 (16) 赋值给 根
打印 ("16 的平方根是：" + 变成字符串(根))</code></pre>

<h2>6. 运算符一览</h2>
<ul>
    <li><b>算术运算</b>： <code>+</code>（加/拼接）、<code>-</code>（减）、<code>*</code>（乘）、<code>/</code>（除）、<code>%</code>（取余）</li>
    <li><b>比较运算</b>： <code>&gt;</code>、<code>&lt;</code>、<code>&gt;=</code>、<code>&lt;=</code>、<code>==</code>（等于）、<code>!=</code>（不等于）</li>
    <li><b>逻辑值</b>： <code>正确</code> (True)、<code>错误</code> (False)</li>
</ul>

<h2>7. 常见错误与处理</h2>
<table>
<tr><th style="width:220px">报错 / 现象</th><th>原因与处理</th></tr>
<tr><td>「无法解释」</td><td>这一行不符合任何语句格式。检查关键字是否写全（例如「时，执行：」的逗号和冒号都不能少）、变量名是否含空格或标点。</td></tr>
<tr><td>「未定义的变量」</td><td>变量名拼错，或使用前没有赋值；中文变量名区分全角与半角字符。</td></tr>
<tr><td>「缩进错误」</td><td>代码块缩进不一致，或空格与 Tab 混用。统一改成 4 个空格。</td></tr>
<tr><td>「步长不能为0」</td><td>范围循环的步长写成了 0。</td></tr>
<tr><td>「循环次数过多（疑似死循环）」</td><td>循环条件永远为真，或范围过大；检查循环变量是否在循环体内被更新。</td></tr>
<tr><td>「调用层级过深」</td><td>函数递归超过 200 层，检查递归出口。</td></tr>
<tr><td>获取输入没反应</td><td>请切到「执行结果」页签，在下方输入栏输入内容并按 Enter；在「程序」页签里输入是无效的。</td></tr>
<tr><td>数字与文字相加报错</td><td>先用 <code>变成字符串</code> 把数字转成文字再拼接，或先用 <code>变成整数</code>/<code>变成小数</code> 把输入的文字转成数字。</td></tr>
</table>

<div class="note">执行按钮在执行期间会变成「停止」，随时可以中断；因为执行在后台线程，界面不会卡死。程序以 UTF-8 保存，导入/保存按钮对应普通 <code>.py</code> 文件，可直接用其他编辑器打开。</div>

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
            messagebox.showerror("错误", '无法创建或打开文档：{0}'.format(e))


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