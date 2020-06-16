import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from . import calendar
from . import logging

logging.init()
bot = commands.Bot(command_prefix='?')

def main():
    load_dotenv()
    
    global events_channel
    bot.loop.create_task(check_schedule())
    bot.run(os.getenv("DISCORD_TOKEN"))

'''
@bot.check
async def is_admin(ctx):
    # Check role for MLH or Lead Mentor
    pass
'''

async def check_schedule():
    await bot.wait_until_ready()
    global events_channel
    events_channel = bot.get_channel(int(os.getenv("DISCORD_EVENTS_ID")))

    while True:
        session = calendar.get_next_session()
        await send_announcement(session)
        await asyncio.sleep(60)

async def send_announcement(session):
    global events_channel
    await events_channel.send(session)

def check_times(current_time, event_time):
    return True

@bot.command(description="Displays next event")
async def next_session(ctx):
    session = calendar.get_next_session()
    await ctx.send(str(session))
