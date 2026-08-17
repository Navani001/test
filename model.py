import enum
import uuid
from datetime import datetime
from uuid import UUID as PyUUID

from sqlalchemy import (
    ForeignKey,
    String,
    Integer,
    Boolean,
    DateTime,
    UniqueConstraint,
    Text,
    Enum as SQLEnum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


# ============================================================
# ENUMS
# ============================================================

class IndicatorCategory(enum.Enum):
    CLINICAL = "CLINICAL"
    ADMINISTRATIVE = "ADMINISTRATIVE"
    DIAGNOSTIC = "DIAGNOSTIC"
    PROCEDURAL = "PROCEDURAL"
    OTHER = "OTHER"


class IndicatorOutput(enum.Enum):
    BOOLEAN = "BOOLEAN"
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    DATE = "DATE"
    ENUM = "ENUM"
    JSON = "JSON"


# ============================================================
# ASSOCIATION TABLES (Many-to-Many Relationships)
# ============================================================

class ConditionIndicator(Base):
    __tablename__ = "condition_indicators"

    condition_version_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("condition_versions.id"), primary_key=True
    )
    indicator_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indicators.id"), primary_key=True
    )


class ConditionIcdCode(Base):
    __tablename__ = "condition_icd_codes"

    condition_version_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("condition_versions.id"), primary_key=True
    )
    icd_code_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("icd_codes.id"), primary_key=True
    )


class IndicatorSection(Base):
    __tablename__ = "indicator_sections"

    indicator_version_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indicators_versions.id"), primary_key=True
    )
    section_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sections.id"), primary_key=True
    )


class IndicatorAtom(Base):
    __tablename__ = "indicator_atoms"

    indicator_version_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indicators_versions.id"), primary_key=True
    )
    atom_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("atoms.id"), primary_key=True
    )


# ============================================================
# MODELS
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    conditions: Mapped[list["Condition"]] = relationship(back_populates="user")
    created_condition_versions: Mapped[list["ConditionVersion"]] = relationship(back_populates="creator")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    schema_name: Mapped[str | None] = mapped_column(String, nullable=True)
    crd_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_base: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    conditions: Mapped[list["Condition"]] = relationship(back_populates="client")


class Condition(Base):
    __tablename__ = "conditions"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False
    )
    current_version_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("condition_versions.id", use_alter=True, name="fk_conditions_current_version_id"),
        nullable=True,
    )
    key: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True, nullable=True)
    user_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    client: Mapped["Client"] = relationship(back_populates="conditions")
    user: Mapped["User | None"] = relationship(back_populates="conditions")
    current_version: Mapped["ConditionVersion | None"] = relationship(
        foreign_keys=[current_version_id], post_update=True
    )
    versions: Mapped[list["ConditionVersion"]] = relationship(
        back_populates="condition", foreign_keys="[ConditionVersion.condition_id]"
    )


class ConditionVersion(Base):
    __tablename__ = "condition_versions"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condition_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conditions.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_draft: Mapped[bool | None] = mapped_column(Boolean, default=True, nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True, nullable=True)
    created_by: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Indexes/Constraints
    __table_args__ = (
        UniqueConstraint("condition_id", "version", name="uq_condition_version"),
    )

    # Relationships
    condition: Mapped["Condition"] = relationship(back_populates="versions", foreign_keys=[condition_id])
    creator: Mapped["User"] = relationship(back_populates="created_condition_versions")

    indicators: Mapped[list["Indicator"]] = relationship(
        secondary="condition_indicators", back_populates="condition_versions"
    )
    icd_codes: Mapped[list["IcdCode"]] = relationship(
        secondary="condition_icd_codes", back_populates="condition_versions"
    )


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    current_version_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("indicators_versions.id", use_alter=True, name="fk_indicators_current_version_id"),
        nullable=True,
    )
    key: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    current_version: Mapped["IndicatorVersion | None"] = relationship(
        foreign_keys=[current_version_id], post_update=True
    )
    versions: Mapped[list["IndicatorVersion"]] = relationship(
        back_populates="indicator", foreign_keys="[IndicatorVersion.indicator_id]"
    )
    condition_versions: Mapped[list["ConditionVersion"]] = relationship(
        secondary="condition_indicators", back_populates="indicators"
    )


class IndicatorVersion(Base):
    __tablename__ = "indicators_versions"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    indicator_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indicators.id"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[IndicatorCategory | None] = mapped_column(
        SQLEnum(IndicatorCategory, name="indicator_category"), nullable=True
    )
    output: Mapped[IndicatorOutput | None] = mapped_column(
        SQLEnum(IndicatorOutput, name="indicator_output"), nullable=True
    )
    cui_code: Mapped[str | None] = mapped_column(String, nullable=True)
    version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True, nullable=True)
    is_draft: Mapped[bool | None] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    indicator: Mapped["Indicator"] = relationship(back_populates="versions", foreign_keys=[indicator_id])
    elements: Mapped[list["IndicatorElement"]] = relationship(back_populates="indicator_version")
    sections: Mapped[list["Section"]] = relationship(
        secondary="indicator_sections", back_populates="indicator_versions"
    )
    atoms: Mapped[list["Atom"]] = relationship(
        secondary="indicator_atoms", back_populates="indicator_versions"
    )


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    indicator_versions: Mapped[list["IndicatorVersion"]] = relationship(
        secondary="indicator_sections", back_populates="sections"
    )


class IndicatorElement(Base):
    __tablename__ = "indicator_elements"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    indicator_version_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("indicators_versions.id"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    indicator_version: Mapped["IndicatorVersion"] = relationship(back_populates="elements")


class IcdCode(Base):
    __tablename__ = "icd_codes"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    condition_versions: Mapped[list["ConditionVersion"]] = relationship(
        secondary="condition_icd_codes", back_populates="icd_codes"
    )


class Atom(Base):
    __tablename__ = "atoms"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    indicator_versions: Mapped[list["IndicatorVersion"]] = relationship(
        secondary="indicator_atoms", back_populates="atoms"
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_key: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    old_data: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    new_data: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user: Mapped["User | None"] = relationship(back_populates="audit_logs")
