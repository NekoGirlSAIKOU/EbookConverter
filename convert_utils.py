from ebook_converter.ebooks.conversion.cli import ProgressBar
from ebook_converter.utils.logging import Log


class MyProgressBar(ProgressBar):
    def __init__(self, log, progress_call_back=...):
        super().__init__(log)
        self.call_back = progress_call_back

    def __call__(self, frac, msg=''):
        if msg:
            percent = int(frac * 100)
            self.log.info(f'{percent}% {msg}')
            if self.call_back is not ...:
                self.call_back(percent, f'{percent}% {msg}')


class MyLog(Log):
    def __init__(self, print_call_back=...):
        super().__init__()
        self.print_call_back = print_call_back

    def prints(self, level, *args, **kwargs):
        if self.print_call_back is not ...:
            self.print_call_back(level, *args, **kwargs)
        if level < self.filter_level:
            return
        print(*args, **kwargs)

    def print_with_flush(self, level, *args, **kwargs):
        if self.print_call_back is not ...:
            self.print_call_back(level, *args, **kwargs)
        if level < self.filter_level:
            return
        print(*args, **kwargs)
