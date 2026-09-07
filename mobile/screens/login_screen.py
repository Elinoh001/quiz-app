from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from services.api_service import ApiService

KV = """
<LoginScreen>:
    name: "login"

    BoxLayout:
        orientation: "vertical"
        padding: 40
        spacing: 20

        Label:
            text: "Quiz App"
            font_size: 32
            size_hint_y: 0.3

        Label:
            text: "Connectez-vous avec votre matricule"
            size_hint_y: 0.1

        TextInput:
            id: matricule_input
            hint_text: "Matricule"
            multiline: False
            size_hint_y: 0.15
            font_size: 20

        Button:
            text: "Se connecter"
            size_hint_y: 0.15
            on_release: root.tenter_connexion()

        Label:
            id: message_label
            text: ""
            color: 1, 0.3, 0.3, 1
            size_hint_y: 0.2
"""

Builder.load_string(KV)


class LoginScreen(Screen):

    def tenter_connexion(self):
        matricule = self.ids.matricule_input.text.strip()

        if not matricule:
            self.ids.message_label.text = "Veuillez entrer votre matricule."
            return

        succes, resultat = ApiService.login(matricule)

        if succes:
            self.ids.message_label.color = (0.3, 1, 0.3, 1)
            self.ids.message_label.text = f"Bienvenue {resultat['nom']} !"
            # Stocke l'élève connecté au niveau de l'app pour les écrans suivants
            self.manager.eleve_connecte = resultat
            self.manager.current = "home"
        else:
            self.ids.message_label.color = (1, 0.3, 0.3, 1)
            self.ids.message_label.text = str(resultat)
