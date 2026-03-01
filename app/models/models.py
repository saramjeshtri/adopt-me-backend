from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Department(Base):
    __tablename__ = "Department"

    department_id   = Column(Integer, primary_key=True, autoincrement=True)
    department_name = Column(String(100), nullable=False)
    department_type = Column(String(50),  nullable=False)
    contact_email   = Column(String(100))
    contact_phone   = Column(String(50))

    reports = relationship("Report", back_populates="department")


class Report(Base):
    __tablename__ = "Report"

    report_id          = Column(Integer, primary_key=True, autoincrement=True)
    report_type        = Column(String(50),  nullable=False)
    report_description = Column(Text,        nullable=False)
    location_address   = Column(String(255), nullable=False)
    latitude           = Column(DECIMAL(10, 8), nullable=False)
    longitude          = Column(DECIMAL(11, 8), nullable=False)
    report_status      = Column(String(50),  nullable=False)
    created_at         = Column(DateTime,    nullable=False, default=datetime.now)
    resolved_at        = Column(DateTime,    nullable=True)
    phoneNr            = Column(String(50))
    email              = Column(String(100))

    department_id = Column(Integer, ForeignKey("Department.department_id"), nullable=False)

    department = relationship("Department", back_populates="reports")
    media      = relationship("Media",     back_populates="report")
    animals    = relationship("Animal",    back_populates="report")


class Media(Base):
    __tablename__ = "Media"

    media_id    = Column(Integer, primary_key=True, autoincrement=True)
    media_type  = Column(String(20),  nullable=False)
    file_url    = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime,    nullable=False, default=datetime.now)

    report_id    = Column(Integer, ForeignKey("Report.report_id"), nullable=False)

    report    = relationship("Report", back_populates="media")


class Animal(Base):
    __tablename__ = "Animal"

    animal_id       = Column(Integer, primary_key=True, autoincrement=True)
    name            = Column(String(100))
    species         = Column(String(50),  nullable=False)
    breed           = Column(String(100))
    age_estimate    = Column(String(20))
    gender          = Column(String(10))
    description     = Column(Text)
    health_status   = Column(String(100))
    adoption_status = Column(String(50),  nullable=False)
    added_at        = Column(DateTime,    nullable=False, default=datetime.now)
    adopted_at      = Column(DateTime,    nullable=True)

    report_id    = Column(Integer, ForeignKey("Report.report_id"),    nullable=True)
    surrender_id = Column(Integer, ForeignKey("AnimalSurrender.surrender_id"), nullable=True)

    report   = relationship("Report",          back_populates="animals")
    surrender = relationship("AnimalSurrender", back_populates="animals", foreign_keys=[surrender_id])
    photos   = relationship("AnimalPhoto",     back_populates="animal")
    meetings = relationship("AdoptionMeeting", back_populates="animal")


class AnimalPhoto(Base):
    __tablename__ = "AnimalPhoto"

    photo_id   = Column(Integer, primary_key=True, autoincrement=True)
    photo_url  = Column(String(500), nullable=False)
    is_primary = Column(Boolean,     nullable=False, default=False)

    animal_id = Column(Integer, ForeignKey("Animal.animal_id"), nullable=False)
    animal    = relationship("Animal", back_populates="photos")


class AdoptionMeeting(Base):
    __tablename__ = "AdoptionMeeting"

    meeting_id     = Column(Integer, primary_key=True, autoincrement=True)
    visitor_name   = Column(String(100), nullable=False)
    visitor_phone  = Column(String(20),  nullable=False)
    visitor_email  = Column(String(100))
    preferred_date = Column(Date,        nullable=False)
    preferred_time = Column(Time,        nullable=False)
    status         = Column(String(50),  nullable=False)
    notes          = Column(Text)
    created_at     = Column(DateTime,    nullable=False, default=datetime.now)

    animal_id = Column(Integer, ForeignKey("Animal.animal_id"), nullable=False)
    animal    = relationship("Animal", back_populates="meetings")


class Event(Base):
    __tablename__ = "events"

    event_id         = Column(Integer, primary_key=True, autoincrement=True)
    title            = Column(String(255), nullable=False)
    description      = Column(Text,        nullable=False)
    location         = Column(String(255), nullable=False)
    event_date       = Column(Date,        nullable=False)
    event_time       = Column(String(10),  nullable=False)
    is_free          = Column(Boolean,     default=True)
    max_participants = Column(Integer,     nullable=True)
    organizer        = Column(String(100), nullable=True)
    created_at       = Column(DateTime,    default=datetime.now)


class AnimalSurrender(Base):
    __tablename__ = "AnimalSurrender"

    surrender_id  = Column(Integer,     primary_key=True, autoincrement=True)
    owner_name    = Column(String(100), nullable=False)
    phone         = Column(String(20),  nullable=False)
    email         = Column(String(100), nullable=True)
    species       = Column(String(50),  nullable=False)
    breed         = Column(String(100), nullable=True)
    age           = Column(String(50),  nullable=True)
    is_vaccinated = Column(String(20),  nullable=True)
    reason        = Column(String(255), nullable=False)
    notes         = Column(Text,        nullable=True)
    status        = Column(String(50),  nullable=False, default='New')
    created_at    = Column(DateTime,    nullable=False, default=datetime.now)

    media   = relationship("AnimalSurrenderMedia", back_populates="surrender", cascade="all, delete-orphan")
    animals = relationship("Animal", back_populates="surrender", foreign_keys="Animal.surrender_id")


class AnimalSurrenderMedia(Base):
    __tablename__ = "AnimalSurrenderMedia"

    media_id     = Column(Integer,     primary_key=True, autoincrement=True)
    file_url     = Column(String(500), nullable=False)
    uploaded_at  = Column(DateTime,    nullable=False, default=datetime.now)

    surrender_id = Column(Integer, ForeignKey("AnimalSurrender.surrender_id"), nullable=False)
    surrender    = relationship("AnimalSurrender", back_populates="media")