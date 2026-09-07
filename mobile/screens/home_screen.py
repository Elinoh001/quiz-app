from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

import theme
from services.api_service import ApiService

KV = """
<HomeScreen>:
    name: "home"

    canvas.before:
        Color:
            rgba: 0.96, 0.97, 0.99, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: [24, 44, 24, 20]
        spacing: 16

        Label:
            id: bienvenue_label
            text: "Bonjour !"
            font_size: "22sp"
            bold: True
            color: 0.12, 0.14, 0.20, 1
            size_hint_y: None
            height: "30dp"
            halign: "left"
            valign: "middle"
            text_size: self.width, None

        ScreenSubtitle:
            text: "Quelle matière veux-tu réviser aujourd'hui ?"

        # La carte a maintenant une hauteur dynamique basée sur son contenu
        Card:
            size_hint_y: None
            height: self.minimum_height   # <-- Correction : hauteur adaptative
            spacing: 12

            FieldLabel:
                text: "MATIÈRE"

            MatiereInput:
                id: matiere_input
                suggestions: []   # sera rempli dynamiquement

            PrimaryButton:
                text: "Chercher un quiz"
                on_release: root.chercher_quiz()

        StatusLabel:
            id: message_label
            text: ""

        Widget:
            size_hint_y: None
            height: "4dp"

        FieldLabel:
            text: "RACCOURCIS"

        BoxLayout:
            orientation: "vertical"
            spacing: 10

            ListRow:
                height: "56dp"
                orientation: "horizontal"
                spacing: 12

                IconLabel:
                    text: "\\u2663"   # ♣ (symbole, pas emoji)
                Label:
                    text: "Voir le classement"
                    color: 0.12, 0.14, 0.20, 1
                    font_size: "15sp"
                    bold: True
                    halign: "left"
                    valign: "middle"
                    text_size: self.width, None
                IconButton:
                    text: "\\u203a"
                    on_release: root.manager.current = "classement"

            ListRow:
                height: "56dp"
                orientation: "horizontal"
                spacing: 12

                IconLabel:
                    text: "\\u2694"   # ⚔ (symbole)
                Label:
                    text: "Défier un élève"
                    color: 0.12, 0.14, 0.20, 1
                    font_size: "15sp"
                    bold: True
                    halign: "left"
                    valign: "middle"
                    text_size: self.width, None
                IconButton:
                    text: "\\u203a"
                    on_release: root.manager.current = "defi_creation"

            ListRow:
                height: "56dp"
                orientation: "horizontal"
                spacing: 12

                IconLabel:
                    text: "\\u2709"   # ✉ (enveloppe)
                Label:
                    id: bouton_notifications
                    text: "Notifications"
                    color: 0.12, 0.14, 0.20, 1
                    font_size: "15sp"
                    bold: True
                    halign: "left"
                    valign: "middle"
                    text_size: self.width, None
                IconButton:
                    text: "\\u203a"
                    on_release: root.manager.current = "notifications"

            ListRow:
                height: "56dp"
                orientation: "horizontal"
                spacing: 12

                IconLabel:
                    text: "\\u21ba"   # ↺ (historique)
                Label:
                    text: "Mon historique"
                    color: 0.12, 0.14, 0.20, 1
                    font_size: "15sp"
                    bold: True
                    halign: "left"
                    valign: "middle"
                    text_size: self.width, None
                IconButton:
                    text: "\\u203a"
                    on_release: root.manager.current = "historique"

        Widget:
"""

Builder.load_string(KV)


class HomeScreen(Screen):

    def on_pre_enter(self):
        eleve = getattr(self.manager, "eleve_connecte", None)
        if eleve:
            self.ids.bienvenue_label.text = f"Bonjour {eleve['nom']} !"
            self.rafraichir_badge_notifications(eleve["matricule"])
        # Charger dynamiquement les matières depuis l'API
        self.charger_matieres()

    def charger_matieres(self):
        succes, resultat = ApiService.lister_matieres()
        if succes:
            # L'API peut renvoyer une liste de chaînes ou de dictionnaires
            if resultat and isinstance(resultat[0], dict):
                suggestions = [m.get("nom") for m in resultat if "nom" in m]
            else:
                suggestions = resultat
            self.ids.matiere_input.suggestions = suggestions
        else:
            # En cas d'échec, on vide la liste (ou on laisse une liste vide)
            self.ids.matiere_input.suggestions = []

    def rafraichir_badge_notifications(self, matricule):
        succes, resultat = ApiService.obtenir_notifications(matricule)
        if succes and resultat["nombre_non_lues"] > 0:
            self.ids.bouton_notifications.text = f"Notifications ({resultat['nombre_non_lues']})"
        else:
            self.ids.bouton_notifications.text = "Notifications"

    def chercher_quiz(self):
        matiere = self.ids.matiere_input.get_text()
        if not matiere:
            self.ids.message_label.color = theme.ERROR
            self.ids.message_label.text = "Veuillez entrer un nom de matière."
            return
        autorise, message = ApiService.verifier_matiere(matiere)
        if autorise:
            self.ids.message_label.color = theme.SUCCESS
            self.ids.message_label.text = "Génération du quiz en cours..."
            self.lancer_generation_quiz(matiere)
        else:
            self.ids.message_label.color = theme.ERROR
            self.ids.message_label.text = message

    def lancer_generation_quiz(self, matiere):
        succes, resultat = ApiService.generer_quiz(matiere)
        if succes:
            quiz_screen = self.manager.get_screen("quiz")
            quiz_screen.charger_quiz(resultat)
            self.ids.message_label.text = ""
            self.manager.current = "quiz"
        else:
            self.ids.message_label.color = theme.ERROR
            self.ids.message_label.text = str(resultat)