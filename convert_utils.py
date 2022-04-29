from threading import Thread

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
        print(level, *args, **kwargs)

    def print_with_flush(self, level, *args, **kwargs):
        if self.print_call_back is not ...:
            self.print_call_back(level, *args, **kwargs)
        if level < self.filter_level:
            return
        print(*args, **kwargs)


class ConvertThread(Thread):
    def __init__(self, args: list, log: Log, reporter: ProgressBar):
        super().__init__()
        self.args = args
        self.log = log
        self.reporter = reporter

    def run(self) -> None:
        try:
            from ebook_converter.main import main as ebook_converter_main

            # For unknown reason without these imports calibre will fail to import this module on android
            import ebook_converter.ebooks.metadata.book.json_codec
            #import ebook_converter.ebooks.docx.to_html

            ebook_converter_main(args=self.args, log=self.log, reporter=self.reporter)
        except Exception as e:
            if isinstance(self.reporter, MyProgressBar) and self.reporter.call_back is not ...:
                self.reporter.call_back(100, f"Failed: {type(e).__name__}: {e}")
                self.log.error(f"Failed: {type(e).__name__}: {e}")
            raise
        else:
            if isinstance(self.reporter, MyProgressBar) and self.reporter.call_back is not ...:
                self.reporter.call_back(100, "Finished")
