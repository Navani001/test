from sqlalchemy import (
    BigInteger,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column


class ParsedFailure(Base):

    __tablename__ = "parsed_failures"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    log_file_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    indicator: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    failure_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    output_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    attempts: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    max_attempts: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "log_file_id",
            "indicator",
            "failure_type",
            "output_type",
            name="uq_parsed_failure",
        ),
    )
    
