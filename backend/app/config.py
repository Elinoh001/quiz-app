import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:Postgres123@localhost:5432/quizapp_db"
    )
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "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")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    ECOLE_NOM: str = os.getenv("ECOLE_NOM", "Mon École")
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "59fee3b0fc3d466d65bc9e50602cd23c7b82d049b2a8eaa4")


settings = Settings()
