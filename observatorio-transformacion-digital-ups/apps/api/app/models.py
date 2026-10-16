from __future__ import annotations
from datetime import UTC, date, datetime
from enum import Enum
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Direction(str, Enum):
    GROWTH = "growth"
    REDUCTION_ACHIEVEMENT = "reduction_achievement"
    LOWER_IS_BETTER = "lower_is_better"
    HIGHER_IS_BETTER = "higher_is_better"


class Dimension(Base):
    __tablename__ = "dimensions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    weight: Mapped[float] = mapped_column(Float, default=0.20)
    target_maturity: Mapped[float] = mapped_column(Float, default=5.0)
    color: Mapped[str] = mapped_column(String(16), default="#00A3FF")


class Objective(Base):
    __tablename__ = "objectives"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    legacy_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    name: Mapped[str] = mapped_column(String(220))
    description: Mapped[str] = mapped_column(Text, default="")
    weight: Mapped[float] = mapped_column(Float, default=0.20)

    key_results: Mapped[list[KeyResult]] = relationship(back_populates="objective", cascade="all, delete-orphan")


class Initiative(Base):
    __tablename__ = "initiatives"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    objective_id: Mapped[int | None] = mapped_column(ForeignKey("objectives.id"), nullable=True)
    scope: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    reported_progress: Mapped[float] = mapped_column(Float, default=0.0)
    verified_progress: Mapped[float | None] = mapped_column(Float, nullable=True)
    progress_verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    progress_verified_by: Mapped[str | None] = mapped_column(String(180), nullable=True)
    progress_verification_note: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(60), default="En desarrollo")
    notion_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_origin: Mapped[str] = mapped_column(String(40), default="notion_snapshot")
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_reference_16: Mapped[bool] = mapped_column(Boolean, default=False)

    objective: Mapped[Objective | None] = relationship()
    leaders: Mapped[list[InitiativeLeader]] = relationship(back_populates="initiative", cascade="all, delete-orphan")
    activities: Mapped[list[Activity]] = relationship(back_populates="initiative", cascade="all, delete-orphan")
    contributions: Mapped[list[InitiativeDimension]] = relationship(back_populates="initiative", cascade="all, delete-orphan")

    @property
    def analytical_progress(self) -> float:
        value = self.verified_progress if self.verified_progress is not None else self.reported_progress
        return max(0.0, min(100.0, value)) / 100.0


class InitiativeLeader(Base):
    __tablename__ = "initiative_leaders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    initiative_id: Mapped[int] = mapped_column(ForeignKey("initiatives.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    email: Mapped[str | None] = mapped_column(String(180), nullable=True)
    notion_user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(60), default="Líder")

    initiative: Mapped[Initiative] = relationship(back_populates="leaders")


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = (UniqueConstraint("initiative_id", "external_id", name="uq_activity_external"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    initiative_id: Mapped[int] = mapped_column(ForeignKey("initiatives.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[str] = mapped_column(String(40))
    parent_external_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    activity_type: Mapped[str] = mapped_column(String(24), default="activity")
    title: Mapped[str] = mapped_column(Text)
    progress: Mapped[float | None] = mapped_column(Float, nullable=True)
    state: Mapped[str | None] = mapped_column(String(60), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(30), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    observation: Mapped[str] = mapped_column(Text, default="")
    notion_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    initiative: Mapped[Initiative] = relationship(back_populates="activities")
    assignees: Mapped[list[ActivityAssignee]] = relationship(back_populates="activity", cascade="all, delete-orphan")
    evidence: Mapped[list[Evidence]] = relationship(back_populates="activity", cascade="all, delete-orphan")


class ActivityAssignee(Base):
    __tablename__ = "activity_assignees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id", ondelete="CASCADE"), index=True)
    name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    email: Mapped[str | None] = mapped_column(String(180), nullable=True)
    notion_user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(40), default="notion")

    activity: Mapped[Activity] = relationship(back_populates="assignees")


class Evidence(Base):
    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(240), default="Evidencia")
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    kind: Mapped[str] = mapped_column(String(40), default="file")
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    activity: Mapped[Activity] = relationship(back_populates="evidence")


class InitiativeDimension(Base):
    __tablename__ = "initiative_dimensions"
    __table_args__ = (UniqueConstraint("initiative_id", "dimension_id", name="uq_initiative_dimension"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    initiative_id: Mapped[int] = mapped_column(ForeignKey("initiatives.id", ondelete="CASCADE"), index=True)
    dimension_id: Mapped[int] = mapped_column(ForeignKey("dimensions.id", ondelete="CASCADE"), index=True)
    contribution_level: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(60), default="provisional_mapping")
    validated: Mapped[bool] = mapped_column(Boolean, default=False)
    note: Mapped[str] = mapped_column(Text, default="")

    initiative: Mapped[Initiative] = relationship(back_populates="contributions")
    dimension: Mapped[Dimension] = relationship()


class KeyResult(Base):
    __tablename__ = "key_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    objective_id: Mapped[int] = mapped_column(ForeignKey("objectives.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(24), unique=True)
    title: Mapped[str] = mapped_column(Text)
    direction: Mapped[str] = mapped_column(String(40), default=Direction.GROWTH.value)
    current_value: Mapped[float] = mapped_column(Float, default=0.0)
    target_value: Mapped[float] = mapped_column(Float, default=1.0)
    baseline_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(40), default="ratio")
    weight: Mapped[float] = mapped_column(Float, default=0.5)
    source: Mapped[str] = mapped_column(String(50), default="demo_seed")

    objective: Mapped[Objective] = relationship(back_populates="key_results")


