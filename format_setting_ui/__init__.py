from typing import Dict, Optional, Union

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.list import MDList
from kivymd.uix.textfield import MDTextField

Builder.load_file('format_setting_ui/BaseOutputSettingUi.kv')
Builder.load_file('format_setting_ui/MobiOutputSettingUi.kv')


class BaseSettingUi(MDList):
    def __init__(self, setting_map: Dict[str, Optional[Union[str, bool]]], **kwargs):
        super().__init__(**kwargs)
        self.setting_map = setting_map
        self.support_settings = [
        ]

    def fill_settings(self):
        """FIll settings map using default settings"""
        pass

    def update_ui(self):
        """Update UI to show updated setting"""
        pass

    def update_setting(self):
        """update setting to save UI changes"""
        pass


class BaseOutputSettingUi(BaseSettingUi):
    tf_book_title: MDTextField = ObjectProperty()

    def __init__(self, setting_map: Dict[str, Optional[Union[str, bool]]], **kwargs):
        super().__init__(setting_map, **kwargs)
        self.support_settings.extend([
            '--title'
        ])

    def fill_settings(self):
        """FIll settings map using default settings"""
        self.setting_map['--title'] = self.setting_map.get('--title', '')

    def update_ui(self):
        """Update UI to show updated setting"""
        self.tf_book_title.text = self.setting_map['--title']

    def update_setting(self):
        """update setting to save UI changes"""
        print('update_setting: save tf_book_title: ', self.tf_book_title.text)
        self.setting_map['--title'] = self.tf_book_title.text


class MobiOutputSettingUi(BaseOutputSettingUi):
    tf_file_type: MDTextField = ObjectProperty()

    def __init__(self, setting_map: Dict[str, Optional[Union[str, bool]]], **kwargs):
        super().__init__(setting_map, **kwargs)
        self.support_settings.extend([
            '--mobi-file-type'
        ])

    def fill_settings(self):
        super(MobiOutputSettingUi, self).fill_settings()
        self.setting_map['--mobi-file-type'] = self.setting_map.get('--mobi-file-type', 'old')

    def update_ui(self):
        super(MobiOutputSettingUi, self).update_ui()
        self.tf_file_type.text = self.setting_map['--mobi-file-type']

    def update_setting(self):
        super(MobiOutputSettingUi, self).update_setting()
        self.setting_map['--mobi-file-type'] = self.tf_file_type.text
