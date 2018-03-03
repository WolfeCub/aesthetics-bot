import os
import glob
import json
import discord
import asyncio
import signal
from importlib import import_module

client = discord.Client()
config = {}
modules = []

def call_method_on_modules_if_exists(method_name, list_of_args):
    for module in modules:
        method = getattr(module, method_name, None)
        if method is not None:
            method(*list_of_args)

def setup():
    global config
    global anime_regex

    if not os.path.exists('config.json'):
        print('No config.json file found')
        exit(1)
    with open('config.json', 'r') as f:
        config = json.loads(f.read())

    check_config_params(config, ['token',
                                 'kitsu_id',
                                 'kitsu_secret',
                                 'prefix',
                                 'COBALT_key'])

    # Import modules
    for item in glob.glob('./modules/*_mod.py'):
        name = os.path.basename(item)[:-3]
        modules.append(import_module('modules.%s' % name))

    # Run setup if exists
    call_method_on_modules_if_exists('setup', [config])

    signal.signal(signal.SIGINT, cleanup)

def cleanup(signum, frame):
    print('\nExiting...')

    # Run cleanup if exists
    call_method_on_modules_if_exists('cleanup', [])
    exit(0)

def check_config_params(json, items):
    should_exit = False
    for item in json:
        if not json[item]:
            print('No value for "%s" found in the config file.' % item)
            should_exit = True

    if should_exit:
        exit(1)

@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='new year, new bot'))
    print('-------------')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-------------')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # We assume that handle exists otherwise it will die
    for module in modules:
        await module.handle(client, config, message)

if __name__ == '__main__':
    setup()
    client.run(config['token'])
