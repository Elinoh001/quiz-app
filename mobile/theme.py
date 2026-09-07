"""
Thème visuel centralisé de l'application.
Définit la palette, les widgets réutilisables et les composants MatiereInput / EleveInput.
"""

from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
PRIMARY = (0.29, 0.33, 0.90, 1)
PRIMARY_DOWN = (0.22, 0.25, 0.72, 1)
PRIMARY_SOFT = (0.93, 0.94, 0.99, 1)
PRIMARY_SOFT_DOWN = (0.87, 0.88, 0.97, 1)

BG = (0.96, 0.97, 0.99, 1)
CARD = (1, 1, 1, 1)

TEXT_DARK = (0.12, 0.14, 0.20, 1)
TEXT_MUTED = (0.45, 0.48, 0.55, 1)
TEXT_ON_PRIMARY = (1, 1, 1, 1)

BORDER = (0.88, 0.89, 0.93, 1)

SUCCESS = (0.11, 0.68, 0.40, 1)
ERROR = (0.90, 0.26, 0.30, 1)
ACCENT = (0.98, 0.60, 0.20, 1)

KV = """
#:import utils kivy.utils

<PrimaryButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ""
    background_down: ""
    color: 1, 1, 1, 1
    font_size: "16sp"
    bold: True
    size_hint_y: None
    height: "52dp"
    canvas.before:
        Color:
            rgba: (0.22, 0.25, 0.72, 1) if self.state == "down" else ((0.75, 0.76, 0.85, 1) if self.disabled else (0.29, 0.33, 0.90, 1))
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [14]

<SecondaryButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ""
    background_down: ""
    color: 0.29, 0.33, 0.90, 1
    font_size: "15sp"
    bold: True
    size_hint_y: None
    height: "48dp"
    canvas.before:
        Color:
            rgba: (0.87, 0.88, 0.97, 1) if self.state == "down" else (0.93, 0.94, 0.99, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [14]

<GhostButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ""
    background_down: ""
    color: (0.29, 0.33, 0.90, 1) if self.state == "down" else (0.45, 0.48, 0.55, 1)
    font_size: "15sp"
    bold: True
    size_hint_y: None
    height: "40dp"

<IconButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ""
    background_down: ""
    color: (0.29, 0.33, 0.90, 1) if self.state == "down" else (0.12, 0.14, 0.20, 1)
    font_size: "20sp"
    bold: True
    size_hint: None, None
    size: "40dp", "40dp"

<StyledInput@TextInput>:
    background_color: 0, 0, 0, 0
    background_normal: ""
    background_active: ""
    background_disabled_normal: ""
    foreground_color: 0.12, 0.14, 0.20, 1
    hint_text_color: 0.62, 0.64, 0.70, 1
    cursor_color: 0.29, 0.33, 0.90, 1
    selection_color: 0.29, 0.33, 0.90, 0.35
    padding: [16, 14, 16, 14]
    font_size: "16sp"
    size_hint_y: None
    height: "52dp"
    multiline: False
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]
        Color:
            rgba: (0.29, 0.33, 0.90, 1) if self.focus else (0.88, 0.89, 0.93, 1)
        Line:
            width: 1.4
            rounded_rectangle: [self.x, self.y, self.width, self.height, 12]

<Card@BoxLayout>:
    orientation: "vertical"
    padding: 16
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [16]

<ListRow@BoxLayout>:
    orientation: "vertical"
    size_hint_y: None
    height: self.minimum_height
    padding: [16, 12, 16, 12]
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]

<ScreenTitle@Label>:
    color: 0.12, 0.14, 0.20, 1
    font_size: "24sp"
    bold: True
    size_hint_y: None
    height: "36dp"
    halign: "left"
    valign: "middle"
    text_size: self.width, None

<ScreenSubtitle@Label>:
    color: 0.45, 0.48, 0.55, 1
    font_size: "14sp"
    size_hint_y: None
    height: self.texture_size[1] + 4
    halign: "left"
    valign: "middle"
    text_size: self.width, None

<FieldLabel@Label>:
    color: 0.35, 0.37, 0.45, 1
    font_size: "13sp"
    bold: True
    size_hint_y: None
    height: "20dp"
    halign: "left"
    valign: "middle"
    text_size: self.width, None

<StatusLabel@Label>:
    color: 0.45, 0.48, 0.55, 1
    font_size: "14sp"
    size_hint_y: None
    height: self.texture_size[1] if self.text else 0
    halign: "center"
    valign: "middle"
    text_size: self.width, None

<RowLabel@Label>:
    color: 0.16, 0.18, 0.24, 1
    font_size: "14sp"
    halign: "left"
    valign: "middle"
    text_size: self.width, None
    size_hint_y: None
    height: self.texture_size[1] + 4

<OptionButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ""
    background_down: ""
    color: 0.12, 0.14, 0.20, 1
    font_size: "15sp"
    halign: "left"
    valign: "middle"
    text_size: self.width - 32, None
    padding: [16, 12]
    size_hint_y: None
    height: "52dp"
    canvas.before:
        Color:
            rgba: (0.93, 0.94, 0.99, 1) if self.state == "down" else (1, 1, 1, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]
        Color:
            rgba: (0.29, 0.33, 0.90, 1) if self.state == "down" else (0.88, 0.89, 0.93, 1)
        Line:
            width: 1.2
            rounded_rectangle: [self.x, self.y, self.width, self.height, 12]

<ProgressTrack@Widget>:
    progress: 0
    size_hint_y: None
    height: "8dp"
    canvas:
        Color:
            rgba: 0.90, 0.91, 0.95, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [4]
        Color:
            rgba: 0.29, 0.33, 0.90, 1
        RoundedRectangle:
            pos: self.pos
            size: (self.width * self.progress, self.height)
            radius: [4]

<TopBackButton@Button>:
    text: "\\u2190"
    background_color: 0, 0, 0, 0
    background_normal: ""
    background_down: ""
    color: (0.29, 0.33, 0.90, 1) if self.state == "down" else (0.12, 0.14, 0.20, 1)
    font_size: "22sp"
    bold: True
    size_hint: None, None
    size: "40dp", "40dp"

# Style pour les icônes (caractères Unicode non-emoji)
<IconLabel@Label>:
    color: 0.12, 0.14, 0.20, 1
    font_size: "20sp"
    size_hint_x: None
    width: "28dp"
    halign: "center"
    valign: "middle"
"""

