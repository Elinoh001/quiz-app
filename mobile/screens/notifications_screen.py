from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label

from services.api_service import ApiService

KV = """
<NotificationsScreen>:
    name: "notifications"

    BoxLayout:
        orientation: "vertical"
        padding: 30
        spacing: 10

        Label:
            text: "Notifications"
            font_size: 26
            size_hint_y: 0.15

        ScrollView:
            size_hint_y: 0.7

            BoxLayout:
                id: liste_notifications
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


class NotificationsScreen(Screen):

    def on_pre_enter(self):
        self.charger_notifications()

    def _creer_label_notification(self, texte):
        """
        Crée un Label dont le retour à la ligne suit sa VRAIE largeur (celle du
        conteneur, mise à jour dynamiquement) et dont la hauteur s'ajuste au
        texte réellement affiché — évite le bug d'un text_size figé trop tôt,
        qui provoquait un retour à la ligne après chaque lettre.
        """
        label = Label(
            text=texte,
            size_hint_y=None,
            halign="left",
            valign="top",
            padding=(10, 10),
        )

        def ajuster_largeur(instance, largeur):
            instance.text_size = (largeur, None)

        def ajuster_hauteur(instance, texture_size):
            instance.height = texture_size[1] + 20

        label.bind(width=ajuster_largeur)
        label.bind(texture_size=ajuster_hauteur)
        return label

    def charger_notifications(self):
        self.ids.liste_notifications.clear_widgets()
        matricule = self.manager.eleve_connecte["matricule"]
        succes, resultat = ApiService.obtenir_notifications(matricule)

        if not succes:
            self.ids.liste_notifications.add_widget(self._creer_label_notification(str(resultat)))
            return

        notifications = resultat["notifications"]

        if not notifications:
            self.ids.liste_notifications.add_widget(
                self._creer_label_notification("Aucune notification pour le moment.")
            )
        else:
            for notif in notifications:
                prefixe = "🔵 " if not notif["lu"] else ""
                self.ids.liste_notifications.add_widget(
                    self._creer_label_notification(f"{prefixe}{notif['message']}")
                )

        # On marque tout comme lu une fois que l'élève a consulté l'écran,
        # pour que le badge de l'accueil se remette à zéro.
        ApiService.marquer_notifications_lues(matricule)