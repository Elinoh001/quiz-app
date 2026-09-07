import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.ai_service import generate_quiz_content

router = APIRouter(prefix="/defis", tags=["defis"])


def _get_eleve_ou_404(db: Session, matricule: str, label: str = "Élève") -> models.Eleve:
    eleve = db.query(models.Eleve).filter(models.Eleve.matricule == matricule).first()
    if not eleve:
        raise HTTPException(status_code=404, detail=f"{label} avec matricule '{matricule}' introuvable.")
    return eleve


def _notifier(db: Session, eleve_id: int, message: str, defi_id: int = None):
    notification = models.Notification(eleve_id=eleve_id, message=message, defi_id=defi_id)
    db.add(notification)


@router.post("/creer", response_model=schemas.DefiQuizResponse)
def creer_defi(payload: schemas.DefiCreateRequest, db: Session = Depends(get_db)):
    initiateur = _get_eleve_ou_404(db, payload.matricule_initiateur, "Initiateur")
    adversaire = _get_eleve_ou_404(db, payload.matricule_adversaire, "Adversaire")

    if initiateur.id == adversaire.id:
        raise HTTPException(status_code=400, detail="Impossible de se défier soi-même.")

    matiere = (
        db.query(models.Matiere)
        .filter(models.Matiere.nom.ilike(payload.matiere))
        .first()
    )
    if not matiere:
        raise HTTPException(status_code=404, detail=f"Matière '{payload.matiere}' introuvable.")
    if matiere.niveau != "universitaire":
        raise HTTPException(
            status_code=403,
            detail=f"'{matiere.nom}' est niveau {matiere.niveau}. Non disponible pour un défi.",
        )

    # Un quiz dédié est généré pour chaque défi, pour garantir que les deux élèves
    # répondent exactement aux mêmes questions (comparaison équitable).
    try:
        questions = generate_quiz_content(matiere.nom)
    except ValueError as erreur:
        raise HTTPException(status_code=502, detail=str(erreur))

    quiz = models.Quiz(matiere_id=matiere.id, contenu_json=json.dumps(questions))
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    defi = models.Defi(
        eleve1_id=initiateur.id,
        eleve2_id=adversaire.id,
        matiere_id=matiere.id,
        quiz_id=quiz.id,
        statut="en_attente",
    )
    db.add(defi)
    db.commit()
    db.refresh(defi)

    _notifier(
        db,
        adversaire.id,
        f"{initiateur.nom} t'a défié en {matiere.nom} ! Réponds au quiz pour tenter de gagner.",
        defi_id=defi.id,
    )
    db.commit()

    questions_publiques = [
        schemas.QuestionPublic(question=q["question"], options=q["options"]) for q in questions
    ]

    return schemas.DefiQuizResponse(
        defi_id=defi.id, quiz_id=quiz.id, matiere=matiere.nom, questions=questions_publiques
    )


@router.post("/{defi_id}/soumettre", response_model=schemas.DefiSubmitResponse)
def soumettre_defi(defi_id: int, payload: schemas.DefiSubmitRequest, db: Session = Depends(get_db)):
    defi = db.query(models.Defi).filter(models.Defi.id == defi_id).first()
    if not defi:
        raise HTTPException(status_code=404, detail="Défi introuvable.")

    eleve = _get_eleve_ou_404(db, payload.matricule)

    if eleve.id not in (defi.eleve1_id, defi.eleve2_id):
        raise HTTPException(status_code=403, detail="Vous ne faites pas partie de ce défi.")

    quiz = db.query(models.Quiz).filter(models.Quiz.id == defi.quiz_id).first()
    questions = json.loads(quiz.contenu_json)

    if len(payload.reponses) != len(questions):
        raise HTTPException(
            status_code=400,
            detail=f"Nombre de réponses incorrect : {len(questions)} attendues.",
        )

    bonnes_reponses = sum(
        1
        for reponse_eleve, question in zip(payload.reponses, questions)
        if reponse_eleve == question["reponse_correcte"]
    )
    score = round((bonnes_reponses / len(questions)) * 100, 2)

    if eleve.id == defi.eleve1_id:
        defi.score_eleve1 = score
    else:
        defi.score_eleve2 = score

    adversaire_a_joue = defi.score_eleve1 is not None and defi.score_eleve2 is not None
    resultat_final = None

    autre_id = defi.eleve2_id if eleve.id == defi.eleve1_id else defi.eleve1_id

    if adversaire_a_joue:
        defi.statut = "termine"
        if defi.score_eleve1 > defi.score_eleve2:
            gagnant_id = defi.eleve1_id
        elif defi.score_eleve2 > defi.score_eleve1:
            gagnant_id = defi.eleve2_id
        else:
            gagnant_id = None

        if gagnant_id is None:
            resultat_final = "Égalité"
        else:
            resultat_final = "Victoire" if gagnant_id == eleve.id else "Défaite"

        # Le deuxième joueur vient de répondre : on notifie le premier joueur
        # (qui attendait) avec le résultat final vu de son côté.
        if gagnant_id is None:
            message_autre = f"Ton défi contre {eleve.nom} est terminé : Égalité !"
        elif gagnant_id == autre_id:
            message_autre = f"Ton défi contre {eleve.nom} est terminé : Victoire !"
        else:
            message_autre = f"Ton défi contre {eleve.nom} est terminé : Défaite."

        _notifier(db, autre_id, message_autre, defi_id=defi.id)
    else:
        defi.statut = "en_cours"
        # Premier joueur à répondre : on notifie l'adversaire qu'il doit jouer.
        _notifier(
            db,
            autre_id,
            f"{eleve.nom} a répondu à ton défi. À toi de jouer pour voir le résultat !",
            defi_id=defi.id,
        )

    db.commit()

    return schemas.DefiSubmitResponse(
        score=score,
        bonnes_reponses=bonnes_reponses,
        total_questions=len(questions),
        adversaire_a_joue=adversaire_a_joue,
        resultat_final=resultat_final,
    )


@router.get("/{matricule}/liste", response_model=schemas.DefiListResponse)
def lister_defis(matricule: str, db: Session = Depends(get_db)):
    eleve = _get_eleve_ou_404(db, matricule)

    defis = (
        db.query(models.Defi)
        .filter((models.Defi.eleve1_id == eleve.id) | (models.Defi.eleve2_id == eleve.id))
        .order_by(models.Defi.date_creation.desc())
        .all()
    )

    entrees = []
    for defi in defis:
        est_eleve1 = defi.eleve1_id == eleve.id
        adversaire_id = defi.eleve2_id if est_eleve1 else defi.eleve1_id
        adversaire = db.query(models.Eleve).filter(models.Eleve.id == adversaire_id).first()
        matiere = db.query(models.Matiere).filter(models.Matiere.id == defi.matiere_id).first()

        entrees.append(
            schemas.DefiEntry(
                defi_id=defi.id,
                matiere=matiere.nom if matiere else "?",
                adversaire_nom=adversaire.nom if adversaire else "?",
                adversaire_matricule=adversaire.matricule if adversaire else "?",
                statut=defi.statut,
                mon_score=defi.score_eleve1 if est_eleve1 else defi.score_eleve2,
                score_adversaire=defi.score_eleve2 if est_eleve1 else defi.score_eleve1,
            )
        )

    return schemas.DefiListResponse(defis=entrees)
