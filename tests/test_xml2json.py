import sys
import os
import json
import unittest

import js2x as json2xml

def read_file(filename):
    with open(filename, "r") as pyfile:
        source = pyfile.read()
    return source

class XML2JSONTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def check_roundtrip(self, source):
        jsstr = json2xml.xml2json(source)
        xstr = json2xml.json2xml(jsstr)
        jsstr2 = json2xml.xml2json(xstr)
        xstr2 = json2xml.json2xml(jsstr2)
        print(f'res: {jsstr}')
        print(f'res XML: {xstr}')
        if jsstr != jsstr2:
            print('XML could not be rendered without loss to JSON')
        assert xstr == xstr2
        assert "1.23" in jsstr2 if "1.23" in source else True
        assert "test" in jsstr2 if "test" in source else True

    def check_files(self, dirs):
        names = []
        for test_dir in dirs:
            print('Test dir %s' % test_dir)
            for n in os.listdir(test_dir):
                if n.endswith('.xml') and not n.startswith('bad'):
                    names.append(os.path.join(test_dir, n))

        for filename in names:
            print('Testing %s' % filename)
            source = read_file(filename)
            self.check_roundtrip(source)

    sys_directories = [
        name for name in sys.path if os.path.exists(name)
    ]

    example_directories = [
        # search 'tests/examples'
        os.path.join(os.path.dirname(__file__), 'examples', 'xml')
    ]

    def test_files(self):
        self.check_files(self.sys_directories)

    def test_examples(self):
        self.check_files(self.example_directories)
