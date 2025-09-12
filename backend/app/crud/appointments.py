from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("", response_model=schemas.AppointmentOut)
def book(appt: schemas.AppointmentCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # optionally verify patient exists
    if not crud.get_patient(db, appt.patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    return crud.create_appointment(db, current_user.id, appt)

@router.get("", response_model=list[schemas.AppointmentOut])
def list_appts(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.list_appointments_for_user(db, current_user.id)

@router.delete("/{appointment_id}")
def cancel(appointment_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    ok = crud.delete_appointment(db, appointment_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": "deleted"}
