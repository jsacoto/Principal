from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import get_settings
from ..data.portfolio_seed import MODEL16_GROUPS, OBJECTIVE_DIMENSION_HEATMAP, REFERENCE_MATURITY
from ..engine import (
    apply_what_if, igmd, igtd, iko, ioc, maturity_by_dimension,
    normalize_kpi, normalize_kr, objective_compliance, prioritize_gaps
)
from ..models import Dimension, Initiative, InitiativeDimension, KPI, Objective


def _load_initiatives(db: Session, scope: str = "all") -> list[Initiative]:
    stmt = select(Initiative).options(selectinload(Initiative.contributions).selectinload(InitiativeDimension.dimension))
    if scope in {"institutional16", "reference16"}:
        child_codes = [code for children in MODEL16_GROUPS.values() for code in children]
        stmt = stmt.where(Initiative.code.in_(child_codes))
    return list(db.scalars(stmt.order_by(Initiative.id)).all())


def _portfolio_inputs(db: Session, scope: str = "all"):
    initiatives = _load_initiatives(db, scope)
    dimensions = list(db.scalars(select(Dimension).order_by(Dimension.code)).all())

    if scope in {"institutional16", "reference16"}:
        by_code = {i.code: i for i in initiatives}
        progress: dict[str, float] = {}
        matrix: dict[str, dict[str, int]] = {}
        for group_code, child_codes in MODEL16_GROUPS.items():
            children = [by_code[c] for c in child_codes if c in by_code]
            if not children:
                continue
            progress[group_code] = sum(i.analytical_progress for i in children) / len(children)
            matrix[group_code] = {}
            for d in dimensions:
                levels = [
                    next((c.contribution_level for c in i.contributions if c.dimension.code == d.code), 0)
                    for i in children
                ]
                matrix[group_code][d.code] = max(levels) if levels else 0
        return initiatives, dimensions, progress, matrix, len(progress)

    progress = {i.code: i.analytical_progress for i in initiatives}
    matrix: dict[str, dict[str, int]] = {}
    for initiative in initiatives:
        matrix[initiative.code] = {c.dimension.code: c.contribution_level for c in initiative.contributions}
    return initiatives, dimensions, progress, matrix, len(initiatives)


def compute_layers(db: Session, scope: str = "all", progress_override: dict[str, float] | None = None) -> dict:
    settings = get_settings()
    initiatives, dimensions, progress, matrix, portfolio_count = _portfolio_inputs(db, scope)
    if progress_override:
        progress.update(progress_override)

    dimension_results = maturity_by_dimension([d.code for d in dimensions], progress, matrix)
    dim_weights = [d.weight for d in dimensions]
    igmd_value = igmd(dimension_results, dim_weights)

    objectives = list(db.scalars(select(Objective).options(selectinload(Objective.key_results)).order_by(Objective.code)).all())
    objective_scores: list[float] = []
    objective_details: list[dict] = []
    kr_scores: dict[str, float] = {}
    for objective in objectives:
        krs = sorted(objective.key_results, key=lambda kr: kr.code)
        if not krs:
            score = 0.0
        else:
            normalized = [normalize_kr(kr.current_value, kr.target_value, kr.direction) for kr in krs]
            for kr, value in zip(krs, normalized):
                kr_scores[kr.code] = value
            weights = [kr.weight for kr in krs]
            total = sum(weights)
            if total <= 0:
                weights = [1 / len(krs)] * len(krs)
            elif abs(total - 1.0) > 1e-6:
                weights = [w / total for w in weights]
            score = objective_compliance(normalized, weights)
        objective_scores.append(score)
        objective_details.append({
            "code": objective.code, "legacy_code": objective.legacy_code, "name": objective.name,
            "compliance": score, "score_5": 5 * score, "weight": objective.weight,
        })
    obj_weights = [o.weight for o in objectives]
    total_obj = sum(obj_weights)
    if abs(total_obj - 1.0) > 1e-6:
        obj_weights = [w / total_obj for w in obj_weights]
    ioc_value, ioc5_value = ioc(objective_scores, obj_weights)

    kpis = list(db.scalars(select(KPI).order_by(KPI.code)).all())
    normalized_kpis = [normalize_kpi(k.current_value, k.target_value, k.direction) for k in kpis]
    kpi_weights = [k.weight for k in kpis]
    total_kpi = sum(kpi_weights)
    if kpis and abs(total_kpi - 1.0) > 1e-6:
        kpi_weights = [w / total_kpi for w in kpi_weights]
    iko_value, iko5_value = iko(normalized_kpis, kpi_weights) if kpis else (0.0, 0.0)

    layer_weights = settings.layer_weights
    igtd_value = igtd(igmd_value, ioc5_value, iko5_value, layer_weights)

    dimension_payload = []
    for d, r in zip(dimensions, dimension_results):
        associated = sorted([i for i, levels in matrix.items() if levels.get(d.code, 0) > 0])
        dimension_payload.append({
            "code": d.code, "name": d.name, "coverage": r.coverage, "maturity": r.maturity,
            "maturity_label": r.label, "weight": d.weight, "target": d.target_maturity,
            "initiatives": associated,
        })

    return {
        "igtd": igtd_value,
        "igmd": igmd_value,
        "ioc": ioc_value,
        "ioc5": ioc5_value,
        "iko": iko_value,
        "iko5": iko5_value,
        "dimension_results": dimension_results,
        "dimensions": dimension_payload,
        "objectives": objective_details,
        "kr_scores": kr_scores,
        "progress": progress,
        "matrix": matrix,
        "portfolio_count": portfolio_count,
        "layer_weights": layer_weights,
    }


