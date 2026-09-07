from fastapi import APIRouter, Depends, HTTPException
from app import models
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _get_eleve_ou_404(db: Session, matricule: str) -> models.Eleve:
    eleve = db.query(models.Eleve).filter(models.Eleve.matricule == matricule).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève introuvable.")
    return eleve


@router.get("/{matricule}", response_model=schemas.NotificationListResponse)
def lister_notifications(matricule: str, db: Session = Depends(get_db)):
    eleve = _get_eleve_ou_404(db, matricule)

    notifications = (
        db.query(models.Notification)
        .filter(models.Notification.eleve_id == eleve.id)
        .order_by(models.Notification.date_creation.desc())
        .limit(50)
        .all()
    )

    nombre_non_lues = sum(1 for n in notifications if not n.lu)

    return schemas.NotificationListResponse(
        notifications=notifications, nombre_non_lues=nombre_non_lues
    )


@router.post("/{matricule}/tout_marquer_lu")
def marquer_tout_comme_lu(matricule: str, db: Session = Depends(get_db)):
    eleve = _get_eleve_ou_404(db, matricule)

    db.query(models.Notification).filter(
        models.Notification.eleve_id == eleve.id,
        models.Notification.lu.is_(False),
    ).update({"lu": True})
    db.commit()

    return {"message": "Toutes les notifications ont été marquées comme lues."}
