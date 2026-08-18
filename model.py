import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


# ============================================================
# BASE
# ============================================================

class Base(DeclarativeBase):
    pass


# ============================================================
# ENUMS
# ============================================================

class IndicatorCategory(str, enum.Enum):
    CLINICAL = "CLINICAL"
    ADMINISTRATIVE = "ADMINISTRATIVE"
    DIAGNOSTIC = "DIAGNOSTIC"
    PROCEDURAL = "PROCEDURAL"
    OTHER = "OTHER"


class IndicatorOutput(str, enum.Enum):
    BOOLEAN = "BOOLEAN"
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    DATE = "DATE"
    ENUM = "ENUM"
    JSON = "JSON"


# ============================================================
# ASSOCIATION TABLES
# ============================================================

# CONDITION - CLIENT
condition_clients = Table(
    "condition_clients",
    Base.metadata,

    Column(
        "condition_id",
        UUID(as_uuid=True),
        ForeignKey("conditions.id"),
        primary_key=True,
    ),

    Column(
        "client_id",
        UUID(as_uuid=True),
        ForeignKey("clients.id"),
        primary_key=True,
    ),
)


# CONDITION VERSION - INDICATOR
condition_indicators = Table(
    "condition_indicators",
    Base.metadata,

    Column(
        "condition_version_id",
        UUID(as_uuid=True),
        ForeignKey("condition_versions.id"),
        primary_key=True,
    ),

    Column(
        "indicator_id",
        UUID(as_uuid=True),
        ForeignKey("indicators.id"),
        primary_key=True,
    ),
)


# INDICATOR VERSION - SECTION
indicator_sections = Table(
    "indicator_sections",
    Base.metadata,

    Column(
        "indicator_version_id",
        UUID(as_uuid=True),
        ForeignKey("indicators_versions.id"),
        primary_key=True,
    ),

    Column(
        "section_id",
        UUID(as_uuid=True),
        ForeignKey("sections.id"),
        primary_key=True,
    ),
)


# CONDITION VERSION - ICD CODE
condition_icd_codes = Table(
    "condition_icd_codes",
    Base.metadata,

    Column(
        "condition_version_id",
        UUID(as_uuid=True),
        ForeignKey("condition_versions.id"),
        primary_key=True,
    ),

    Column(
        "icd_code_id",
        UUID(as_uuid=True),
        ForeignKey("icd_codes.id"),
        primary_key=True,
    ),
)


# INDICATOR VERSION - ATOM
indicator_atoms = Table(
    "indicator_atoms",
    Base.metadata,

    Column(
        "indicator_version_id",
        UUID(as_uuid=True),
        ForeignKey("indicators_versions.id"),
        primary_key=True,
    ),

    Column(
        "atom_id",
        UUID(as_uuid=True),
        ForeignKey("atoms.id"),
        primary_key=True,
    ),
)


# ============================================================
# USER
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    username: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    password: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # User -> Conditions
    conditions: Mapped[list["Condition"]] = relationship(
        back_populates="user",
    )

    # User -> Condition Versions created by user
    created_condition_versions: Mapped[
        list["ConditionVersion"]
    ] = relationship(
        back_populates="created_by_user",
    )

    # User -> Audit Logs
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user",
    )


# ============================================================
# CLIENT
# ============================================================

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    schema_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    crd_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_base: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Client <-> Condition
    conditions: Mapped[list["Condition"]] = relationship(
        secondary=condition_clients,
        back_populates="clients",
    )


# ============================================================
# CONDITION
# ============================================================

class Condition(Base):
    __tablename__ = "conditions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("condition_versions.id"),
        nullable=True,
    )

    key: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Condition -> User
    user: Mapped["User"] = relationship(
        back_populates="conditions",
    )

    # Condition <-> Client
    clients: Mapped[list["Client"]] = relationship(
        secondary=condition_clients,
        back_populates="conditions",
    )

    # Condition -> Versions
    versions: Mapped[list["ConditionVersion"]] = relationship(
        back_populates="condition",
        foreign_keys="ConditionVersion.condition_id",
    )

    # Condition -> Current Version
    current_version: Mapped[
        "ConditionVersion | None"
    ] = relationship(
        foreign_keys=[current_version_id],
        post_update=True,
    )


