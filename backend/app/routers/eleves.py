from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/eleves", tags=["eleves"])


@router.get("", response_model=list[schemas.EleveResponse])
def lister_eleves(db: Session = Depends(get_db)):
    """
    Retourne la liste de tous les élèves (matricule, nom, école).
    Utilisée par l'application mobile pour le champ adversaire dans les défis.
    """
    eleves = db.query(models.Eleve).all()
    return eleves