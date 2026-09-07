from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from services.api_service import ApiService

KV = """
<HomeScreen>:
    name: "home"

    BoxLayout:
        orientation: "vertical"
        padding: 40
        spacing: 20

        Label:
            id: bienvenue_label
            text: "Quelle matière veux-tu réviser ?"
            font_size: 22
            size_hint_y: 0.2

        TextInput:
            id: matiere_input
            hint_text: "Nom de la matière (ex: Algorithmique)"
            multiline: False
            size_hint_y: 0.15
            font_size: 20

        Button:
            text: "Chercher un quiz"
            size_hint_y: 0.15
            on_release: root.chercher_quiz()

        Button:
            text: "Voir le classement"
            size_hint_y: 0.1
            on_release: root.manager.current = "classement"

        Button:
            text: "Défier un élève"
            size_hint_y: 0.1
            on_release: root.manager.current = "defi_creation"

        Button:
            id: bouton_notifications
            text: "Notifications"
            size_hint_y: 0.1
            on_release: root.manager.current = "notifications"

        Button:
            text: "Mon historique"
            size_hint_y: 0.1
            on_release: root.manager.current = "historique"

        Label:
            id: message_label
            text: ""
            size_hint_y: 0.3
"""

Builder.load_string(KV)


class HomeScreen(Screen):

    def on_pre_enter(self):
        eleve = getattr(self.manager, "eleve_connecte", None)
        if eleve:
            self.ids.bienvenue_label.text = f"Bonjour {eleve['nom']}, quelle matière veux-tu réviser ?"
            self.rafraichir_badge_notifications(eleve["matricule"])

    def rafraichir_badge_notifications(self, matricule):
        succes, resultat = ApiService.obtenir_notifications(matricule)
        if succes and resultat["nombre_non_lues"] > 0:
            self.ids.bouton_notifications.text = f"Notifications ({resultat['nombre_non_lues']})"
        else:
            self.ids.bouton_notifications.text = "Notifications"

    def chercher_quiz(self):
        matiere = self.ids.matiere_input.text.strip()

        if not matiere:
            self.ids.message_label.text = "Veuillez entrer un nom de matière."
            return

        autorise, message = ApiService.verifier_matiere(matiere)

        if autorise:
            self.ids.message_label.color = (0.3, 1, 0.3, 1)
            self.ids.message_label.text = "Génération du quiz en cours..."
            self.lancer_generation_quiz(matiere)
        else:
            self.ids.message_label.color = (1, 0.3, 0.3, 1)
            self.ids.message_label.text = message

    def lancer_generation_quiz(self, matiere):
        succes, resultat = ApiService.generer_quiz(matiere)

        if succes:
            quiz_screen = self.manager.get_screen("quiz")
            quiz_screen.charger_quiz(resultat)
            self.ids.message_label.text = ""
            self.manager.current = "quiz"
        else:
            self.ids.message_label.color = (1, 0.3, 0.3, 1)
            self.ids.message_label.text = str(resultat)
