from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse

import theme
from services.api_service import ApiService

KV = """
<NotificationsScreen>:
    name: "notifications"

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
                text: "Notifications"

        ScreenSubtitle:
            text: "Tes dernières nouvelles."

        ScrollView:
            do_scroll_x: False

            BoxLayout:
                id: liste_notifications
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: 8
                padding: [0, 6, 0, 6]
"""

Builder.load_string(KV)


class NotificationsScreen(Screen):

    def on_pre_enter(self):
        self.charger_notifications()

    def _creer_notification(self, texte, non_lue=False):
        card = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="60dp",
            padding=(12, 8),
            spacing=10,
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
            if non_lue:
                Color(0.29, 0.33, 0.90, 0.1)  # fond bleu très léger
                rect_fond = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])

        def _sync_rect(instance, _value, rect=rect, rect_fond=None):
            rect.pos = instance.pos
            rect.size = instance.size
            if rect_fond:
                rect_fond.pos = instance.pos
                rect_fond.size = instance.size

        card.bind(pos=_sync_rect, size=_sync_rect)

        # Pastille si non lue
        if non_lue:
            pastille = Widget(size_hint=(None, None), size=("10dp", "10dp"))
            with pastille.canvas:
                Color(0.29, 0.33, 0.90, 1)
                cercle = Ellipse(pos=pastille.pos, size=pastille.size)
            pastille.bind(pos=lambda inst, val: setattr(cercle, 'pos', val))
            pastille.bind(size=lambda inst, val: setattr(cercle, 'size', val))
            card.add_widget(pastille)
        else:
            # Espace réservé pour aligner le texte
            card.add_widget(Widget(size_hint=(None, None), size=("10dp", "10dp")))

        label = Label(
            text=texte,
            color=(0.12, 0.14, 0.20, 1),
            font_size="15sp",
            halign="left",
            valign="middle",
            text_size=(self.width - 70, None),
        )
        label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w - 70, None)))
        card.add_widget(label)

        return card

    def charger_notifications(self):
        self.ids.liste_notifications.clear_widgets()
        matricule = self.manager.eleve_connecte["matricule"]
        succes, resultat = ApiService.obtenir_notifications(matricule)

        if not succes:
            self.ids.liste_notifications.add_widget(
                self._creer_notification(str(resultat), non_lue=False)
            )
            return

        notifications = resultat["notifications"]

        if not notifications:
            self.ids.liste_notifications.add_widget(
                self._creer_notification("Aucune notification pour le moment.", non_lue=False)
            )
        else:
            for notif in notifications:
                self.ids.liste_notifications.add_widget(
                    self._creer_notification(notif['message'], non_lue=not notif["lu"])
                )

        ApiService.marquer_notifications_lues(matricule)