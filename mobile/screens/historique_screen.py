from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle

import theme
from services.api_service import ApiService

KV = """
<HistoriqueScreen>:
    name: "historique"

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
                text: "Mon historique"

        Label:
            id: resume_label
            text: ""
            font_size: "15sp"
            color: 0.45, 0.48, 0.55, 1
            size_hint_y: None
            height: self.texture_size[1] + 4 if self.text else 0

        ScrollView:
            do_scroll_x: False

            BoxLayout:
                id: liste_historique
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: 8
                padding: [0, 6, 0, 6]
"""

Builder.load_string(KV)


class HistoriqueScreen(Screen):

    def on_pre_enter(self):
        self.charger_historique()

    def _creer_entree(self, date, matiere, score):
        card = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="56dp",
            padding=(16, 8),
            spacing=12,
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[10])

        def _sync_rect(instance, _value, rect=rect):
            rect.pos = instance.pos
            rect.size = instance.size

        card.bind(pos=_sync_rect, size=_sync_rect)

        # Date et matière
        infos = Label(
            text=f"{date}  •  {matiere}",
            color=(0.12, 0.14, 0.20, 1),
            font_size="14sp",
            halign="left",
            valign="middle",
            text_size=(self.width - 100, None),
        )
        infos.bind(width=lambda inst, w: setattr(inst, 'text_size', (w - 100, None)))
        card.add_widget(infos)

        # Score avec pastille
        score_label = Label(
            text=f"{score}%",
            color=(1, 1, 1, 1),
            font_size="14sp",
            bold=True,
            size_hint=(None, None),
            size=("52dp", "28dp"),
            halign="center",
            valign="middle",
        )
        couleur = (0.11, 0.68, 0.40, 1) if score >= 50 else (0.90, 0.26, 0.30, 1)
        with score_label.canvas.before:
            Color(*couleur)
            rect_score = RoundedRectangle(pos=score_label.pos, size=score_label.size, radius=[8])

        def _sync_score(instance, _value, rect=rect_score):
            rect.pos = instance.pos
            rect.size = instance.size

        score_label.bind(pos=_sync_score, size=_sync_score)
        card.add_widget(score_label)

        return card

    def charger_historique(self):
        self.ids.liste_historique.clear_widgets()
        self.ids.resume_label.text = ""
        matricule = self.manager.eleve_connecte["matricule"]
        succes, resultat = ApiService.obtenir_historique(matricule)

        if not succes:
            label = Label(
                text=str(resultat),
                color=theme.ERROR,
                font_size="14sp",
                size_hint_y=None,
                height=40,
                halign="left",
                valign="middle",
                text_size=(self.width - 48, None),
            )
            label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w - 48, None)))
            self.ids.liste_historique.add_widget(label)
            return

        self.ids.resume_label.text = (
            f"{resultat['nombre_quiz']} quiz passés — moyenne générale : {resultat['moyenne_generale']}%"
        )

        if not resultat["historique"]:
            label = Label(
                text="Aucun quiz passé pour le moment.",
                color=theme.TEXT_MUTED,
                font_size="14sp",
                size_hint_y=None,
                height=40,
                halign="left",
                valign="middle",
                text_size=(self.width - 48, None),
            )
            label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w - 48, None)))
            self.ids.liste_historique.add_widget(label)
            return

        for entree in resultat["historique"]:
            date = entree["date_passage"][:10]
            matiere = entree["matiere"]
            score = entree["score"]
            self.ids.liste_historique.add_widget(
                self._creer_entree(date, matiere, score)
            )