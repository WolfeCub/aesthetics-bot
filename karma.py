import time
import re
import sqlite3

__KARMA_REGEX = re.compile(r'<@!{0,1}(\d*?)> {0,1}(\+\+|--)')
__COOLDOWN_IN_SECONDS = 3600
__connection = sqlite3.connect('karma.db')
__c = __connection.cursor()
__c.execute("CREATE TABLE IF NOT EXISTS karma(\
 id int PRIMARY KEY NOT NULL,\
 timestamp datetime DEFAULT (CAST(strftime('%s', 'now') AS INT)),\
 amount int NOT NULL);")

def cleanup():
    __connection.commit()
    __connection.close()

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

    __c.execute('SELECT * FROM karma WHERE id=?', (user_id,))
    tup = __c.fetchone()
    if tup:
        if (time.time() - tup[1]) > cooldown:
            __c.execute("UPDATE karma SET amount=?, timestamp=(CAST(strftime('%s', 'now') AS INT)) WHERE id=?", (tup[2]+change, user_id)) 
            await client.send_message(message.channel, '%s %s a karma. Currently: %d' % (message.server.get_member(user_id).display_name, m, tup[2]+change))
        else:
            await client.send_message(message.channel, 'That user gained karma too recently please wait some time. %d minutes left.' % __time_left(tup[1], cooldown))
    else:
        __c.execute('INSERT INTO karma (id, amount) VALUES (?, 1)', (user_id,))
        await client.send_message(message.channel, '%s gained their first karma. Congrats!' % message.server.get_member(user_id).display_name)

def __check_karma_regex(message):
    matches = __KARMA_REGEX.match(message.content)
    if not matches:
        return
    return (matches.group(1), matches.group(2))

async def handle(client, config, message):
    matches = __check_karma_regex(message)
    if matches:
        if message.author.id == matches[0]:
            await client.send_message(message.channel, 'You cannot edit your own karma.')
        else:
            await __update_database_if_valid(client, message, matches[0], matches[1])
