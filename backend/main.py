from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Optional

# ----------------------
# CONFIG
# ----------------------
DATABASE_URL = "postgresql+psycopg2://muser:health369@localhost:5432/bharat_health"
SECRET_KEY = "9b3aef88c9c44a7db1a52af83c7b9218d5c98c25b8c84c408cfd3a8d2c7a30f1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ----------------------
# Database setup
# ----------------------
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ----------------------
# Models
# ----------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=func.now())

    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=True)
    condition = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    remind_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="reminders")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    user = relationship("User", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")


Base.metadata.create_all(bind=engine, checkfirst=True)

# ----------------------
# Security utils
# ----------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ----------------------
# Schemas
# ----------------------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class PatientCreate(BaseModel):
    name: str
    age: int
    gender: Optional[str] = None
    condition: Optional[str] = None


class PatientOut(PatientCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ReminderCreate(BaseModel):
    message: str
    remind_at: Optional[datetime] = None


class ReminderOut(ReminderCreate):
    id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AppointmentCreate(BaseModel):
    doctor: str
    date: datetime
    patient_id: int


class AppointmentOut(AppointmentCreate):
    id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ----------------------
# Dependency
# ----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------
# Auth helper
# ----------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exception
    return user

# ----------------------
# FastAPI app
# ----------------------
app = FastAPI(title="Bharat Health Buddy API")

# ----------------------
# Auth endpoints
# ----------------------
@app.post("/auth/register", status_code=201, response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == user.username) | (User.email == user.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already registered")
    hashed = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ----------------------
# User endpoints
# ----------------------
@app.get("/users/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

# ----------------------
# Patients CRUD
# ----------------------
@app.post("/patients", response_model=PatientOut)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = Patient(**patient.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.get("/patients", response_model=List[PatientOut])
def list_patients(
    name: Optional[str] = Query(None),
    age: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Patient)
    if name:
        query = query.filter(Patient.name.ilike(f"%{name}%"))
    if age:
        query = query.filter(Patient.age == age)
    return query.all()


@app.get("/patients/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p


@app.put("/patients/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, patient: PatientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    for key, value in patient.model_dump().items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return p


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(p)
    db.commit()
    return {"message": "Patient deleted"}

# ----------------------
# Reminders
# ----------------------
@app.post("/reminders", response_model=ReminderOut)
def create_reminder(rem: ReminderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = Reminder(**rem.model_dump(), user_id=current_user.id)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@app.get("/reminders", response_model=List[ReminderOut])
def list_reminders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Reminder).filter(Reminder.user_id == current_user.id).all()


@app.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(r)
    db.commit()
    return {"message": "Reminder deleted"}

# ----------------------
# Appointments
# ----------------------
@app.post("/appointments", response_model=AppointmentOut)
def book_appointment(appt: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.id == appt.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    a = Appointment(doctor=appt.doctor, date=appt.date, user_id=current_user.id, patient_id=appt.patient_id)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@app.get("/appointments", response_model=List[AppointmentOut])
def list_appointments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Appointment).filter(Appointment.user_id == current_user.id).all()


@app.delete("/appointments/{appointment_id}")
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    a = db.query(Appointment).filter(Appointment.id == appointment_id, Appointment.user_id == current_user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(a)
    db.commit()
    return {"message": "Appointment canceled"}

# ----------------------
# Extra endpoints
# ----------------------
@app.post("/symptoms")
def check_symptoms(payload: dict, current_user: User = Depends(get_current_user)):
    return {"possible_conditions": ["Common Cold", "Flu", "Allergy"], "received": payload}


@app.get("/home-remedies/{condition}")
def home_remedies(condition: str, current_user: User = Depends(get_current_user)):
    remedies = {
        "headache": ["Drink ginger tea", "Rest", "Use cold compress"],
        "cough": ["Honey", "Steam inhalation"],
    }
    return {"condition": condition, "remedies": remedies.get(condition.lower(), ["No remedies found"])}


@app.get("/nearby-hospitals")
def nearby_hospitals(lat: float, lon: float, current_user: User = Depends(get_current_user)):
    return [
        {"name": "AIIMS Hospital", "distance_km": 2.5},
        {"name": "City Clinic", "distance_km": 4.2}
    ]


@app.get("/health-camps")
def health_camps():
    return [
        {"title": "Free Eye Checkup", "date": "2025-09-10", "location": "Community Hall"},
        {"title": "Blood Donation Drive", "date": "2025-09-15", "location": "City Hospital"}
    ]


@app.get("/")
def root():
    return {"msg": "Bharat Health Buddy API — running. Visit /docs for interactive API UI."}
