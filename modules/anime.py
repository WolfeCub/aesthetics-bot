import sys
import re
import discord
from Pymoe import Kitsu

__ANIME_REGEX = re.compile(r'.*{{(.*?)}}.*')
__KITSU = None

def __create_message_from_results(results, original_query):
    anime = results[0]['attributes']
    embed = discord.Embed(
        title       = anime['canonicalTitle'],
        type        = 'rich',
        description = re.sub(r'\[Written by MAL Rewrite\]|\(Source: .*?\)', '', anime['synopsis']),
        url         = 'https://kitsu.io/anime/%s' % anime['slug']
        )
    embed.set_thumbnail(url=anime['posterImage']['large'])
    embed.add_field(name='Score', value=anime['averageRating'])
    embed.add_field(name='Episodes', value=anime['episodeCount'])
    embed.add_field(name='Status', value=anime['status'].title())
    embed.add_field(name='Aired', value='%s\n%s' % (anime['startDate'], anime['endDate']))
    return embed

def __check_anime_regex(message):
    matches = __ANIME_REGEX.match(message.content)
    if matches:
        return matches.group(1)
    return None

def setup(client_id, client_secret):
    global __KITSU

    print('Establishing connection to Kitsu... ', end='')
    __KITSU = Kitsu(client_id, client_secret)
    if not __KITSU:
        print('Error connecting exiting ...')
        exit(1)
    print('Done')

async def handle(client, config, message):
    match = __check_anime_regex(message)
    if match:
        client.send_typing(message.channel)
        results = __KITSU.anime.search(match)
        if results:
            await client.send_message(message.channel, embed=__create_message_from_results(results, match))
        else:
            await client.send_message(message.channel, 'No results found.')
