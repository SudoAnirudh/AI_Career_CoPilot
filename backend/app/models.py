import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    DateTime,
    Date,
    ForeignKey,
    JSON,
    Uuid
)
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    clerk_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profiles = relationship("Profile", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1)
    raw_text = Column(Text, nullable=True)
    skills = Column(JSON, nullable=True)  # JSON structure: {"languages": [], "frameworks": [], ...}
    projects = Column(JSON, nullable=True)  # JSON structure: List of projects
    education = Column(JSON, nullable=True)
    experience = Column(JSON, nullable=True)
    certifications = Column(JSON, nullable=True)
    resume_url = Column(String, nullable=True)
    embedding_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="profiles")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    skills_required = Column(JSON, nullable=True)
    location = Column(String, nullable=True)
    remote = Column(Boolean, default=False)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    experience_years_min = Column(Integer, nullable=True)
    experience_years_max = Column(Integer, nullable=True)
    source = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    source_hash = Column(String, unique=True, nullable=False, index=True)
    match_score = Column(Float, nullable=True, index=True)
    match_explanation = Column(JSON, nullable=True)
    status = Column(String, default="discovered", index=True)  # e.g., discovered, saved, applied, etc.
    posted_date = Column(Date, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    embedding_id = Column(String, nullable=True)

    contacts = relationship("Contact", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False, index=True)
    domain = Column(String, nullable=True)
    overview = Column(Text, nullable=True)
    tech_stack = Column(JSON, nullable=True)
    funding_stage = Column(String, nullable=True)
    team_size = Column(String, nullable=True)
    recent_news = Column(JSON, nullable=True)
    ai_focus = Column(Text, nullable=True)
    why_fit = Column(Text, nullable=True)
    last_researched_at = Column(DateTime, nullable=True)


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    job_id = Column(Uuid, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=True)
    title = Column(String, nullable=True)
    company = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    email = Column(String, nullable=True)
    email_confidence = Column(Float, default=0.0)
    connection_degree = Column(Integer, nullable=True)
    source = Column(String, nullable=True)  # e.g., LinkedIn, Alumni
    status = Column(String, default="discovered", index=True)  # e.g., discovered, pending_outreach, contacted
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="contacts")
    messages = relationship("Message", back_populates="contact", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    contact_id = Column(Uuid, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Uuid, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    type = Column(String, nullable=False)  # e.g., linkedin_referral, cold_email, follow_up
    draft = Column(Text, nullable=False)
    final_text = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    status = Column(String, default="draft")  # e.g., draft, sent, replied
    created_at = Column(DateTime, default=datetime.utcnow)

    contact = relationship("Contact", back_populates="messages")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Uuid, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_version = Column(Integer, default=1)
    status = Column(String, default="saved", index=True)  # e.g., saved, applied, interviewing, offered, rejected
    applied_date = Column(Date, nullable=True)
    platform = Column(String, nullable=True)
    interview_rounds = Column(JSON, nullable=True)  # List of interview round details
    offer_details = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
