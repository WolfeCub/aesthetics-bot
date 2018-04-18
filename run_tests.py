import os
import glob
from importlib import import_module

for item in glob.glob('./mods-available/*_mod.py'):
    name = os.path.basename(item)[:-3]
    import_module(f'mods-available.{name}')
