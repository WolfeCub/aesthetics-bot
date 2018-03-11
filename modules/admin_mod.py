from botutils import has_prefix, get_content_without_prefix

__VALID_ROLES = ['Executive', 'They can never remove the exec role']

async def __handle_clear(client, message, args):
    if len(args) < 2:
        await client.send_message(message.channel, 'Incorrect syntax')
        return
    
    if args[1] == 'all' or args[1] == '*':
        await client.purge_from(message.channel)
        return

    try:
        await client.purge_from(message.channel, limit=int(args[1]))
    except ValueError:
        await client.send_message(message.channel, 'Invalid amount of messages')
        return


async def handle(client, config, message):
    if message.author.top_role.name in __VALID_ROLES:
        return

    if not has_prefix(config, message):
        return

    content = get_content_without_prefix(config,message)
    args = content.split()

    if args[0] == 'clear':
        await __handle_clear(client, message, args)
