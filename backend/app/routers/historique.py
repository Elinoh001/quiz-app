from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/historique", tags=["historique"])


@router.get("/{matricule}", response_model=schemas.HistoriqueResponse)
def obtenir_historique(matricule: str, db: Session = Depends(get_db)):
    eleve = db.query(models.Eleve).filter(models.Eleve.matricule == matricule).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève introuvable.")

    resultats = (
        db.query(models.Resultat)
        .filter(models.Resultat.eleve_id == eleve.id)
        .order_by(models.Resultat.date_passage.desc())
        .all()
    )

    historique = [
        schemas.HistoriqueEntry(
            matiere=resultat.quiz.matiere.nom if resultat.quiz and resultat.quiz.matiere else "?",
            score=resultat.score,
            date_passage=resultat.date_passage,
        )
        for resultat in resultats
    ]

    moyenne_generale = round(sum(e.score for e in historique) / len(historique), 2) if historique else 0.0

    return schemas.HistoriqueResponse(
        historique=historique,
        moyenne_generale=moyenne_generale,
        nombre_quiz=len(historique),
    )
