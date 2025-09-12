from sqlalchemy.orm import Session
from . import models, schemas, auth

# --------- USERS ----------
def get_user_by_username_or_email(db: Session, username: str, email: str):
    return db.query(models.User).filter(
        (models.User.username == username) | (models.User.email == email)
    ).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --------- PATIENTS ----------
def create_patient(db: Session, patient: schemas.PatientCreate, user_id: int):
    db_patient = models.Patient(
        name=patient.name, age=patient.age, condition=patient.condition, owner_id=user_id
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def get_patients(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Patient).offset(skip).limit(limit).all()

# --------- APPOINTMENTS ----------
def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    db_appt = models.Appointment(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        date_time=appointment.date_time,
        notes=appointment.notes,
    )
    db.add(db_appt)
    db.commit()
    db.refresh(db_appt)
    return db_appt

def get_appointments(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Appointment).offset(skip).limit(limit).all()

# --------- REMINDERS ----------
def create_reminder(db: Session, reminder: schemas.ReminderCreate):
    db_rem = models.Reminder(
        patient_id=reminder.patient_id,
        message=reminder.message,
        due_date=reminder.due_date,
    )
    db.add(db_rem)
    db.commit()
    db.refresh(db_rem)
    return db_rem

def get_reminders(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Reminder).offset(skip).limit(limit).all()
