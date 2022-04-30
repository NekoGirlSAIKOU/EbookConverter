from __future__ import annotations
import os
import sys
from pathlib import Path
from threading import Thread
from typing import Optional, Dict, Union

from kivy.clock import mainthread
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.toolbar import MDToolbar, MDActionTopAppBarButton
from plyer.utils import platform

from format_setting_ui import MobiOutputSettingUi, BaseSettingUi, BaseOutputSettingUi, BaseInputSettingUi, \
    EpubInputSettingUi, MobiInputSettingUi, EpubOutputSettingUi
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
Label.font_name = "NotoSansCJK-Regular.ttc"
MDLabel.font_name = "NotoSansCJK-Regular.ttc"
MDActionTopAppBarButton.font_name = "fonts/materialdesignicons-webfont.ttf"
MDIcon.font_name = "fonts/materialdesignicons-webfont.ttf"


class InputBottomNavigationPage(MDBoxLayout):
    label_tip: MDLabel = ObjectProperty()
    scroll_view: ScrollView = ObjectProperty()
    convert_bottom_navigation_page: ConvertBottomNavigationPage = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_setting_ui: Optional[BaseSettingUi] = None

        self._input_format: Optional[str] = None

    @property
    def input_format(self):
        return self._input_format

    @input_format.setter
    def input_format(self, value):
        self._input_format = value
        self.label_tip.text = f"Input setting for {value}:"

        if self.current_setting_ui:
            self.update_setting()
            self.scroll_view.remove_widget(self.current_setting_ui)
            pass
        if value == 'epub':
            self.current_setting_ui = EpubInputSettingUi(self.setting_map)
        elif value == 'mobi':
            self.current_setting_ui = MobiInputSettingUi(self.setting_map)
        else:
            self.current_setting_ui = BaseInputSettingUi(self.setting_map)

        self.scroll_view.add_widget(self.current_setting_ui)
        self.current_setting_ui.update_ui()

    @property
    def setting_map(self):
        return self.convert_bottom_navigation_page.setting_map


    @property
    def supported_settings(self):
        return self.current_setting_ui.supported_settings

    def update_setting(self):
        """update setting to save UI changes"""
        self.current_setting_ui.update_setting()


class ConvertBottomNavigationPage(ScrollView):
    input_bottom_navigation_page: InputBottomNavigationPage = ObjectProperty()
    output_bottom_navigation_page: OutputBottomNavigationPage = ObjectProperty()

    btn_select: MDRectangleFlatButton = ObjectProperty()
    btn_convert: MDRectangleFlatButton = ObjectProperty()
    label_message: Label = ObjectProperty()
    progress_bar: MDProgressBar = ObjectProperty()
    label_log: MDLabel = ObjectProperty()
    file_chooser = get_file_chooser()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_path = None
        self.setting_map: Dict[str, Optional[Union[str, bool]]] = {}
        self.convert_thread:Optional[Thread] = None

    @property
    def input_format(self):
        return self.input_bottom_navigation_page.input_format

    @input_format.setter
    def input_format(self, value):
        self.input_bottom_navigation_page.input_format = value

    @property
    def output_format(self):
        return self.output_bottom_navigation_page.output_format

    def update_setting(self):
        self.input_bottom_navigation_page.update_setting()
        self.output_bottom_navigation_page.update_setting()

    @property
    def setting_list(self):
        r = []
        for item in self.setting_map.items():
            if item[0] in self.input_bottom_navigation_page.supported_settings \
                    or item[0] in self.output_bottom_navigation_page.supported_settings:
                if isinstance(item[1], bool):
                    if item[1]:
                        r.append(item[0])
                else:
                    if item[1] is not None:
                        r.append(item[0])
                        r.append(item[1])
        return r

    def select_file_to_convert(self):
        self.file_path = None
        if self.file_chooser:
            if platform == 'android':
                self.file_chooser.open_file(on_selection=self.on_open_file)
            else:
                file_paths = self.file_chooser.open_file()
                self.on_open_file(file_paths)

    @mainthread # Android may callback this on other thread.
    def on_open_file(self, file_path):
        if file_path:
            file_path = file_path[0]
            self.file_path = file_path
            self.log(f"Select input file: {file_path}")
            self.btn_convert.disabled = False
            self.get_root_window()
            self.input_format = file_path[file_path.rfind('.') + 1:]

    def start_convert(self):
        from utils_convert import MyProgressBar, MyLog
        from utils_convert import ConvertThread
        self.label_message.text = "Converting"
        self.progress_bar.value = 0
        log = MyLog(print_call_back=self.on_log_callback)
        progress = MyProgressBar(log, progress_call_back=self.on_progress_changed)
        self.update_setting()
        log.info("Convert setting: ", self.setting_list)
        args = ["ebook-convert", self.file_path,
                self.file_path + '.' + self.output_bottom_navigation_page.output_format]
        args.extend(self.setting_list)
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
        except Exception as e:
            self.label_message.text = str(e)
        else:
            self.label_message.text = "All modules can be imported."

    def log(self, *args):
        self.label_log.text = ' '.join(list(str(i) for i in args)) + '\n' + self.label_log.text


