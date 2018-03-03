import re
import asyncio
import aiohttp
import json
from datetime import datetime as dt
from discord import Embed

__COURSE_REGEX = re.compile(r'\A[a-zA-Z]{3}(?:[a-dA-D]\d{2}|\d{3})\Z')

def __is_cobalt_regex(message):
    '''
    Return a constant indicating SHUTTLE, COURSE, etc
    '''
    matches = __COURSE_REGEX.match(message.content) # debating on having them still use !ut, or just call csc108
    
    return True if matches else None

def __create_course_embed(course):
    embed = Embed(
        title       = course['code'][0:8],
        type        = 'rich',
        description = course['description'],
        color       = 16777215,
        timestamp   = dt.now(),
    )
    
    embed.add_field(name='Term', value=course['term'], inline=True)
    embed.add_field(name='Prerequisite', value="None" if course['prerequisites'] == "" else course['prerequisites'], inline=True)
    
    embed.set_footer(text='Brought to you by the Cobalt API')
    
    return embed

def __clean_course_dup(course_list):
    course_set = {course_list[0]['code'][0:8]: course_list[0]}
    
    for course in course_list[1:]:
        if course['code'][0:-1] in course_set:
            course_set[course['code'][0:8]]['term'] += '\n %s' % course['term']
        else:
            course_set[course['code'][0:8]] = course
            
    return list(course_set.values())
    
async def __request_course(client, message, config, course_name):
    '''
    Grab information if any for the course specified by the user.
    '''
    
    params = {'q': 'code:"%s" AND term:"2017"' % course_name.upper().strip()}
    headers = {'Authorization': config['COBALT_key']}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://cobalt.qas.im/api/1.0/courses/filter', params=params, headers=headers) as r:
                if r.status == 200:
                    course_query = await r.json()
                    if course_query == []:
                        await client.send_message(message.channel, ':slight_frown: **||** Nothing came up.')
                    else:
                        return course_query
                
    except Exception as err:
        print("Error in cobalt module!")
        print(err)
        await client.send_message(message.channel, 'There was an error with grabbing the information, oh no! :dizzy_face:')
            
    return None
            
async def handle(client, config, message):
    if message.channel.name not in config['school_channels']:
        return

    if not __is_cobalt_regex(message):
        return
    
    # Do the cobalt things
    course_info = await __request_course(client, message, config, message.content)
    if course_info:
        course_info = __clean_course_dup(course_info)
        await client.send_message(message.channel, ':package: **||** Here are the result(s).')
        for course in course_info:
            await client.send_message(message.channel,
                                      embed= __create_course_embed(course))
