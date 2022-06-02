import os
from typing import Optional

from plyer.facades import FileChooser
from plyer.utils import platform


def get_file_chooser() -> Optional[FileChooser]:
    if platform == 'android':
        # from plyer.platforms.android.filechooser import AndroidFileChooser
        from android_file_chooser_saf import AndroidFileChooserSAF
        from my_android_file_chooser import MyAndroidFileChooser
        try:
            os.listdir('/sdcard/Android')
        except:
            return AndroidFileChooserSAF()
        else:
            # If we have the permission to read and write to external storage, there
            # is no need to use the SAF implementation.
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
