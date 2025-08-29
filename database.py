from sqlalchemy import func, create_engine, Column, Integer, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import enum

Base = declarative_base()


class Priority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketModel(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )

    claude_suggested_priority = Column(Enum(Priority), nullable=True)
    claude_suggested_response = Column(String, nullable=True)
    tokens_used = Column(Integer, nullable=True)


DATABASE_URL = "sqlite:///./tickets.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

print(Priority.MEDIUM.value)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
