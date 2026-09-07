from kivy.factory import Factory
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

import theme
from services.api_service import ApiService

KV = """
<QuizScreen>:
    name: "quiz"

    canvas.before:
        Color:
            rgba: 0.96, 0.97, 0.99, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: [24, 44, 24, 24]
        spacing: 14

        BoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: "24dp"

            Label:
                id: matiere_label
                text: ""
                font_size: "13sp"
                bold: True
                color: 0.29, 0.33, 0.90, 1
                halign: "left"
                valign: "middle"
                text_size: self.width, None

            Label:
                id: progression_label
                text: ""
                font_size: "13sp"
                color: 0.45, 0.48, 0.55, 1
                halign: "right"
                valign: "middle"
                text_size: self.width, None

        # Carte progression avec barre
        Card:
            size_hint_y: None
            height: "70dp"
            padding: [16, 10]
            spacing: 6

            BoxLayout:
                orientation: "vertical"
                spacing: 4

                Label:
                    text: "Progression"
                    font_size: "11sp"
                    color: 0.45, 0.48, 0.55, 1
                    size_hint_y: None
                    height: "16dp"

                ProgressTrack:
                    id: progress_track
                    progress: 0

        # Carte question
        Card:
            id: question_card
            size_hint_y: None
            height: self.minimum_height
            padding: [20, 18]

            Label:
                id: question_label
                text: ""
                font_size: "19sp"
                bold: True
                color: 0.12, 0.14, 0.20, 1
                size_hint_y: None
                height: self.texture_size[1]
                halign: "left"
                valign: "top"
                text_size: self.width, None

        # Options dans un ScrollView
        ScrollView:
            do_scroll_x: False

            BoxLayout:
                id: options_container
                orientation: "vertical"
                spacing: 10
                size_hint_y: None
                height: self.minimum_height
                padding: [0, 8, 0, 8]

        # Carte résultat avec pastille
        Card:
            id: resultat_card
            size_hint_y: None
            height: self.minimum_height if resultat_label.text else 0
            opacity: 1 if resultat_label.text else 0
            padding: [16, 14]
            spacing: 8

            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: "30dp"
                spacing: 12

                Label:
                    id: pastille_score
                    text: ""
                    size_hint_x: None
                    width: "60dp"
                    font_size: "16sp"
                    bold: True
                    color: 1, 1, 1, 1
                    halign: "center"
                    valign: "middle"
                    canvas.before:
                        Color:
                            rgba: self.background_color if hasattr(self, 'background_color') else (0.11, 0.68, 0.40, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]

                Label:
                    id: resultat_label
                    text: ""
                    font_size: "16sp"
                    bold: True
                    color: 0.12, 0.14, 0.20, 1
                    size_hint_y: None
                    height: self.texture_size[1]
                    halign: "left"
                    valign: "middle"
                    text_size: self.width, None

        PrimaryButton:
            id: bouton_retour
            text: "Retour à l'accueil"
            opacity: 0
            disabled: True
            on_release: root.manager.current = "home"
"""

Builder.load_string(KV)


class QuizScreen(Screen):
    quiz_id = None
    defi_id = None
    questions = []
    index_courant = 0
    reponses_donnees = []

    def charger_quiz(self, quiz_data, defi_id=None):
        self.quiz_id = quiz_data["quiz_id"]
        self.defi_id = defi_id
        self.questions = quiz_data["questions"]
        self.index_courant = 0
        self.reponses_donnees = []
        suffixe = " · DÉFI" if defi_id else ""
        self.ids.matiere_label.text = f"{quiz_data['matiere'].upper()}{suffixe}"
        self.ids.resultat_label.text = ""
        self.ids.pastille_score.text = ""
        self.ids.bouton_retour.opacity = 0
        self.ids.bouton_retour.disabled = True
        self.afficher_question()

    def afficher_question(self):
        question = self.questions[self.index_courant]
        total = len(self.questions)

        self.ids.progression_label.text = f"Question {self.index_courant + 1} / {total}"
        self.ids.progress_track.progress = (self.index_courant) / total
        self.ids.question_label.text = question["question"]

        self.ids.options_container.clear_widgets()
        lettres = ["A", "B", "C", "D", "E", "F"]
        OptionButton = Factory.OptionButton
        for index_option, texte_option in enumerate(question["options"]):
            lettre = lettres[index_option] if index_option < len(lettres) else str(index_option + 1)
            bouton = OptionButton(text=f"{lettre}.  {texte_option}")
            bouton.bind(on_release=lambda instance, i=index_option: self.choisir_reponse(i))
            self.ids.options_container.add_widget(bouton)

    def choisir_reponse(self, index_choisi):
        self.reponses_donnees.append(index_choisi)

        if self.index_courant + 1 < len(self.questions):
            self.index_courant += 1
            self.afficher_question()
        else:
            self.ids.progress_track.progress = 1
            self.terminer_quiz()

    def terminer_quiz(self):
        self.ids.question_label.text = ""
        self.ids.options_container.clear_widgets()
        self.ids.progression_label.text = "Terminé"
        self.ids.resultat_label.text = "Calcul du score..."

        matricule = self.manager.eleve_connecte["matricule"]

        if self.defi_id:
            succes, resultat = ApiService.soumettre_defi(self.defi_id, matricule, self.reponses_donnees)
        else:
            succes, resultat = ApiService.soumettre_quiz(self.quiz_id, matricule, self.reponses_donnees)

        if succes and self.defi_id:
            score = resultat['score']
            texte = (
                f"Ton score : {score}%\n"
                f"{resultat['bonnes_reponses']}/{resultat['total_questions']} bonnes réponses\n\n"
            )
            if resultat["adversaire_a_joue"]:
                texte += f"Résultat du défi : {resultat['resultat_final']}"
            else:
                texte += "En attente que l'adversaire joue son quiz."
            self.ids.resultat_label.text = texte
        elif succes:
            score = resultat['score']
            self.ids.resultat_label.text = (
                f"Score : {score}%\n"
                f"{resultat['bonnes_reponses']}/{resultat['total_questions']} bonnes réponses"
            )
        else:
            self.ids.resultat_label.text = f"Erreur : {resultat}"
            score = 0

        # Mise à jour de la pastille
        pastille = self.ids.pastille_score
        pastille.text = f"{score}%"
        if score >= 50:
            pastille.background_color = (0.11, 0.68, 0.40, 1)  # vert
        else:
            pastille.background_color = (0.90, 0.26, 0.30, 1)  # rouge

        self.ids.bouton_retour.opacity = 1
        self.ids.bouton_retour.disabled = False