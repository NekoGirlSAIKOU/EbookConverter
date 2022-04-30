import webbrowser

from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp


class AboutScreen(Screen):
    app = ObjectProperty()
    parent_screen = ObjectProperty()

    def __init__(self, app: MDApp, parent_screen: Screen, **kw):
        super().__init__(**kw)
        self.app = app
        self.parent_screen = parent_screen

    def on_leave_button_clicked(self):
        self.app.sm.switch_to(self.parent_screen, direction='left')

    def open_url(self, url):
        webbrowser.open(url)
