"""
Service IA : génère des questions de quiz via l'API Groq pour une matière donnée.
Groq propose un accès gratuit (sans carte bancaire) à des modèles open-weight
performants (Llama, GPT-OSS...), avec des limites de requêtes largement suffisantes
pour un projet comme celui-ci. Toujours appelé côté serveur uniquement — la clé API
ne doit jamais être exposée côté mobile.

Récupérer une clé gratuite sur : https://console.groq.com/keys
"""

import json

from groq import Groq

from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

PROMPT_TEMPLATE = """Tu es un générateur de quiz pour des étudiants universitaires.

Génère {nb_questions} questions à choix multiples de niveau universitaire sur la matière : "{matiere}".
Les questions doivent être précises, variées, et correspondre à un vrai programme universitaire
(pas des questions triviales de niveau secondaire).

Réponds UNIQUEMENT avec un JSON valide, sans aucun texte avant ou après, exactement dans ce format :

{{
  "questions": [
    {{
      "question": "texte de la question",
      "options": ["option A", "option B", "option C", "option D"],
      "reponse_correcte": 0
    }}
  ]
}}

"reponse_correcte" est l'index (0 à 3) de la bonne réponse dans le tableau "options".
"""


def generate_quiz_content(matiere: str, nb_questions: int = 5) -> list[dict]:
    """
    Appelle l'API Groq pour générer une liste de questions.
    Retourne une liste de dicts : {"question": str, "options": [str, ...], "reponse_correcte": int}
    Lève une ValueError si la réponse n'est pas un JSON exploitable.
    """
    prompt = PROMPT_TEMPLATE.format(matiere=matiere, nb_questions=nb_questions)

    reponse = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    texte = reponse.choices[0].message.content.strip()
    # Filet de sécurité si le modèle entoure le JSON de balises markdown
    texte = texte.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(texte)
        questions = data["questions"]
    except (json.JSONDecodeError, KeyError) as erreur:
        raise ValueError(f"Réponse IA invalide, impossible de générer le quiz : {erreur}")

    return questions
