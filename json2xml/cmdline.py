import sys, os, argparse

from . import *

from . import __version__

infos = dict(
    json2xml=dict(func=lambda x, y, **kw: json2xml(x, filename=y, **kw),
                    desc="Convert JSON to XML (json2xml)")
    , xml2json=dict(func=lambda x, y, **kw: xml2json(x, filename=y, **kw),
                    desc="Convert XML to JSON (json2xml)")
)

def json2xmlrun():
    run(prog="json2xml")

def xml2jsonrun():
    run(prog="xml2json")

def getparser(prog, description='What the program does', parser=None):
    if parser is None:
        parser = argparse.ArgumentParser(
            prog=prog,
            description=description)
    parser.add_argument('filename', nargs='?')
    parser.add_argument('-e', '--show-empty', action='store_true')
    parser.add_argument('-f', '--annotate-fields', action='store_true')
    parser.add_argument('-i', '--indent', type=int, const=1, nargs='?',
                        metavar='N', help='Indent output with N spaces')
    parser.add_argument('-o', '--output', type=str, metavar='FILE',
                        help='Write output to FILE')
    parser.add_argument('-g', '--debug', action='store_true',
                        help='Keep line number information')
    version = __version__
    parser.add_argument('-v', '--version', action='version', version=f'{prog} {version}')

    return parser

def run(prog):
    info = infos[prog]
    parser = getparser(prog=prog, description=info['desc'])
    args = parser.parse_args()
    parsefun=info['func']
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
    debug = True if args.debug else False

    pfkw = { k: v for k,v in vars(args).items() if k != 'filename' }
    if 'debug' in pfkw:
        pfkw['include_attributes'] = pfkw['debug']


    if isinstance(parsefun, list):
        res = ''
        for i, pfun in enumerate(parsefun):
            res = pfun(input, fname, **pfkw)
            if debug:
                if isinstance(res, str):
                    with open(fname + '.' + f'{i}', 'w') as f:
                        f.write(res)
            input = res
        print(res, file=out)
    else:
        print(parsefun(input, fname, **pfkw), file=out)
