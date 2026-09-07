from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

import theme
from services.api_service import ApiService

KV = """
<DefiCreationScreen>:
    name: "defi_creation"

    canvas.before:
        Color:
            rgba: 0.96, 0.97, 0.99, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: [24, 44, 24, 20]
        spacing: 14

        BoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: "40dp"
            spacing: 8

            TopBackButton:
                on_release: root.manager.current = "home"

            ScreenTitle:
                text: "Défier un élève"

        ScreenSubtitle:
            text: "Choisis la matière et ton adversaire."

        Card:
            size_hint_y: None
            height: "130dp"
            spacing: 10

            FieldLabel:
                text: "MATIÈRE"

            MatiereInput:
                id: matiere_input
                suggestions: []

        Card:
            size_hint_y: None
            height: "110dp"
            spacing: 10

            FieldLabel:
                text: "ADVERSAIRE"

            EleveInput:
                id: adversaire_input
                suggestions: []

        StatusLabel:
            id: message_label
            text: ""

        PrimaryButton:
            text: "Lancer le défi"
            on_release: root.lancer_defi()

        GhostButton:
            text: "Voir mes défis"
            on_release: root.manager.current = "defis_liste"
"""

Builder.load_string(KV)


class DefiCreationScreen(Screen):

    def on_pre_enter(self):
        self.charger_matieres()
        self.charger_eleves()

    def charger_matieres(self):
        succes, resultat = ApiService.lister_matieres()
        if succes:
            if resultat and isinstance(resultat[0], dict):
                suggestions = [m.get("nom") for m in resultat if "nom" in m]
            else:
                suggestions = resultat
            self.ids.matiere_input.suggestions = suggestions
        else:
            self.ids.matiere_input.suggestions = [
                "Algorithmique", "Base de données", "Réseaux",
                "Systèmes d'exploitation", "UML", "Mathématiques"
            ]

    def charger_eleves(self):
        succes, resultat = ApiService.lister_eleves()
        if succes:
            # On suppose que resultat est une liste de dicts avec "matricule" et "nom"
            suggestions = [f"{e['matricule']} - {e['nom']}" for e in resultat]
            self.ids.adversaire_input.suggestions = suggestions
        else:
            self.ids.adversaire_input.suggestions = []

    def lancer_defi(self):
        matiere = self.ids.matiere_input.get_text()
        adversaire_texte = self.ids.adversaire_input.get_text()

        if not matiere:
            self.ids.message_label.color = theme.ERROR
            self.ids.message_label.text = "Veuillez choisir une matière."
            return

        if not adversaire_texte:
            self.ids.message_label.color = theme.ERROR
            self.ids.message_label.text = "Veuillez choisir un adversaire."
            return

        # Extraire le matricule si le format "matricule - nom" a été utilisé
        if " - " in adversaire_texte:
            adversaire = adversaire_texte.split(" - ")[0].strip()
        else:
            adversaire = adversaire_texte.strip()

        mon_matricule = self.manager.eleve_connecte["matricule"]

        self.ids.message_label.color = theme.TEXT_MUTED
        self.ids.message_label.text = "Création du défi en cours..."

        succes, resultat = ApiService.creer_defi(mon_matricule, adversaire, matiere)

        if succes:
            quiz_screen = self.manager.get_screen("quiz")
            quiz_screen.charger_quiz(resultat["quiz"], defi_id=resultat["defi_id"])
            self.ids.message_label.text = ""
            self.manager.current = "quiz"
        else:
            self.ids.message_label.color = theme.ERROR
            self.ids.message_label.text = str(resultat)