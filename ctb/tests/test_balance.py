import pytest

from ctb import balance


def test_简单燃烧():
    assert balance("H2+O2=H2O") == "2H2+O2=2H2O"


def test_炼铁():
    assert balance("Fe2O3+CO=Fe+CO2") == "Fe2O3+3CO=2Fe+3CO2"


def test_置换反应():
    assert balance("Cu+AgNO3=Cu(NO3)2+Ag") == "Cu+2AgNO3=Cu(NO3)2+2Ag"


def test_带括号():
    assert balance("Al+H2SO4=Al2(SO4)3+H2") == "2Al+3H2SO4=Al2(SO4)3+3H2"


def test_箭头():
    assert balance("H2+O2->H2O") == "2H2+O2=2H2O"


def test_离子中和():
    assert balance("H^1++OH^1-=H2O") == "H^1++OH^1-=H2O"


def test_离子碳酸根():
    assert balance("CO3^2-+H^1+=HCO3^1-") == "CO3^2-+H^1+=HCO3^1-"


def test_离子需要系数():
    assert balance("H^1++CO3^2-=H2O+CO2") == "2H^1++CO3^2-=H2O+CO2"


def test_格式错误():
    with pytest.raises(ValueError):
        balance("H2+O2")


def test_无法配平():
    with pytest.raises(ValueError):
        balance("H2=O2")