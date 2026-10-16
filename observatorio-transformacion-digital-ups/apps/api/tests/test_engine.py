import pytest

from app.engine import (
    dimension_coverage, maturity_by_dimension, igmd, normalize_kr,
    objective_compliance, ioc, normalize_kpi, iko, igtd, sensitivity,
    prioritize_gaps
)


def test_dimension_formula_exact():
    progress = {"A": 1.0, "B": 0.5, "C": 0.0}
    levels = {"A": 3, "B": 2, "C": 1}
    coverage, denom = dimension_coverage(progress, levels)
    assert denom == 6
    assert coverage == pytest.approx((3 + 1 + 0) / 6)
    assert 5 * coverage == pytest.approx(3.3333333333)


def test_igmd_weighted():
    results = maturity_by_dimension(
        ["D1", "D2"],
        {"A": 1.0, "B": 0.5},
        {"A": {"D1": 3, "D2": 0}, "B": {"D1": 0, "D2": 3}},
    )
    assert igmd(results, [0.5, 0.5]) == pytest.approx(3.75)


def test_okr_kpi_and_global_index():
    kr1 = normalize_kr(80, 100, "growth")
    kr2 = normalize_kr(30, 50, "reduction_achievement")
    obj = objective_compliance([kr1, kr2], [0.5, 0.5])
    ioc_value, ioc5_value = ioc([obj, 1.0], [0.5, 0.5])
    assert kr1 == pytest.approx(0.8)
    assert kr2 == pytest.approx(0.6)
    assert obj == pytest.approx(0.7)
    assert ioc_value == pytest.approx(0.85)
    assert ioc5_value == pytest.approx(4.25)

    n1 = normalize_kpi(80, 100, "higher_is_better")
    n2 = normalize_kpi(1.2, 1.0, "lower_is_better")
    iko_value, iko5_value = iko([n1, n2], [0.5, 0.5])
    assert n1 == pytest.approx(0.8)
    assert n2 == pytest.approx(1.0 / 1.2)
    assert iko5_value == pytest.approx(5 * iko_value)
    value = igtd(4.0, ioc5_value, iko5_value, [0.5, 0.3, 0.2])
    assert 0 <= value <= 5


def test_sensitivity_and_gap_rule():
    results = maturity_by_dimension(
        ["D1"],
        {"A": 0.2, "B": 0.3},
        {"A": {"D1": 3}, "B": {"D1": 2}},
    )
    gaps = prioritize_gaps(results, {"A": {"D1": 3}, "B": {"D1": 2}}, {"KR1": 0.59, "KR2": 0.6})
    assert len(gaps["initiatives"]) == 2
    assert gaps["initiatives"][0]["initiative"] == "A"
    assert gaps["key_results"] == [{"kr": "KR1", "compliance": 0.59}]
    assert sensitivity(3, 5) == pytest.approx(3.0)
