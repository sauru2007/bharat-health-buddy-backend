from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.post("", response_model=schemas.ReminderOut)
def create_reminder(rem: schemas.ReminderCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.create_reminder(db, current_user.id, rem)

@router.get("", response_model=list[schemas.ReminderOut])
def list_reminders(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.list_reminders_for_user(db, current_user.id)

@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    ok = crud.delete_reminder(db, reminder_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "deleted"}