def executive_summary(db: Session, scope: str = "all") -> dict:
    layers = compute_layers(db, scope)
    from ..models import Activity, Evidence
    if scope in {"institutional16", "reference16"}:
        child_codes = [code for children in MODEL16_GROUPS.values() for code in children]
        initiative_ids = list(db.scalars(select(Initiative.id).where(Initiative.code.in_(child_codes))).all())
        activity_count = db.query(Activity).filter(Activity.initiative_id.in_(initiative_ids)).count() if initiative_ids else 0
        evidence_count = (
            db.query(Evidence)
            .join(Activity, Evidence.activity_id == Activity.id)
            .filter(Activity.initiative_id.in_(initiative_ids))
            .count()
            if initiative_ids else 0
        )
    else:
        activity_count = db.query(Activity).count()
        evidence_count = db.query(Evidence).count()
    return {
        "igtd": layers["igtd"],
        "igmd": {"normalized": layers["igmd"] / 5.0, "score_5": layers["igmd"], "label":"Madurez Estructural", "color":"#00A3FF"},
        "ioc": {"normalized": layers["ioc"], "score_5": layers["ioc5"], "label":"Cumplimiento Estratégico", "color":"#8A2BE2"},
        "iko": {"normalized": layers["iko"], "score_5": layers["iko5"], "label":"Desempeño Operativo", "color":"#FF9500"},
        "layer_weights": {"igmd":layers["layer_weights"][0],"ioc":layers["layer_weights"][1],"iko":layers["layer_weights"][2]},
        "dimensions": layers["dimensions"],
        "objectives": layers["objectives"],
        "reference_maturity": REFERENCE_MATURITY,
        "heatmap": OBJECTIVE_DIMENSION_HEATMAP,
        "portfolio_count": layers["portfolio_count"],
        "activity_count": activity_count,
        "evidence_count": evidence_count,
        "data_notes": [
            "Las iniciativas y actividades provienen de una instantánea de la cartera Notion al 2026-10-16.",
            "La matriz I(i,d) incluida es provisional y editable; los valores no validados se identifican como tales.",
            "Los KRs y KPIs incluidos son datos mock de arranque para demostrar el motor; no deben interpretarse como mediciones oficiales UPS.",
            "La vista Modelo 16 agrega 1.a/1.b, 3.a/3.b y 8.a/8.b bajo sus números institucionales para conservar exactamente 16 iniciativas conceptuales.",
        ],
    }


def what_if(db: Session, initiative_code: str, progress_percent: float, scope: str = "all") -> dict:
    base = compute_layers(db, scope)
    effective_code = initiative_code
    if scope in {"institutional16", "reference16"} and initiative_code not in base["progress"]:
        effective_code = initiative_code.split(".", 1)[0]
    if effective_code not in base["progress"]:
        raise KeyError(initiative_code)
    simulated_progress = apply_what_if(base["progress"], effective_code, progress_percent / 100.0)
    sim = compute_layers(db, scope, {effective_code: simulated_progress[effective_code]})
    base_dims = {d["code"]: d["maturity"] for d in base["dimensions"]}
    sim_dims = {d["code"]: d["maturity"] for d in sim["dimensions"]}
    return {
        "initiative_code": initiative_code,
        "original_progress_percent": base["progress"][effective_code] * 100,
        "simulated_progress_percent": progress_percent,
        "original_igmd": base["igmd"],
        "simulated_igmd": sim["igmd"],
        "original_igtd": base["igtd"],
        "simulated_igtd": sim["igtd"],
        "delta_igtd": sim["igtd"] - base["igtd"],
        "dimension_deltas": {code: sim_dims[code] - base_dims[code] for code in base_dims},
    }


def gaps(db: Session, scope: str = "all") -> dict:
    layers = compute_layers(db, scope)
    return prioritize_gaps(layers["dimension_results"], layers["matrix"], layers["kr_scores"])


def data_quality(db: Session) -> list[dict]:
    from ..models import Activity
    issues: list[dict] = []
    initiatives = list(db.scalars(select(Initiative).options(selectinload(Initiative.activities))).all())
    for i in initiatives:
        for a in i.activities:
            if a.start_date and a.end_date and a.end_date < a.start_date:
                issues.append({"severity":"critical","initiative":i.code,"activity":a.external_id,"type":"invalid_date_range","message":"Fecha fin anterior a fecha inicio."})
            if a.progress is not None and a.progress >= 100 and (a.state or "").lower() in {"en desarrollo","iniciado","por iniciar","no iniciado"}:
                issues.append({"severity":"high","initiative":i.code,"activity":a.external_id,"type":"progress_state_mismatch","message":f"Avance 100% con estado '{a.state}'."})
            if a.title.strip().lower() in {"hola","test","prueba"}:
                issues.append({"severity":"high","initiative":i.code,"activity":a.external_id,"type":"test_row","message":"Fila de prueba o basura detectada."})
        if i.code == "24" and i.reported_progress == 0 and any((a.state or "").lower() == "completo" for a in i.activities):
            issues.append({"severity":"critical","initiative":i.code,"activity":None,"type":"initiative_progress_mismatch","message":"El título reporta 0%, pero las actividades visibles están marcadas como completas."})
    return issues
