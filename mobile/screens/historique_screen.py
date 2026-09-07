from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label

from services.api_service import ApiService

KV = """
<HistoriqueScreen>:
    name: "historique"

    BoxLayout:
        orientation: "vertical"
        padding: 30
        spacing: 10

        Label:
            text: "Mon historique"
            font_size: 26
            size_hint_y: 0.12

        Label:
            id: resume_label
            text: ""
            font_size: 16
            size_hint_y: 0.1

        ScrollView:
            size_hint_y: 0.63

            BoxLayout:
                id: liste_historique
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


class HistoriqueScreen(Screen):

    def on_pre_enter(self):
        self.charger_historique()

    def charger_historique(self):
        self.ids.liste_historique.clear_widgets()
        self.ids.resume_label.text = ""
        matricule = self.manager.eleve_connecte["matricule"]
        succes, resultat = ApiService.obtenir_historique(matricule)

        if not succes:
            self.ids.liste_historique.add_widget(Label(text=str(resultat), size_hint_y=None, height=40))
            return

        self.ids.resume_label.text = (
            f"{resultat['nombre_quiz']} quiz passés — moyenne générale : {resultat['moyenne_generale']}%"
        )

        if not resultat["historique"]:
            self.ids.liste_historique.add_widget(
                Label(text="Aucun quiz passé pour le moment.", size_hint_y=None, height=40)
            )
            return

        for entree in resultat["historique"]:
            date_affichee = entree["date_passage"][:10]  # AAAA-MM-JJ, suffisant pour l'affichage
            texte = f"{date_affichee} — {entree['matiere']} : {entree['score']}%"
            self.ids.liste_historique.add_widget(Label(text=texte, size_hint_y=None, height=40))
