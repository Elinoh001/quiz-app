from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, RoundedRectangle, Ellipse

import theme
from services.api_service import ApiService

KV = """
<ClassementScreen>:
    name: "classement"

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
                text: "Classement"

        ScreenSubtitle:
            text: "Les meilleurs scores moyens de la classe."

        ScrollView:
            do_scroll_x: False

            BoxLayout:
                id: liste_classement
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: 8
                padding: [0, 6, 0, 6]
"""

Builder.load_string(KV)

# Couleurs pour les rangs 1,2,3
COULEURS_RANG = {
    1: (0.96, 0.77, 0.25, 1),   # or
    2: (0.75, 0.78, 0.80, 1),   # argent
    3: (0.80, 0.50, 0.20, 1)    # bronze
}


class ClassementScreen(Screen):

    def on_pre_enter(self):
        self.charger_classement()

    def _ligne_vide(self, texte):
        row = BoxLayout(orientation="vertical", size_hint_y=None, height=48, padding=(16, 12))
        row.add_widget(Label(text=texte, color=(0.45, 0.48, 0.55, 1), font_size="14sp"))
        return row

    def _label_gauche(self, texte, color, font_size, bold=False, halign="left"):
        label = Label(
            text=texte,
            color=color,
            font_size=font_size,
            bold=bold,
            halign=halign,
            valign="middle",
        )
        label.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        return label

    def charger_classement(self):
        self.ids.liste_classement.clear_widgets()
        succes, resultat = ApiService.obtenir_classement()

        if not succes:
            self.ids.liste_classement.add_widget(self._ligne_vide(str(resultat)))
            return

        if not resultat:
            self.ids.liste_classement.add_widget(self._ligne_vide("Aucun résultat pour le moment."))
            return

        for entree in resultat:
            rang = entree["rang"]

            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=56,
                padding=(16, 8),
                spacing=12,
            )

            with row.canvas.before:
                Color(1, 1, 1, 1)
                rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[12])

            def _sync_rect(instance, _value, rect=rect):
                rect.pos = instance.pos
                rect.size = instance.size

            row.bind(pos=_sync_rect, size=_sync_rect)

            # Pastille de rang
            pastille = Label(
                text=str(rang),
                font_size="14sp",
                bold=True,
                color=(1, 1, 1, 1),
                size_hint=(None, None),
                size=("36dp", "36dp"),
                halign="center",
                valign="middle",
            )
            couleur = COULEURS_RANG.get(rang, (0.29, 0.33, 0.90, 1))
            with pastille.canvas.before:
                Color(*couleur)
                cercle = Ellipse(pos=pastille.pos, size=pastille.size)

            def _sync_cercle(instance, _value, cercle=cercle):
                cercle.pos = instance.pos
                cercle.size = instance.size

            pastille.bind(pos=_sync_cercle, size=_sync_cercle)
            row.add_widget(pastille)

            # Informations (nom + nombre de quiz)
            infos = BoxLayout(orientation="vertical")
            infos.add_widget(
                self._label_gauche(
                    f"{entree['nom']}  ({entree['matricule']})",
                    (0.12, 0.14, 0.20, 1),
                    "14sp",
                    bold=True,
                )
            )
            infos.add_widget(
                self._label_gauche(
                    f"{entree['nombre_quiz']} quiz passés",
                    (0.45, 0.48, 0.55, 1),
                    "12sp",
                )
            )
            row.add_widget(infos)

            # Score
            score_label = Label(
                text=f"{entree['score_moyen']}%",
                color=(0.11, 0.68, 0.40, 1),
                font_size="15sp",
                bold=True,
                size_hint_x=None,
                width=60,
                halign="right",
                valign="middle",
            )
            row.add_widget(score_label)

            self.ids.liste_classement.add_widget(row)