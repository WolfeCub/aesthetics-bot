import discord

def __get_valid_roles(config, message, names):
    val = []
    for role in message.server.roles:
        low = role.name.lower()
        if low in names and low in config['valid_roles']:
            val.append(role)
    return val

async def handle(client, config, message):
    content = message.content[len(config['prefix']):]
    potential_roles = content.split()

    if potential_roles[0] != 'giveroles':
        return

    client.send_typing(message.channel)

    if len(message.author.roles) > 1:
        await client.send_message(message.channel, 'You already have a role.')
        return    

    roles = [x.lower() for x in potential_roles[1:]]

    role_objects = __get_valid_roles(config, message, roles)
    if len(role_objects) > 0:
        await client.add_roles(message.author, *role_objects)
        await client.send_message(message.channel, 'Roles added: %s' % ', '.join(map(lambda x: x.name, role_objects)))
    else:
        await client.send_message(message.channel, 'No valid roles specified')
