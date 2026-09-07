from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Eleve(Base):
    __tablename__ = "eleves"

    id = Column(Integer, primary_key=True, index=True)
    matricule = Column(String, unique=True, index=True, nullable=False)
    nom = Column(String, nullable=False)
    ecole = Column(String, nullable=False)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())

    resultats = relationship("Resultat", back_populates="eleve")


class Matiere(Base):
    __tablename__ = "matieres"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, index=True, nullable=False)
    # niveau attendu : "universitaire" ou "secondaire"
    niveau = Column(String, nullable=False, default="universitaire")


class Quiz(Base):
    __tablename__ = "quiz"

    id = Column(Integer, primary_key=True, index=True)
    matiere_id = Column(Integer, ForeignKey("matieres.id"), nullable=False)
    contenu_json = Column(String, nullable=False)  # questions/réponses générées, en JSON
    date_creation = Column(DateTime(timezone=True), server_default=func.now())

    matiere = relationship("Matiere")


class Resultat(Base):
    __tablename__ = "resultats"

    id = Column(Integer, primary_key=True, index=True)
    eleve_id = Column(Integer, ForeignKey("eleves.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable=False)
    score = Column(Float, nullable=False)
    date_passage = Column(DateTime(timezone=True), server_default=func.now())

    eleve = relationship("Eleve", back_populates="resultats")
    quiz = relationship("Quiz")


class Defi(Base):
    __tablename__ = "defis"

    id = Column(Integer, primary_key=True, index=True)
    eleve1_id = Column(Integer, ForeignKey("eleves.id"), nullable=False)
    eleve2_id = Column(Integer, ForeignKey("eleves.id"), nullable=False)
    matiere_id = Column(Integer, ForeignKey("matieres.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable=False)
    statut = Column(String, nullable=False, default="en_attente")  # en_attente, en_cours, termine
    score_eleve1 = Column(Float, nullable=True)
    score_eleve2 = Column(Float, nullable=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    eleve_id = Column(Integer, ForeignKey("eleves.id"), nullable=False)  # destinataire
    defi_id = Column(Integer, ForeignKey("defis.id"), nullable=True)
    message = Column(String, nullable=False)
    lu = Column(Boolean, nullable=False, default=False)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
