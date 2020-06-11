import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from . import calendar

bot = commands.Bot(command_prefix='?')

def main():
    load_dotenv()
    global events_channel
    bot.loop.create_task(check_schedule())
    bot.run(os.getenv("TOKEN"))

@bot.check
async def is_admin(ctx):
    # Check 
    pass

async def check_schedule():
    await bot.wait_until_ready()

    while True:
        await asyncio.sleep(60)

async def send_announcement(session):
    global events_channel
    await events_channel.send(session)

def check_times(current_time, event_time):
    return True

@bot.command(description="Displays next event")
async def next_event(ctx):
    event = calendar.get_next_event()
    ctx.send(str(event))