from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label

from services.api_service import ApiService

KV = """
<DefisListeScreen>:
    name: "defis_liste"

    BoxLayout:
        orientation: "vertical"
        padding: 30
        spacing: 10

        Label:
            text: "Mes défis"
            font_size: 26
            size_hint_y: 0.15

        ScrollView:
            size_hint_y: 0.7

            BoxLayout:
                id: liste_defis
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: 5

        Button:
            text: "Retour"
            size_hint_y: 0.15
            on_release: root.manager.current = "defi_creation"
"""

Builder.load_string(KV)


class DefisListeScreen(Screen):

    def on_pre_enter(self):
        self.charger_defis()

    def charger_defis(self):
        self.ids.liste_defis.clear_widgets()
        matricule = self.manager.eleve_connecte["matricule"]
        succes, resultat = ApiService.lister_defis(matricule)

        if not succes:
            self.ids.liste_defis.add_widget(Label(text=str(resultat), size_hint_y=None, height=40))
            return

        if not resultat:
            self.ids.liste_defis.add_widget(
                Label(text="Aucun défi pour le moment.", size_hint_y=None, height=40)
            )
            return

        for defi in resultat:
            mon_score = defi["mon_score"] if defi["mon_score"] is not None else "?"
            score_adv = defi["score_adversaire"] if defi["score_adversaire"] is not None else "?"
            texte = (
                f"{defi['matiere']} vs {defi['adversaire_nom']} ({defi['adversaire_matricule']}) — "
                f"[{defi['statut']}] Toi: {mon_score}%  Adversaire: {score_adv}%"
            )
            self.ids.liste_defis.add_widget(Label(text=texte, size_hint_y=None, height=50))
