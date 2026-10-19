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


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=10, max_length=200)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=10, max_length=200)
    new_password: str = Field(min_length=10, max_length=200)


class ActivityUpdateRequest(BaseModel):
    progress: float | None = Field(default=None, ge=0, le=100)
    state: str | None = Field(default=None, max_length=60)
    priority: str | None = Field(default=None, max_length=30)
    start_date: date | None = None
    end_date: date | None = None
    observation: str | None = Field(default=None, max_length=4000)
    justification: str = Field(min_length=3, max_length=4000)


class AdminUserCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=10, max_length=200)
    role: Literal["admin", "responsible"] = "responsible"
    initiative_codes: list[str] = []


class AdminUserUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    is_active: bool | None = None
    role: Literal["admin", "responsible"] | None = None
    initiative_codes: list[str] | None = None


class InitiativeActivityCreate(BaseModel):
    external_id: str = Field(min_length=1, max_length=40)
    title: str = Field(min_length=3, max_length=2000)
    progress: float | None = Field(default=0, ge=0, le=100)
    state: str = Field(default="Por Iniciar", max_length=60)
    priority: str = Field(default="Media", max_length=30)
    start_date: date | None = None
    end_date: date | None = None
    observation: str = Field(default="", max_length=4000)
    in_field: str = Field(default="", max_length=1000)
    responsible_name: str = Field(default="", max_length=180)
    responsible_email: str = Field(default="", max_length=320)


class InitiativeCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=20, pattern=r"^[A-Za-z0-9._-]+$")
    objective_code: Literal["O1", "O2", "O3", "O4", "O5"]
    scope: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10, max_length=5000)
    leader_name: str = Field(min_length=2, max_length=180)
    leader_email: str = Field(default="", max_length=320)
    status: str = Field(default="Por Iniciar", max_length=60)
    contributions: dict[str, int]
    activities: list[InitiativeActivityCreate] = []


class ScheduleForecastResponse(BaseModel):
    model: str
    generated_on: date
    target_date: date
    scope: str
    assumption: str
    current: dict
    projected: dict
    delta: dict
    schedule_coverage: dict
    initiatives: list[dict]
    limitations: list[str]
