import sys
import os

if not os.path.exists(os.path.join(os.path.dirname(globals()['__file__']), 'base.py')):
    sys.stderr.write("Failed to locate the base settings file. Quitting.\n")
    sys.exit(1)
try:
    from pizza.settings.base import *
except ImportError, error:
    sys.stderr.write("Failed to import from the base settings file. Quitting.\n")
    sys.stderr.write(str(error) + "\n")
    sys.exit(1)
