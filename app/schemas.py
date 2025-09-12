from pydantic import BaseModel, EmailStr
from datetime import datetime

# ---------------- Users ----------------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    class Config:
        from_attributes = True

# ---------------- Patients ----------------
class PatientCreate(BaseModel):
    name: str
    age: int
    condition: str | None = None

class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    condition: str | None
    class Config:
        from_attributes = True

# ---------------- Appointments ----------------
class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    date_time: datetime
    notes: str | None = None

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    date_time: datetime
    notes: str | None
    class Config:
        from_attributes = True

# ---------------- Reminders ----------------
class ReminderCreate(BaseModel):
    patient_id: int
    message: str
    due_date: datetime

class ReminderResponse(BaseModel):
    id: int
    patient_id: int
    message: str
    due_date: datetime
    class Config:
        from_attributes = True
