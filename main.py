"""
Command line interface to conversion sub-system.
Just to test how to get outputs and progress from
ebook_converter and how to control it.
"""
from __future__ import annotations
import sys
from ebook_converter.ebooks.conversion.cli import ProgressBar
from ebook_converter.main import main as ebook_converter_main
from ebook_converter.utils.logging import Log


class MyProgressBar(ProgressBar):
    def __call__(self, frac, msg=''):
        if msg:
            percent = int(frac * 100)
            print(f'{percent}% {msg}')


class MyLog(Log):
    def prints(self, level, *args, **kwargs):
        if level < self.filter_level:
            return
        print(*args, **kwargs)

    def print_with_flush(self, level, *args, **kwargs):
        if level < self.filter_level:
            return
        print(*args, **kwargs)


def main():
    log = MyLog()
    ebook_converter_main(args=sys.argv, log=log, reporter=MyProgressBar(log))


if __name__ == '__main__':
    main()
