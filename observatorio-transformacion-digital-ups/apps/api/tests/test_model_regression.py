import pytest

from app.engine import (
    dimension_coverage,
    igmd,
    igtd,
    iko,
    ioc,
    maturity_by_dimension,
    maturity_label,
    normalize_kpi,
    normalize_kr,
    sensitivity,
)


def test_ups_maturity_equations_reference_case():
    """Locks the formal UPS C_d -> M_d -> IGMD equations against regression."""
    progress = {"I1": 0.80, "I2": 0.50, "I3": 0.25}
    matrix = {
        "I1": {"D1": 3, "D2": 1},
        "I2": {"D1": 2, "D2": 2},
        "I3": {"D1": 1, "D2": 3},
    }

    d1_coverage, d1_den = dimension_coverage(progress, {k: v["D1"] for k, v in matrix.items()})
    assert d1_den == 6
    assert d1_coverage == pytest.approx((0.80 * 3 + 0.50 * 2 + 0.25 * 1) / 6)

    dims = maturity_by_dimension(["D1", "D2"], progress, matrix)
    assert dims[0].maturity == pytest.approx(5 * d1_coverage)
    assert igmd(dims, [0.5, 0.5]) == pytest.approx((dims[0].maturity + dims[1].maturity) / 2)


def test_ups_okr_kpi_and_igtd_contract():
    """Locks IOC, IKO and the calibrated lambda=(0.50,0.30,0.20) combination."""
    kr_scores = [normalize_kr(75, 100, "growth"), normalize_kr(20, 25, "reduction_achievement")]
    objective_score = sum(kr_scores) / 2
    ioc_value, ioc5 = ioc([objective_score, 1.0], [0.6, 0.4])
    assert ioc_value == pytest.approx(0.6 * objective_score + 0.4)
    assert ioc5 == pytest.approx(5 * ioc_value)

    kpi_scores = [normalize_kpi(90, 100, "higher_is_better"), normalize_kpi(8, 10, "lower_is_better")]
    iko_value, iko5 = iko(kpi_scores, [0.5, 0.5])
    assert iko_value == pytest.approx(0.95)
    assert iko5 == pytest.approx(4.75)

    value = igtd(3.4, ioc5, iko5, [0.50, 0.30, 0.20])
    assert value == pytest.approx(0.50 * 3.4 + 0.30 * ioc5 + 0.20 * iko5)


def test_ups_maturity_band_boundaries_are_stable():
    assert maturity_label(1.0) == "Inicial"
    assert maturity_label(1.1) == "Emergente"
    assert maturity_label(2.5) == "Emergente"
    assert maturity_label(2.6) == "En desarrollo"
    assert maturity_label(3.5) == "En desarrollo"
    assert maturity_label(3.6) == "Avanzado"
    assert maturity_label(4.5) == "Avanzado"
    assert maturity_label(4.6) == "Transformador"
    assert maturity_label(5.0) == "Transformador"


def test_ups_sensitivity_rule_is_unchanged():
    assert sensitivity(0, 10) == pytest.approx(0.0)
    assert sensitivity(1, 10) == pytest.approx(0.5)
    assert sensitivity(2, 10) == pytest.approx(1.0)
    assert sensitivity(3, 10) == pytest.approx(1.5)
