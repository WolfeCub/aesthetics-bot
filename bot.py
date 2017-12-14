import os
import re
import json
import discord
import asyncio
import spice_api as spice
import html2text as h2t

client = discord.Client()
creds = ()
config = {}

def setup():
    global config

    if not os.path.exists('config.json'):
        print('No config.json file found')
        exit(1)
    with open('config.json', 'r') as f:
        config = json.loads(f.read())

    if not config['token']:
        print('No token value found in config file')
        exit(1)
    elif not config['MALuser'] or not config['MALpass']:
        print('No MAL credentials found in config file')
        exit(1)


def create_message_from_results(results):
    anime = results[0]
    embed = discord.Embed(
        title       = anime.title,
        type        = 'rich',
        description = re.sub(r'\[.*?\]|\n', '', h2t.html2text(anime.synopsis)).replace('  ', ' '),
        url         = 'https://myanimelist.net/anime/%s' % anime.id,
        )
    embed.set_thumbnail(url=anime.image_url)
    embed.add_field(name='Score', value=anime.score)
    embed.add_field(name='Episodes', value=anime.episodes)
    embed.add_field(name='Status', value=anime.status)
    embed.add_field(name='Aired', value='%s -> %s' % (anime.dates[0], anime.dates[1]))
    return embed

@client.event
async def on_ready():
    global creds
    creds = spice.init_auth(config['MALuser'], config['MALpass'])
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.name == 'anime-recommendation-thread':
        results = spice.search(message.content, spice.get_medium('anime'), creds)
        await client.send_message(message.channel,
                                  embed=create_message_from_results(results))

setup()
client.run(config['token'])
