import os
import sys
import asyncio
import pytz
import datetime
import random
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

bot = commands.Bot(command_prefix='-event ')
COLOUR = 0xF8BA2B
IMG_URL = 'https://mlh.github.io/announcement-bot/img/social.jpg'


def main():
    load_dotenv()
    sys.stdout.flush()
    global events_channel_id, guild_id, role_id
    try:
        token = os.getenv("DISCORD_TOKEN")
        events_channel_id = int(os.getenv("DISCORD_EVENTS_ID"))
        guild_id = int(os.getenv("DISCORD_GUILD_ID"))
        role_id = int(os.getenv("DISCORD_ROLE_ID"))
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

    global events_channel, default_role, events_channel_id, guild_id, role_id
    events_channel = bot.get_channel(events_channel_id)
    default_role = bot.get_guild(guild_id).get_role(role_id) 

    while True:
        session = cal.get_next_session()
        if session != None and session.title != None:
            await set_status(session)
            try:
                announcement_time_first = (session.start - datetime.timedelta(minutes=10))
                announcement_time_last = (session.start - datetime.timedelta(minutes=3))
                if check_times(announcement_time_first):
                    await send_long_announcement(session)
                elif check_times(announcement_time_last):
                    await send_short_announcement(session)
            except Exception as e:
                print(f"Session was invalid: {e}")
        await asyncio.sleep(60)

async def set_status(session):
    twitch_url = "https://twitch.tv"
    title = f"{session.title} {get_time_diff(session.start)}"
    if session.url[:len(twitch_url)] == twitch_url:
        activity = discord.Streaming(name=title,
                                     url=session.url,
                                     platform="Twitch",)
    else:
        activity = discord.Activity(name=title,
                                    type=discord.ActivityType.watching)
    await bot.change_presence(status=discord.Status.online, activity=activity)

async def send_long_announcement(session):
    global events_channel, default_role
    
    embed = discord.Embed(title=session.title,
                        description=session.description,
                        url=session.url,
                        colour=COLOUR)

    embed.set_footer(text=session.url)
    
    if session.img_url != None:
        embed.set_image(url=session.img_url)
    else:
        embed.set_image(url=IMG_URL)
    if session.speaker != None:
        embed.set_author(name=session.speaker)
    
    await events_channel.send(f'Hey {default_role.mention}s, - We have a session in 10 minutes! :tada:\n ({str(session.start.strftime("%H:%M ET"))})', embed=embed)
    await add_reactions(await events_channel.fetch_message(events_channel.last_message_id))
    print("Long announcement made")

async def send_short_announcement(session):
    global events_channel, default_role
    await events_channel.send(f'Just 3 minutes until we have **{session.title}**! :tada:\n {session.url}\n{default_role.mention}')
    await add_reactions(await events_channel.fetch_message(events_channel.last_message_id))
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
    diff = announcement_time.replace(tzinfo=pytz.UTC) - datetime.datetime.now().replace(tzinfo=pytz.UTC)
    diff_args = str(diff).split(':')
    if (diff.total_seconds() < 0):
        return "happening NOW!"
    else:
        return "in " + diff_args[0] + ":" + diff_args[1] + " hr"

async def add_reactions(message):
    emojis = ["💻", "🙌", "🔥", "💯", "🍕", "🎉", "🥳", "💡", "📣"]
    random.shuffle(emojis)
    try:
        for emoji in emojis[:4]:
            await message.add_reaction(emoji)
    except Exception as e:
        print(f"Exception adding Reactions: {e}")

@bot.command(description="Displays next event")
async def next_session(ctx):
    session = cal.get_next_session()
    print("Sending next session via command")
    if session != None:
        embed = discord.Embed(title=session.title,
                            description=f'Starting at {str(session.start.strftime("%H:%M ET on %B %d"))}',
                            url=session.calendar_url,
                            colour=COLOUR)

        if session.img_url != None:
            embed.set_image(url=session.img_url)
        else:
            embed.set_image(url=IMG_URL)

        if session.speaker != None:
            embed.set_author(name=session.speaker)

        await ctx.send(f'Here\'s the next session at {str(session.start.strftime("%H:%M GMT on %B %d"))}!', embed=embed)
        try:
            await add_reactions(await ctx.channel.fetch_message(ctx.channel.last_message_id))
        except Exception as e:
            print(f"Exception getting last message ID: {e}")

@bot.after_invoke
async def after_invoke(ctx):
    try:
        await ctx.message.delete()
    except Exception as e:
        print(f"Exception deleting message: {e}")

if __name__ == '__main__':
    main()
