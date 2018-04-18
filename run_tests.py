import os
import glob
import unittest
from importlib import import_module

# Import the entry point and make sure syntax is good then
# close HTTP connection to discord so it exits nicely
import bot
bot.client.http.session.close()

# Import each module to see if it's syntactically correct
for item in glob.glob('./mods-available/*_mod.py'):
    name = os.path.basename(item)[:-3]
    import_module(f'mods-available.{name}')

# Run all unit tests in the test folder
suite = unittest.TestLoader().discover('./tests/', '*_tests.py')
unittest.TextTestRunner().run(suite)
