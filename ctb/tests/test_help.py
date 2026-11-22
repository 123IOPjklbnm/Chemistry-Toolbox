import io

from ctb import ctbhelp


def _capture(*args, **kwargs):
    """捕获 ctbhelp 的输出文本。"""
    buf = io.StringIO()
    ctbhelp(*args, file=buf, **kwargs)
    return buf.getvalue()


# ---------- 总览 ----------

def test_总览包含基本信息():
    out = _capture()
    assert "ctb" in out
    assert "0.3.0" in out
    assert "balance" in out
    assert "mass" in out
    assert "parse_formula" in out
    assert "ctbhelp" in out


def test_总览包含用法示例():
    out = _capture()
    assert "H2+O2=H2O" in out
    assert "2H2+O2=2H2O" in out


def test_总览包含仓库链接():
    out = _capture()
    assert "github.com" in out


# ---------- 具体函数 ----------

def test_balance帮助():
    out = _capture("balance")
    assert "balance" in out
    assert "配平" in out
    assert "H2+O2=H2O" in out
    assert "2H2+O2=2H2O" in out


def test_mass帮助():
    out = _capture("mass")
    assert "mass" in out
    assert "mode" in out
    assert "35.5" in out              # 氯的特例要提到
    assert "1.008" in out


def test_parse_formula帮助():
    out = _capture("parse_formula")
    assert "parse_formula" in out
    assert "字典" in out


def test_ctbhelp帮助():
    out = _capture("ctbhelp")
    assert "ctbhelp" in out


# ---------- 大小写不敏感 ----------

def test_大小写不敏感():
    a = _capture("Balance")
    b = _capture("balance")
    assert a == b


# ---------- 未找到 ----------

def test_未知主题():
    out = _capture("not_a_function")
    assert "未找到" in out
    assert "not_a_function" in out


def test_未知主题提示可用列表():
    out = _capture("foo")
    assert "balance" in out
    assert "mass" in out


# ---------- 非法类型 ----------

def test_非字符串参数():
    out = _capture(123)
    assert "必须是字符串" in out or "str" in out


# ---------- 默认输出流 ----------

def test_默认输出到stdout(capsys):
    ctbhelp()
    captured = capsys.readouterr()
    assert "ctb" in captured.out