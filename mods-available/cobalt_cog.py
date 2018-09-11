import re
import asyncio
import aiohttp
import discord
import time
from discord.ext import commands
from botutils import timestamp
from discord import Embed

class CobaltCog():
    def __init__(self, bot):
        self.bot = bot
        self.__HEADERS = {'Authorization': self.bot.get_config('COBALT_key')}
        self.__COURSE_REGEX = re.compile(r'\A[a-zA-Z]{3}(?:[a-dA-D]\d{2}|\d{3})\Z') #consider allowing wild cards

    async def __error(self, ctx, error):
        print(f'Error in Cobalt Cog: \n Offending command: {ctx.command.qualified_name} \n {error}')

    @commands.command(name='ping')
    async def test(self, ctx):
        ''' Test command that will remain here like "you can never remove the exec" role.'''
        await ctx.send("pong")

    def __is_valid_arg(self, regex, code: str):
        ''' Returns whether the regex matches the string or not.'''
        return regex.match(code)

    def __get_time_string_from_seconds(self, seconds):
        '''
        Returns string of time given in seconds. 
        '''
        m = divmod(seconds, 60)[0]
        h, m = divmod(m, 60)

        if h == 0:
            h = 12

        return '%d:%02d PM' %(h % 12, m) if h > 12 else '%d:%02d AM' % (h, m)

    @commands.command(name='course', aliases=['c'])
    async def get_course(self, ctx, course_code : str):
        if self.__is_valid_arg(self.__COURSE_REGEX, course_code):
            course_info = await self.__request_course(ctx, course_code)

            if course_info:
                course_info = self.__clean_course_dup(course_info)
                await ctx.send(':package: **||** Here are the result(s).')
                for course in course_info:
                    await ctx.send(embed= self.__create_course_embed(course))

    async def __request_course(self, ctx, course_name: str):
        ''' Sends a request to the Cobalt API to retrieve information'''
        year = str(timestamp().year)
        params = { 'q': 'code:"%s" AND term:"%s"' % (course_name.upper().strip(), year) }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://cobalt.qas.im/api/1.0/courses/filter', params=params, headers=self.__HEADERS) as r:
                    if r.status == 200:
                        course_query = await r.json()
                        if course_query == []:
                            await ctx.send(':slight_frown: **||** Nothing came up.')
                        else:
                            return course_query

        except Exception as err:
            print("Error in cobalt module!")
            print(err)
            await ctx.send('There was an error with grabbing the information, oh no! :dizzy_face:')

        return None

    def __clean_course_dup(self, courses : []):
        ''' Joins all courses with the same code into a single course object(used loosely) '''
        course_set = {courses[0]['code'][0:8]: courses[0]}

        for course in courses[1:]:
            if course['code'][0:-1] in course_set:
                course_set[course['code'][0:8]]['term'] += '\n %s' % course['term']
            else:
                course_set[course['code'][0:8]] = course

        return list(course_set.values())

    def __create_course_embed(self, course):
        embed = Embed(
            title       = course['code'][0:8],
            type        = 'rich',
            description = course['description'],
            color       = 16777215,
            timestamp   = timestamp(),
        )

        embed.add_field(name='Term', value=course['term'], inline=True)
        embed.add_field(name='Prerequisite', value="None" if course['prerequisites'] == "" else course['prerequisites'], inline=True)

        embed.set_footer(text='Brought to you by the Cobalt API')

        return embed

    @commands.command(name='shuttle', aliases=['s'])
    async def get_shuttle(self, ctx):
        shuttle_info = await self.__request_shuttle(ctx)

        if shuttle_info:
            for route in shuttle_info['routes']:
                await ctx.send(embed= self.__create_shuttle_embed(route))

    async def __request_shuttle(self, ctx):
        now = time.strftime('%Y-%m-%d')

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://cobalt.qas.im/api/1.0/transportation/shuttles/{now}', headers=self.__HEADERS) as r:
                    if r.status == 200:
                        shuttle_query = await r.json()
                        if not shuttle_query['routes']:
                            await ctx.send('There are no shuttles running today. :(')
                        else:
                            return shuttle_query
        except Exception as err:
            print("Error in cobalt module!")
            print(err)
            await ctx.send('Error contacting server')

    def __create_shuttle_embed(self, route):
        '''
        Creates a shuttle embed
        '''
        embed = Embed(
            title       = f'Shuttle Times for {timestamp().strftime("%B %d, %Y")} - {route["name"]} :oncoming_bus:',
            type        = 'rich',
            description = '`**` indicates rush hour.\n The regular one-way ticket fare is $6.00.',
            color       = 16777215,
            timestamp   = timestamp(),
        )

        for stop in route['stops']:
            timing = ''
            for stop_time in stop['times']:
                timing += f'{self.__get_time_string_from_seconds(stop_time["time"])} {"**" if stop_time["rush_hour"] else ""}\n'

            embed.add_field(name=':busstop: %s' % stop['location'], value=timing, inline=True)

        embed.set_footer(text='Brought to you by the Cobalt API')

        return embed

def setup(bot):
    bot.add_cog(CobaltCog(bot))