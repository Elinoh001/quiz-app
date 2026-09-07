from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import quiz
from app.routers import admin
from app.routers import auth
from app.routers import classement
from app.routers import defis
from app.routers import historique
from app.routers import matieres
from app.routers import notifications
from app.routers import eleves   # <-- ajout de l'import manquant

# Crée les tables si elles n'existent pas encore
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quiz App API", version="0.1.0")

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
app.include_router(eleves.router)   # <-- maintenant reconnu


@app.get("/")
def root():
    return {"message": "Quiz App API en ligne"}