class LogFile(Base):
    __tablename__ = "log_files"

    id = Column(Integer, primary_key=True)

    s3_key = Column(String, unique=True, nullable=False)

    status = Column(
        String,
        default="PENDING"
    )

    attempts = Column(
        Integer,
        default=0
    )

    error_message = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    processed_at = Column(
        DateTime,
        nullable=True
    )
