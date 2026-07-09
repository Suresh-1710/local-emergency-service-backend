import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, Numeric, String, Text, DateTime, func
from sqlalchemy.orm import relationship

from database import Base


class WorkerCategory(str, enum.Enum):
    plumber = "plumber"
    electrician = "electrician"
    carpenter = "carpenter"


class WorkerStatus(str, enum.Enum):
    available = "available"
    busy = "busy"
    offline = "offline"


class IssueStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    completed = "completed"
    cancelled = "cancelled"


class Client(Base):
    __tablename__ = "clients"

    client_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    home_address_text = Column(String(255), nullable=False)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    issues = relationship("Issue", back_populates="client")


class Worker(Base):
    __tablename__ = "workers"

    worker_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    experience_years = Column(Integer, nullable=False)
    category = Column(Enum(WorkerCategory, native_enum=False, length=20), nullable=False, index=True)
    location_text = Column(String(255), nullable=False)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)
    photo_url = Column(String(255), nullable=True)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    status = Column(Enum(WorkerStatus, native_enum=False, length=20), nullable=False, default=WorkerStatus.available, index=True)
    created_at = Column(DateTime, server_default=func.now())

    accepted_issues = relationship("Issue", back_populates="worker")


class Issue(Base):
    __tablename__ = "issues"

    issue_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
    category = Column(Enum(WorkerCategory, native_enum=False, length=20), nullable=False, index=True)
    description = Column(Text, nullable=False)
    photo_url = Column(String(255), nullable=True)
    location_text = Column(String(255), nullable=False)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)
    status = Column(Enum(IssueStatus, native_enum=False, length=20), nullable=False, default=IssueStatus.pending, index=True)
    accepted_by = Column(Integer, ForeignKey("workers.worker_id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    client = relationship("Client", back_populates="issues")
    worker = relationship("Worker", back_populates="accepted_issues")
