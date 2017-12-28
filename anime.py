import sys
import re
import discord
import spice_api as spice
import html2text as h2t

__ANIME_REGEX = re.compile(r'{{(.*?)}}')

def __fuzzy_match_best_result(results, original_query):
    best_match = None
    lowest = sys.maxsize

    for anime in results:
        dist = __levenshtein(anime.title, original_query)
        if dist < lowest:
            best_match = anime
            lowest = dist

    return best_match

def __create_message_from_results(results, original_query):
    anime = __fuzzy_match_best_result(results, original_query)
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
def __levenshtein(s1, s2):
    if len(s1) < len(s2):
        return __levenshtein(s2, s1)

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

def __check_anime_regex(message):
    matches = __ANIME_REGEX.match(message.content)
    if matches:
        return matches.group(1)
    return None

async def handle(client, config, message):
    match = __check_anime_regex(message)
    if match:
        client.send_typing(message.channel)
        results = spice.search(match, spice.get_medium('anime'), config['mal_creds'])
        await client.send_message(message.channel,
                                  embed=__create_message_from_results(results, match))