class KPI(Base):
    __tablename__ = "kpis"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(24), unique=True)
    title: Mapped[str] = mapped_column(Text)
    dimension_id: Mapped[int | None] = mapped_column(ForeignKey("dimensions.id"), nullable=True, index=True)
    objective_id: Mapped[int | None] = mapped_column(ForeignKey("objectives.id"), nullable=True, index=True)
    direction: Mapped[str] = mapped_column(String(40), default=Direction.HIGHER_IS_BETTER.value)
    current_value: Mapped[float] = mapped_column(Float, default=0.0)
    target_value: Mapped[float] = mapped_column(Float, default=1.0)
    unit: Mapped[str] = mapped_column(String(40), default="ratio")
    weight: Mapped[float] = mapped_column(Float, default=0.1)
    source: Mapped[str] = mapped_column(String(50), default="demo_seed")

    dimension: Mapped[Dimension | None] = relationship()
    objective: Mapped[Objective | None] = relationship()


class TraceabilityRecord(Base):
    __tablename__ = "traceability_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_type: Mapped[str] = mapped_column(String(40), index=True)
    from_key: Mapped[str] = mapped_column(String(100), index=True)
    to_type: Mapped[str] = mapped_column(String(40), index=True)
    to_key: Mapped[str] = mapped_column(String(100), index=True)
    relation: Mapped[str] = mapped_column(String(80), default="contributes_to")
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(60), default="model")
    note: Mapped[str] = mapped_column(Text, default="")


class IndexLog(Base):
    __tablename__ = "index_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, index=True)
    igmd: Mapped[float] = mapped_column(Float)
    ioc: Mapped[float] = mapped_column(Float)
    ioc5: Mapped[float] = mapped_column(Float)
    iko: Mapped[float] = mapped_column(Float)
    iko5: Mapped[float] = mapped_column(Float)
    igtd: Mapped[float] = mapped_column(Float)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    source: Mapped[str] = mapped_column(String(50), default="computed")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(180))
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(32), default="responsible", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, onupdate=utcnow_naive)

    permissions: Mapped[list["UserInitiativePermission"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    sessions: Mapped[list["AuthSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserInitiativePermission(Base):
    __tablename__ = "user_initiative_permissions"
    __table_args__ = (UniqueConstraint("user_id", "initiative_id", name="uq_user_initiative_permission"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    initiative_id: Mapped[int] = mapped_column(ForeignKey("initiatives.id", ondelete="CASCADE"), index=True)
    can_edit: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive)

    user: Mapped[User] = relationship(back_populates="permissions")
    initiative: Mapped[Initiative] = relationship()


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship(back_populates="sessions")


class ActivityProgressLog(Base):
    __tablename__ = "activity_progress_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id", ondelete="CASCADE"), index=True)
    old_progress: Mapped[float | None] = mapped_column(Float, nullable=True)
    new_progress: Mapped[float | None] = mapped_column(Float, nullable=True)
    old_state: Mapped[str | None] = mapped_column(String(60), nullable=True)
    new_state: Mapped[str | None] = mapped_column(String(60), nullable=True)
    justification: Mapped[str] = mapped_column(Text)
    changed_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, index=True)

    activity: Mapped[Activity] = relationship()
    changed_by: Mapped[User] = relationship()


class EvidenceUpload(Base):
    __tablename__ = "evidence_uploads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id", ondelete="CASCADE"), index=True)
    original_name: Mapped[str] = mapped_column(String(300))
    stored_name: Mapped[str] = mapped_column(String(120), unique=True)
    content_type: Mapped[str] = mapped_column(String(160), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text, default="")
    uploaded_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, index=True)

    activity: Mapped[Activity] = relationship()
    uploaded_by: Mapped[User] = relationship()
