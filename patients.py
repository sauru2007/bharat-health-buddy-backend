from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Patient
from pydantic import BaseModel

router = APIRouter(prefix="/patients", tags=["Patients"])

class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str

@router.post("/")
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    new_patient = Patient(name=patient.name, age=patient.age, gender=patient.gender)
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return {"message": "Patient created successfully", "patient": new_patient}

@router.get("/")
def list_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()

@router.get("/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()
    return {"message": "Patient deleted successfully"}