class OutputBottomNavigationPage(MDBoxLayout):
    btn_choose_format: MDFlatButton = ObjectProperty()
    menu_formats: MDDropdownMenu = ObjectProperty()
    scroll_view: ScrollView = ObjectProperty()
    convert_bottom_navigation_page: ConvertBottomNavigationPage = ObjectProperty()
    SUPPORTED_OUTPUT_FORMATS = ['epub', 'mobi']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_setting_ui: Optional[BaseSettingUi] = None

        self._output_format = 'mobi'

        self.menu_formats = MDDropdownMenu(width_mult=4)
        self.menu_formats.items = list({
                                           "viewclass": "OneLineListItem",
                                           "text": format,
                                           "on_release": lambda x=format: self.on_format_chosen(x),
                                       } for format in self.SUPPORTED_OUTPUT_FORMATS)

    @property
    def output_format(self):
        return self._output_format

    @output_format.setter
    def output_format(self, value):
        self._output_format = value
        self.btn_choose_format.text = f"Choose output format: {value}"

        if self.current_setting_ui:
            self.update_setting()
            self.scroll_view.remove_widget(self.current_setting_ui)
            pass
        if value == 'epub':
            self.current_setting_ui = EpubOutputSettingUi(self.setting_map)
        elif value == 'mobi':
            self.current_setting_ui = MobiOutputSettingUi(self.setting_map)
        else:
            self.current_setting_ui = BaseOutputSettingUi(self.setting_map)

        self.scroll_view.add_widget(self.current_setting_ui)
        self.current_setting_ui.update_ui()

    def on_format_chosen(self, value):
        self.menu_formats.dismiss()
        self.output_format = value

    @property
    def setting_map(self):
        return self.convert_bottom_navigation_page.setting_map

    @property
    def supported_settings(self):
        return self.current_setting_ui.supported_settings

    def update_setting(self):
        """update setting to save UI changes"""
        self.current_setting_ui.update_setting()


class MainScreen(Screen):
    toolbar_menu: MDDropdownMenu = ObjectProperty()
    input_bottom_navigation_page: InputBottomNavigationPage = ObjectProperty()
    convert_bottom_navigation_page: ConvertBottomNavigationPage = ObjectProperty()
    output_bottom_navigation_page: OutputBottomNavigationPage = ObjectProperty()

    def __init__(self, app: MainApp, **kw):
        super().__init__(**kw)
        self.app = app
        self.toolbar_menu = MDDropdownMenu(width_mult=4)
        self.toolbar_menu.items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Setting",
                "on_release": self.on_setting_menu_clicked,
            }
        ]

    @property
    def file_path(self):
        return self.convert_bottom_navigation_page.file_path

    def on_toolbar_menu_clicked(self, button):
        self.toolbar_menu.caller = button
        self.toolbar_menu.open()

    def on_setting_menu_clicked(self):
        self.toolbar_menu.dismiss()
        self.app.sm.switch_to(screen=SettingScreen(self.app, self))


class SettingScreen(Screen):
    app = ObjectProperty()
    parent_screen = ObjectProperty()

    def __init__(self, app: MainApp, parent_screen: Screen, **kw):
        super().__init__(**kw)
        self.app = app
        self.parent_screen = parent_screen

    def on_leave_button_clicked(self):
        self.app.sm.switch_to(self.parent_screen, direction='left')


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_screen: Optional[MainScreen] = None
        self.sm: Optional[ScreenManager] = None

    def build(self):
        self.main_screen = MainScreen(self)
        self.sm = ScreenManager()
        self.sm.add_widget(self.main_screen)
        return self.sm

    def on_start(self):
        self.main_screen.input_bottom_navigation_page.input_format = None
        self.main_screen.output_bottom_navigation_page.output_format = 'mobi'

    def on_pause(self):
        return True

    def on_stop(self):
        self.main_screen = None
        self.sm = None


if __name__ == '__main__':
    MainApp().run()
