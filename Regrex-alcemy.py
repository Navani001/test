from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    BigInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Run(Base):
    __tablename__ = "runs"

    run_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True
    )

    success_inference: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    total_inference: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    # Relationships
    failure_stats: Mapped[list["FailureStat"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan"
    )

    failures: Mapped[list["Failure"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan"
    )

    llm_throughput: Mapped[list["LLMThroughput"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan"
    )

    condition_throughput: Mapped[list["ConditionThroughput"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan"
    )


class FailureStat(Base):
    __tablename__ = "failure_stats"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    run_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("runs.run_id"),
        nullable=False
    )

    attempt: Mapped[int] = mapped_column(Integer, nullable=False)

    decode: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    malformed_table: Mapped[int] = mapped_column(Integer, default=0)
    max_token: Mapped[int] = mapped_column(Integer, default=0)
    parse: Mapped[int] = mapped_column(Integer, default=0)
    schema_validation: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)

    run: Mapped["Run"] = relationship(
        back_populates="failure_stats"
    )


class Failure(Base):
    __tablename__ = "failures"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    run_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("runs.run_id"),
        nullable=False
    )

    request_id_raw: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    audit_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    condition: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # Present for base failures, NULL for aggregate failures
    indicator: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # TRUE  -> aggregate
    # FALSE -> base
    isagg: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    output_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    task_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    failure_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    attempt: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    max_attempts: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    run: Mapped["Run"] = relationship(
        back_populates="failures"
    )


class LLMThroughput(Base):
    __tablename__ = "llm_throughput"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    run_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("runs.run_id"),
        nullable=False
    )

    elapsed_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    overall_tok_per_sec: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    tokens: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True
    )

    run: Mapped["Run"] = relationship(
        back_populates="llm_throughput"
    )


class ConditionThroughput(Base):
    __tablename__ = "condition_throughput"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    run_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("runs.run_id"),
        nullable=False
    )

    condition_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    tok_per_sec: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    tokens: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True
    )

    run: Mapped["Run"] = relationship(
        back_populates="condition_throughput"
    )
