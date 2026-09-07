from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import admin, auth, classement, defis, historique, matieres, notifications, quiz

# Crée les tables si elles n'existent pas encore (suffisant pour le développement ;
# pour la prod, utiliser Alembic pour gérer les migrations proprement)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quiz App API", version="0.1.0")

# Autorise l'interface d'admin (fichier HTML statique) à appeler l'API depuis
# n'importe quelle origine. À restreindre à un domaine précis en production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(matieres.router)
app.include_router(quiz.router)
app.include_router(classement.router)
app.include_router(defis.router)
app.include_router(admin.router)
app.include_router(notifications.router)
app.include_router(historique.router)


@app.get("/")
def root():
    return {"message": "Quiz App API en ligne"}
