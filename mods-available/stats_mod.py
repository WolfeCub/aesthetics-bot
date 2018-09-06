from pymongo import MongoClient

async def handle(client, config, message):
    mongo_client = MongoClient(config['mongo_connection'])
    database = mongo_client[str(message.guild.id)]

    users = database.users
    users.update_one({'_id': str(message.author.id)}, 
                     {
                         '$set': {'nickname': message.author.display_name},
                         '$inc': {f'messages_sent.{message.channel.id}': 1}
                     }, 
                     upsert=True)

    users.update_one({'_id': str(message.author.id), 'username': {'$exists': False}},
                     {'$set':
                         {
                             'name': message.author.name,
                             'discriminator': message.author.discriminator
                         }
                     })

    channels = database.channels
    channels.update_one({'_id': str(message.channel.id)},
                        {
                            '$set': {'name': message.channel.name},
                            '$inc': {'message_count': 1}
                        },
                        upsert=True)

    servers = database.servers
    servers.update_one({'_id': str(message.guild.id)},
                       {
                           '$set': {'name': message.guild.name},
                           '$inc': {'messages_sent': 1}
                       },
                       upsert=True)

    mongo_client.close()

async def handle_message_delete(client, config, message):
    mongo_client = MongoClient(config['mongo_connection'])
    database = mongo_client[str(message.guild.id)]

    servers = database.servers
    servers.update_one({'_id': str(message.guild.id)},
                       {
                           '$set': {'name': message.guild.name},
                           '$inc': {'messages_deleted': 1}
                       },
                       upsert=True)

    mongo_client.close()

async def handle_message_edit(client, config, before, after):
    mongo_client = MongoClient(config['mongo_connection'])
    database = mongo_client[str(after.guild.id)]

    servers = database.servers
    servers.update_one({'_id': str(after.guild.id)},
                       {
                           '$set': {'name': after.guild.name},
                           '$inc': {'messages_edited': 1}
                       },
                       upsert=True)

    mongo_client.close()

async def handle_reaction_add(client, config, reaction, user):
    mongo_client = MongoClient(config['mongo_connection'])
    database = mongo_client[str(reaction.message.guild.id)]

    servers = database.servers
    servers.update_one({'_id': str(reaction.message.guild.id)},
                       {
                           '$set': {'name': reaction.message.guild.name},
                           '$inc': {'reactions_sent': 1}
                       },
                       upsert=True)

    mongo_client.close()

async def handle_reaction_remove(client, config, reaction, user):
    mongo_client = MongoClient(config['mongo_connection'])
    database = mongo_client[str(reaction.message.guild.id)]

    servers = database.servers
    servers.update_one({'_id': str(reaction.message.guild.id)},
                       {
                           '$set': {'name': reaction.message.guild.name},
                           '$inc': {'reactions_deleted': 1}
                       },
                       upsert=True)

    mongo_client.close()

async def handle_reaction_clear(client, config, message, reactions):
    mongo_client = MongoClient(config['mongo_connection'])
    database = mongo_client[str(message.guild.id)]

    servers = database.servers
    servers.update_one({'_id': str(message.guild.id)},
                       {
                           '$set': {'name': message.guild.name},
                           '$inc': {'reactions_deleted': -len(reactions)}
                       },
                       upsert=True)

    mongo_client.close()
