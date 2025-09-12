from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("", response_model=schemas.PatientOut)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.create_patient(db, patient)

@router.get("", response_model=list[schemas.PatientOut])
def list_patients(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.list_patients(db)

@router.get("/{patient_id}", response_model=schemas.PatientOut)
def get_one(patient_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    p = crud.get_patient(db, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p

@router.put("/{patient_id}", response_model=schemas.PatientOut)
def update_one(patient_id: int, patient: schemas.PatientCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    p = crud.update_patient(db, patient_id, patient)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p

@router.delete("/{patient_id}")
def delete_one(patient_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    ok = crud.delete_patient(db, patient_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "deleted"}
