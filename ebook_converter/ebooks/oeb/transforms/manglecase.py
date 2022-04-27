"""
CSS case-mangling transform.
"""
import string

from lxml import etree

from ebook_converter import constants as const
from ebook_converter.ebooks.oeb import base
from ebook_converter.ebooks.oeb import parse_utils
from ebook_converter.ebooks.oeb.stylizer import Stylizer


__license__ = 'GPL v3'
__copyright__ = '2008, Marshall T. Vandegrift <llasram@gmail.com>'

CASE_MANGLER_CSS = """
.calibre_lowercase {
    font-variant: normal;
    font-size: 0.65em;
}
"""

TEXT_TRANSFORMS = {'capitalize', 'uppercase', 'lowercase'}


class CaseMangler(object):

    @classmethod
    def config(cls, cfg):
        return cfg

    @classmethod
    def generate(cls, opts):
        return cls()

    def __call__(self, oeb, context):
        oeb.logger.info('Applying case-transforming CSS...')
        self.oeb = oeb
        self.opts = context
        self.profile = context.source
        self.mangle_spine()

    def mangle_spine(self):
        id, href = self.oeb.manifest.generate('manglecase', 'manglecase.css')
        self.oeb.manifest.add(id, href, base.CSS_MIME, data=CASE_MANGLER_CSS)
        for item in self.oeb.spine:
            html = item.data
            relhref = item.relhref(href)
            etree.SubElement(html.find(base.tag('xhtml', 'head')),
                             base.tag('xhtml', 'link'), rel='stylesheet',
                             href=relhref, type=base.CSS_MIME)
            stylizer = Stylizer(html, item.href, self.oeb, self.opts,
                                self.profile)
            self.mangle_elem(html.find(base.tag('xhtml', 'body')), stylizer)

    def text_transform(self, transform, text):
        if transform == 'capitalize':
            return string.capwords(text)
        elif transform == 'uppercase':
            return text.upper()
        elif transform == 'lowercase':
            return text.lower()
        return text

    def split_text(self, text):
        results = ['']
        isupper = text[0].isupper()
        for char in text:
            if char.isupper() == isupper:
                results[-1] += char
            else:
                isupper = not isupper
                results.append(char)
        return results

    def smallcaps_elem(self, elem, attr):
        texts = self.split_text(getattr(elem, attr))
        setattr(elem, attr, None)
        last = elem if attr == 'tail' else None
        attrib = {'class': 'calibre_lowercase'}
        for text in texts:
            if text.isupper():
                if last is None:
                    elem.text = text
                else:
                    last.tail = text
            else:
                child = elem.makeelement(base.tag('xhtml', 'span'),
                                         attrib=attrib)
                child.text = text.upper()
                if last is None:
                    elem.insert(0, child)
                else:
                    # addnext() moves the tail for some reason
                    tail = last.tail
                    last.addnext(child)
                    last.tail = tail
                    child.tail = None
                last = child

    def mangle_elem(self, elem, stylizer):
        if not isinstance(elem.tag, (str, bytes)) or \
           parse_utils.namespace(elem.tag) != const.XHTML_NS:
            return
        children = list(elem)
        style = stylizer.style(elem)
        transform = style['text-transform']
        variant = style['font-variant']
        if elem.text:
            if transform in TEXT_TRANSFORMS:
                elem.text = self.text_transform(transform, elem.text)
            if variant == 'small-caps':
                self.smallcaps_elem(elem, 'text')
        for child in children:
            self.mangle_elem(child, stylizer)
            if child.tail:
                if transform in TEXT_TRANSFORMS:
                    child.tail = self.text_transform(transform, child.tail)
                if variant == 'small-caps':
                    self.smallcaps_elem(child, 'tail')
