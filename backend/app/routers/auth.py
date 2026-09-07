from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.EleveResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    eleve = db.query(models.Eleve).filter(models.Eleve.matricule == payload.matricule).first()
    if not eleve:
        raise HTTPException(status_code=401, detail="Matricule inconnu. Accès refusé.")
    return eleve
