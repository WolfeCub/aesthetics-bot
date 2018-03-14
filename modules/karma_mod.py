import time
import re
from pymongo import MongoClient

__KARMA_REGEX = re.compile(r'<@!{0,1}(\d*?)> {0,1}(\+\+|--)')
__COOLDOWN_IN_SECONDS = 1#3600
__client = None

def setup(config):
    global __client
    __client = MongoClient('localhost', 27017)

def cleanup():
    __client.close()

def __log_karma_given_event(message, user_id):
    __client.aesthetics.users.update({'_id': message.author.id}, {'$inc': {f'karma_given.{user_id}': 1}}, upsert=True)

def __log_karma_received_event(message, user_id):
    __client.aesthetics.users.update({'_id': user_id}, {'$inc': {f'karma_from.{message.author.id}': 1}}, upsert=True)

def __time_left(time_in_db, cooldown):
    return (cooldown/60) - ((time.time() - time_in_db)/60)

async def __update_database_if_valid(client, message, user_id, operation):
    cooldown = __COOLDOWN_IN_SECONDS
    if operation == '++':
        change = 1
        m = 'gained'
    elif operation == '--':
        cooldown *= 2
        change = -1
        m = 'lost'

    result = __client.aesthetics.users.find_one({'_id': user_id})

    if result is not None and result.get('karma_timestamp', False):
        if (time.time() - result['karma_timestamp']) > cooldown:
            __client.aesthetics.users.update_one({'_id': user_id}, {'$inc': {'karma': change}, '$set': {'karma_timestamp': time.time()}})
            __log_karma_given_event(message, user_id)
            __log_karma_received_event(message, user_id)
            await client.send_message(message.channel, '%s %s a karma. Currently: %d' % (message.server.get_member(user_id).display_name, m, result['karma']+change))
        else:
            await client.send_message(message.channel, 'That user gained karma too recently please wait some time. %d minutes left.' % __time_left(result['karma_timestamp'], cooldown))
    else:
        __client.aesthetics.users.update_one({'_id': user_id}, {'$inc': {'karma': change}, '$set': {'karma_timestamp': time.time()}}, upsert=True)
        __log_karma_given_event(message, user_id)
        __log_karma_received_event(message, user_id)
        await client.send_message(message.channel, '%s %s their first karma.' % (message.server.get_member(user_id).display_name, 'gained' if change > 0 else 'lost'))

async def handle(client, config, message):
    matches = __KARMA_REGEX.findall(message.content)
    if matches:
        for match in matches:
            if message.author.id == match[0]:
                await client.send_message(message.channel, 'You cannot edit your own karma.')
            else:
                client.send_typing(message.channel)
                await __update_database_if_valid(client, message, match[0], match[1])
