from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .auth import get_current_user
from .models import User
from .database import get_db

router = APIRouter()

@router.post("/symptoms")
def check_symptoms(payload: dict, current_user: User = Depends(get_current_user)):
    symptom_map = {"fever": ["Flu", "Cold", "COVID-19"], "cough": ["Cold", "Bronchitis"]}
    received = payload.get("symptoms", [])
    possible_conditions = []
    for symptom in received:
        possible_conditions.extend(symptom_map.get(symptom.lower(), []))
    return {"possible_conditions": list(set(possible_conditions)), "received": received}

@router.get("/home-remedies/{condition}")
def home_remedies(condition: str, current_user: User = Depends(get_current_user)):
    remedies = {"headache": ["Ginger tea", "Rest"], "fever": ["Hydration", "Paracetamol"]}
    return {"condition": condition, "remedies": remedies.get(condition.lower(), ["No remedies found"])}

@router.get("/nearby-hospitals")
def nearby_hospitals(lat: float, lon: float, current_user: User = Depends(get_current_user)):
    return [{"name": "AIIMS", "distance_km": 2.5}, {"name": "City Clinic", "distance_km": 4.2}]

@router.get("/health-camps")
def health_camps():
    return [{"title": "Eye Checkup", "date": "2025-09-10", "location": "Community Hall"}]
