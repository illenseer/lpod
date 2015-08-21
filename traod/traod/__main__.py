from __future__ import print_function, division, absolute_import

from traod.semantics import LogProgSemantics
from traod.parser import LogProgParser
from traod.generator import generate_prog
from grako.exceptions import SemanticError

import click
import json
import string
import sys

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument(
    'filename',
    type=click.File('r'),
)
@click.option(
    '--backend',
    '-b',
    type=click.Choice(['metalpod', 'asprin']),
    default='metalpod',
    help='Backend to solve LPOD instance. Default: metalpod'
)
@click.option(
    '--strategy',
    '-s',
    type=click.Choice(['pareto', 'incl', 'card']),
    default='pareto',
    help='Strategy for LPOD instance. Default: pareto'
)
@click.option(
    '--generator',
    '-g',
    type=click.Choice(['split', 'cabalar']),
    default='split',
    help=(
        'Generator for LPOD instance: Split programs or Cabalar translation. '
        'Default: split'
    )
)
def main(filename, backend, strategy, generator):
    text = filename.read()
    parser = LogProgParser(parseinfo=False)
    try:
        ast = parser.parse(
            text,
            'program',
            filename=filename,
            whitespace=string.whitespace,
            nameguard=True,
            semantics=LogProgSemantics()
        )
    except SemanticError as e:
        print(e)
        sys.exit(1)

    prog = generate_prog(ast, backend, generator, strategy)
    print(prog)
