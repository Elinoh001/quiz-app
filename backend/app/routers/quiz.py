import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.ai_service import generate_quiz_content

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("/generate", response_model=schemas.QuizResponse)
def generer_quiz(payload: schemas.QuizGenerateRequest, db: Session = Depends(get_db)):
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
            detail=f"'{matiere.nom}' est niveau {matiere.niveau}. "
            "Seules les matières universitaires sont disponibles.",
        )

    # Cache simple : réutilise le dernier quiz généré pour cette matière au lieu
    # de rappeler l'IA à chaque fois. À affiner plus tard (ex: limite d'âge du cache,
    # plusieurs quiz par matière pour varier les questions).
    quiz = (
        db.query(models.Quiz)
        .filter(models.Quiz.matiere_id == matiere.id)
        .order_by(models.Quiz.date_creation.desc())
        .first()
    )

    if quiz:
        questions = json.loads(quiz.contenu_json)
    else:
        try:
            questions = generate_quiz_content(matiere.nom)
        except ValueError as erreur:
            raise HTTPException(status_code=502, detail=str(erreur))

        quiz = models.Quiz(matiere_id=matiere.id, contenu_json=json.dumps(questions))
        db.add(quiz)
        db.commit()
        db.refresh(quiz)

    # Ne jamais renvoyer "reponse_correcte" au client
    questions_publiques = [
        schemas.QuestionPublic(question=q["question"], options=q["options"])
        for q in questions
    ]

    return schemas.QuizResponse(quiz_id=quiz.id, matiere=matiere.nom, questions=questions_publiques)


@router.post("/submit", response_model=schemas.SubmitResponse)
def soumettre_quiz(payload: schemas.SubmitRequest, db: Session = Depends(get_db)):
    quiz = db.query(models.Quiz).filter(models.Quiz.id == payload.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz introuvable.")

    eleve = db.query(models.Eleve).filter(models.Eleve.matricule == payload.matricule).first()
    if not eleve:
        raise HTTPException(status_code=401, detail="Matricule inconnu.")

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

    resultat = models.Resultat(eleve_id=eleve.id, quiz_id=quiz.id, score=score)
    db.add(resultat)
    db.commit()

    return schemas.SubmitResponse(
        score=score,
        bonnes_reponses=bonnes_reponses,
        total_questions=len(questions),
    )
