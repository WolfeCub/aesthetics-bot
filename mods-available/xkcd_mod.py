import requests
import discord
from botutils import *
from random import randint

__CURRENT_NUM = None

def fetch_comic_from_api(number=None):
    url = f'https://xkcd.com/{number if number else ""}/info.0.json'
    r = requests.get(url)
    if r.ok:
        return r.json()

def generate_embed(comic):
    e = discord.Embed(title=comic['safe_title'])
    e.set_image(url=comic['img'])
    return e

def setup(config):
    json = fetch_comic_from_api()
    if json is not None:
        global __CURRENT_NUM
        __CURRENT_NUM = json['num']
        print(f'Successfully got current comic #{__CURRENT_NUM}')
    else:
        print('Unable to contact xkcd')

def get_comic_per_args(command_args):
    comic = None
    
    if len(command_args) < 2 or command_args[1] == 'current':
        comic = fetch_comic_from_api()
    elif command_args[1] == 'random':
        comic = fetch_comic_from_api(randint(1, __CURRENT_NUM))
    elif str.isdigit(command_args[1]):
        comic = fetch_comic_from_api(command_args[1])

    return comic

async def handle(client, config, message):
    if not has_prefix(config, message):
        return

    content = get_content_without_prefix(config, message)
    command_args = content.split()

    if command_args[0] != 'xkcd':
        return

    comic = get_comic_per_args(command_args)

    if comic is not None:
        await client.send_message(message.channel, embed=generate_embed(comic))
    else:
        await client.send_message(message.channel, 'Invalid number or command specified.')

