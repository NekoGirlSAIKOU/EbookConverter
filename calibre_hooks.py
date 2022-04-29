"""
Hook some function to make calibre work on android.
"""
import os

import pkg_resources

resource_filename_ori = None


def resource_filename(package_or_requirement: str, resource_name: str):
    if resource_name.endswith(".py"):
        # py will be compiled to pyc so I have to change it.
        resource_name += '.txt'
    return os.path.join(os.environ["EBOOK_CONVERTER_ROOT"], package_or_requirement, resource_name)


def hook():
    global resource_filename_ori
    resource_filename_ori = pkg_resources.resource_filename
    pkg_resources.resource_filename = resource_filename
