from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from screens.login_screen import LoginScreen
from screens.home_screen import HomeScreen
from screens.quiz_screen import QuizScreen
from screens.classement_screen import ClassementScreen
from screens.defi_creation_screen import DefiCreationScreen
from screens.defis_liste_screen import DefisListeScreen
from screens.notifications_screen import NotificationsScreen
from screens.historique_screen import HistoriqueScreen


class QuizScreenManager(ScreenManager):
    """ScreenManager étendu pour garder en mémoire l'élève connecté
    et le partager entre tous les écrans de l'app."""
    eleve_connecte = None


class QuizApp(App):
    def build(self):
        sm = QuizScreenManager()
        sm.add_widget(LoginScreen())
        sm.add_widget(HomeScreen())
        sm.add_widget(QuizScreen())
        sm.add_widget(ClassementScreen())
        sm.add_widget(DefiCreationScreen())
        sm.add_widget(DefisListeScreen())
        sm.add_widget(NotificationsScreen())
        sm.add_widget(HistoriqueScreen())
        sm.current = "login"
        return sm


if __name__ == "__main__":
    QuizApp().run()
