from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    matricule: str


class EleveResponse(BaseModel):
    id: int
    matricule: str
    nom: str
    ecole: str

    class Config:
        from_attributes = True


class MatiereCheckResponse(BaseModel):
    nom: str
    niveau: str
    autorise: bool
    message: str


class QuizGenerateRequest(BaseModel):
    matiere: str


class QuestionPublic(BaseModel):
    """Question envoyée au client — sans la bonne réponse."""
    question: str
    options: list[str]


class QuizResponse(BaseModel):
    quiz_id: int
    matiere: str
    questions: list[QuestionPublic]


class SubmitRequest(BaseModel):
    quiz_id: int
    matricule: str
    reponses: list[int]  # index choisi par l'élève pour chaque question, dans l'ordre


class SubmitResponse(BaseModel):
    score: float  # pourcentage, ex: 80.0
    bonnes_reponses: int
    total_questions: int


class ClassementEntry(BaseModel):
    rang: int
    matricule: str
    nom: str
    score_moyen: float
    nombre_quiz: int


class ClassementResponse(BaseModel):
    classement: list[ClassementEntry]


class DefiCreateRequest(BaseModel):
    matricule_initiateur: str
    matricule_adversaire: str
    matiere: str


class DefiQuizResponse(BaseModel):
    defi_id: int
    quiz_id: int
    matiere: str
    questions: list[QuestionPublic]


class DefiSubmitRequest(BaseModel):
    defi_id: int
    matricule: str
    reponses: list[int]


class DefiSubmitResponse(BaseModel):
    score: float
    bonnes_reponses: int
    total_questions: int
    adversaire_a_joue: bool
    # "Victoire" / "Défaite" / "Égalité" une fois les deux joueurs passés, sinon None
    resultat_final: Optional[str] = None


class DefiEntry(BaseModel):
    defi_id: int
    matiere: str
    adversaire_nom: str
    adversaire_matricule: str
    statut: str
    mon_score: Optional[float] = None
    score_adversaire: Optional[float] = None


class DefiListResponse(BaseModel):
    defis: list[DefiEntry]


# --- Administration (élèves et matières) ---

class EleveCreate(BaseModel):
    matricule: str
    nom: str
    ecole: str


class EleveUpdate(BaseModel):
    matricule: Optional[str] = None
    nom: Optional[str] = None
    ecole: Optional[str] = None


class EleveAdminResponse(BaseModel):
    id: int
    matricule: str
    nom: str
    ecole: str

    class Config:
        from_attributes = True


class MatiereCreate(BaseModel):
    nom: str
    niveau: str  # "universitaire" ou "secondaire"


class MatiereUpdate(BaseModel):
    nom: Optional[str] = None
    niveau: Optional[str] = None


class MatiereAdminResponse(BaseModel):
    id: int
    nom: str
    niveau: str

    class Config:
        from_attributes = True


# --- Notifications ---

class NotificationResponse(BaseModel):
    id: int
    message: str
    lu: bool
    defi_id: Optional[int] = None
    date_creation: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    nombre_non_lues: int


# --- Historique ---

class HistoriqueEntry(BaseModel):
    matiere: str
    score: float
    date_passage: datetime


class HistoriqueResponse(BaseModel):
    historique: list[HistoriqueEntry]
    moyenne_generale: float
    nombre_quiz: int
