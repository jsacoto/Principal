from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    Activity, ActivityAssignee, Dimension, Evidence, Initiative, InitiativeDimension,
    InitiativeLeader, KPI, KeyResult, Objective, TraceabilityRecord
)
from .data.portfolio_seed import (
    ACTIVITIES, ACTIVITY_RESPONSIBLE_IDS, DIMENSIONS, INITIATIVES, KEY_RESULTS, KPIS, OBJECTIVES,
    OBJECTIVE_DIMENSION_HEATMAP, PROVISIONAL_CONTRIBUTIONS, SNAPSHOT_DATE, USER_DIRECTORY
)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _verified_progress(activities: list[dict]) -> float | None:
    values = [float(a["progress"]) for a in activities if a.get("activity_type") == "activity" and a.get("progress") is not None]
    return round(sum(values) / len(values), 2) if values else None


def seed_database(db: Session, force: bool = False) -> None:
    existing = db.scalar(select(Initiative).limit(1))
    if existing and not force:
        return

    if force:
        for model in [TraceabilityRecord, KPI, KeyResult, InitiativeDimension, ActivityAssignee, Evidence, Activity, InitiativeLeader, Initiative, Objective, Dimension]:
            db.query(model).delete()
        db.commit()

    dims: dict[str, Dimension] = {}
    for item in DIMENSIONS:
        obj = Dimension(**item, target_maturity=5.0)
        db.add(obj); dims[item["code"]] = obj

    objs: dict[str, Objective] = {}
    for item in OBJECTIVES:
        obj = Objective(**item)
        db.add(obj); objs[item["code"]] = obj
    db.flush()

    initiatives: dict[str, Initiative] = {}
    for item in INITIATIVES:
        activity_rows = ACTIVITIES.get(item["code"], [])
        initiative = Initiative(
            code=item["code"], title=item["title"], objective_id=objs[item["objective"]].id,
            scope=item.get("scope"), description=item["description"],
            reported_progress=item["progress"], verified_progress=_verified_progress(activity_rows),
            status=item["status"], notion_url=item["notion_url"], data_origin="notion_snapshot",
            last_synced_at=datetime.fromisoformat(SNAPSHOT_DATE), is_reference_16=item["reference16"],
        )
        db.add(initiative); db.flush(); initiatives[item["code"]] = initiative
        db.add(TraceabilityRecord(
            from_type="initiative", from_key=item["code"], to_type="objective", to_key=item["objective"],
            relation="aligned_to", source="notion_legacy_objective"
        ))
        for leader in item["leaders"]:
            db.add(InitiativeLeader(
                initiative_id=initiative.id, name=leader["name"], email=leader.get("email"),
                notion_user_id=leader.get("notion_user_id"), role=leader.get("role", "Líder")
            ))

        for a in activity_rows:
            activity = Activity(
                initiative_id=initiative.id, external_id=a["external_id"],
                parent_external_id=a.get("parent_external_id"), activity_type=a.get("activity_type", "activity"),
                title=a["title"], progress=a.get("progress"), state=a.get("state"), priority=a.get("priority"),
                start_date=parse_date(a.get("start_date")), end_date=parse_date(a.get("end_date")),
                observation=a.get("observation", ""), evidence_count=a.get("evidence_count", 0),
                raw_data={"snapshot_source": "Notion", "snapshot_date": SNAPSHOT_DATE},
            )
            db.add(activity); db.flush()
            db.add(TraceabilityRecord(
                from_type="initiative", from_key=item["code"], to_type="activity",
                to_key=f"{item['code']}:{a['external_id']}", relation="contains", source="notion_snapshot"
            ))
            responsible_ids = ACTIVITY_RESPONSIBLE_IDS.get(item["code"], {}).get(a["external_id"], [])
            if responsible_ids:
                for user_id in responsible_ids:
                    resolved = USER_DIRECTORY.get(user_id)
                    name, email = resolved if resolved else (f"Notion user · {user_id[-8:]}", None)
                    db.add(ActivityAssignee(
                        activity_id=activity.id, name=name, email=email,
                        notion_user_id=user_id, source="notion_activity"
                    ))
            else:
                for leader in item["leaders"]:
                    db.add(ActivityAssignee(
                        activity_id=activity.id, name=leader["name"], email=leader.get("email"),
                        notion_user_id=leader.get("notion_user_id"), source="initiative_leader_fallback"
                    ))
            if a.get("evidence_count", 0):
                for idx in range(a["evidence_count"]):
                    evidence_key = f"{item['code']}:{a['external_id']}:evidence:{idx + 1}"
                    db.add(Evidence(
                        activity_id=activity.id,
                        label=f"Evidencia registrada en Notion {idx + 1}",
                        url=None,
                        kind="notion_file_reference",
                        verified=False,
                    ))
                    db.add(TraceabilityRecord(
                        from_type="activity", from_key=f"{item['code']}:{a['external_id']}",
                        to_type="evidence", to_key=evidence_key, relation="supported_by", source="notion_snapshot"
                    ))

    db.flush()
    for code, levels in PROVISIONAL_CONTRIBUTIONS.items():
        for dim_code, level in levels.items():
            db.add(InitiativeDimension(
                initiative_id=initiatives[code].id, dimension_id=dims[dim_code].id,
                contribution_level=level, source="provisional_objective_mapping", validated=False,
                note="Matriz inicial editable; debe validarse contra la matriz institucional de contribución I(i,d)."
            ))
            if level > 0:
                db.add(TraceabilityRecord(
                    from_type="initiative", from_key=code, to_type="dimension", to_key=dim_code,
                    relation="contributes_to", weight=float(level), source="provisional_objective_mapping"
                ))

    for code, objective, title, current, target, direction, weight, unit in KEY_RESULTS:
        db.add(KeyResult(
            objective_id=objs[objective].id, code=code, title=title, direction=direction,
            current_value=current, target_value=target, weight=weight, unit=unit, source="demo_seed"
        ))
        db.add(TraceabilityRecord(
            from_type="objective", from_key=objective, to_type="key_result", to_key=code,
            relation="measured_by", weight=weight, source="demo_seed"
        ))

    kr_objective = {code: objective for code, objective, *_ in KEY_RESULTS}
    for code, dimension, title, current, target, direction, weight, unit in KPIS:
        objective_code = f"O{dimension[1:]}"
        db.add(KPI(
            code=code, title=title, dimension_id=dims[dimension].id, objective_id=objs[objective_code].id, direction=direction,
            current_value=current, target_value=target, weight=weight, unit=unit, source="demo_seed"
        ))
        db.add(TraceabilityRecord(
            from_type="dimension", from_key=dimension, to_type="kpi", to_key=code,
            relation="measured_by", weight=weight, source="demo_seed"
        ))
        for kr_code, kr_obj in kr_objective.items():
            if kr_obj == objective_code:
                db.add(TraceabilityRecord(
                    from_type="key_result", from_key=kr_code, to_type="kpi", to_key=code,
                    relation="operationalized_by", source="demo_seed"
                ))

    for objective, dim_levels in OBJECTIVE_DIMENSION_HEATMAP.items():
        for dimension, level in dim_levels.items():
            if level > 0:
                db.add(TraceabilityRecord(
                    from_type="objective", from_key=objective, to_type="dimension", to_key=dimension,
                    relation="strategic_intensity", weight=float(level), source="model_seed"
                ))
                db.add(TraceabilityRecord(
                    from_type="dimension", from_key=dimension, to_type="objective", to_key=objective,
                    relation="supports_objective", weight=float(level), source="model_seed"
                ))

    db.commit()
