import sys
import re
import discord
from botutils import *
from Pymoe import Kitsu

__ANIME_GET_REGEX = re.compile(r'.*{{(.*?)}}.*')
__ANIME_SEARCH_REGEX = re.compile(r'.*\[\[(.*?)\]\].*')
__KITSU = None

def __create_small_embed_from_result(result, index):
    anime = result['attributes']
    embed = discord.Embed(
        title       = '%d) %s' % (index+1, anime['canonicalTitle']),
        type        = 'rich',
        description = ' '.join(re.sub(r'\[Written by MAL Rewrite\]|\(Source: .*?\)', '', anime['synopsis']).split()[0:7]) + '...',
        url         = 'https://kitsu.io/anime/%s' % anime['slug']
        )
    embed.set_thumbnail(url=anime['posterImage']['large'])
    embed.add_field(name='Score', value=anime['averageRating'])
    embed.add_field(name='Status', value=anime['status'].title())
    return embed

def __create_full_embed_from_result(result):
    anime = result['attributes']
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

def __get_range(results):
    l = len(results)
    return 3 if l > 3 else l

async def __delete_messages(client, messages):
    for mes in messages:
        await mes.delete()

async def __send_full_embed(client, message, results, reply):
    try:
        await message.channel.send(embed=__create_full_embed_from_result(results[int(reply.content)-1]))
    except ValueError:
        await message.channel.send('Invalid selection. You must select a number.')

async def __anime_search(client, message, results):
    if results is None:
        return
    messages_to_delete = []

    for i in range(__get_range(results)):
        messages_to_delete.append(await message.channel.send(embed=__create_small_embed_from_result(results[i], i)))

    reply = await client.wait_for('message', timeout=60, check=lambda m: m.author.id == message.author.id and m.channel.name == message.channel.name)
    messages_to_delete.append(reply)

    await __send_full_embed(client, message, results, reply)
    await __delete_messages(client, messages_to_delete)

def __check_regex(message, regex):
    matches = regex.match(message.content)
    if matches:
        return matches.group(1)
    return None

def setup(config):
    global __KITSU

    client_id = config['kitsu_id']
    client_secret = config['kitsu_secret']

    print('Establishing connection to Kitsu... ', end='')
    __KITSU = Kitsu(client_id, client_secret)
    if not __KITSU:
        print('Error connecting exiting ...')
        exit(1)
    print('Done')

async def handle(client, config, message):
    if not is_channel_valid(config, 'anime_channels', message):
        return

    get_match    = __check_regex(message, __ANIME_GET_REGEX)
    search_match = __check_regex(message, __ANIME_SEARCH_REGEX)

    match = search_match if search_match else get_match
    if match is not None:
        message.channel.typing()
        results = __KITSU.anime.search(match)
        if results is not None and get_match is not None:
            await message.channel.send(embed=__create_full_embed_from_result(results[0]))
        elif search_match is not None:
            await __anime_search(client, message, results)
        else:
            await message.channel.send('No results found.')
