import mimetypes
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
            from ebook_converter.ebooks.conversion.cli import main as ebook_converter_main
            import pkg_resources
            mimetypes.init([pkg_resources.resource_filename('ebook_converter',
                                                            'data/mime.types')])

            # For unknown reason without these imports calibre will fail to import this module on android
            import ebook_converter.ebooks.metadata.book.json_codec
            import ebook_converter.ebooks.docx.to_html
            import ebook_converter.ebooks.unihandecode.unidecoder
            import ebook_converter.ebooks.txt
            import ebook_converter.ebooks.txt.processor
            import ebook_converter.ebooks.metadata.meta
            import ebook_converter.ebooks.metadata.html
            import ebook_converter.ebooks.oeb.transforms.metadata
            import ebook_converter.ebooks.html.input
            import ebook_converter.ebooks.conversion.utils
            import ebook_converter.utils.smartypants
            import ebook_converter.ebooks.mobi.reader
            import ebook_converter.ebooks.mobi.reader.mobi6
            import ebook_converter.ebooks.mobi.reader.mobi8

            ebook_converter_main(args=self.args, log=self.log, reporter=self.reporter)
        except Exception as e:
            if isinstance(self.reporter, MyProgressBar) and self.reporter.call_back is not ...:
                self.reporter.call_back(100, f"Failed: {type(e).__name__}: {e}")
                self.log.error(f"Failed: {type(e).__name__}: {e}")
            raise
        else:
            if isinstance(self.reporter, MyProgressBar) and self.reporter.call_back is not ...:
                self.reporter.call_back(100, "Finished")
