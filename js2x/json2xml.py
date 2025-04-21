import sys
import json
from io import StringIO
import lxml.etree
import os
import math


INFSTR = '1e309'


replace = {'\\': '\\\\', '\n': '\\n', '\r': '\\r', '\t': '\\t', '"': '\\"'}


def escapejson(text):
    for c in replace:
        if c in text:
            text = text.replace(c, replace[c])
    for i in range(0x20):
        c = chr(i)
        if c in text:
            text = text.replace(c, '\\u%04x' % (ord(c),))
    return text


class JSON2XMLPrinter:
    input = {}
    output = None
    level = 0
    count = 0
    indent = None
    indentstr = ' '

    def __init__(self, output=sys.stdout):
        self.output = output
        self.count = 0
        self.level = 0

    def __call__(self, dict, name='dict'):
        self.input = dict
        # self.write('<?xml version="1.0"?>')
        self.dispatch(dict, name=name)

    def fill(self):
        if self.indent and self.count > 0:
            self.output.write('\n' + self.indentstr * self.level * self.indent)
        elif self.indent == 0:
            self.output.write('\n')

    def write(self, str):
        self.output.write(str)

    def welem(self, name, content):
        self.output.write(f'<{name}>{content}</{name}>')

    def wstart(self, name, attrs={}):
        self.fill()
        attrstr = ''
        for a in attrs:
            attrstr += f'{a}="{attrs[a]}"'
        if attrstr:
            attrstr = ' ' + attrstr
        self.output.write(f'<{name}{attrstr}>')
        self.level += 1
        self.count += 1

    def wend(self, name, fill=True):
        self.level -= 1
        if fill:
            self.fill()
        self.output.write(f'</{name}>')

    def dispatch(self, d, name='dict'):
        if isinstance(d, dict):
            cname = d['_class'] if '_class' in d else None
            self.wstart(name, {'_class': cname} if cname else {})
            for k in d:
                if k == '_class':
                    continue
                if not isinstance(d[k], dict) and not isinstance(d[k], list):
                    self.wstart(k)
                self.dispatch(d[k], k)
                if not isinstance(d[k], dict) and not isinstance(d[k], list):
                    self.wend(k)
            self.wend(name)
        elif isinstance(d, list):
            self.wstart(name, {'_class': 'list'})
            for k in d:
                if not isinstance(k, dict) and not isinstance(k, list):
                    self.wstart('item')
                self.dispatch(k, name='item')
                if not isinstance(k, dict) and not isinstance(k, list):
                    self.wend('item')
            self.wend(name)
        elif isinstance(d, int) or isinstance(d, float):
#            self.wstart(name)
            self.wstart('num')
            if math.isinf(d):
                self.write(f'{INFSTR}')
            else:
                self.write(f'{d}')
            self.wend('num', False)
#            self.wend(name)
        elif isinstance(d, str):
#            self.wstart(name)
            self.wstart('str')
            self.write(escapejson(d.replace('&', '&amp;').replace('<', '&lt;')))
            self.wend('str', False)
#            self.wend(name)
        else:
#            self.wstart(name)
            self.write(json.dumps(d))
#            self.wend(name)


def runXSLT(docstr, xsltfname, params={}, base=None):
    if not os.path.isabs(xsltfname):
        if base is None:
            base = os.path.dirname(sys.modules[__name__].__file__)
        xsltfname = os.path.join(base, xsltfname)
    with open(xsltfname) as f:
        xsltstr = f.read()
    xsltdoc = lxml.etree.fromstring(xsltstr)
    transform = lxml.etree.XSLT(xsltdoc)
    xmldoc = lxml.etree.fromstring(docstr)
    result = transform(xmldoc, **params)
    return str(result)


def xml2json(xmlstr, filename=None, indent=None, **kw):
    ilev = 1 if indent is None else int(indent)
    indent = 0 if indent is None or indent == 0 else 1
    params = dict(indentstr="'%s'" % (' ' * ilev), indent='%d' % indent)
    return runXSLT(xmlstr, 'xsl/xml2json.xsl', params=params)


def json2xml(jstr, filename=None, indent=None, **kw):
    jdict = json.loads(jstr)
    name = 'dict'
    if isinstance(jdict, dict) and len(jdict) == 1:
        c1, c2 = list(jdict.items())[0]
        if isinstance(c2, dict) or True:
            name, jdict = c1, c2
    output = StringIO()
    jp = JSON2XMLPrinter(output)
    jp.indent = indent
    jp(jdict, name=name)
    xstr = output.getvalue()
    return xstr
