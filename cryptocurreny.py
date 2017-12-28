from coinmarketcap import Market

currency_mapping = {}

def setup():
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
    content = message.content[len(config['prefix']):]
    command_args = content.split()

    if len(command_args) != 2:
        return
    if command_args[0] != 'val':
        return

    client.send_typing(message.channel)
    value = None
    command_args[1] = command_args[1].upper()
    if command_args[1] in currency_mapping:
        coin_market = Market()
        try:
            data = coin_market.ticker(currency_mapping[command_args[1]], limit=1, convert = 'CAD')[0]
            value = float(data['price_cad'])
            await client.send_message(message.channel, 'Value of %s: $%.2fCAD' % (command_args[1], value))
        except Exception as err:
            await client.send_message(message.channel, 'There was an error fetching the value of %s!' % command_args[1])
            print('Error fetching token %s' % command_args[1])
            print('%s\n' % err)
    else:
        await client.send_message(message.channel, 'Token %s not found!' % command_args[1])
