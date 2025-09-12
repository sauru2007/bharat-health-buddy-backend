from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "muser_schema"}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")

    patients = relationship("Patient", back_populates="owner")
    appointments = relationship("Appointment", back_populates="doctor")


class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = {"schema": "muser_schema"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    age = Column(Integer, nullable=False)
    condition = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("muser_schema.users.id"))

    owner = relationship("User", back_populates="patients")
    reminders = relationship("Reminder", back_populates="patient")


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = {"schema": "muser_schema"}

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("muser_schema.patients.id"))
    doctor_id = Column(Integer, ForeignKey("muser_schema.users.id"))
    date_time = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)

    patient = relationship("Patient")
    doctor = relationship("User", back_populates="appointments")


class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = {"schema": "muser_schema"}

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("muser_schema.patients.id"))
    message = Column(Text, nullable=False)
    due_date = Column(DateTime, nullable=False)

    patient = relationship("Patient", back_populates="reminders")
