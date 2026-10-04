import webbrowser
import os

def show_help(self):
    """打开帮助网页（自动生成/更新）"""
    # 获取当前脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    help_dir = os.path.join(base_dir, "help")
    help_file = os.path.join(help_dir, "help.html")
    
    # 如果 help 文件夹不存在则创建
    if not os.path.exists(help_dir):
        os.makedirs(help_dir)
    
    # 如果 help.html 已存在，先删除（防止被篡改）
    if os.path.exists(help_file):
        os.remove(help_file)
    
    # 生成新的帮助内容（HTML格式）
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>化学工具箱 v2.0 - 帮助</title>
    <style>
        body {
            font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
            background: #f5f7fa;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 960px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            padding: 30px 40px;
        }
        h1 {
            color: #1a73e8;
            border-bottom: 3px solid #1a73e8;
            padding-bottom: 12px;
            margin-top: 0;
        }
        h2 {
            color: #2c3e50;
            margin-top: 28px;
            border-left: 5px solid #1a73e8;
            padding-left: 15px;
        }
        h3 {
            color: #34495e;
            margin-top: 20px;
        }
        .section {
            margin-bottom: 30px;
        }
        .highlight {
            background: #e8f0fe;
            padding: 12px 18px;
            border-radius: 6px;
            font-family: "Courier New", monospace;
            color: #1a1a1a;
        }
        .formula {
            font-family: "Courier New", monospace;
            background: #f0f0f0;
            padding: 2px 8px;
            border-radius: 4px;
        }
        ul {
            line-height: 1.8;
        }
        .note {
            background: #fff8e1;
            border-left: 5px solid #ffb300;
            padding: 12px 18px;
            border-radius: 4px;
            margin: 15px 0;
        }
        footer {
            margin-top: 40px;
            border-top: 1px solid #ddd;
            padding-top: 15px;
            text-align: center;
            color: #888;
            font-size: 14px;
        }
        .badge {
            display: inline-block;
            background: #1a73e8;
            color: white;
            padding: 2px 12px;
            border-radius: 20px;
            font-size: 14px;
            margin-left: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }
        th {
            background: #f2f2f2;
        }
        .code {
            background: #f4f4f4;
            padding: 12px 16px;
            border-radius: 6px;
            font-family: "Courier New", monospace;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 化学工具箱 v2.0 <span class="badge">帮助手册</span></h1>
        <p><strong>最后更新：</strong>2025年6月18日</p>
        
        <div class="section">
            <h2>📌 快速入门</h2>
            <p>化学工具箱是一款集成了化学计算、配平、元素查询等多种功能的桌面辅助软件。</p>
            <ul>
                <li>点击顶部功能按钮进入对应模块。</li>
                <li>在“计算”菜单中可进行摩尔质量、浓度、比例求解等计算。</li>
                <li>“实用功能”菜单包含 pH 计算、气体定律、热化学等 16 种工具。</li>
                <li>“实用功能”菜单底部的“插件功能”可加载用户自定义的 Python 插件。</li>
            </ul>
        </div>

        <div class="section">
            <h2>⚖️ 配平功能</h2>
            <p>支持普通化学方程式和离子方程式的配平。</p>
            <ul>
                <li><strong>离子符号约定：</strong><span class="formula">*</span> 表示阳离子（正电荷），<span class="formula">^</span> 表示阴离子（负电荷）。</li>
                <li>例如：<span class="formula">HCO3^ + H* = CO2 + H2O</span></li>
                <li>配平结果系数为蓝色，化合价正价绿色，负价红色。</li>
            </ul>
            <div class="highlight">
                示例：H2+O2=H2O → 2H₂+O₂=2H₂O<br>
                Fe2O3+CO=Fe+CO2 → Fe₂O₃+3CO=2Fe+3CO₂
            </div>
        </div>

        <div class="section">
            <h2>🧮 计算功能（8个标签页）</h2>
            <ul>
                <li><strong>摩尔质量：</strong>输入化学式，计算相对分子质量。</li>
                <li><strong>浓度计算：</strong>由溶质质量、体积、摩尔质量求物质的量浓度。</li>
                <li><strong>稀释计算：</strong>利用 C₁V₁ = C₂V₂ 求稀释后浓度。</li>
                <li><strong>比例求解：</strong>支持 a/b=c/x 或 a/b=x/d 两种形式求解 x。</li>
                <li><strong>元素百分比：</strong>计算化学式中各元素的质量分数。</li>
                <li><strong>经验式确定：</strong>输入各元素质量或百分比，自动确定最简式。</li>
                <li><strong>浓度换算：</strong>质量分数与摩尔浓度的相互换算。</li>
                <li><strong>产率计算：</strong>根据实际产量和理论产量计算百分产率。</li>
            </ul>
        </div>

        <div class="section">
            <h2>🔧 实用功能（16项工具）</h2>
            <ul>
                <li>pH计算器（强酸/强碱、弱酸/弱碱）</li>
                <li>理想气体状态方程（PV=nRT）</li>
                <li>热化学计算（热量、燃烧热）</li>
                <li>氧化数计算（输入化合物自动分析）</li>
                <li>有机化学工具（官能团识别、同分异构体计数）</li>
                <li>溶解度查询（常见物质及规则）</li>
                <li>缓冲溶液 pH 计算（Henderson-Hasselbalch方程）</li>
                <li>酸碱滴定计算（求碱体积）</li>
                <li>光谱分析（波长-能量转换）</li>
                <li>化学动力学（阿伦尼乌斯方程、半衰期）</li>
                <li>电化学（能斯特方程）</li>
                <li>化学平衡（由 K 求 ΔG°）</li>
                <li>热力学（ΔG = ΔH - TΔS）</li>
                <li>气体分压（道尔顿分压定律）</li>
                <li>核化学（放射性衰变半衰期计算）</li>
                <li>溶液配制计算（目标浓度、体积求溶质质量）</li>
            </ul>
        </div>

        <div class="section">
            <h2>🧩 插件系统</h2>
            <p>将符合规范的 Python 插件放入 <span class="formula">plugins</span> 文件夹，重启后即可在“实用功能 → 插件功能”下使用。</p>
            <p>插件必须定义 <span class="formula">Plugin</span> 类，实现 <span class="formula">__init__(app)</span>、<span class="formula">get_menu_name()</span> 和 <span class="formula">run()</span> 方法。</p>
            <div class="note">
                💡 示例插件：<strong>简易机械效率计算器</strong> 已内置，可参考其代码开发更多插件。
            </div>
        </div>

        <div class="section">
            <h2>🗂️ 其他辅助功能</h2>
            <ul>
                <li><strong>文件 → 导出结果：</strong>将当前计算结果保存为文本文件。</li>
                <li><strong>工具 → 单位换算：</strong>常用化学单位换算速查。</li>
                <li><strong>工具 → 实验记录：</strong>内置简易实验笔记本，可保存文本。</li>
            </ul>
        </div>

        <div class="section">
            <h2>📋 注意事项</h2>
            <ul>
                <li>氯元素的相对原子质量取 <strong>35.5</strong>，其他元素按整数（四舍五入）。</li>
                <li>温度单位使用 <strong>开尔文 (K)</strong>，浓度单位使用 <strong>mol/L</strong>。</li>
                <li>离子方程式中 <span class="formula">*</span> 和 <span class="formula">^</span> 的数量代表电荷数，如 <span class="formula">Ca**</span> 表示 Ca²⁺，<span class="formula">SO4^^</span> 表示 SO₄²⁻。</li>
                <li>所有计算支持浮点数输入（如 1.5、0.02）。</li>
            </ul>
        </div>

        <div class="section">
            <h2>📅 版本历史</h2>
            <table>
                <tr><th>版本</th><th>更新内容</th></tr>
                <tr><td>v2.0</td><td>新增15项功能、插件系统、电化学/平衡/热力学等计算</td></tr>
                <tr><td>v1.0</td><td>配平、周期表、pH、气体定律、热化学、氧化还原、有机、溶解度、缓冲、滴定、光谱、动力学</td></tr>
                <tr><td>v0.5</td><td>离子配平（*^格式）、下标显示、化合价标注</td></tr>
                <tr><td>v0.1</td><td>初始版本（基础配平、30种元素）</td></tr>
            </table>
        </div>

        <footer>
            <p>化学工具箱 © 2025 | 开源协议 MIT | 开发者：化学爱好者</p>
            <p>本帮助页面每次打开时自动重新生成，确保内容为最新版本。</p>
        </footer>
    </div>
</body>
</html>'''
    
    # 写入新文件
    with open(help_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 使用系统默认浏览器打开
    webbrowser.open(help_file)
    self.update_status("已打开帮助页面")