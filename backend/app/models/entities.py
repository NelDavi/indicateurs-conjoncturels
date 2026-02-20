import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import CITEXT, INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class FrequencyCode(str, enum.Enum):
    D = "D"
    W = "W"
    M = "M"
    Q = "Q"
    S = "S"
    A = "A"


class WorkflowStatus(str, enum.Enum):
    BROUILLON = "BROUILLON"
    EN_VALIDATION = "EN_VALIDATION"
    VALIDE = "VALIDE"
    PUBLIE = "PUBLIE"
    ARCHIVE = "ARCHIVE"


class RoleScope(str, enum.Enum):
    SYSTEM = "SYSTEM"
    INTERNAL = "INTERNAL"
    PUBLIC_API = "PUBLIC_API"


class ImportStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"
    PROCESSED = "PROCESSED"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)
    scope: Mapped[RoleScope] = mapped_column(Enum(RoleScope), default=RoleScope.INTERNAL)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(CITEXT, unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    full_name: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    frequency: Mapped[FrequencyCode] = mapped_column(Enum(FrequencyCode))
    unit: Mapped[str] = mapped_column(Text)
    base_year: Mapped[int | None] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(Text)
    methodology: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    sector_id: Mapped[int | None] = mapped_column(ForeignKey("sectors.id", ondelete="SET NULL"))
    workflow_state: Mapped[WorkflowStatus] = mapped_column(Enum(WorkflowStatus), default=WorkflowStatus.BROUILLON)
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)


class Sector(Base):
    __tablename__ = "sectors"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)


class DataSeries(Base):
    __tablename__ = "data_series"
    __table_args__ = (UniqueConstraint("indicator_id", "code", name="uq_data_series_indicator_code"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicators.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    decimals: Mapped[int] = mapped_column(Integer, default=2)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    indicator: Mapped[Indicator] = relationship()


class Observation(Base):
    __tablename__ = "observations"
    __table_args__ = (
        UniqueConstraint("series_id", "period_date", "revision_number", name="uq_observation_revision"),
        CheckConstraint("revision_number >= 0", name="ck_observation_revision_nonnegative"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    series_id: Mapped[int] = mapped_column(ForeignKey("data_series.id", ondelete="CASCADE"))
    period_date: Mapped[date] = mapped_column(Date)
    value: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    revision_number: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[WorkflowStatus] = mapped_column(Enum(WorkflowStatus), default=WorkflowStatus.BROUILLON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Import(Base):
    __tablename__ = "imports"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    indicator_id: Mapped[int | None] = mapped_column(ForeignKey("indicators.id", ondelete="SET NULL"))
    file_name: Mapped[str] = mapped_column(Text)
    status: Mapped[ImportStatus] = mapped_column(Enum(ImportStatus), default=ImportStatus.UPLOADED)
    validation_report: Mapped[dict | None] = mapped_column(JSONB)


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    entity_type: Mapped[str] = mapped_column(Text)
    entity_id: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    old_data: Mapped[dict | None] = mapped_column(JSONB)
    new_data: Mapped[dict | None] = mapped_column(JSONB)
    ip_address: Mapped[str | None] = mapped_column(INET)
    correlation_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
