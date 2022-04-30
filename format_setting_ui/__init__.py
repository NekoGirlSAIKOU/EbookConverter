from typing import Dict, Optional, Union

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList
from kivymd.uix.selectioncontrol import MDCheckbox
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


class CheckboxLabel(MDBoxLayout):
    lbl: MDLabel = ObjectProperty()
    lbl_helper_text: MDLabel = ObjectProperty
    chk_box: MDCheckbox = ObjectProperty()

    @property
    def text(self):
        return self.lbl.text

    @text.setter
    def text(self, value):
        self.lbl.text = value

    @property
    def helper_text(self):
        return self.lbl_helper_text.text

    @helper_text.setter
    def helper_text(self, value):
        self.lbl_helper_text.text = value

    @property
    def active(self):
        return self.chk_box.active

    @active.setter
    def active(self, value):
        self.chk_box.active = value


class BaseSettingUi(MDList):
    def __init__(self, setting_map: Dict[str, Optional[Union[str, bool]]], **kwargs):
        super().__init__(**kwargs)
        self.setting_map = setting_map
        self.supported_settings = [
        ]
        self.setting_binds: Dict[str, Union[CheckboxLabel, MDTextField]] = {}

    def update_ui(self):
        """Update UI to show updated setting"""
        for key, widget in self.setting_binds.items():
            if isinstance(widget, MDTextField):
                widget.text = optional_str2str(self.setting_map[key])
            elif isinstance(widget, CheckboxLabel):
                widget.active = self.setting_map[key]
            else:
                raise RuntimeError(f"Unsupported bounded widget: {type(widget).__name__}")

    def update_setting(self):
        """update setting to save UI changes"""
        for key, widget in self.setting_binds.items():
            if isinstance(widget, MDTextField):
                self.setting_map[key] = str2optional_str(widget.text)
            elif isinstance(widget, CheckboxLabel):
                self.setting_map[key] = widget.active
            else:
                raise RuntimeError(f"Unsupported bounded widget: {type(widget).__name__}")

    def bind_settings(self, calibre_arg: str, default_value: Optional[Union[str, bool]],
                      widget: Union[CheckboxLabel, MDTextField]):
        self.supported_settings.append(calibre_arg)
        self.setting_map[calibre_arg] = self.setting_map.get(calibre_arg, default_value)
        self.setting_binds[calibre_arg] = widget


class BaseOutputSettingUi(BaseSettingUi):
    tf_book_title: MDTextField = ObjectProperty()

    def __init__(self, setting_map: Dict[str, Optional[Union[str, bool]]], **kwargs):
        super().__init__(setting_map, **kwargs)
        self.bind_settings('--title', None, self.tf_book_title)


class MobiOutputSettingUi(BaseOutputSettingUi):
    tf_file_type: MDTextField = ObjectProperty()
    tf_personal_doc: MDTextField = ObjectProperty()
    chk_lbl_dont_compress: CheckboxLabel = ObjectProperty()
    chk_lbl_no_inline_toc: CheckboxLabel = ObjectProperty()
    chk_lbl_share_not_sync: CheckboxLabel = ObjectProperty()

    def __init__(self, setting_map: Dict[str, Optional[Union[str, bool]]], **kwargs):
        super().__init__(setting_map, **kwargs)
        self.bind_settings('--mobi-file-type', 'old', self.tf_file_type)
        self.bind_settings('--personal-doc', '[PDOC]', self.tf_personal_doc)
        self.bind_settings('--dont-compress', False, self.chk_lbl_dont_compress)
        self.bind_settings('--no-inline-toc', False, self.chk_lbl_no_inline_toc)
        self.bind_settings('--share-not-sync', False, self.chk_lbl_share_not_sync)


class BaseInputSettingUi(BaseSettingUi):
    def __init__(self, setting_map: Dict[str, Optional[Union[str, bool]]], **kwargs):
        super().__init__(setting_map, **kwargs)


class EpubInputSettingUi(BaseInputSettingUi):
    tf_input_encoding: MDTextField = ObjectProperty()

    def __init__(self, setting_map: Dict[str, Optional[Union[str, bool]]], **kwargs):
        super().__init__(setting_map, **kwargs)
        self.bind_settings('--input-encoding', None, self.tf_input_encoding)
