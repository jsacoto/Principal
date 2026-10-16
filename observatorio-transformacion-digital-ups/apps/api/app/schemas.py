from __future__ import annotations
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field


class LayerWeights(BaseModel):
    igmd: float = 0.50
    ioc: float = 0.30
    iko: float = 0.20


class DimensionMetric(BaseModel):
    code: str
    name: str
    coverage: float
    maturity: float
    maturity_label: str
    weight: float
    target: float = 5.0
    initiatives: list[str] = []


class ObjectiveMetric(BaseModel):
    code: str
    legacy_code: str | None = None
    name: str
    compliance: float
    score_5: float
    weight: float


class LayerMetric(BaseModel):
    normalized: float
    score_5: float
    label: str
    color: str


class ExecutiveSummary(BaseModel):
    igtd: float
    igmd: LayerMetric
    ioc: LayerMetric
    iko: LayerMetric
    layer_weights: LayerWeights
    dimensions: list[DimensionMetric]
    objectives: list[ObjectiveMetric]
    reference_maturity: dict[str, float]
    heatmap: dict[str, dict[str, int]]
    portfolio_count: int
    activity_count: int
    evidence_count: int
    data_notes: list[str]


class LeaderOut(BaseModel):
    name: str
    email: str | None = None
    role: str
    source: str = "notion"


class ActivityOut(BaseModel):
    id: int
    external_id: str
    parent_external_id: str | None = None
    activity_type: str
    title: str
    progress: float | None = None
    state: str | None = None
    priority: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    observation: str = ""
    evidence_count: int = 0
    notion_url: str | None = None
    assignees: list[LeaderOut] = []


class InitiativeOut(BaseModel):
    id: int
    code: str
    title: str
    objective_code: str | None = None
    objective_name: str | None = None
    scope: str | None = None
    description: str
    reported_progress: float
    verified_progress: float | None = None
    progress_verified_at: datetime | None = None
    progress_verified_by: str | None = None
    progress_verification_note: str = ""
    analytical_progress: float
    status: str
    notion_url: str | None = None
    leaders: list[LeaderOut] = []
    contributions: dict[str, int] = {}
    activities: list[ActivityOut] = []


class WhatIfRequest(BaseModel):
    initiative_code: str
    progress_percent: float = Field(ge=0, le=100)


class WhatIfResponse(BaseModel):
    initiative_code: str
    original_progress_percent: float
    simulated_progress_percent: float
    original_igmd: float
    simulated_igmd: float
    original_igtd: float
    simulated_igtd: float
    delta_igtd: float
    dimension_deltas: dict[str, float]


class GapItem(BaseModel):
    initiative: str
    dimension: str
    contribution: int
    maturity: float
    sensitivity: float


class KRGapItem(BaseModel):
    kr: str
    compliance: float


class GapResponse(BaseModel):
    initiatives: list[GapItem]
    key_results: list[KRGapItem]


class InitiativeVerificationRequest(BaseModel):
    progress_percent: float = Field(ge=0, le=100)
    verified_by: str = Field(min_length=2, max_length=180)
    note: str = Field(min_length=2, max_length=2000)
