from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle

import theme
from services.api_service import ApiService

KV = """
<DefisListeScreen>:
    name: "defis_liste"

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
                on_release: root.manager.current = "defi_creation"

            ScreenTitle:
                text: "Mes défis"

        ScreenSubtitle:
            text: "Suis tes duels avec tes camarades."

        ScrollView:
            do_scroll_x: False

            BoxLayout:
                id: liste_defis
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: 8
                padding: [0, 6, 0, 6]
"""

Builder.load_string(KV)


class DefisListeScreen(Screen):

    def on_pre_enter(self):
        self.charger_defis()

    def _creer_defi(self, defi):
        card = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="70dp",
            padding=(16, 8),
            spacing=12,
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])

        def _sync_rect(instance, _value, rect=rect):
            rect.pos = instance.pos
            rect.size = instance.size

        card.bind(pos=_sync_rect, size=_sync_rect)

        # Icône de défi (symbole)
        icon = Label(
            text="\\u2694",  # ⚔
            font_size="20sp",
            color=(0.29, 0.33, 0.90, 1),
            size_hint=(None, None),
            size=("30dp", "30dp"),
        )
        card.add_widget(icon)

        # Informations
        infos = BoxLayout(orientation="vertical", spacing=2)
        matiere_label = Label(
            text=defi['matiere'],
            color=(0.12, 0.14, 0.20, 1),
            font_size="14sp",
            bold=True,
            halign="left",
            valign="middle",
            text_size=(self.width - 140, None),
        )
        matiere_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w - 140, None)))
        infos.add_widget(matiere_label)

        adversaire = Label(
            text=f"vs {defi['adversaire_nom']}",
            color=(0.45, 0.48, 0.55, 1),
            font_size="12sp",
            halign="left",
            valign="middle",
            text_size=(self.width - 140, None),
        )
        adversaire.bind(width=lambda inst, w: setattr(inst, 'text_size', (w - 140, None)))
        infos.add_widget(adversaire)
        card.add_widget(infos)

        # Badge statut
        statut = defi['statut'].upper()
        couleurs = {
            "EN_COURS": (0.98, 0.60, 0.20, 1),   # orange
            "TERMINE": (0.11, 0.68, 0.40, 1),    # vert
            "GAGNE": (0.11, 0.68, 0.40, 1),
            "PERDU": (0.90, 0.26, 0.30, 1),
        }
        couleur = couleurs.get(statut, (0.45, 0.48, 0.55, 1))
        badge = Label(
            text=statut,
            color=(1, 1, 1, 1),
            font_size="11sp",
            bold=True,
            size_hint=(None, None),
            size=("80dp", "24dp"),
            halign="center",
            valign="middle",
        )
        with badge.canvas.before:
            Color(*couleur)
            rect_badge = RoundedRectangle(pos=badge.pos, size=badge.size, radius=[8])

        def _sync_badge(instance, _value, rect=rect_badge):
            rect.pos = instance.pos
            rect.size = instance.size

        badge.bind(pos=_sync_badge, size=_sync_badge)
        card.add_widget(badge)

        return card

    def charger_defis(self):
        self.ids.liste_defis.clear_widgets()
        matricule = self.manager.eleve_connecte["matricule"]
        succes, resultat = ApiService.lister_defis(matricule)

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
            self.ids.liste_defis.add_widget(label)
            return

        if not resultat:
            label = Label(
                text="Aucun défi pour le moment.",
                color=theme.TEXT_MUTED,
                font_size="14sp",
                size_hint_y=None,
                height=40,
                halign="left",
                valign="middle",
                text_size=(self.width - 48, None),
            )
            label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w - 48, None)))
            self.ids.liste_defis.add_widget(label)
            return

        for defi in resultat:
            self.ids.liste_defis.add_widget(self._creer_defi(defi))