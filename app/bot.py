import os
import sys
import asyncio
import pytz
import datetime
import discord
from discord.ext import commands
from discord.http import LoginFailure
from dotenv import load_dotenv
from schedule import cal

def my_except_hook(exctype, value, traceback):
    if exctype == LoginFailure:
        print(value)
        sys.exit(14)
    else:
        sys.__excepthook__(exctype, value, traceback)
sys.excepthook = my_except_hook

bot = commands.Bot(command_prefix='?')

def main():
    load_dotenv()
    sys.stdout.flush()
    global events_channel_id, guild_id, role_id, role_ttp_id, role_techtonica_id, utc
    utc=pytz.UTC
    try:
        token = os.getenv("DISCORD_TOKEN")
        events_channel_id = int(os.getenv("DISCORD_EVENTS_ID"))
        guild_id = int(os.getenv("DISCORD_GUILD_ID"))
        role_id = int(os.getenv("DISCORD_ROLE_ID"))
        role_ttp_id = int(os.getenv("DISCORD_ROLE_TTP_ID"))
        role_techtonica_id = int(os.getenv("DISCORD_ROLE_TECHTONICA_ID"))
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

    global events_channel, fellow_role, ttp_fellow_role, techtonica_role, events_channel_id, guild_id, role_id, role_ttp_id, role_techtonica_id
    events_channel = bot.get_channel(events_channel_id)
    fellow_role = bot.get_guild(guild_id).get_role(role_id) 
    ttp_fellow_role = bot.get_guild(guild_id).get_role(role_ttp_id)
    techtonica_role = bot.get_guild(guild_id).get_role(role_techtonica_id)

    while True:
        session = cal.get_next_session()
        if session != None:
            twitch_url = "https://twitch.tv"
            title = f"{session.title} {get_time_diff(session.start)}"
            if session.url[:len(twitch_url)] == twitch_url:
                activity = discord.Streaming(name=title,
                                             details=title,
                                             url=session.url,
                                             platform="Twitch",)
            else:
                activity = discord.Activity(name=title,
                                            type=discord.ActivityType.watching)
            await bot.change_presence(status=discord.Status.online, activity=activity)
            try:
                announcement_time_first = (session.start - datetime.timedelta(minutes=15))
                announcement_time_last = (session.start - datetime.timedelta(minutes=3))
                if check_times(announcement_time_first):
                    await send_long_announcement(session)
                elif check_times(announcement_time_last):
                    await send_short_announcement(session)
            except Exception as e:
                print(f"Session was invalid: {e}")
        await asyncio.sleep(60)

async def send_long_announcement(session):
    global events_channel, fellow_role, ttp_fellow_role, techtonica_role
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

    embed.set_footer(text=session.url)
    embed.set_image(url=IMG_URL)
    await events_channel.send(f'Hey {fellow_role.mention}s, {ttp_fellow_role.mention}s, and {techtonica_role.mention} - We have a session in 15 minutes! :tada:\n ({str(session.start.strftime("%H:%M GMT"))})', embed=embed)
    print("Long announcement made")

async def send_short_announcement(session):
    global events_channel, fellow_role, ttp_fellow_role, techtonica_role
    await events_channel.send(f'Just 3 minutes until we have **{session.title}**! :tada:\n {session.url}\n{fellow_role.mention} {ttp_fellow_role.mention} {techtonica_role.mention}')
    print("Short announcement made")

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

def get_time_diff(announcement_time):
    global utc
    current_time = datetime.datetime.now()
    current_time = current_time.replace(tzinfo=utc)
    announcement_time = announcement_time.replace(tzinfo=utc)
    diff = announcement_time - current_time
    SECONDS_24HR = 86400
    SECONDS_10HR = 36000
    if (diff.total_seconds() < 0):
        return "happening NOW!"
    elif diff.total_seconds() < SECONDS_10HR:
        return "in " + str(diff)[:4] + " hr"
    elif diff.total_seconds() < SECONDS_24HR:
        return "in " + str(diff)[:5] + "hr"
    else: #if over 24 hours a way
        return "in " + str(diff)[:11] + "hr"

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
