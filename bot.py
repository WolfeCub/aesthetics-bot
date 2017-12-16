import os
import sys
import re
import json
import discord
import asyncio
import spice_api as spice
import html2text as h2t

client = discord.Client()
creds = ()
config = {}
anime_regex = None

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
                                 'prefix'
                                 'anime_channels'])
    anime_regex = re.compile(r'{{(.*?)}}')

def check_config_params(json, items):
    should_exit = False
    for item in json:
        if not json[item]:
            print('No value for "%s" found in the config file.' % item)
            should_exit = True

    if should_exit:
        exit(1)
    elif not config['COBALT_key']:
        print('No COBALT credentials found in config file')
        exit(1)

def fuzzy_match_best_result(results, original_query):
    best_match = None
    lowest = sys.maxsize

    for anime in results:
        dist = levenshtein(anime.title, original_query)
        if dist < lowest:
            best_match = anime
            lowest = dist

    return best_match

def create_message_from_results(results, original_query):
    anime = fuzzy_match_best_result(results, original_query)
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

# source: wikibooks.org
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def check_anime_regex(message):
    matches = anime_regex.match(message.content)
    if matches:
        return matches.group(1)
    return None

async def handle_anime_message(message):
    match = check_anime_regex(message)
    if match:
        results = spice.search(match, spice.get_medium('anime'), creds)
        await client.send_message(message.channel,
                                  embed=create_message_from_results(results, match))


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
    if message.channel.name in config['anime_channels']:
        await handle_anime_message(message)

setup()
client.run(config['token'])
