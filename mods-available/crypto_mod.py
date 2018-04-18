import discord
from botutils import *
from coinmarketcap import Market

currency_mapping = {}

def __create_message(result):
    embed = discord.Embed(
        title       = '%s: %s' % (result['name'], result['symbol']),
        description = '',
        type        = 'rich',
        url         = 'https://coinmarketcap.com/currencies/%s/' % result['id'],
        colour      = discord.Colour(65280) if float(result['percent_change_24h']) > 0 else discord.Colour(16711680),
    )
    embed.set_thumbnail(url='https://files.coinmarketcap.com/static/img/coins/128x128/%s.png' % result['id'])
    embed.add_field(name='Value CAD:', value='$%.2f' % float(result['price_cad']))
    embed.add_field(name='Value USD:', value='$%.2f' % float(result['price_usd']))
    embed.add_field(name='Value BTC:', value='%.7fBTC' % float(result['price_btc']))
    embed.add_field(name='1 Hour Change:', value='%s%%' % result['percent_change_1h'], inline=False)
    embed.add_field(name='24 Hour Change:', value='%s%%' % result['percent_change_24h'])
    embed.add_field(name='7 Day Change:', value='%s%%' % result['percent_change_7d'])
    return embed

def setup(config):
    print('Fetching cryptocurrency tokens...', end='')
    total_coins = 0
    global currency_mapping
    coin_market = Market()
    try:
        data = coin_market.ticker('', limit=0)
        for coin in data:
            currency_mapping[coin["symbol"].upper()] = coin["id"]
            total_coins += 1
        print(' %d tokens added!' % (total_coins))
    except Exception as err:
        print(' error fetching tokens!')
        print('%s\n' % err)

async def handle(client, config, message):
    if not is_channel_valid(config, 'crypto_channels', message):
        return

    if not has_prefix(config, message):
        return

    content = get_content_without_prefix(config, message)
    command_args = content.split()

    if len(command_args) != 2:
        return
    if command_args[0] != 'val':
        return

    client.send_typing(message.channel)
    command_args[1] = command_args[1].upper()
    if command_args[1] in currency_mapping:
        coin_market = Market()
        try:
            data = coin_market.ticker(currency_mapping[command_args[1]], limit=1, convert = 'CAD')[0]
            await client.send_message(message.channel, embed=__create_message(data))
        except Exception as err:
            await client.send_message(message.channel, 'There was an error fetching the value of %s!' % command_args[1])
            print('Error fetching token %s' % command_args[1])
            print('%s\n' % err)
    else:
        await client.send_message(message.channel, 'Token %s not found!' % command_args[1])
