from pymongo import MongoClient

__client = None

def setup(config):
    global __client
    __client = MongoClient(config['mongo_connection'])

def cleanup():
    __client.close()

async def handle(client, config, message):
    users = __client.aesthetics.users
    users.update_one({'_id': message.author.id}, 
                     {
                         '$set': {'nickname': message.author.display_name},
                         '$inc': {f'messages_sent.{message.channel.id}': 1}
                     }, 
                     upsert=True)

    users.update_one({'_id': message.author.id, 'username': {'$exists': False}},
                     {'$set':
                         {
                             'name': message.author.name,
                             'discriminator': message.author.discriminator
                         }
                     })

    channels = __client.aesthetics.channels
    channels.update_one({'_id': message.channel.id},
                        {
                            '$set': {'name': message.channel.name},
                            '$inc': {'message_count': 1}
                        },
                        upsert=True)

    servers = __client.aesthetics.servers
    servers.update_one({'_id': message.server.id},
                       {
                           '$set': {'name': message.server.name},
                           '$inc': {'messages_sent': 1}
                       },
                       upsert=True)

async def handle_message_delete(client, message):
    servers = __client.aesthetics.servers
    servers.update_one({'_id': message.server.id},
                       {
                           '$set': {'name': message.server.name},
                           '$inc': {'messages_deleted': 1}
                       },
                       upsert=True)

async def handle_message_edit(client, before, after):
    servers = __client.aesthetics.servers
    servers.update_one({'_id': after.server.id},
                       {
                           '$set': {'name': after.server.name},
                           '$inc': {'messages_edited': 1}
                       },
                       upsert=True)

async def handle_reaction_add(client, reaction, user):
    servers = __client.aesthetics.servers
    servers.update_one({'_id': reaction.message.server.id},
                       {
                           '$set': {'name': reaction.message.server.name},
                           '$inc': {'reactions_sent': 1}
                       },
                       upsert=True)

async def handle_reaction_remove(client, reaction, user):
    servers = __client.aesthetics.servers
    servers.update_one({'_id': reaction.message.server.id},
                       {
                           '$set': {'name': reaction.message.server.name},
                           '$inc': {'reactions_deleted': 1}
                       },
                       upsert=True)

async def handle_reaction_clear(client, message, reactions):
    servers = __client.aesthetics.servers
    servers.update_one({'_id': message.server.id},
                       {
                           '$set': {'name': message.server.name},
                           '$inc': {'reactions_deleted': -len(reactions)}
                       },
                       upsert=True)
