import os
import sys
import asyncio
import datetime
import discord
from discord.ext import commands
from discord.http import LoginFailure
from dotenv import load_dotenv
from schedule import cal
from util import logging

def my_except_hook(exctype, value, traceback):
    if exctype == LoginFailure:
        print(value)
        sys.exit(14)
    else:
        sys.__excepthook__(exctype, value, traceback)
sys.excepthook = my_except_hook

logging.init()
bot = commands.Bot(command_prefix='?')

def main():
    load_dotenv()

    global events_channel_id, guild_id, role_id, role_ttp_id
    try:
        token = os.getenv("DISCORD_TOKEN")
        events_channel_id = int(os.getenv("DISCORD_EVENTS_ID"))
        guild_id = int(os.getenv("DISCORD_GUILD_ID"))
        role_id = int(os.getenv("DISCORD_ROLE_ID"))
        role_ttp_id = int(os.getenv("DISCORD_ROLE_TTP_ID"))
        if not token:
            print(f"msg=\"Token was missing!\"")
            sys.exit(14)
    except Exception as e:
        print(f"msg=\"error parsing environment variables\", error=\"{e}\"")
        sys.exit(14)

    bot.loop.create_task(check_schedule())
    bot.run(token)

async def check_schedule():
    await bot.wait_until_ready()

    global events_channel, fellow_role, ttp_fellow_role, events_channel_id, guild_id, role_id, role_ttp_id
    events_channel = bot.get_channel(events_channel_id)
    fellow_role = bot.get_guild(guild_id).get_role(role_id) 
    ttp_fellow_role = bot.get_guild(guild_id).get_role(role_ttp_id) 

    while True:
        session = cal.get_next_session()
        if session != None:
            try:
                announcement_time_first = (session.start - datetime.timedelta(minutes=15))
                announcement_time_last = (session.start - datetime.timedelta(minutes=3))
                if check_times(announcement_time_first):
                    await send_long_announcement(session)
                elif check_times(announcement_time_last):
                    await send_short_announcement(session)
            except:
                print("Session was invalid")
        await asyncio.sleep(60)

async def send_long_announcement(session):
    global events_channel, fellow_role, ttp_fellow_role
    IMG_URL = 'https://mlh.will-russell.com/img/discord-session.jpg'
    
    if session.description == None or len(session.description) > 255:
        if check_url(session.url):
            embed = discord.Embed(title=session.title,
                                description=session.url,
                                url=session.url,
                                colour=0x1D539F)
        else:
            embed = discord.Embed(title=session.title,
                                description=session.url,
                                colour=0x1D539F)
    else:
        if check_url(session.url):
            embed = discord.Embed(title=session.title,
                                description=session.description,
                                url=session.url,
                                colour=0x1D539F)
        else:
            embed = discord.Embed(title=session.title,
                                description=session.description,
                                colour=0x1D539F)    
        
    if session.speaker != None:
        embed.set_author(name=session.speaker)
    embed.set_footer(text=session.url)
    embed.set_image(url=IMG_URL)
    await events_channel.send(f'Hey {fellow_role.mention}s and {ttp_fellow_role.mention}s - We have a session in 15 minutes! :tada:\n ({str(session.start.strftime("%H:%M GMT"))})', embed=embed)

async def send_short_announcement(session):
    global events_channel, fellow_role, ttp_fellow_role
    await events_channel.send(f'Just 3 minutes until we have **{session.title}**! :tada:\n {session.url}\n{fellow_role.mention} {ttp_fellow_role.mention}')

def check_times(announcement_time):
    current_time = datetime.datetime.now()
    current_year = current_time.strftime("%Y")
    current_month = current_time.strftime("%m")
    current_day = current_time.strftime("%d")
    current_hour = current_time.strftime("%H")
    current_minute = current_time.strftime("%M")

    announcement_year = announcement_time.strftime("%Y")
    announcement_month = announcement_time.strftime("%m")
    announcement_day = announcement_time.strftime("%d")
    announcement_hour = announcement_time.strftime("%H")
    announcement_minute = announcement_time.strftime("%M")

    if current_year == announcement_year and current_month == announcement_month and current_day == announcement_day:
        if current_hour == announcement_hour and current_minute == announcement_minute:
            return True
        else:
            return False
    else:
        return False

def check_url(url):
    if url[:8] == "https://":
        return True
    else:
        return False

@bot.command(description="Displays next event")
async def next_session(ctx):
    session = cal.get_next_session()
    print("Sending next session via command")
    if session != None:
        if check_url(session.url):
            embed = discord.Embed(title=session.title,
                                description=f'Starting at {str(session.start.strftime("%H:%M GMT on %B %d"))}',
                                url=session.url,
                                colour=0x1D539F)
        else:
            embed = discord.Embed(title=session.title,
                                description=f'Starting at {str(session.start.strftime("%H:%M GMT on %B %d"))}',
                                colour=0x1D539F)

        await ctx.send(f'Here\'s the next session at {str(session.start.strftime("%H:%M GMT on %B %d"))}!', embed=embed)

if __name__ == '__main__':
    main()