Builder.load_string(KV)


class MatiereInput(BoxLayout):
    """
    Champ de saisie pour une matière, avec un bouton ouvrant un menu déroulant
    de suggestions. L'utilisateur peut soit taper, soit sélectionner.
    """

    def __init__(self, suggestions=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = 8
        self.size_hint_y = None
        self.height = "56dp"  # hauteur légèrement augmentée

        # Champ texte principal (StyledInput défini dans le KV, récupéré via Factory)
        self.text_input = Factory.StyledInput(hint_text="ex : Algorithmique")
        self.text_input.multiline = False
        self.add_widget(self.text_input)

        # Bouton pour ouvrir le menu déroulant
        self.dropdown_button = Button(
            text="▾",
            size_hint=(None, None),
            size=("56dp", "56dp"),
            background_normal="",
            background_color=(0.29, 0.33, 0.90, 1),
            color=(1, 1, 1, 1),
            font_size="20sp",
        )
        self.dropdown_button.bind(on_release=self.open_dropdown)
        self.add_widget(self.dropdown_button)

        # Suggestions (liste de chaînes)
        self.suggestions = suggestions or []
        self.dropdown = DropDown()

    def open_dropdown(self, *args):
        """Ouvre le menu déroulant avec les suggestions actuelles."""
        self.dropdown.clear_widgets()
        # Largeur du dropdown alignée sur la largeur totale du champ (texte + bouton + espacement)
        total_width = self.text_input.width + self.dropdown_button.width + self.spacing
        self.dropdown.auto_width = False
        self.dropdown.width = total_width

        for matiere in self.suggestions:
            btn = Button(
                text=matiere,
                size_hint_y=None,
                height="48dp",
                size_hint_x=None,
                width=total_width,
                background_normal="",
                background_color=(1, 1, 1, 1),
                color=(0.12, 0.14, 0.20, 1),
                font_size="16sp",
                halign="left",
                valign="middle",
                padding=(16, 0),
            )
            btn.bind(on_release=lambda instance, m=matiere: self.select_matiere(m))
            self.dropdown.add_widget(btn)

        self.dropdown.open(self.dropdown_button)

    def select_matiere(self, matiere):
        """Remplit le champ texte avec la matière sélectionnée."""
        self.text_input.text = matiere
        self.dropdown.dismiss()

    def get_text(self):
        """Retourne le texte saisi (sans espaces superflus)."""
        return self.text_input.text.strip()


class EleveInput(MatiereInput):
    """
    Champ de saisie pour un élève avec menu déroulant des suggestions.
    Hérite de MatiereInput et personnalise le hint_text.
    """

    def __init__(self, suggestions=None, **kwargs):
        super().__init__(suggestions=suggestions, **kwargs)
        self.text_input.hint_text = "ex : ETU2024-015"


# Enregistrement des classes pour les utiliser dans les fichiers KV
Factory.register('MatiereInput', cls=MatiereInput)
Factory.register('EleveInput', cls=EleveInput)