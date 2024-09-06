#! /usr/bin/env python3
#####################
# Discord Bot Test
# 
#
#####################
import os
import sys
import random

import discord
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv

sys.path.append('./')
from logparser import scum_logparser

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
FTP_SERVER = os.getenv("SCUM_FTP_SERVER")
FTP_USER = os.getenv("SCUM_FTP_USER")
FTP_PASSWORD = os.getenv("SCUM_FTP_PASSWORD")
KILL_FEED_CHANNEL = os.getenv("SCUM_KILL_FEED_CHANNEL")
ADMIN_LOG = os.getenv("SCUM_ADMIN_LOG")

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="!",intents=intents)
lp = None

@client.event
async def on_ready():
    global lp
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
        f'Starting log parser.'
    )
    lp = scum_logparser(FTP_SERVER, FTP_USER, FTP_PASSWORD, ADMIN_LOG)
    log_parser_killfeed.start()

@tasks.loop(seconds=10.0)
async def log_parser_killfeed():
    global lp
    await client.wait_until_ready()
    msgs = lp.scum_log_parse()
    channel = client.get_channel(int(KILL_FEED_CHANNEL))
    if len(msgs) > 0:
        for msg in msgs:
            await channel.send(msg)

@client.command(name='99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)

@client.command(name='\\/')
async def spock(ctx):
    star_trek_quotes = [
        'Live long and prosper',
        'To boldly go where no one has gone before',
        (
            'Heading,  '
            'the third star from the left and follow the bow!'
        ),
    ]

    response = random.choice(star_trek_quotes)
    await ctx.send(response)


@client.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@client.command(name='create-channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

client.run(TOKEN)