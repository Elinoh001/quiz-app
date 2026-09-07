from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


def verifier_cle_admin(x_admin_key: str = Header(...)):
    """
    Dépendance de sécurité : toutes les routes admin exigent l'en-tête
    'X-Admin-Key' correspondant à ADMIN_API_KEY défini dans .env.
    Volontairement simple (pas de vrai système d'utilisateurs) mais suffisant
    pour empêcher n'importe qui d'appeler ces routes.
    """
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Clé d'administration invalide.")


# ---------- Élèves ----------

@router.get("/eleves", response_model=list[schemas.EleveAdminResponse], dependencies=[Depends(verifier_cle_admin)])
def lister_eleves(db: Session = Depends(get_db)):
    return db.query(models.Eleve).order_by(models.Eleve.nom).all()


@router.post("/eleves", response_model=schemas.EleveAdminResponse, dependencies=[Depends(verifier_cle_admin)])
def creer_eleve(payload: schemas.EleveCreate, db: Session = Depends(get_db)):
    if db.query(models.Eleve).filter(models.Eleve.matricule == payload.matricule).first():
        raise HTTPException(status_code=400, detail="Ce matricule existe déjà.")

    eleve = models.Eleve(matricule=payload.matricule, nom=payload.nom, ecole=payload.ecole)
    db.add(eleve)
    db.commit()
    db.refresh(eleve)
    return eleve


@router.put("/eleves/{eleve_id}", response_model=schemas.EleveAdminResponse, dependencies=[Depends(verifier_cle_admin)])
def modifier_eleve(eleve_id: int, payload: schemas.EleveUpdate, db: Session = Depends(get_db)):
    eleve = db.query(models.Eleve).filter(models.Eleve.id == eleve_id).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève introuvable.")

    if payload.matricule is not None:
        eleve.matricule = payload.matricule
    if payload.nom is not None:
        eleve.nom = payload.nom
    if payload.ecole is not None:
        eleve.ecole = payload.ecole

    db.commit()
    db.refresh(eleve)
    return eleve


@router.delete("/eleves/{eleve_id}", dependencies=[Depends(verifier_cle_admin)])
def supprimer_eleve(eleve_id: int, db: Session = Depends(get_db)):
    eleve = db.query(models.Eleve).filter(models.Eleve.id == eleve_id).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève introuvable.")

    db.delete(eleve)
    db.commit()
    return {"message": "Élève supprimé."}


# ---------- Matières ----------

@router.get("/matieres", response_model=list[schemas.MatiereAdminResponse], dependencies=[Depends(verifier_cle_admin)])
def lister_matieres(db: Session = Depends(get_db)):
    return db.query(models.Matiere).order_by(models.Matiere.nom).all()


@router.post("/matieres", response_model=schemas.MatiereAdminResponse, dependencies=[Depends(verifier_cle_admin)])
def creer_matiere(payload: schemas.MatiereCreate, db: Session = Depends(get_db)):
    if payload.niveau not in ("universitaire", "secondaire"):
        raise HTTPException(status_code=400, detail="Le niveau doit être 'universitaire' ou 'secondaire'.")

    if db.query(models.Matiere).filter(models.Matiere.nom.ilike(payload.nom)).first():
        raise HTTPException(status_code=400, detail="Cette matière existe déjà.")

    matiere = models.Matiere(nom=payload.nom, niveau=payload.niveau)
    db.add(matiere)
    db.commit()
    db.refresh(matiere)
    return matiere


@router.put("/matieres/{matiere_id}", response_model=schemas.MatiereAdminResponse, dependencies=[Depends(verifier_cle_admin)])
def modifier_matiere(matiere_id: int, payload: schemas.MatiereUpdate, db: Session = Depends(get_db)):
    matiere = db.query(models.Matiere).filter(models.Matiere.id == matiere_id).first()
    if not matiere:
        raise HTTPException(status_code=404, detail="Matière introuvable.")

    if payload.niveau is not None and payload.niveau not in ("universitaire", "secondaire"):
        raise HTTPException(status_code=400, detail="Le niveau doit être 'universitaire' ou 'secondaire'.")

    if payload.nom is not None:
        matiere.nom = payload.nom
    if payload.niveau is not None:
        matiere.niveau = payload.niveau

    db.commit()
    db.refresh(matiere)
    return matiere


@router.delete("/matieres/{matiere_id}", dependencies=[Depends(verifier_cle_admin)])
def supprimer_matiere(matiere_id: int, db: Session = Depends(get_db)):
    matiere = db.query(models.Matiere).filter(models.Matiere.id == matiere_id).first()
    if not matiere:
        raise HTTPException(status_code=404, detail="Matière introuvable.")

    db.delete(matiere)
    db.commit()
    return {"message": "Matière supprimée."}
