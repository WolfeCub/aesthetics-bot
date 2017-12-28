import os
import json
import discord
import asyncio
import anime
import signal
import cobalt_module
import karma
import roles
import spice_api as spice

client = discord.Client()
config = {}

def setup():
    global config
    global anime_regex

    if not os.path.exists('config.json'):
        print('No config.json file found')
        exit(1)
    with open('config.json', 'r') as f:
        config = json.loads(f.read())

    check_config_params(config, ['token',
                                 'MALuser',
                                 'MALpass',
                                 'prefix',
                                 'anime_channels',
                                 'school_channels',
                                 'COBALT_key'])

    signal.signal(signal.SIGINT, cleanup)

def cleanup(signum, frame):
    print('\nExiting...')
    karma.cleanup()
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
    config['mal_creds'] = spice.init_auth(config['MALuser'], config['MALpass'])
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith(config['prefix']):
        await roles.handle(client, config, message)
    else:
        if message.channel.name in config['anime_channels']:
            await anime.handle(client, config, message)
        if message.channel.name in config['school_channels']:
            await cobalt_module.handle(client, config, message)
        await karma.handle(client, config, message)

setup()
client.run(config['token'])
