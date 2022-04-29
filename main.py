from __future__ import annotations
import os
import sys
from pathlib import Path
from threading import Thread
from typing import Optional

from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDMenu, MDDropdownMenu
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.toolbar import MDToolbar, MDActionTopAppBarButton
from plyer.utils import platform

from utils_platform import get_file_chooser
import hooks_calibre
import hooks_plyer

if getattr(sys, "frozen", False):  # bundle mode with PyInstaller
    os.environ["EBOOK_CONVERTER_ROOT"] = sys._MEIPASS
else:
    sys.path.append(os.path.abspath(__file__).split("demos")[0])
    os.environ["EBOOK_CONVERTER_ROOT"] = str(Path(__file__).parent.absolute())

hooks_calibre.hook()
hooks_plyer.hook()
# For unknown reason it won't display icons properly without this. It should load it automatically.
MDActionTopAppBarButton.font_name = "fonts/materialdesignicons-webfont.ttf"


class MyBoxLayout(BoxLayout):
    def my_callback(self):
        print("Hello")


class MainScreen(Screen):
    NAME = "MainScreen"
    toolbar_menu: MDDropdownMenu = ObjectProperty()
    toolbar: MDToolbar = ObjectProperty()
    btn_select: MDRectangleFlatButton = ObjectProperty()
    btn_convert: MDRectangleFlatButton = ObjectProperty()
    label_message: Label = ObjectProperty()
    progress_bar: MDProgressBar = ObjectProperty()
    label_log: MDLabel = ObjectProperty()
    file_chooser = get_file_chooser()

    def __init__(self, app: MainApp, **kw):
        super().__init__(**kw)
        self.app = app
        self.file_path: Optional[str] = None
        self.convert_thread: Optional[Thread] = None
        self.toolbar_menu = MDDropdownMenu(width_mult=4)
        self.toolbar_menu.items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Setting",
                "on_release": self.on_setting_menu_clicked,
            }
        ]

    def select_file_to_convert(self):
        self.file_path = None
        if self.file_chooser:
            if platform == 'android':
                self.file_chooser.open_file(on_selection=self.on_open_file)
            else:
                file_paths = self.file_chooser.open_file()
                self.on_open_file(file_paths)

    def on_open_file(self, file_path):
        if file_path:
            self.file_path = file_path[0]
            self.log(f"Select input file: {file_path[0]}")
            self.btn_convert.disabled = False

    def start_convert(self):
        from utils_convert import MyProgressBar, MyLog
        from utils_convert import ConvertThread
        self.label_message.text = "Converting"
        self.progress_bar.value = 0
        log = MyLog(print_call_back=self.on_log_callback)
        progress = MyProgressBar(log, progress_call_back=self.on_progress_changed)
        args = ["ebook-convert", self.file_path, self.file_path + '.mobi']
        self.log('Start converting')
        self.log(f"args: {args}")

        self.convert_thread = ConvertThread(args=args, log=log,
                                            reporter=progress)
        self.convert_thread.start()

    def on_progress_changed(self, percent: int, msg: str):
        self.label_message.text = msg
        self.progress_bar.value = percent
        if percent == 100:
            self.btn_select.disabled = False
            self.convert_thread = None

    def on_log_callback(self, level, *args, **kwargs):
        INFO = 1
        if level >= INFO:
            self.log(*args)

    def test_load_modules(self):
        try:
            import bs4
            import css_parser
            import filelock
            import html2text
            import lxml
            import msgpack
            import odf
            import PIL
            import dateutil
            import tinycss
            import kivy
            import kivymd
            import plyer
            import chardet
            import html5_parser
        except Exception as e:
            self.label_message.text = str(e)
        else:
            self.label_message.text = "All modules can be imported."

    def on_toolbar_menu_clicked(self, button):
        self.toolbar_menu.caller = button
        self.toolbar_menu.open()

    def on_setting_menu_clicked(self):
        self.toolbar_menu.dismiss()
        self.app.sm.switch_to(screen=SettingScreen(self.app,self))

    def log(self, *args):
        self.label_log.text = ' '.join(list(str(i) for i in args)) + '\n' + self.label_log.text


class SettingScreen(Screen):
    app = ObjectProperty()
    parent_screen = ObjectProperty()

    def __init__(self, app:MainApp, parent_screen: Screen, **kw):
        super().__init__(**kw)
        self.app = app
        self.parent_screen = parent_screen

    def on_leave_button_clicked(self):
        self.app.sm.switch_to(self.parent_screen, direction='left')


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sm: Optional[ScreenManager] = None

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(self))
        return self.sm

    def on_pause(self):
        return True

    def on_stop(self):
        self.sm = None


if __name__ == '__main__':
    MainApp().run()
