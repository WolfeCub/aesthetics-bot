import sys
from pymongo import MongoClient
from botutils import has_prefix, get_content_without_prefix

from pprint import pprint

__client = None

def setup(config):
    global __client
    __client = MongoClient(config['mongo_connection'])

def cleanup():
    __client.close()

async def __should_return(client, message, module, module_namespace='mods-enabled'):
    if sys.modules.get(f'{module_namespace}.{module}_mod') is not None:
        return False
    else:
        await client.send_message(message.channel, \
            f"Module '{module}' has not been enabled. Please enabled it to use this command.'")
        return True

def __get_results_iterator(res, field, x=10):
    val = res.next()
    i = 0
    while i < x and val is not None:
        try:
            r = field(val)
            yield f"{i+1}) {val['name']} - {r}"
        except KeyError:
            continue
        finally:
            val = res.next()

        i+=1

async def __send_top_x_results(client, message, res, field):
    await client.send_message(message.channel, '\n'.join(__get_results_iterator(res, field)))

async def __handle_top_karma(client, message, args):
    if await __should_return(client, message, 'karma'):
        return

    users = __client.aesthetics.users
    res = users.aggregate([
        { 
            '$sort': { 'karma': -1 } 
        }])

    await __send_top_x_results(client, message, res, lambda x: x['karma'])

async def __handle_top_messages(client, message, args):
    if await __should_return(client, message, 'stats'):
        return

    users = __client.aesthetics.users
    res = users.aggregate([
        { 
            '$project': { 'messages_sent': { '$objectToArray': '$messages_sent' }, 'name': '$name' } 
        }, 
        { 
            '$unwind': '$messages_sent'
        }, 
        { 
            '$group': { '_id': '$_id', 'total_messages_sent': { '$sum': '$messages_sent.v' }, 'name': { '$first': '$name' } } 
        }, 
        { 
            '$sort': { 'total_messages_sent': -1 } 
        }])
        
    await __send_top_x_results(client, message, res, lambda x: x['total_messages_sent'])


async def __handle_top_channel(client, message, args):
    users = __client.aesthetics.users
    res = users.aggregate([
        { 
            '$sort': { f'messages_sent.{message.channel.id}': -1 }
        }])

    await __send_top_x_results(client, message, res, lambda x: x['messages_sent'][str(message.channel.id)])

# Needs the methods to be declared before this can be defined
__HANDLE_COMMAND_MAP = {
    'karma': __handle_top_karma,
    'messages': __handle_top_messages,
    'channel': __handle_top_channel
}

async def __print_usage(client, message, args):
    await client.send_message(message.channel, f"Usage: `!top [{', '.join(__HANDLE_COMMAND_MAP.keys())}]`")

async def handle(client, config, message):
    if not has_prefix(config, message):
        return

    content = get_content_without_prefix(config,message)
    args = content.split()

    if args[0] == 'top':
        function = __HANDLE_COMMAND_MAP.get(args[1], __print_usage)
        await function(client, message, args)

