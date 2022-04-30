from typing import Dict, Optional, Union

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList
from kivymd.uix.textfield import MDTextField

Builder.load_file('format_setting_ui/BaseSettingUi.kv')

Builder.load_file('format_setting_ui/BaseOutputSettingUi.kv')
Builder.load_file('format_setting_ui/MobiOutputSettingUi.kv')

Builder.load_file('format_setting_ui/BaseInputSettingUi.kv')
Builder.load_file('format_setting_ui/EpubInputSettingUi.kv')


def str2optional_str(s: str):
    """convert 'None' and 'null' to None"""
    if s.lower() == 'none' or s.lower() == 'null':
        return None
    else:
        return s


def optional_str2str(s: Optional[str]):
    """convert None to 'null'"""
    if s is None:
        return 'null'
    else:
        return s


class BaseSettingUi(MDList):
    def __init__(self, setting_map: Dict[str, Optional[Union[str, bool]]], **kwargs):
        super().__init__(**kwargs)
        self.setting_map = setting_map
        self.supported_settings = [
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
        self.supported_settings.extend([
            '--title'
        ])

    def fill_settings(self):
        """FIll settings map using default settings"""
        self.setting_map['--title'] = self.setting_map.get('--title', None)

    def update_ui(self):
        """Update UI to show updated setting"""
        self.tf_book_title.text = optional_str2str(self.setting_map['--title'])

    def update_setting(self):
        """update setting to save UI changes"""
        print('update_setting: save tf_book_title: ', self.tf_book_title.text)
        self.setting_map['--title'] = str2optional_str(self.tf_book_title.text)


class MobiOutputSettingUi(BaseOutputSettingUi):
    tf_file_type: MDTextField = ObjectProperty()
    tf_personal_doc: MDTextField = ObjectProperty()

    def __init__(self, setting_map: Dict[str, Optional[Union[str, bool]]], **kwargs):
        super().__init__(setting_map, **kwargs)
        self.supported_settings.extend([
            '--mobi-file-type',
            '--personal-doc'
        ])

    def fill_settings(self):
        super(MobiOutputSettingUi, self).fill_settings()
        self.setting_map['--mobi-file-type'] = self.setting_map.get('--mobi-file-type', 'old')
        self.setting_map['--personal-doc'] = self.setting_map.get('--personal-doc', '[PDOC]')

    def update_ui(self):
        super(MobiOutputSettingUi, self).update_ui()
        self.tf_file_type.text = optional_str2str(self.setting_map['--mobi-file-type'])
        self.tf_personal_doc.text = optional_str2str(self.setting_map['--personal-doc'])

    def update_setting(self):
        super(MobiOutputSettingUi, self).update_setting()
        self.setting_map['--mobi-file-type'] = str2optional_str(self.tf_file_type.text)
        self.setting_map['--personal-doc'] = str2optional_str(self.tf_personal_doc.text)


class BaseInputSettingUi(BaseSettingUi):
    tf_book_title: MDTextField = ObjectProperty()

    def __init__(self, setting_map: Dict[str, Optional[Union[str, bool]]], **kwargs):
        super().__init__(setting_map, **kwargs)
        self.supported_settings.extend([

        ])

    def fill_settings(self):
        """FIll settings map using default settings"""
        pass

    def update_ui(self):
        """Update UI to show updated setting"""
        pass

    def update_setting(self):
        """update setting to save UI changes"""
        pass


class EpubInputSettingUi(BaseInputSettingUi):
    tf_input_encoding: MDTextField = ObjectProperty()

    def __init__(self, setting_map: Dict[str, Optional[Union[str, bool]]], **kwargs):
        super().__init__(setting_map, **kwargs)
        self.supported_settings.extend([
            '--input-encoding'
        ])

    def fill_settings(self):
        """FIll settings map using default settings"""
        self.setting_map['--input-encoding'] = self.setting_map.get('--input-encoding', None)

    def update_ui(self):
        """Update UI to show updated setting"""
        self.tf_input_encoding.text = optional_str2str(self.setting_map['--input-encoding'])

    def update_setting(self):
        """update setting to save UI changes"""
        self.setting_map['--input-encoding'] = str2optional_str(self.tf_input_encoding.text)
