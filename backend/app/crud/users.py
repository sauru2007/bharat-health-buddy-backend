from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_current_user, get_db
from ..schemas import UserOut, UserCreate
from .. import crud

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def read_me(current_user = Depends(get_current_user)):
    return current_user
