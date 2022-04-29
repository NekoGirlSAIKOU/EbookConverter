import re

from lxml import etree
try:
    import html5_parser
except:
    html5_parser = None

from ebook_converter import constants as const
from ebook_converter import xml_replace_entities
from ebook_converter.ebooks.chardet import strip_encoding_declarations
from ebook_converter.ebooks.chardet import xml_to_unicode
from ebook_converter.utils.cleantext import clean_xml_chars


def parse_html5(raw, decoder=None, log=None, discard_namespaces=False,
                line_numbers=True, linenumber_attribute=None,
                replace_entities=True, fix_newlines=True):
    if not html5_parser:
        raise RuntimeError("No html5_parser installed")
    if isinstance(raw, bytes):
        raw = xml_to_unicode(raw)[0] if decoder is None else decoder(raw)
    if replace_entities:
        raw = xml_replace_entities(raw)
    if fix_newlines:
        raw = raw.replace('\r\n', '\n').replace('\r', '\n')
    raw = clean_xml_chars(raw)
    root = html5_parser.parse(raw, maybe_xhtml=not discard_namespaces,
                              line_number_attr=linenumber_attribute,
                              keep_doctype=False, sanitize_names=True)
    if ((discard_namespaces and root.tag != 'html') or
        (not discard_namespaces and
         (root.tag != '{%s}%s' % (const.XHTML_NS, 'html') or root.prefix))):
        raise ValueError('Failed to parse correctly, root has tag: %s and '
                         'prefix: %s' % (root.tag, root.prefix))
    return root


def handle_private_entities(data):
    # Process private entities
    pre = ''
    idx = data.find('<html')
    if idx == -1:
        idx = data.find('<HTML')
    if idx > -1:
        pre = data[:idx]
        num_of_nl_in_pre = pre.count('\n')
        if '<!DOCTYPE' in pre:  # Handle user defined entities
            user_entities = {}
            for match in re.finditer(r'<!ENTITY\s+(\S+)\s+([^>]+)', pre):
                val = match.group(2)
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                user_entities[match.group(1)] = val
            if user_entities:
                data = ('\n' * num_of_nl_in_pre) + data[idx:]
                pat = re.compile(r'&(%s);' % ('|'.join(user_entities.keys())))
                data = pat.sub(lambda m: user_entities[m.group(1)], data)
    return data


def parse(raw, decoder=None, log=None, line_numbers=True,
          linenumber_attribute=None, replace_entities=True,
          force_html5_parse=False):
    if isinstance(raw, bytes):
        raw = xml_to_unicode(raw)[0] if decoder is None else decoder(raw)
    raw = handle_private_entities(raw)
    if replace_entities:
        raw = xml_replace_entities(raw).replace('\0', '')  # Handle &#0;
    raw = raw.replace('\r\n', '\n').replace('\r', '\n')

    # Remove any preamble before the opening html tag as it can cause problems,
    # especially doctypes, preserve the original linenumbers by inserting
    # newlines at the start
    pre = raw[:2048]
    for match in re.finditer(r'<\s*html', pre, flags=re.I):
        newlines = raw.count('\n', 0, match.start())
        raw = ('\n' * newlines) + raw[match.start():]
        break

    raw = strip_encoding_declarations(raw, limit=10*1024,
                                      preserve_newlines=True)
    if force_html5_parse:
        return parse_html5(raw, log=log, line_numbers=line_numbers,
                           linenumber_attribute=linenumber_attribute,
                           replace_entities=False, fix_newlines=False)
    try:
        ans = etree.fromstring(raw)
        if ans.tag != '{%s}html' % const.XHTML_NS:
            raise ValueError('Root tag is not <html> in the XHTML namespace')
        if linenumber_attribute:
            for elem in ans.iter(etree.element):
                if elem.sourceline is not None:
                    elem.set(linenumber_attribute, str(elem.sourceline))
        return ans
    except Exception:
        if log is not None:
            log.exception('Failed to parse as XML, parsing as tag soup')
        return parse_html5(raw, log=log, line_numbers=line_numbers,
                           linenumber_attribute=linenumber_attribute,
                           replace_entities=False, fix_newlines=False)


if __name__ == '__main__':
    root = parse_html5('\n<html><head><title>a\n</title><p b=1 c=2 a=0>&nbsp;'
                       '\n<b>b<svg ass="wipe" viewbox="0">',
                       discard_namespaces=False)
    print(etree.tostring(root, encoding='utf-8'))
    print()
