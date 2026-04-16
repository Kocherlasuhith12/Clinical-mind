import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, SmallInteger,
    DateTime, Enum, DECIMAL, ARRAY, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class UserRole(str, enum.Enum):
    doctor = "doctor"
    asha = "asha"
    admin = "admin"


class Language(str, enum.Enum):
    ta = "ta"
    hi = "hi"
    en = "en"


class CaseStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    urgent = "urgent"
    failed = "failed"   # ← add this


class ClinicTier(str, enum.Enum):
    phc = "phc"
    chc = "chc"
    district = "district"


class Clinic(Base):
    __tablename__ = "clinics"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    district = Column(String(100))
    state = Column(String(60))
    lat = Column(DECIMAL(9, 6))
    lng = Column(DECIMAL(9, 6))
    tier = Column(Enum(ClinicTier), default=ClinicTier.phc)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="clinic")


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.asha)
    language = Column(Enum(Language), default=Language.en)
    clinic_id = Column(UUID(as_uuid=True), ForeignKey("clinics.id"), nullable=True)
    password_hash = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    clinic = relationship("Clinic", back_populates="users")
    cases = relationship("PatientCase", back_populates="submitted_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")


class PatientCase(Base):
    __tablename__ = "patient_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    patient_age = Column(SmallInteger)
    patient_sex = Column(Enum("M", "F", "O", name="sex_enum"))
    symptoms_text = Column(Text)
    symptoms_language = Column(Enum(Language), default=Language.en)
    symptoms_translated = Column(Text)
    audio_url = Column(Text)
    image_urls = Column(ARRAY(Text), default=list)
    status = Column(Enum(CaseStatus), default=CaseStatus.pending)
    is_offline = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submitted_by_user = relationship("User", back_populates="cases")
    diagnosis = relationship("Diagnosis", back_populates="case", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="case")


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("patient_cases.id"), unique=True, nullable=False)
    model_used = Column(String(50))
    primary_dx = Column(Text)
    differentials = Column(JSONB)
    confidence = Column(DECIMAL(4, 3))
    is_emergency = Column(Boolean, default=False)
    emergency_reason = Column(Text)
    treatment_plan = Column(Text)
    precautions = Column(Text)
    when_to_refer = Column(Text)
    references = Column(JSONB)
    raw_response = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("PatientCase", back_populates="diagnosis")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    case_id = Column(UUID(as_uuid=True), ForeignKey("patient_cases.id"), nullable=True)
    action = Column(String(50))
    ip_address = Column(INET)
    extra_metadata = Column("metadata", JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
    case = relationship("PatientCase", back_populates="audit_logs")


class SyncQueue(Base):
    __tablename__ = "sync_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("patient_cases.id"))
    payload = Column(JSONB)
    synced = Column(Boolean, default=False)
    retries = Column(SmallInteger, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    synced_at = Column(DateTime, nullable=True)