import theme  # Thème d'abord

from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from screens.login_screen import LoginScreen
from screens.home_screen import HomeScreen
from screens.quiz_screen import QuizScreen
from screens.classement_screen import ClassementScreen
from screens.defi_creation_screen import DefiCreationScreen
from screens.defis_liste_screen import DefisListeScreen
from screens.notifications_screen import NotificationsScreen
from screens.historique_screen import HistoriqueScreen

Window.size = (360, 640)

class QuizScreenManager(ScreenManager):
    eleve_connecte = None

class QuizApp(App):
    def build(self):
        sm = QuizScreenManager(transition=FadeTransition(duration=0.25))
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