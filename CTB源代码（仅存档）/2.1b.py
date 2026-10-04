# ==================== 主应用程序 ====================
import importlib.util
import os
import sys
from types import ModuleType

class ChemistryToolbox:
    def __init__(self, root):
        self.root = root
        self.root.title("化学工具箱 v2.0")
        self.root.geometry("1200x800")
        self.default_font = ("Microsoft YaHei", 10)
        self.title_font = ("Microsoft YaHei", 12, "bold")
        self.plugins = []  # 存储已加载的插件
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
        self.load_plugins()  # 加载插件
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
class Plugin:
    def __init__(self, app):
        self.app = app
        self.name = "示例插件"
    
    def get_menu_name(self):
        return self.name
    
    def run(self):
        self.app.clear_content()
        tk.Label(self.app.content_frame, text="这是一个示例插件", font=self.app.title_font).pack(pady=20)
        tk.Label(self.app.content_frame, text="你可以在这里添加自定义功能", font=self.app.default_font).pack()
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
        tk.Label(self.content_frame, text="化学方程式配平 v2.0", font=self.title_font, fg="blue").pack(pady=10)
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
                    f.write("化学工具箱 v2.0 计算结果\n")
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
    
    def show_tutorial(self):
        messagebox.showinfo("使用教程", "化学工具箱 v2.0 新增功能：\n- 元素百分比、经验式确定\n- 浓度换算、产率计算\n- 电化学（能斯特方程）\n- 化学平衡、热力学计算\n- 气体分压、核化学（半衰期）\n- 溶液配制计算\n原有功能全部保留。\n离子方程式：*阳离子，^阴离子。\n插件功能：将.py插件放入plugins文件夹，重启后自动加载。")
    
    def show_about(self):
        messagebox.showinfo("关于", "化学工具箱 v2.0\n新增15项功能，插件系统支持。\n保留全部1.0功能。\n作者：化学爱好者")
    
    def show_help(self):
        messagebox.showinfo("帮助", "点击上方按钮选择功能。\n计算菜单含8个标签页。\n实用功能含16项工具。\n插件：plugins文件夹内的.py文件需定义Plugin类，实现__init__(app)、get_menu_name()、run()方法。")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChemistryToolbox(root)
    root.mainloop()