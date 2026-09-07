"""
Couche Service : centralise tous les appels HTTP vers le backend.
Les écrans ne doivent jamais appeler `requests` directement — ils passent par ici,
comme le pattern Repository déjà utilisé dans FormForge.
"""

import requests

# À remplacer par l'URL réelle du serveur une fois déployé
BASE_URL = "http://127.0.0.1:8000"


class ApiService:

    @staticmethod
    def login(matricule: str):
        """
        Tente une connexion par matricule.
        Retourne (succes: bool, donnees_ou_message: dict|str)
        """
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"matricule": matricule},
                timeout=5,
            )
            if response.status_code == 200:
                return True, response.json()
            return False, response.json().get("detail", "Erreur de connexion.")
        except requests.exceptions.RequestException:
            return False, "Impossible de joindre le serveur. Vérifiez votre connexion."

    @staticmethod
    def verifier_matiere(nom_matiere: str):
        """
        Vérifie si une matière est disponible (universitaire) avant de lancer un quiz.
        Retourne (autorise: bool, message: str)
        """
        try:
            response = requests.get(f"{BASE_URL}/matieres/{nom_matiere}", timeout=5)
            data = response.json()
            return data.get("autorise", False), data.get("message", "")
        except requests.exceptions.RequestException:
            return False, "Impossible de joindre le serveur. Vérifiez votre connexion."

    @staticmethod
    def lister_matieres():
        """
        Récupère la liste des matières universitaires disponibles (noms uniquement).
        Retourne (succes: bool, donnees_ou_message: list|str)
        Le backend renvoie une liste de chaînes, ex: ["Algorithmique", "Base de données", ...]
        """
        try:
            response = requests.get(f"{BASE_URL}/matieres", timeout=10)
            if response.status_code == 200:
                return True, response.json()
            return False, "Erreur lors de la récupération des matières."
        except requests.exceptions.RequestException:
            return False, "Impossible de joindre le serveur. Vérifiez votre connexion."

    @staticmethod
    def lister_eleves():
        """
        Récupère la liste des élèves (matricule, nom, etc.) pour peupler
        le champ adversaire dans la création de défi.
        Retourne (succes: bool, donnees_ou_message: list|str)
        La liste est généralement une liste de dictionnaires.
        """
        try:
            # Utiliser un endpoint public (à implémenter côté backend)
            response = requests.get(f"{BASE_URL}/eleves", timeout=10)
            if response.status_code == 200:
                return True, response.json()
            return False, "Erreur lors de la récupération des élèves."
        except requests.exceptions.RequestException:
            return False, "Impossible de joindre le serveur. Vérifiez votre connexion."

    @staticmethod
    def generer_quiz(nom_matiere: str):
        """
        Demande la génération (ou récupération en cache) d'un quiz pour une matière.
        Retourne (succes: bool, donnees_ou_message: dict|str)
        """
        try:
            response = requests.post(
                f"{BASE_URL}/quiz/generate",
                json={"matiere": nom_matiere},
                timeout=30,  # la génération IA peut prendre quelques secondes
            )
            if response.status_code == 200:
                return True, response.json()
            return False, response.json().get("detail", "Erreur lors de la génération du quiz.")
        except requests.exceptions.RequestException:
            return False, "Impossible de joindre le serveur. Vérifiez votre connexion."

    @staticmethod
    def soumettre_quiz(quiz_id: int, matricule: str, reponses: list):
        """
        Envoie les réponses de l'élève et récupère le score.
        Retourne (succes: bool, donnees_ou_message: dict|str)
        """
        try:
            response = requests.post(
                f"{BASE_URL}/quiz/submit",
                json={"quiz_id": quiz_id, "matricule": matricule, "reponses": reponses},
                timeout=10,
            )
            if response.status_code == 200:
                return True, response.json()
            return False, response.json().get("detail", "Erreur lors de la soumission.")
        except requests.exceptions.RequestException:
            return False, "Impossible de joindre le serveur. Vérifiez votre connexion."

    @staticmethod
    def obtenir_classement(matiere: str = None):
        """
        Récupère le classement général, ou filtré sur une matière si précisée.
        Retourne (succes: bool, donnees_ou_message: list|str)
        """
        try:
            params = {"matiere": matiere} if matiere else {}
            response = requests.get(f"{BASE_URL}/classement", params=params, timeout=10)
            if response.status_code == 200:
                return True, response.json()["classement"]
            return False, "Erreur lors de la récupération du classement."
        except requests.exceptions.RequestException:
            return False, "Impossible de joindre le serveur. Vérifiez votre connexion."

    @staticmethod
    def creer_defi(matricule_initiateur: str, matricule_adversaire: str, matiere: str):
        """
        Crée un défi entre deux élèves sur une matière donnée.
        Retourne (succes: bool, donnees_ou_message: dict|str)
        """
        try:
            response = requests.post(
                f"{BASE_URL}/defis/creer",
                json={
                    "matricule_initiateur": matricule_initiateur,
                    "matricule_adversaire": matricule_adversaire,
                    "matiere": matiere,
                },
                timeout=30,
            )
            if response.status_code == 200:
                return True, response.json()
            return False, response.json().get("detail", "Erreur lors de la création du défi.")
        except requests.exceptions.RequestException:
            return False, "Impossible de joindre le serveur. Vérifiez votre connexion."

    @staticmethod
    def soumettre_defi(defi_id: int, matricule: str, reponses: list):
        """
        Envoie les réponses d'un élève pour un défi en cours.
        Retourne (succes: bool, donnees_ou_message: dict|str)
        """
        try:
            response = requests.post(
                f"{BASE_URL}/defis/{defi_id}/soumettre",
                json={"defi_id": defi_id, "matricule": matricule, "reponses": reponses},
                timeout=10,
            )
            if response.status_code == 200:
                return True, response.json()
            return False, response.json().get("detail", "Erreur lors de la soumission du défi.")
        except requests.exceptions.RequestException:
            return False, "Impossible de joindre le serveur. Vérifiez votre connexion."

    @staticmethod
    def lister_defis(matricule: str):
        """
        Récupère la liste des défis (en cours et terminés) d'un élève.
        Retourne (succes: bool, donnees_ou_message: list|str)
        """
        try:
            response = requests.get(f"{BASE_URL}/defis/{matricule}/liste", timeout=10)
            if response.status_code == 200:
                return True, response.json()["defis"]
            return False, "Erreur lors de la récupération des défis."
        except requests.exceptions.RequestException:
            return False, "Impossible de joindre le serveur. Vérifiez votre connexion."

    @staticmethod
    def obtenir_notifications(matricule: str):
        """
        Récupère les notifications d'un élève ainsi que le nombre de non lues.
        Retourne (succes: bool, donnees_ou_message: dict|str)
        Le dict contient : {"notifications": [...], "nombre_non_lues": int}
        """
        try:
            response = requests.get(f"{BASE_URL}/notifications/{matricule}", timeout=10)
            if response.status_code == 200:
                return True, response.json()
            return False, "Erreur lors de la récupération des notifications."
        except requests.exceptions.RequestException:
            return False, "Impossible de joindre le serveur. Vérifiez votre connexion."

    @staticmethod
    def marquer_notifications_lues(matricule: str):
        """
        Marque toutes les notifications d'un élève comme lues.
        Retourne (succes: bool, message: str)
        """
        try:
            response = requests.post(f"{BASE_URL}/notifications/{matricule}/tout_marquer_lu", timeout=10)
            if response.status_code == 200:
                return True, "OK"
            return False, "Erreur lors de la mise à jour des notifications."
        except requests.exceptions.RequestException:
            return False, "Impossible de joindre le serveur. Vérifiez votre connexion."

    @staticmethod
    def obtenir_historique(matricule: str):
        """
        Récupère l'historique des quiz passés par un élève (matière, score, date),
        avec la moyenne générale et le nombre total de quiz.
        Retourne (succes: bool, donnees_ou_message: dict|str)
        """
        try:
            response = requests.get(f"{BASE_URL}/historique/{matricule}", timeout=10)
            if response.status_code == 200:
                return True, response.json()
            return False, "Erreur lors de la récupération de l'historique."
        except requests.exceptions.RequestException:
            return False, "Impossible de joindre le serveur. Vérifiez votre connexion."