"""
Hook some function to make calibre work on android.
"""
from plyer.utils import platform
AndroidStoragePath_get_sdcard_dir_origin=None

def AndroidStoragePath_get_sdcard_dir(self):
    try :
        return AndroidStoragePath_get_sdcard_dir_origin(self)
    except:
        return "/sdcard"


def hook():
    if platform == 'android':
        global AndroidStoragePath_get_sdcard_dir_origin
        from plyer.platforms.android.storagepath import AndroidStoragePath
        AndroidStoragePath_get_sdcard_dir_origin = AndroidStoragePath.get_sdcard_dir
        AndroidStoragePath.get_sdcard_dir = AndroidStoragePath_get_sdcard_dir
