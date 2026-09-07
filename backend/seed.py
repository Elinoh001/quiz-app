"""
Script de test : insère quelques élèves et matières pour pouvoir tester
le login et la vérification de matière sans attendre le back-office admin.

Utilisation : python seed.py
"""

from backend.app.database import Base, SessionLocal, engine
from backend.app.models import Eleve, Matiere

Base.metadata.create_all(bind=engine)

db = SessionLocal()

eleves = [
    Eleve(matricule="3230", nom="Rakoto Jean", ecole="ENI Fianarantsoa"),
    Eleve(matricule="3231", nom="Rasoa Marie", ecole="ENI Fianarantsoa"),
]

matieres = [
    Matiere(nom="Algorithmique", niveau="universitaire"),
    Matiere(nom="Base de données", niveau="universitaire"),
    Matiere(nom="Réseaux", niveau="universitaire"),
    Matiere(nom="Systèmes d'exploitation", niveau="universitaire"),
    Matiere(nom="UML", niveau="universitaire"),
    Matiere(nom="Mathématiques", niveau="secondaire"),
]

for e in eleves:
    if not db.query(Eleve).filter_by(matricule=e.matricule).first():
        db.add(e)

for m in matieres:
    if not db.query(Matiere).filter_by(nom=m.nom).first():
        db.add(m)

db.commit()
db.close()

print("Données de test insérées.")
