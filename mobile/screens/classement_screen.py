from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label

from services.api_service import ApiService

KV = """
<ClassementScreen>:
    name: "classement"

    BoxLayout:
        orientation: "vertical"
        padding: 30
        spacing: 10

        Label:
            text: "Classement général"
            font_size: 26
            size_hint_y: 0.15

        ScrollView:
            size_hint_y: 0.7

            BoxLayout:
                id: liste_classement
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: 5

        Button:
            text: "Retour"
            size_hint_y: 0.15
            on_release: root.manager.current = "home"
"""

Builder.load_string(KV)


class ClassementScreen(Screen):

    def on_pre_enter(self):
        self.charger_classement()

    def charger_classement(self):
        self.ids.liste_classement.clear_widgets()
        succes, resultat = ApiService.obtenir_classement()

        if not succes:
            self.ids.liste_classement.add_widget(Label(text=str(resultat), size_hint_y=None, height=40))
            return

        if not resultat:
            self.ids.liste_classement.add_widget(
                Label(text="Aucun résultat pour le moment.", size_hint_y=None, height=40)
            )
            return

        for entree in resultat:
            texte = (
                f"#{entree['rang']}  {entree['nom']} ({entree['matricule']}) — "
                f"{entree['score_moyen']}%  ({entree['nombre_quiz']} quiz)"
            )
            self.ids.liste_classement.add_widget(Label(text=texte, size_hint_y=None, height=40))
