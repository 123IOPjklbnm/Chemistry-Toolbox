import pytest

from ctb import mass


# ---------- mode=1 精确值 ----------

def test_单元素():
    assert mass("H") == pytest.approx(1.008, abs=1e-3)
    assert mass("C") == pytest.approx(12.011, abs=1e-3)
    assert mass("Ag") == pytest.approx(107.87, abs=1e-2)


def test_简单分子():
    assert mass("H2O") == pytest.approx(18.015, abs=1e-3)
    assert mass("CO2") == pytest.approx(44.009, abs=1e-3)
    assert mass("NaCl") == pytest.approx(58.44, abs=1e-2)


def test_带括号():
    # Ca(OH)2 = 40.078 + 15.999*2 + 1.008*2 = 74.092
    assert mass("Ca(OH)2") == pytest.approx(74.092, abs=1e-3)
    assert mass("Fe2(SO4)3") == pytest.approx(399.858, abs=1e-3)


def test_显式mode1():
    assert mass("H", 1) == pytest.approx(1.008, abs=1e-3)
    assert mass("CO2", 1) == pytest.approx(44.009, abs=1e-3)


# ---------- mode=2 近似值 ----------

def test_近似单元素():
    assert mass("H", 2) == 1.0
    assert mass("C", 2) == 12.0
    assert mass("Ag", 2) == 108.0


def test_近似氯():
    assert mass("Cl", 2) == 35.5
    assert mass("Cl2", 2) == 71.0
    assert mass("NaCl", 2) == 58.5


def test_近似分子():
    assert mass("H2O", 2) == 18.0
    assert mass("CO2", 2) == 44.0
    assert mass("Fe2(SO4)3", 2) == 400.0


# ---------- 默认参数 ----------

def test_默认等于mode1():
    assert mass("H2O") == mass("H2O", 1)


# ---------- 错误处理 ----------

def test_非法mode():
    with pytest.raises(ValueError):
        mass("H", 0)
    with pytest.raises(ValueError):
        mass("H", 3)
    with pytest.raises(ValueError):
        mass("H", "1")


def test_非法输入():
    with pytest.raises(ValueError):
        mass("")
    with pytest.raises(ValueError):
        mass(None)
    with pytest.raises(KeyError):
        mass("Xx")
    with pytest.raises(KeyError):
        mass("H2XxO")