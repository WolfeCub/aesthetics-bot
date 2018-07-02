from pymongo import MongoClient

async def handle(client, config, message):
    mongo_client = MongoClient(config['mongo_connection'])
    database = mongo_client[message.server.id]

    users = database.users
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

    channels = database.channels
    channels.update_one({'_id': message.channel.id},
                        {
                            '$set': {'name': message.channel.name},
                            '$inc': {'message_count': 1}
                        },
                        upsert=True)

    servers = database.servers
    servers.update_one({'_id': message.server.id},
                       {
                           '$set': {'name': message.server.name},
                           '$inc': {'messages_sent': 1}
                       },
                       upsert=True)

    mongo_client.close()

async def handle_message_delete(client, config, message):
    mongo_client = MongoClient(config['mongo_connection'])
    database = mongo_client[message.server.id]

    servers = database.servers
    servers.update_one({'_id': message.server.id},
                       {
                           '$set': {'name': message.server.name},
                           '$inc': {'messages_deleted': 1}
                       },
                       upsert=True)

    mongo_client.close()

async def handle_message_edit(client, config, before, after):
    mongo_client = MongoClient(config['mongo_connection'])
    database = mongo_client[after.server.id]

    servers = database.servers
    servers.update_one({'_id': after.server.id},
                       {
                           '$set': {'name': after.server.name},
                           '$inc': {'messages_edited': 1}
                       },
                       upsert=True)

    mongo_client.close()

async def handle_reaction_add(client, config, reaction, user):
    mongo_client = MongoClient(config['mongo_connection'])
    database = mongo_client[reaction.message.server.id]

    servers = database.servers
    servers.update_one({'_id': reaction.message.server.id},
                       {
                           '$set': {'name': reaction.message.server.name},
                           '$inc': {'reactions_sent': 1}
                       },
                       upsert=True)

    mongo_client.close()

async def handle_reaction_remove(client, config, reaction, user):
    mongo_client = MongoClient(config['mongo_connection'])
    database = mongo_client[reaction.message.server.id]

    servers = database.servers
    servers.update_one({'_id': reaction.message.server.id},
                       {
                           '$set': {'name': reaction.message.server.name},
                           '$inc': {'reactions_deleted': 1}
                       },
                       upsert=True)

    mongo_client.close()

async def handle_reaction_clear(client, config, message, reactions):
    mongo_client = MongoClient(config['mongo_connection'])
    database = mongo_client[message.server.id]

    servers = database.servers
    servers.update_one({'_id': message.server.id},
                       {
                           '$set': {'name': message.server.name},
                           '$inc': {'reactions_deleted': -len(reactions)}
                       },
                       upsert=True)

    mongo_client.close()
