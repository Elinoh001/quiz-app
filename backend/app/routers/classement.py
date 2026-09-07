from typing import Optional

from fastapi import APIRouter, Depends, Query
from app import models
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db

router = APIRouter(prefix="/classement", tags=["classement"])


@router.get("", response_model=schemas.ClassementResponse)
def obtenir_classement(
    matiere: Optional[str] = Query(None, description="Filtrer le classement sur une matière précise"),
    db: Session = Depends(get_db),
):
    query = db.query(
        models.Eleve.matricule,
        models.Eleve.nom,
        func.avg(models.Resultat.score).label("score_moyen"),
        func.count(models.Resultat.id).label("nombre_quiz"),
    ).join(models.Resultat, models.Resultat.eleve_id == models.Eleve.id)

    if matiere:
        query = (
            query.join(models.Quiz, models.Quiz.id == models.Resultat.quiz_id)
            .join(models.Matiere, models.Matiere.id == models.Quiz.matiere_id)
            .filter(models.Matiere.nom.ilike(matiere))
        )

    lignes = (
        query.group_by(models.Eleve.id)
        .order_by(func.avg(models.Resultat.score).desc())
        .all()
    )

    classement = [
        schemas.ClassementEntry(
            rang=i + 1,
            matricule=ligne.matricule,
            nom=ligne.nom,
            score_moyen=round(ligne.score_moyen, 2),
            nombre_quiz=ligne.nombre_quiz,
        )
        for i, ligne in enumerate(lignes)
    ]

    return schemas.ClassementResponse(classement=classement)
