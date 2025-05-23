import sys
import os
import json
import unittest

import js2x as json2xml

def read_file(filename):
    with open(filename, "r") as pyfile:
        source = pyfile.read()
    return source

class JSON2XMLTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def check_roundtrip(self, source, origRestored=True):
        xstr = json2xml.json2xml(source)
        jsstr = json2xml.xml2json(xstr)
        xstr2 = json2xml.json2xml(jsstr)
        jsstr2 = json2xml.xml2json(xstr2)
        if len(xstr) < 250:
            print(f'res XML: {xstr}')
            print(f'res JSON: {jsstr}')
        assert xstr == xstr2
        assert jsstr == jsstr2
        assert "1.23" in jsstr2 if "1.23" in source else True
        assert "test" in jsstr2 if "test" in source else True

        if origRestored:
            ost = json.loads(jsstr)
            if isinstance(ost, dict) and 'dict' in ost and \
               (isinstance(ost['dict'], dict) or isinstance(ost['dict'], list)):
                ost = ost['dict']
            assert json.dumps(ost) == json.dumps(json.loads(source))

    def check_files(self, dirs, origRestored=True):
        names = []
        for test_dir in dirs:
            print('\n\n* Test dir %s' % test_dir)
            for n in os.listdir(test_dir):
                if n.endswith('.json') and not n.startswith('bad'):
                    names.append(os.path.join(test_dir, n))

        for filename in names:
            print('\n** Test file %s' % filename)
            source = read_file(filename)
            self.check_roundtrip(source, origRestored=origRestored)

    sys_directories = [
        name for name in sys.path if os.path.exists(name)
    ]

    example_directories = [
        # search 'tests/examples'
        os.path.join(os.path.dirname(__file__), 'examples', 'json'),
        os.path.join(os.path.dirname(__file__), 'examples', 'json', 'system')
    ]

    bad_example_directories = [
        os.path.join(os.path.dirname(__file__), 'examples', 'json', 'system', 'bad')
    ]

    def test_files(self):
        self.check_files(self.sys_directories)

    def test_examples(self):
        self.check_files(self.example_directories)

    def test_bad_examples(self):
        self.check_files(self.bad_example_directories, False)

    def test_objects(self):
        self.check_roundtrip('{"n": "12"}')

    def test_layout_1(self):
        xstr = json2xml.json2xml('{}')
        assert xstr == '<dict></dict>'

    def test_layout_2(self):
        xstr = json2xml.json2xml('123.45')
        assert xstr == '<num>123.45</num>'

    def test_layout_3(self):
        xstr = json2xml.json2xml('"abc"')
        assert xstr == '<str>abc</str>'
