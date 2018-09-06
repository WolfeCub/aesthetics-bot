import io
import binascii
import discord
import json
from contextlib import suppress
from botutils import *
from base64 import b64decode

dbf_to_card_map = {}
rarity_to_cost_map = {
    'FREE': 0,
    'COMMON': 40,
    'RARE': 100,
    'EPIC': 400,
    'LEGENDARY': 1600
    }
hero_name_map = {
    'Anduin Wrynn': 'PRIEST',
    'Tyrande Whisperwind': 'PRIEST',
    'Garrosh Hellscream': 'WARRIOR',
    'Magni_Bronzebeard': 'WARRIOR',
    'Jaina Proudmoore': 'MAGE',
    'Medivh': 'MAGE',
    'Khadgar': 'MAGE',
    'Thrall': 'SHAMAN',
    'Morgl the Oracle': 'SHAMAN',
    'Uther Lightbringer': 'PALADIN',
    'Lady Liadrin': 'PALADIN',
    'Prince Arthas': 'PALADIN',
    'Rexxar': 'HUNTER',
    'Alleria Windrunner': 'HUNTER',
    'Gul\'dan': 'WARLOCK',
    'Nemsy Necrofizzle': 'WARLOCK',
    'Valeera Sanguinar': 'ROGUE',
    'Maiev Shadowsong': 'ROGUE',
    'Malfurion Stormrage': 'DRUID',
    'Lunara': 'DRUID'
    }

def setup(config):
    global dbf_to_card_map
    print('Parsing card data ...')
    data = json.load(open('cards.json', 'r'))
    for card in data:
        with suppress(KeyError):
            dbf_to_card_map[card['dbfId']] = card

def __read_varint(stream):
    shift = 0
    result = 0
    while True:
        c = stream.read(1)
        if c == "":
            raise EOFError("Unexpected EOF while reading varint")
        i = ord(c)
        result |= (i & 0x7f) << shift
        shift += 7
        if not (i & 0x80):
            break

    return result

def __get_format_string(format_id):
    if format_id == 2:
        return 'Standard'
    elif format_id == 1:
        return 'Wild'
    else:
        return 'Other'

def __sort_by_mana(cards):
    sort = sorted(cards, key=lambda c: dbf_to_card_map[c[0]]['cost'])
    formatted = [f'{card[1]}x {__get_card_name(card[0])}' for card in sort]
    return formatted

def __add_fields(embed, class_cards, neutral_cards):
    embed.add_field(name='Class Cards', value='\n'.join(__sort_by_mana(class_cards)))
    embed.add_field(name='Neutral Cards', value='\n'.join(__sort_by_mana(neutral_cards)))

def __create_embed(deckstring, hero, form, class_cards, neutral_cards):
    embed = discord.Embed(
        title = f'{hero} - {__get_format_string(form)}',
        type  = 'rich',
        url   = f'https://deck.codes/{deckstring}'
        )
    embed.set_footer(text=sum(rarity_to_cost_map[dbf_to_card_map[d[0]]['rarity']] for d in class_cards + neutral_cards),\
                     icon_url='http://tb.himg.baidu.com/sys/portrait/item/b2df777a3030303531327600')
    __add_fields(embed, class_cards, neutral_cards)

    return embed

def __is_class_card(dbfId, hero):
    return dbf_to_card_map[dbfId]['cardClass'] == hero_name_map[hero]

def __get_card_name(dbfId):
    return dbf_to_card_map[dbfId]['name']

async def __handle_deck_decode(client, message, args):
    stream = io.BytesIO(b64decode(args[1]))

    header      = __read_varint(stream)
    version     = __read_varint(stream)
    deck_format = __read_varint(stream)
    hero_count  = __read_varint(stream)
    if (header != 0 or version != 1 or deck_format > 3 or
        deck_format < 0 or hero_count != 1):
        raise ValueError("Invalid deck header found")

    hero = __get_card_name(__read_varint(stream))
    class_cards = []
    neutral_cards = []
    for c in range(__read_varint(stream)):
        val = __read_varint(stream)
        dictionary = class_cards if __is_class_card(val, hero) else neutral_cards
        dictionary.append((val, 1))

    for c in range(__read_varint(stream)):
        val = __read_varint(stream)
        dictionary = class_cards if __is_class_card(val, hero) else neutral_cards
        dictionary.append((val, 2))

    for c in range(__read_varint(stream)):
        val = __read_varint(stream)
        num = __read_varint(stream)
        dictionary = class_cards if __is_class_card(val, hero) else neutral_cards
        dictionary.append((val, num))

    await message.channel.send(embed=__create_embed(args[1], hero, deck_format, class_cards, neutral_cards))

def __handle_card_search(client, message, args):
    pass

async def handle(client, config, message):
    if not has_prefix(config, message):
        return

    content = get_content_without_prefix(config, message)
    args = content.split()

    if args[0] != 'hs':
        return

    try:
        await __handle_deck_decode(client, message, args)
    except (binascii.Error, TypeError, ValueError):
        __handle_card_search()
