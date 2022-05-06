import sys

from thoth.cli import app

if len(sys.argv) == 1:
    app(['--help'])
else:
    app()
