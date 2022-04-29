from typing import Optional

from plyer.facades import FileChooser
from plyer.utils import platform


def get_file_chooser() -> Optional[FileChooser]:
    if platform == 'android':
        from plyer.platforms.android.filechooser import AndroidFileChooser
        from my_android_file_chooser import MyAndroidFileChooser
        return MyAndroidFileChooser()

    elif platform == 'ios':
        from plyer.platforms.ios.filechooser import IOSFileChooser
        return IOSFileChooser()
    elif platform == 'win':
        from plyer.platforms.win.filechooser import WinFileChooser
        return WinFileChooser()
    elif platform == 'macosx':
        from plyer.platforms.macosx.filechooser import MacOSXFileChooser
        return MacOSXFileChooser()
    elif platform == 'linux':
        from plyer.platforms.linux.filechooser import LinuxFileChooser
        return LinuxFileChooser()
    else:
        return None
