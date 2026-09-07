from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from services.api_service import ApiService

KV = """
<DefiCreationScreen>:
    name: "defi_creation"

    BoxLayout:
        orientation: "vertical"
        padding: 40
        spacing: 15

        Label:
            text: "Défier un autre élève"
            font_size: 24
            size_hint_y: 0.15

        TextInput:
            id: adversaire_input
            hint_text: "Matricule de l'adversaire"
            multiline: False
            size_hint_y: 0.12
            font_size: 18

        TextInput:
            id: matiere_input
            hint_text: "Matière (ex: Réseaux)"
            multiline: False
            size_hint_y: 0.12
            font_size: 18

        Button:
            text: "Lancer le défi"
            size_hint_y: 0.15
            on_release: root.lancer_defi()

        Button:
            text: "Voir mes défis"
            size_hint_y: 0.12
            on_release: root.manager.current = "defis_liste"

        Button:
            text: "Retour"
            size_hint_y: 0.12
            on_release: root.manager.current = "home"

        Label:
            id: message_label
            text: ""
            size_hint_y: 0.2
"""

Builder.load_string(KV)


class DefiCreationScreen(Screen):

    def lancer_defi(self):
        adversaire = self.ids.adversaire_input.text.strip()
        matiere = self.ids.matiere_input.text.strip()

        if not adversaire or not matiere:
            self.ids.message_label.text = "Veuillez remplir les deux champs."
            return

        mon_matricule = self.manager.eleve_connecte["matricule"]
        self.ids.message_label.color = (1, 1, 1, 1)
        self.ids.message_label.text = "Création du défi en cours..."

        succes, resultat = ApiService.creer_defi(mon_matricule, adversaire, matiere)

        if succes:
            quiz_screen = self.manager.get_screen("quiz")
            quiz_screen.charger_quiz(resultat, defi_id=resultat["defi_id"])
            self.ids.message_label.text = ""
            self.manager.current = "quiz"
        else:
            self.ids.message_label.color = (1, 0.3, 0.3, 1)
            self.ids.message_label.text = str(resultat)