# ============================================================
# CONDITION VERSION
# ============================================================

class ConditionVersion(Base):
    __tablename__ = "condition_versions"

    __table_args__ = (
        UniqueConstraint(
            "condition_id",
            "version",
            name="uq_condition_version",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    condition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conditions.id"),
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    is_draft: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Version -> Condition
    condition: Mapped["Condition"] = relationship(
        back_populates="versions",
        foreign_keys=[condition_id],
    )

    # Version -> User
    created_by_user: Mapped["User"] = relationship(
        back_populates="created_condition_versions",
    )

    # Condition Version <-> Indicator
    indicators: Mapped[list["Indicator"]] = relationship(
        secondary=condition_indicators,
        back_populates="condition_versions",
    )

    # Condition Version <-> ICD Code
    icd_codes: Mapped[list["ICDCode"]] = relationship(
        secondary=condition_icd_codes,
        back_populates="condition_versions",
    )


# ============================================================
# INDICATOR
# ============================================================

class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("indicators_versions.id"),
        nullable=True,
    )

    key: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Indicator -> Versions
    versions: Mapped[list["IndicatorVersion"]] = relationship(
        back_populates="indicator",
        foreign_keys="IndicatorVersion.indicator_id",
    )

    # Indicator -> Current Version
    current_version: Mapped[
        "IndicatorVersion | None"
    ] = relationship(
        foreign_keys=[current_version_id],
        post_update=True,
    )

    # Indicator <-> Condition Version
    condition_versions: Mapped[
        list["ConditionVersion"]
    ] = relationship(
        secondary=condition_indicators,
        back_populates="indicators",
    )


# ============================================================
# INDICATOR VERSION
# ============================================================

class IndicatorVersion(Base):
    __tablename__ = "indicators_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    indicator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("indicators.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    category: Mapped[IndicatorCategory] = mapped_column(
        SAEnum(
            IndicatorCategory,
            name="indicator_category",
        ),
        nullable=False,
    )

    output: Mapped[IndicatorOutput] = mapped_column(
        SAEnum(
            IndicatorOutput,
            name="indicator_output",
        ),
        nullable=False,
    )

    cui_code: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    version: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    is_draft: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Indicator Version -> Indicator
    indicator: Mapped["Indicator"] = relationship(
        back_populates="versions",
        foreign_keys=[indicator_id],
    )

    # Indicator Version <-> Section
    sections: Mapped[list["Section"]] = relationship(
        secondary=indicator_sections,
        back_populates="indicator_versions",
    )

    # Indicator Version -> Elements
    elements: Mapped[list["IndicatorElement"]] = relationship(
        back_populates="indicator_version",
    )

    # Indicator Version <-> Atoms
    atoms: Mapped[list["Atom"]] = relationship(
        secondary=indicator_atoms,
        back_populates="indicator_versions",
    )


# ============================================================
# SECTION
# ============================================================

class Section(Base):
    __tablename__ = "sections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Section <-> Indicator Version
    indicator_versions: Mapped[
        list["IndicatorVersion"]
    ] = relationship(
        secondary=indicator_sections,
        back_populates="sections",
    )


# ============================================================
# INDICATOR ELEMENT
# ============================================================

class IndicatorElement(Base):
    __tablename__ = "indicator_elements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    indicator_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("indicators_versions.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Element -> Indicator Version
    indicator_version: Mapped["IndicatorVersion"] = relationship(
        back_populates="elements",
    )


# ============================================================
# ICD CODE
# ============================================================

class ICDCode(Base):
    __tablename__ = "icd_codes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    code: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ICD Code <-> Condition Version
    condition_versions: Mapped[
        list["ConditionVersion"]
    ] = relationship(
        secondary=condition_icd_codes,
        back_populates="icd_codes",
    )


# ============================================================
# ATOM
# ============================================================

class Atom(Base):
    __tablename__ = "atoms"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Atom <-> Indicator Version
    indicator_versions: Mapped[
        list["IndicatorVersion"]
    ] = relationship(
        secondary=indicator_atoms,
        back_populates="atoms",
    )


# ============================================================
# AUDIT LOG
# ============================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    entity_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    entity_key: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    old_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    new_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    # Audit Log -> User
    user: Mapped["User | None"] = relationship(
        back_populates="audit_logs",
    )
