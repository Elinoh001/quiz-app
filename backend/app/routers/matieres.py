from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/matieres", tags=["matieres"])


@router.get("/{nom}", response_model=schemas.MatiereCheckResponse)
def verifier_matiere(nom: str, db: Session = Depends(get_db)):
    matiere = db.query(models.Matiere).filter(models.Matiere.nom.ilike(nom)).first()

    if not matiere:
        return schemas.MatiereCheckResponse(
            nom=nom,
            niveau="inconnu",
            autorise=False,
            message=f"La matière '{nom}' n'existe pas dans la base. Vérifiez l'orthographe ou contactez un administrateur.",
        )

    if matiere.niveau != "universitaire":
        return schemas.MatiereCheckResponse(
            nom=matiere.nom,
            niveau=matiere.niveau,
            autorise=False,
            message=f"'{matiere.nom}' est une matière de niveau {matiere.niveau}. Seules les matières universitaires sont disponibles sur cette application.",
        )

    return schemas.MatiereCheckResponse(
        nom=matiere.nom,
        niveau=matiere.niveau,
        autorise=True,
        message="Matière valide, quiz disponible.",
    )
