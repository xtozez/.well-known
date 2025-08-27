from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean, Float, JSON, Index
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class LeadStatusEnum(str, enum.Enum):
    prospect = "Prospect"
    contact_qualifie = "Contact_qualifie"
    fiche_renseignements = "Fiche_renseignements"
    reservation = "Reservation"
    acte = "Acte"
    archive = "Archive"
    hors_cible = "Hors_cible"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True)
    source = Column(String, index=True)
    campaign = Column(String, nullable=True)
    channel = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, index=True)
    phone_e164 = Column(String, index=True)
    contact_pref = Column(String, nullable=True)
    consent = Column(Boolean, default=False)
    message = Column(String, nullable=True)
    project_type = Column(String, nullable=True)
    typology = Column(String, nullable=True)
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    zipcode = Column(String, nullable=True)
    city = Column(String, nullable=True)
    origin = Column(String, nullable=True)

    status = Column(Enum(LeadStatusEnum), default=LeadStatusEnum.prospect, index=True)

    interactions = relationship("Interaction", back_populates="lead", cascade="all,delete-orphan")
    assignments = relationship("Assignment", back_populates="lead", cascade="all,delete-orphan")
    reservations = relationship("Reservation", back_populates="lead", cascade="all,delete-orphan")

    __table_args__ = (
        Index("ix_lead_email_phone", "email", "phone_e164"),
    )


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"))
    type = Column(String)
    content = Column(String)
    author = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="interactions")


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True)
    program = Column(String)
    lot = Column(String)
    type = Column(String)
    area = Column(Float)
    price = Column(Float)
    status = Column(String, index=True)
    url_plan = Column(String, nullable=True)

    reservations = relationship("Reservation", back_populates="property")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"))
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"))
    price = Column(Float)
    option_date = Column(DateTime, default=datetime.utcnow)
    option_expires = Column(DateTime, nullable=True)
    status = Column(String, default="en_cours")

    lead = relationship("Lead", back_populates="reservations")
    property = relationship("Property", back_populates="reservations")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"))
    advisor = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="assignments")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=True)
    title = Column(String)
    due_date = Column(DateTime, nullable=True)
    owner = Column(String, index=True)
    reminder = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id", ondelete="CASCADE"), nullable=True)
    filename = Column(String)
    filetype = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    actor = Column(String)
    action = Column(String)
    entity = Column(String)
    entity_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    payload = Column(JSON, nullable=True)
