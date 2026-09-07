from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

from services.api_service import ApiService

KV = """
<QuizScreen>:
    name: "quiz"

    BoxLayout:
        orientation: "vertical"
        padding: 30
        spacing: 15

        Label:
            id: matiere_label
            text: ""
            font_size: 18
            size_hint_y: 0.1

        Label:
            id: progression_label
            text: ""
            size_hint_y: 0.1

        Label:
            id: question_label
            text: ""
            font_size: 20
            size_hint_y: 0.3
            text_size: self.width, None

        BoxLayout:
            id: options_container
            orientation: "vertical"
            spacing: 10
            size_hint_y: 0.4

        Label:
            id: resultat_label
            text: ""
            font_size: 22
            size_hint_y: 0.1

        Button:
            id: bouton_retour
            text: "Retour à l'accueil"
            size_hint_y: 0.1
            opacity: 0
            disabled: True
            on_release: root.manager.current = "home"
"""

Builder.load_string(KV)


class QuizScreen(Screen):

    quiz_id = None
    defi_id = None  # None = quiz normal, sinon = ce quiz fait partie d'un défi
    questions = []
    index_courant = 0
    reponses_donnees = []

    def charger_quiz(self, quiz_data, defi_id=None):
        """Appelé par HomeScreen (quiz normal) ou DefiScreen (défi) une fois le quiz prêt."""
        self.quiz_id = quiz_data["quiz_id"]
        self.defi_id = defi_id
        self.questions = quiz_data["questions"]
        self.index_courant = 0
        self.reponses_donnees = []
        suffixe = " (Défi)" if defi_id else ""
        self.ids.matiere_label.text = f"Matière : {quiz_data['matiere']}{suffixe}"
        self.ids.resultat_label.text = ""
        self.ids.bouton_retour.opacity = 0
        self.ids.bouton_retour.disabled = True
        self.afficher_question()

    def afficher_question(self):
        question = self.questions[self.index_courant]
        total = len(self.questions)

        self.ids.progression_label.text = f"Question {self.index_courant + 1} / {total}"
        self.ids.question_label.text = question["question"]

        self.ids.options_container.clear_widgets()
        for index_option, texte_option in enumerate(question["options"]):
            bouton = Button(text=texte_option)
            bouton.bind(on_release=lambda instance, i=index_option: self.choisir_reponse(i))
            self.ids.options_container.add_widget(bouton)

    def choisir_reponse(self, index_choisi):
        self.reponses_donnees.append(index_choisi)

        if self.index_courant + 1 < len(self.questions):
            self.index_courant += 1
            self.afficher_question()
        else:
            self.terminer_quiz()

    def terminer_quiz(self):
        self.ids.question_label.text = ""
        self.ids.options_container.clear_widgets()
        self.ids.progression_label.text = ""
        self.ids.resultat_label.text = "Calcul du score..."

        matricule = self.manager.eleve_connecte["matricule"]

        if self.defi_id:
            succes, resultat = ApiService.soumettre_defi(self.defi_id, matricule, self.reponses_donnees)
        else:
            succes, resultat = ApiService.soumettre_quiz(self.quiz_id, matricule, self.reponses_donnees)

        if succes and self.defi_id:
            texte = (
                f"Ton score : {resultat['score']}%  "
                f"({resultat['bonnes_reponses']}/{resultat['total_questions']} bonnes réponses)\n"
            )
            if resultat["adversaire_a_joue"]:
                texte += f"Résultat du défi : {resultat['resultat_final']}"
            else:
                texte += "En attente que l'adversaire joue son quiz."
            self.ids.resultat_label.text = texte
        elif succes:
            self.ids.resultat_label.text = (
                f"Score : {resultat['score']}%  "
                f"({resultat['bonnes_reponses']}/{resultat['total_questions']} bonnes réponses)"
            )
        else:
            self.ids.resultat_label.text = f"Erreur : {resultat}"

        self.ids.bouton_retour.opacity = 1
        self.ids.bouton_retour.disabled = False
