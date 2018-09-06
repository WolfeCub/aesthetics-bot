import requests
import json
import discord
from botutils import has_prefix, get_content_without_prefix

from pprint import pprint

def __add_fields_to_edmbed(embed, stats, game_type):
    wins = stats['top1']['valueInt']
    matches = stats['matches']['valueInt']
    win_percent = (wins/matches)*100

    embed.add_field(name=f'{game_type} Wins', value=wins)
    embed.add_field(name=f'{game_type} Win%', value=f"{wins}/{matches} = **{win_percent:.1f}%**")
    embed.add_field(name=f'{game_type} K/d', value=stats['kd']['value'])

def __create_embed_from_result(result, username, platform='pc'):
    embed = discord.Embed(
        title       = result['epicUserHandle'],
        url         = f'https://fortnitetracker.com/profile/{platform}/{username}'
        )

    # Global Stats
    global_stats = {o['key']:o['value'] for o in result['lifeTimeStats']}
    embed.add_field(name='Total Wins', value=global_stats['Wins'])
    embed.add_field(name='Total Win%', value=global_stats['Win%'])
    embed.add_field(name='Total K/d', value=global_stats['K/d'])

    __add_fields_to_edmbed(embed, result['stats']['p9'], 'Squads')
    __add_fields_to_edmbed(embed, result['stats']['p2'], 'Solo')
    __add_fields_to_edmbed(embed, result['stats']['p10'], 'Duo')
    
    return embed

async def handle(client, config, message):
    if not has_prefix(config, message):
        return

    content = get_content_without_prefix(config,message)
    args = content.split()

    if args[0] != 'fortnite':
        return
    if len(args) < 2:
        await message.channel.send('Usage: !fortnite [epic games name] <platform:optional pc, xbl or psn>')
        return

    platform = 'pc'
    num_args = len(args)
    username = ' '.join(args[1:])
    if num_args > 2 and args[-1] in ['pc', 'xbl', 'psn']:
        platform = args[-1]
        username = ' '.join(args[1:-1])
    
    # p2 -> solo
    # p10 -> duo
    # p9 -> squad
    url = f'https://api.fortnitetracker.com/v1/profile/{platform}/{username}'
    request = requests.get(url, headers={'TRN-Api-Key': config['fortnite_tracker_apikey']})

    if not request.ok:
        await message.channel.send("Error: A request error returned.")
        return

    r_result = json.loads(request.content)

    error = r_result.get('error')
    if error is not None:
        await message.channel.send(f"Error: {error}")
    else:
        await message.channel.send(embed=__create_embed_from_result(r_result, platform))
