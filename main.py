import os
import sys
from pathlib import Path
from threading import Thread
from typing import Optional

from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.textfield import MDTextField
from plyer.utils import platform

from platform_utils import get_file_chooser
import calibre_hooks  # Enable hooks

if getattr(sys, "frozen", False):  # bundle mode with PyInstaller
    os.environ["EBOOK_CONVERTER_ROOT"] = sys._MEIPASS
else:
    sys.path.append(os.path.abspath(__file__).split("demos")[0])
    os.environ["EBOOK_CONVERTER_ROOT"] = str(Path(__file__).parent.absolute())

os.environ["EBOOK_CONVERTER_ASSETS"] = os.path.join(
    os.environ["EBOOK_CONVERTER_ROOT"], f"assets"
)
if not os.path.exists(os.environ["EBOOK_CONVERTER_ASSETS"]):
    os.environ["EBOOK_CONVERTER_ASSETS"] = os.environ["EBOOK_CONVERTER_ROOT"]

calibre_hooks.hook()


class MyBoxLayout(BoxLayout):
    def my_callback(self):
        print("Hello")


class MainScreen(Screen):
    btn_select: MDRectangleFlatButton = ObjectProperty()
    btn_convert: MDRectangleFlatButton = ObjectProperty()
    label_message: Label = ObjectProperty()
    progress_bar: MDProgressBar = ObjectProperty()
    label_log: MDLabel = ObjectProperty()
    file_chooser = get_file_chooser()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.file_path: Optional[str] = None
        self.convert_thread: Optional[Thread] = None

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
        from convert_utils import MyProgressBar, MyLog
        from convert_utils import ConvertThread
        # For unknown reason without this calibre will fail to import this module on android
        import ebook_converter.ebooks.metadata.book.json_codec
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
        except Exception as e:
            self.label_message.text = str(e)
        else:
            self.label_message.text = "All modules can be imported."

    def log(self, *args):
        self.label_log.text = ' '.join(list(str(i) for i in args)) + '\n' + self.label_log.text


class MainApp(MDApp):
    pass


if __name__ == '__main__':
    MainApp().run()
