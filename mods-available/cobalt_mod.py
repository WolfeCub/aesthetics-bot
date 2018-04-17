import re
import asyncio
import aiohttp
import json
import time
from datetime import datetime as dt
from discord import Embed
from botutils import is_channel_valid

__COURSE_REGEX = re.compile(r'\A[a-zA-Z]{3}(?:[a-dA-D]\d{2}|\d{3})\Z')
__EXAM_REGEX = re.compile(r'exam \A[a-zA-Z]{3}(?:[a-dA-D]\d{2}|\d{3})\Z')
__SHUTTLE_REGEX = re.compile(r'!shuttle')

__HEADERS = None

def __set_headers(config):
    global __HEADERS
    if __HEADERS is None:
        __HEADERS = {'Authorization': config['COBALT_key']}

def __is_cobalt_regex(message, regex):
    '''
    Returns whether the regex matches or not.
    '''
    matches = regex.match(message.content) # debating on having them still use !ut, or just call csc108

    return True if matches else None

def __create_course_embed(course):
    '''
    Creates a course embed
    '''
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

def __create_shuttle_embed(route):
    '''
    Creates a shuttle embed
    '''
    embed = Embed(
        title       = 'Shuttle Times for %s %s :oncoming_bus:' % (dt.now(), route['name']),
        type        = 'rich',
        description = '`**` indicates rush hour.\n The regular one-way ticket fare is $6.00.',
        color       = 16777215,
        timestamp   = dt.now(),
    )

    for stop in route['stops']:
        timing = ''

        for stop_time in stop['time']:
            timing += '%s %s\n' % (stop_time, '**' if stop_time['rush_hour'] else '') #should probably work on formatting time

        embed.add_field(name=':busstop: %s' % stop['location'], value=timing, inline=True)

    return embed

def __clean_course_dup(course_list):
    course_set = {course_list[0]['code'][0:8]: course_list[0]}

    for course in course_list[1:]:
        if course['code'][0:-1] in course_set:
            course_set[course['code'][0:8]]['term'] += '\n %s' % course['term']
        else:
            course_set[course['code'][0:8]] = course

    return list(course_set.values())

async def __request_course(client, message, config):
    '''
    Grab information if any for the course specified by the user.
    '''

    course_name = message.content
    params = {'q': 'code:"%s" AND term:"2017"' % course_name.upper().strip()}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://cobalt.qas.im/api/1.0/courses/filter', params=params, headers=__HEADERS) as r:
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

async def __request_shuttle_times(client, message, config):
    '''
    Grabs the current day's shuttle times.
    '''
    now = time.strftime('%Y-%m-%d')

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://cobalt.qas.im/api/1.0/transportation/shuttles/%s' % now, headers=__HEADERS) as r:
                if r.status == 200:
                    shuttle_times = await r.json()
                    if shuttle_times == []:
                        await client.send_message(message.channel, 'No shuttles running today. :(')
                    else:
                        return shuttle_times
    except:
        await client.send_message(message.channel, 'Error contacting server')

async def handle(client, config, message):
    if is_channel_valid(config, 'school_channels', message):
        return

    __set_headers(config)

    # Do the cobalt shuttle things
    # if (__is_cobalt_regex(message, __SHUTTLE_REGEX)):
    #     shuttle_times = await __request_shuttle_times(client, message, config)

    #     if shuttle_times:
    #         for shuttle in shuttle_times:
    #             await client.send_message(message.channel,
    #                                      embed= __create_shuttle_embed(shuttle))

    # Do the cobalt course things
    if (__is_cobalt_regex(message, __COURSE_REGEX)):
        course_info = await __request_course(client, message, config)

        if course_info:
            course_info = __clean_course_dup(course_info)
            await client.send_message(message.channel, ':package: **||** Here are the result(s).')
            for course in course_info:
                await client.send_message(message.channel,
                                          embed= __create_course_embed(course))

    # Do the cobalt exam things
    # if (__is_cobalt_regex(message, __EXAM_REGEX)):
    #     pass

