from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

import theme
from services.api_service import ApiService

KV = """
<LoginScreen>:
    name: "login"

    canvas.before:
        Color:
            rgba: 0.20, 0.25, 0.75, 1   # fond bleu foncé
        Rectangle:
            pos: self.pos
            size: self.size
        # Dégradé simulé : rectangle plus clair en haut
        Color:
            rgba: 0.29, 0.33, 0.90, 1
        Rectangle:
            pos: self.pos
            size: (self.width, self.height * 0.5)

    FloatLayout:

        # Logo circulaire
        BoxLayout:
            size_hint: None, None
            size: "100dp", "100dp"
            pos_hint: {"center_x": 0.5, "top": 0.85}
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Ellipse:
                    pos: self.pos
                    size: self.size
            Label:
                text: "QA"
                font_size: "36sp"
                bold: True
                color: 0.29, 0.33, 0.90, 1

        # Titre et sous-titre
        Label:
            text: "Quiz App"
            font_size: "28sp"
            bold: True
            color: 1, 1, 1, 1
            size_hint: 1, None
            height: "40dp"
            pos_hint: {"top": 0.68}
            halign: "center"

        Label:
            text: "Révise, défie, progresse"
            font_size: "15sp"
            color: 1, 1, 1, 0.9
            size_hint: 1, None
            height: "24dp"
            pos_hint: {"top": 0.62}
            halign: "center"

        # Carte blanche
        BoxLayout:
            orientation: "vertical"
            size_hint: 1, None
            height: "300dp"
            pos_hint: {"top": 0.58}
            padding: [28, 30, 28, 20]
            spacing: 18
            canvas.before:
                Color:
                    rgba: 0.96, 0.97, 0.99, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]
                # Ombre portée (simulée par un rectangle décalé)
                Color:
                    rgba: 0, 0, 0, 0.1
                RoundedRectangle:
                    pos: self.x - 4, self.y - 4
                    size: self.width + 8, self.height + 8
                    radius: [24]

            ScreenTitle:
                text: "Connexion"
                font_size: "20sp"
                halign: "center"

            ScreenSubtitle:
                text: "Entre ton matricule pour continuer"
                halign: "center"

            FieldLabel:
                text: "MATRICULE"
                halign: "left"

            StyledInput:
                id: matricule_input
                hint_text: "ex : ETU2024-018"
                on_text_validate: root.tenter_connexion()

            StatusLabel:
                id: message_label
                text: ""

            PrimaryButton:
                text: "Se connecter"
                on_release: root.tenter_connexion()
"""

Builder.load_string(KV)

class LoginScreen(Screen):
    def tenter_connexion(self):
        matricule = self.ids.matricule_input.text.strip()
        if not matricule:
            self.ids.message_label.color = theme.ERROR
            self.ids.message_label.text = "Veuillez entrer votre matricule."
            return
        succes, resultat = ApiService.login(matricule)
        if succes:
            self.ids.message_label.color = theme.SUCCESS
            self.ids.message_label.text = f"Bienvenue {resultat['nom']} !"
            self.manager.eleve_connecte = resultat
            self.manager.current = "home"
        else:
            self.ids.message_label.color = theme.ERROR
            self.ids.message_label.text = str(resultat)