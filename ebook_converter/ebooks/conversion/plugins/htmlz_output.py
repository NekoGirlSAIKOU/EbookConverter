import io
import os

from ebook_converter.customize.conversion import OutputFormatPlugin, \
    OptionRecommendation
from ebook_converter.ptempfile import TemporaryDirectory


__license__ = 'GPL 3'
__copyright__ = '2011, John Schember <john@nachtimwald.com>'
__docformat__ = 'restructuredtext en'


class HTMLZOutput(OutputFormatPlugin):

    name = 'HTMLZ Output'
    author = 'John Schember'
    file_type = 'htmlz'
    commit_name = 'htmlz_output'
    ui_data = {'css_choices': {'class': 'Use CSS classes',
                               'inline': 'Use the style attribute',
                               'tag': 'Use HTML tags wherever possible'},
               'sheet_choices': {'external': 'Use an external CSS file',
                                 'inline': 'Use a <style> tag in the HTML '
                                 'file'}}

    options = {
        OptionRecommendation(name='htmlz_css_type', recommended_value='class',
            level=OptionRecommendation.LOW,
            choices=list(ui_data['css_choices']),
            help='Specify the handling of CSS. Default is class.\n'
                 'class: {class}\n'
                 'inline: {inline}\n'
                 'tag: {tag}'.format(**ui_data['css_choices'])),
        OptionRecommendation(name='htmlz_class_style', recommended_value='external',
            level=OptionRecommendation.LOW,
            choices=list(ui_data['sheet_choices']),
            help='How to handle the CSS when using css-type = \'class\'.\n'
                 'Default is external.\n'
                 'external: {external}\n'
                 'inline: {inline}'.format(**ui_data['sheet_choices'])),
        OptionRecommendation(name='htmlz_title_filename',
            recommended_value=False, level=OptionRecommendation.LOW,
            help='If set this option causes the file name of the HTML file '
                 'inside the HTMLZ archive to be based on the book title.'
        )
    }

    def convert(self, oeb_book, output_path, input_plugin, opts, log):
        from lxml import etree
        from ebook_converter.ebooks.oeb.base import OEB_IMAGES, SVG_MIME
        from ebook_converter.ebooks.metadata.opf2 import OPF, metadata_to_opf
        from ebook_converter.utils.zipfile import ZipFile
        from ebook_converter.utils.filenames import ascii_filename

        # HTML
        if opts.htmlz_css_type == 'inline':
            from ebook_converter.ebooks.htmlz.oeb2html import OEB2HTMLInlineCSSizer
            OEB2HTMLizer = OEB2HTMLInlineCSSizer
        elif opts.htmlz_css_type == 'tag':
            from ebook_converter.ebooks.htmlz.oeb2html import OEB2HTMLNoCSSizer
            OEB2HTMLizer = OEB2HTMLNoCSSizer
        else:
            from ebook_converter.ebooks.htmlz.oeb2html import OEB2HTMLClassCSSizer as OEB2HTMLizer

        with TemporaryDirectory(u'_htmlz_output') as tdir:
            htmlizer = OEB2HTMLizer(log)
            html = htmlizer.oeb2html(oeb_book, opts)

            fname = u'index'
            if opts.htmlz_title_filename:
                from ebook_converter.utils.filenames import shorten_components_to
                fname = shorten_components_to(100, (ascii_filename(str(oeb_book.metadata.title[0])),))[0]
            with open(os.path.join(tdir, fname+u'.html'), 'wb') as tf:
                if isinstance(html, str):
                    html = html.encode('utf-8')
                tf.write(html)

            # CSS
            if opts.htmlz_css_type == 'class' and opts.htmlz_class_style == 'external':
                with open(os.path.join(tdir, u'style.css'), 'wb') as tf:
                    tf.write(htmlizer.get_css(oeb_book))

            # Images
            images = htmlizer.images
            if images:
                if not os.path.exists(os.path.join(tdir, u'images')):
                    os.makedirs(os.path.join(tdir, u'images'))
                for item in oeb_book.manifest:
                    if item.media_type in OEB_IMAGES and item.href in images:
                        if item.media_type == SVG_MIME:
                            data = etree.tostring(item.data, encoding='unicode')
                        else:
                            data = item.data
                        fname = os.path.join(tdir, u'images', images[item.href])
                        with open(fname, 'wb') as img:
                            img.write(data)

            # Cover
            cover_path = None
            try:
                cover_data = None
                if oeb_book.metadata.cover:
                    term = oeb_book.metadata.cover[0].term
                    cover_data = oeb_book.guide[term].item.data
                if cover_data:
                    from ebook_converter.utils.img import save_cover_data_to
                    cover_path = os.path.join(tdir, u'cover.jpg')
                    with open(cover_path, 'w') as cf:
                        cf.write('')
                    save_cover_data_to(cover_data, cover_path)
            except:
                import traceback
                traceback.print_exc()

            # Metadata
            with open(os.path.join(tdir, u'metadata.opf'), 'wb') as mdataf:
                opf = OPF(io.BytesIO(etree.tostring(oeb_book.metadata.to_opf1(), encoding='UTF-8')))
                mi = opf.to_book_metadata()
                if cover_path:
                    mi.cover = u'cover.jpg'
                mdataf.write(metadata_to_opf(mi))

            htmlz = ZipFile(output_path, 'w')
            htmlz.add_dir(tdir)
