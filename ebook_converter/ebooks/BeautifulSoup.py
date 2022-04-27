# License: GPLv3 Copyright: 2019, Kovid Goyal <kovid at kovidgoyal.net>
is_html5_parser_exists = True
import bs4
try:
    from html5_parser import soup as html5_soup
except:
    is_html5_parser_exists = False

from ebook_converter.ebooks import chardet
from ebook_converter.utils import cleantext


def parse_html(markup):
    if not is_html5_parser_exists:
        raise RuntimeError("No html5_parser")

    if isinstance(markup, str):
        markup = chardet.strip_encoding_declarations(markup)
        markup = chardet.substitute_entites(markup)
    else:
        markup = chardet.xml_to_unicode(markup, strip_encoding_pats=True,
                                        resolve_entities=True)[0]
    markup = cleantext.clean_xml_chars(markup)
    return html5_soup.parse(markup, return_root=False)


def prettify(soup):
    ans = soup.prettify()
    if isinstance(ans, bytes):
        ans = ans.decode('utf-8')
    return ans


def html5_parser(markup='', *a, **kw):
    return parse_html(markup)


def beautiful_soup_parser(markup='', *a, **kw):
    return bs4.BeautifulSoup(markup, 'xml')
