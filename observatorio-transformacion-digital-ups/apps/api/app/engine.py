from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

EPSILON = 1e-9


@dataclass(frozen=True)
class DimensionResult:
    code: str
    coverage: float
    maturity: float
    label: str
    denominator: float


@dataclass(frozen=True)
class ObjectiveResult:
    code: str
    compliance: float


@dataclass(frozen=True)
class KPIResult:
    code: str
    normalized: float


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def weighted_sum(values: Sequence[float], weights: Sequence[float]) -> float:
    if len(values) != len(weights):
        raise ValueError("Values and weights must have the same length")
    if not values:
        return 0.0
    if any(w < 0 for w in weights):
        raise ValueError("Weights cannot be negative")
    total = sum(weights)
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"Weights must sum to 1.0, got {total}")
    return sum(v * w for v, w in zip(values, weights))


def maturity_label(maturity: float) -> str:
    # The formal UPS bands are expressed to one decimal (0.0–1.0, 1.1–2.5, ...).
    # Classify on the displayed one-decimal score so boundary semantics remain exact.
    m = round(max(0.0, min(5.0, maturity)), 1)
    if m <= 1.0:
        return "Inicial"
    if m <= 2.5:
        return "Emergente"
    if m <= 3.5:
        return "En desarrollo"
    if m <= 4.5:
        return "Avanzado"
    return "Transformador"


def dimension_coverage(progress_by_initiative: Mapping[str, float], contribution_by_initiative: Mapping[str, int]) -> tuple[float, float]:
    """C_d = sum(E_i * I_i,d) / sum(I_i,d). E_i is [0,1], I is {0,1,2,3}."""
    denominator = 0.0
    numerator = 0.0
    for initiative, contribution in contribution_by_initiative.items():
        if contribution not in (0, 1, 2, 3):
            raise ValueError("Contribution level must be one of 0,1,2,3")
        denominator += contribution
        numerator += clamp01(progress_by_initiative.get(initiative, 0.0)) * contribution
    if denominator <= EPSILON:
        return 0.0, 0.0
    return numerator / denominator, denominator


def maturity_by_dimension(
    dimensions: Iterable[str],
    progress_by_initiative: Mapping[str, float],
    matrix: Mapping[str, Mapping[str, int]],
) -> list[DimensionResult]:
    results: list[DimensionResult] = []
    for dimension in dimensions:
        contribution = {initiative: per_dimension.get(dimension, 0) for initiative, per_dimension in matrix.items()}
        coverage, denominator = dimension_coverage(progress_by_initiative, contribution)
        maturity = 5.0 * coverage
        results.append(DimensionResult(dimension, coverage, maturity, maturity_label(maturity), denominator))
    return results


def igmd(dimension_results: Sequence[DimensionResult], dimension_weights: Sequence[float]) -> float:
    return weighted_sum([r.maturity for r in dimension_results], dimension_weights)


def normalize_kr(current: float, target: float, direction: str) -> float:
    """
    Formal model:
      growth / achievement: min(1, x/m)
      reduction_achievement: min(1, r/r*) where r is the reduction achieved
    The engine also supports lower_is_better for KRs expressed as the raw level to minimize.
    """
    if target <= 0 and direction in {"growth", "reduction_achievement"}:
        raise ValueError("Target must be > 0")
    if direction in {"growth", "reduction_achievement"}:
        return clamp01(current / target)
    if direction == "lower_is_better":
        if current <= 0:
            return 1.0 if target >= 0 else 0.0
        return clamp01(target / current)
    raise ValueError(f"Unsupported KR direction: {direction}")


def objective_compliance(normalized_krs: Sequence[float], kr_weights: Sequence[float]) -> float:
    return weighted_sum([clamp01(v) for v in normalized_krs], kr_weights)


def ioc(objective_scores: Sequence[float], objective_weights: Sequence[float]) -> tuple[float, float]:
    score = weighted_sum([clamp01(v) for v in objective_scores], objective_weights)
    return score, 5.0 * score


def normalize_kpi(current: float, target: float, direction: str) -> float:
    if direction == "higher_is_better":
        if target <= 0:
            raise ValueError("Target must be > 0")
        return clamp01(current / target)
    if direction == "lower_is_better":
        if current <= 0:
            return 1.0
        return clamp01(target / current)
    raise ValueError(f"Unsupported KPI direction: {direction}")


def iko(normalized_kpis: Sequence[float], kpi_weights: Sequence[float]) -> tuple[float, float]:
    score = weighted_sum([clamp01(v) for v in normalized_kpis], kpi_weights)
    return score, 5.0 * score


def igtd(igmd_value: float, ioc5_value: float, iko5_value: float, layer_weights: Sequence[float] = (0.5, 0.3, 0.2)) -> float:
    return weighted_sum([igmd_value, ioc5_value, iko5_value], list(layer_weights))


def sensitivity(contribution_level: int, dimension_denominator: float) -> float:
    """Delta M_d / Delta E_i = 5 * I_i,d / sum_i(I_i,d)."""
    if contribution_level not in (0, 1, 2, 3):
        raise ValueError("Contribution level must be one of 0,1,2,3")
    if dimension_denominator <= EPSILON:
        return 0.0
    return 5.0 * contribution_level / dimension_denominator


def prioritize_gaps(
    dimension_results: Sequence[DimensionResult],
    matrix: Mapping[str, Mapping[str, int]],
    kr_compliance: Mapping[str, float],
    maturity_threshold: float = 3.0,
    kr_threshold: float = 0.60,
) -> dict[str, list[dict]]:
    weak_dimensions = {r.code: r for r in dimension_results if r.maturity < maturity_threshold}
    initiatives: list[dict] = []
    for initiative, contributions in matrix.items():
        for dimension, level in contributions.items():
            if dimension in weak_dimensions and level in (2, 3):
                r = weak_dimensions[dimension]
                initiatives.append({
                    "initiative": initiative,
                    "dimension": dimension,
                    "contribution": level,
                    "maturity": r.maturity,
                    "sensitivity": sensitivity(level, r.denominator),
                })
    initiatives.sort(key=lambda item: (-item["sensitivity"], item["maturity"], item["initiative"]))
    weak_krs = [
        {"kr": code, "compliance": clamp01(value)}
        for code, value in kr_compliance.items()
        if clamp01(value) < kr_threshold
    ]
    weak_krs.sort(key=lambda item: item["compliance"])
    return {"initiatives": initiatives, "key_results": weak_krs}


def apply_what_if(progress_by_initiative: Mapping[str, float], initiative_code: str, new_progress: float) -> dict[str, float]:
    updated = dict(progress_by_initiative)
    updated[initiative_code] = clamp01(new_progress)
    return updated
