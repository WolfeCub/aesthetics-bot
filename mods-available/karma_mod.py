import time
import re
from pymongo import MongoClient

__KARMA_REGEX = re.compile(r'<@!{0,1}(\d*?)> {0,1}(\+\+|--)')
__COOLDOWN_IN_SECONDS = 3600


def __log_karma_given_event(database, message, user_id):
    database.users.update({'_id': str(message.author.id)}, {'$inc': {f'karma_given.{user_id}': 1}}, upsert=True)

def __log_karma_received_event(database, message, user_id):
    database.aesthetics.users.update({'_id': user_id}, {'$inc': {f'karma_from.{message.author.id}': 1}}, upsert=True)

def __time_left(time_in_db, cooldown):
    return (cooldown/60) - ((time.time() - time_in_db)/60)

async def __update_database_if_valid(client, config, message, user_id, operation):
    mongo_client = MongoClient(config['mongo_connection'])
    database = mongo_client[str(message.guild.id)]

    cooldown = __COOLDOWN_IN_SECONDS
    if operation == '++':
        change = 1
        m = 'gained'
    elif operation == '--':
        cooldown *= 2
        change = -1
        m = 'lost'

    result = database.users.find_one({'_id': user_id})

    if result is not None and result.get('karma_timestamp', False):
        if (time.time() - result['karma_timestamp']) > cooldown:
            database.users.update_one({'_id': user_id}, {'$inc': {'karma': change}, '$set': {'karma_timestamp': time.time()}})
            __log_karma_given_event(database, message, user_id)
            __log_karma_received_event(database, message, user_id)
            await message.channel.send('%s %s a karma. **Currently: %d**\nGiven by: %s' % (message.guild.get_member(user_id).display_name, m, result['karma']+change, message.author.display_name))
        else:
            await message.channel.send('That user gained karma too recently please wait some time. %d minutes left.' % __time_left(result['karma_timestamp'], cooldown))
    else:
        database.users.update_one({'_id': user_id}, {'$inc': {'karma': change}, '$set': {'karma_timestamp': time.time()}}, upsert=True)
        __log_karma_given_event(database, message, user_id)
        __log_karma_received_event(database, message, user_id)
        await message.channel.send('%s %s their first karma\nGiven by: %s' % (message.guild.get_member(user_id).display_name, 'gained' if change > 0 else 'lost', message.author.display_name))

    mongo_client.close()

async def handle(client, config, message):
    matches = __KARMA_REGEX.findall(message.content)
    if matches:
        for match in matches:
            if str(message.author.id) == match[0]:
                await message.channel.send('You cannot edit your own karma.')
            else:
                message.channel.typing()
                await __update_database_if_valid(client, config, message, int(match[0]), match[1])
