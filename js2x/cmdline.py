import sys
import os
import argparse

from .json2xml import json2xml, xml2json

from . import __version__

infos = dict(
    js2x=dict(func=lambda x, y, **kw: json2xml(x, filename=y, **kw),
              desc="Convert JSON to XML (JS2X)"),
    x2js=dict(func=lambda x, y, **kw: xml2json(x, filename=y, **kw),
              desc="Convert XML to JSON (JS2X)")
)


def json2xmlrun():
    run(prog="js2x")


def xml2jsonrun():
    run(prog="x2js")


def getparser(prog, description='What the program does', parser=None):
    if parser is None:
        parser = argparse.ArgumentParser(
            prog=prog,
            description=description)
    parser.add_argument('filename', nargs='?')
    parser.add_argument('-i', '--indent', type=int, const=1, nargs='?',
                        metavar='N', help='Indent output with N spaces')
    parser.add_argument('-o', '--output', type=str, metavar='FILE',
                        help='Write output to FILE')
    version = __version__
    parser.add_argument('-v', '--version', action='version', version=f'{prog} {version}')

    return parser


def run(prog):
    info = infos[prog]
    parser = getparser(prog=prog, description=info['desc'])
    args = parser.parse_args()
    parsefun = info['func']
    processargs(args, parsefun)


def processargs(args, parsefun):

    input = ''
    if not args.filename or args.filename == '-':
        input = sys.stdin.read()
        fname = 'stdin'
    else:
        fname = args.filename
        input = open(args.filename).read()
    out = sys.stdout
    if args.output:
        out = open(args.output, 'w')

    pfkw = {k: v for k, v in vars(args).items() if k != 'filename'}

    print(parsefun(input, fname, **pfkw), file=out)
