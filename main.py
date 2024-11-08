#! /usr/bin/env python3
"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: A Discord bot that will handle log files generated by a SCUM server
                  and will send various events to discord.
"""
# pylint: disable=global-statement, too-many-branches, too-many-lines, import-error
import os
import sys
import random
import traceback

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv

# pylint: disable=wrong-import-position
# sys.path.append('./')
from modules.datamanager import ScumLogDataManager
from modules.logparser import LoginParser, KillParser, BunkerParser, FamepointParser, \
    AdminParser
from modules.sftploader import ScumSFTPLogParser
from modules.output import Output
from modules.configmanager import ConfigManager
# pylint: enable=wrong-import-position

load_dotenv()
LOG_CHECK_INTERVAL = os.getenv("LOG_CHECK_INTERVAL")

if LOG_CHECK_INTERVAL is None:
    LOG_CHECK_INTERVAL = 60.0
else:
    LOG_CHECK_INTERVAL = float(LOG_CHECK_INTERVAL)

HELP_COMMAND = os.getenv("BOT_HELP_COMMAND")
if HELP_COMMAND is None:
    HELP_COMMAND = "buffi"


WEAPON_LOOKUP = {
    "Compound_Bow_C": "compund bow"
}

MAX_MESSAGE_LENGTH = 1000

heartbeat = datetime.now()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix="!",intents=intents)
lp: None

logging = Output()
config = None

@client.event
async def on_ready():
    """Function is called when bot is ready"""
    global lp
    global heartbeat
    guild = None
    for guild in client.guilds:
        if config.guild in (guild.name, str(guild.id)):
            # print("found")
            break

    if guild is not None:
        logging.info(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})\n'
            f'Starting log parser.'
        )
    #call database manager to initialize db
    db = ScumLogDataManager(config.database_file)

    # Open SFTP connection to the game server
    lp = ScumSFTPLogParser(server=config.sftp_server, port=config.sftp_port, passwd=config.sftp_password,
                           user=config.sftp_user, logdirectoy=config.log_directory,
                           database=config.database_file, debug_callback=None)

    # Inital load of guild members
    await load_guild_members(db)

    # Start the loop that checks log files periodically
    if not log_parser_loop.is_running():
        logging.info("Starting main loop.")
        heartbeat = datetime.now()
        log_parser_loop.start()

    if not watchdog.is_running():
        logging.info("Starting main loop watchdog.")
        watchdog.start()

def _convert_time(in_sec: int) -> str:
    days = 0
    hours = 0
    minutes = 0
    seconds = in_sec

    days = int(in_sec / 86400)
    seconds = in_sec % 86400

    hours = int(seconds / 3600)
    seconds = seconds % 3600

    minutes = int(seconds / 60)
    seconds = int(seconds % 60)

    return f"{days:02d}d {hours:02d}:{minutes:02d}:{seconds:02d}"

def _get_date_for_age(in_sec: int) -> datetime:
    return datetime.today() - timedelta(days=in_sec)

def _get_timestamp(string):
    return datetime.strptime(string, "%Y.%m.%d-%H.%M.%S").timestamp()

async def _reply(context, msg) -> None:
    if len(msg) > MAX_MESSAGE_LENGTH:
        chunks = []
        chunk = ""
        for line in msg.split("\n"):
            if len(chunk) + len(line) < MAX_MESSAGE_LENGTH:
                chunk += f"{line}\n"
            else:
                chunks.append(chunk)
                chunk = f"{line}\n"
        for _chunk in chunks:
            if config.config["reply"] == "same_channel":
                await context.reply(_chunk)
            else:
                await context.author.send(_chunk)
    else:
        if config.config["reply"] == "same_channel":
            await context.reply(msg)
        else:
            await context.author.send(msg)

async def _reply_author(context, msg) -> None:
    if len(msg) > MAX_MESSAGE_LENGTH:
        chunks = []
        chunk = ""
        for line in msg.split("\n"):
            if len(chunk) + len(line) < MAX_MESSAGE_LENGTH:
                chunk += f"{line}\n"
            else:
                chunks.append(chunk)
                chunk = f"{line}\n"
        for _chunk in chunks:
            await context.author.send(_chunk)
    else:
        await context.author.send(msg)

def _check_guild_roles(guild_roles, role) -> bool:
    retval = False
    for role in guild_roles:
        if role.name == role:
            retval = True
    return retval

def _check_user_bot_role(name: str, bot_role: str, super_admin: bool = False):
    db = ScumLogDataManager(config.database_file)
    user = db.get_guild_member(name)
    user_ok = False

    if len(user) == 0:
        if name == config.super_admin_user and super_admin:
            return True
        # user not in DB so return
        else:
            return False

    if user[name]['bot_role'] == "deny":
        return False

    if config.BOT_ROLES.index(user[name]['bot_role']) >= config.BOT_ROLES.index(bot_role):
        user_ok = True

    if name == config.super_admin_user and super_admin:
        user_ok = True

    return user_ok

async def send_debug_message(message):
    """Function will send debug messages"""
    channel = client.get_channel(int(config.debug_channel))
    await channel.send(message)

async def handle_login(msgs, file, dbconnection):
    """parse messages from login log files"""
    channel = client.get_channel(int(config.log_feed_channel))
    p = LoginParser()
    for m in msgs[file]:
        if not isinstance(m,set):
            for mm in str.split(m,"\n"):
                msg = p.parse(mm)
                if msg and dbconnection.check_message_send(msg["hash"]):
                    player_data = dbconnection.get_player_status(msg["username"])
                    if len(player_data) == 0:
                        player_data.append({'drone': False})
                    if not msg['drone'] and not player_data[0]['drone']:
                    # pylint: disable=line-too-long
                        msg_str = f"Player: {msg['username']}, logged "
                        msg_str += f"{msg['state']} @ [X={msg['coordinates']['x']} "
                        msg_str += f"Y={msg['coordinates']['y']} Z={msg['coordinates']['z']}]"
                        msg_str += f"(https://scum-map.com/en/map/place/{msg['coordinates']['x']}"
                        msg_str += f",{msg['coordinates']['y']},3)"
                        if config.config["publish_login"] and \
                            (datetime.now().timestamp() - _get_timestamp(msg['timestamp']) < 600):
                            await channel.send(msg_str)

                if msg and dbconnection.check_message_send(msg["hash"]):
                    if not msg['drone'] and player_data[0]['drone']:
                        msg['drone'] = True
                    dbconnection.store_message_send(msg["hash"])
                    dbconnection.update_player(msg)
                    # pylint: enable=line-too-long

async def handle_kills(msgs, file, dbconnection):
    """function to construct and send kill messages"""
    channel = client.get_channel(int(config.log_feed_channel))
    player_insults = [
        'bad boy',
        'savage',
        'bandit',
        'hero',
        'murderer'
    ]

    player_insult = random.choice(player_insults)
    p = KillParser()
    for m in msgs[file]:
        if not isinstance(m,set):
            for mm in str.split(m,"\n"):
                msg = p.parse(mm)
                if msg and dbconnection.check_message_send(msg["hash"]):
                    if msg["event"]["Weapon"] in WEAPON_LOOKUP:
                        weapon = WEAPON_LOOKUP[[msg["event"]["Weapon"]]]
                    else:
                        weapon = msg["event"]["Weapon"]
                    msg_str = f"Player {msg['event']['Killer']['ProfileName']} "
                    msg_str += f"was a {player_insult} "
                    msg_str += f"and killed {msg['event']['Victim']['ProfileName']} "
                    msg_str += f"with a {weapon}."

                    if config.config["publish_kills"]:
                        await channel.send(msg_str)
                    dbconnection.store_message_send(msg["hash"])

async def handle_bunkers(msgs, file, dbconnection):
    """handle bunker events"""
    channel = client.get_channel(int(config.log_feed_channel))
    p = BunkerParser()
    for m in msgs[file]:
        if not isinstance(m,set):
            for mm in str.split(m,"\n"):
                msg = p.parse(mm)
                if msg and dbconnection.check_message_send(msg["hash"]):
                    # Bunker activaed

                    bunker_data = dbconnection.get_active_bunkers(msg['name'])
                    if len(bunker_data) == 0:
                        bunker_data.append({"active": 0})

                    if msg["active"] and bunker_data[0]['active'] == 0:
                        msg_str = f"Bunker {msg['name']} was activated. "
                        if len(msg["coordinates"]) != 0:
                            msg_str += f"Coordinates @ [X={msg['coordinates']['x']} "
                            msg_str += f"Y={msg['coordinates']['y']} "
                            msg_str += f"Z={msg['coordinates']['z']}]"
                            msg_str += "(https://scum-map.com/en/map/place/"
                            msg_str += f"{msg['coordinates']['x']}"
                            msg_str += f",{msg['coordinates']['y']},3)"
                        elif 'coordinates' in bunker_data[0]:
                            msg_str += f"Coordinates @ [X={bunker_data[0]['coordinates']['x']} "
                            msg_str += f"Y={bunker_data[0]['coordinates']['y']} "
                            msg_str += f"Z={bunker_data[0]['coordinates']['z']}]"
                            msg_str += "(https://scum-map.com/en/map/place/"
                            msg_str += f"{bunker_data[0]['coordinates']['x']}"
                            msg_str += f",{bunker_data[0]['coordinates']['y']},3)"
                        else:
                            msg_str += "Bunker coordinates unkown, "
                            msg_str += "it wasnt't discovered previously."
                        if config.config["publish_bunkers"]:
                            await channel.send(msg_str)
                    dbconnection.update_bunker_status(msg)
                    dbconnection.store_message_send(msg["hash"])

async def handle_fame(msgs, file, dbconnection):
    """handle fame point events"""
    # channel = client.get_channel(int(config.log_feed_channel))
    fp = FamepointParser()
    for m in msgs[file]:
        if not isinstance(m,set):
            for mm in str.split(m,"\n"):
                msg = fp.parse(mm)
                if msg and dbconnection.check_message_send(msg["hash"]):
                    logging.debug(f"Player: {msg['name']} has {msg['points']} Points.")
                    dbconnection.update_fame_points(msg)
                    dbconnection.store_message_send(msg["hash"])

async def handle_admin_log(msgs, file, dbconnection):
    """handle admin log events"""
    # channel = client.get_channel(int(config.log_feed_channel))
    fp = AdminParser()
    for m in msgs[file]:
        if not isinstance(m,set):
            for mm in str.split(m,"\n"):
                msg = fp.parse(mm)
                if msg and dbconnection.check_message_send(msg["hash"]):
                    logging.debug(f"Admin: {msg['name']} has called a type {msg['type']} command.")
                    dbconnection.store_message_send(msg["hash"])
                    dbconnection.update_admin_audit(msg)
                    if config.config["publish_admin_log"]:
                        channel = client.get_channel(int(config.log_feed_channel))
                        msg_str = f"{msg['time']} - Admin: "
                        msg_str += f"{msg['name']} invoked "
                        msg_str += f"{msg['type']}: {msg['action']}\n"
                        await channel.send(msg_str)

async def load_guild_members(db: ScumLogDataManager):
    """load guild members and add new members to database"""
    current_members = db.get_guild_member()
    logging.info("Updating guild members.")
    for guild in client.guilds:
        if config.guild in (guild.name, str(guild.id)):
            if guild.owner.name not in current_members:
                current_members.update({
                    guild.owner.name: {
                        "id": guild.owner.id,
                        "guild_role": "",
                        "bot_role": "owner"
                    }
                })
                db.update_guild_member(guild.owner.id, guild.owner.name,
                    "", "owner")

            for member in guild.members:
                update_member = False
                roles= []
                for role in guild.get_member(member.id).roles:
                    roles.append(role.name)

                if member.name not in current_members:
                    # add member
                    logging.info(f"Found new discord member: {member}.")
                    if member.name == guild.owner.name:
                        bot_role= "owner"
                    elif member.name == config.super_admin_user:
                        bot_role = "owner"
                    elif _check_guild_roles(member.roles, config.super_admin_role):
                        bot_role= "owner"
                    elif member.name == config.admin_user:
                        bot_role = "admin"
                    elif _check_guild_roles(member.roles, config.user_role):
                        bot_role= "user"
                    elif _check_guild_roles(member.roles, config.admin_role):
                        bot_role= "admin"
                    else:
                        bot_role = "deny"

                    current_members.update({
                        member.name: {
                            "id": member.id,
                            "guild_role": ",".join(roles),
                            "bot_role": bot_role
                        }
                    })
                    update_member = True
                else:
                    # update guild roles if necessary
                    bot_role = current_members[member.name]["bot_role"]
                    if _check_guild_roles(member.roles, config.user_role) \
                            and not _check_user_bot_role(member.name, "user"):
                        bot_role = "user"

                    if ",".join(roles) != current_members[member.name]["guild_role"]:
                        logging.info(f"Update existing discord member: {member}")
                        current_members.update({
                            member.name: {
                                "id": member.id,
                                "guild_role": ",".join(roles),
                                "bot_role": bot_role
                            }
                        })

                        update_member = True

                if update_member:
                    db.update_guild_member(member.id, member.name,
                                           current_members[member.name]["guild_role"],
                                           current_members[member.name]["bot_role"])

            break

@tasks.loop(seconds=60)
async def watchdog():
    """A watchdog for the main loop"""
    logging.info("Watchdog execute.")
    _now = datetime.now()
    if _now.timestamp() - heartbeat.timestamp() > config.log_check_interval * 5:
        logging.error(f"Main loop not running for {config.log_check_interval * 5} seconds. \
                      Attempting to restart.")

        if log_parser_loop.is_running():
            logging.error("Main loop was still running, restart main loop.")
            log_parser_loop.restart()
        else:
            logging.error("Main loop was dead. Starting main loop.")
            log_parser_loop.start()

@tasks.loop(seconds=LOG_CHECK_INTERVAL)
async def log_parser_loop():
    """Loop to parse logfiles and handle outputs"""
    global heartbeat
    db = ScumLogDataManager(config.database_file)
    await client.wait_until_ready()
    msgs = await lp.scum_log_parse()
    if len(msgs) > 0:
        for file_key in msgs:
            if "login" in file_key:
                await handle_login(msgs, file_key, db)
            elif "kill" in file_key and "event" not in file_key:
                await handle_kills(msgs, file_key, db)
            elif "gameplay" in file_key:
                await handle_bunkers(msgs, file_key, db)
            elif "famepoints" in file_key:
                await handle_fame(msgs, file_key, db)
            elif "admin" in file_key:
                await handle_admin_log(msgs, file_key, db)

    if datetime.now().minute % 10 == 0:
        await load_guild_members(db)

    if datetime.now().hour == 0 and datetime.now().minute == 0:
        db.discard_old_logfiles(30*86400)
        db.discard_aged_messages(30*86400)
        db.discard_old_admin_audtis(60*86400)
    db.close()
    heartbeat = datetime.now()

@log_parser_loop.error
async def on_loop_error(error):
    """Error handler for the loop"""
    logging.error(f"Error during loop occoured: {error}")
    if log_parser_loop.failed() and not log_parser_loop.is_running():
        log_parser_loop.start()
    elif log_parser_loop.failed and log_parser_loop.is_running():
        log_parser_loop.restart()
    else:
        if not log_parser_loop.is_running():
            log_parser_loop.start()
        elif log_parser_loop.is_running():
            log_parser_loop.restart()

@client.command(name="debug")
async def command_debug(ctx, *args):
    """some debug functions"""
    if not config.experimental:
        return
    db = ScumLogDataManager(config.database_file)
    if args[0] == "dump_all":
        await _reply_author(ctx, "Current configuration")
        msg_str = ""
        for cfg in config.config.items():
            msg_str += f"{cfg[0]}: {cfg[1]}\n"
        await _reply_author(ctx, msg_str)

        await _reply_author(ctx, "Members stored in DB.")
        members = db.get_guild_member()
        msg_str = ""
        for member, member_data in members.items():
            msg_str += f"{member} - Discord Role: {member_data['guild_role']}"
            msg_str += f" - Bot Role: {member_data['bot_role']}\n"
        await _reply_author(ctx, msg_str)

        await _reply_author(ctx, "Current Environment")
        msg_str = ""
        for key,value in os.environ.items():
            if key in config.ENV_AVAILABLE_KEYS:
                msg_str += f"{key}: {value}\n"

        await _reply_author(ctx, "Guild members:")
        for guild in client.guilds:
            if config.guild in (guild.name, guild.id):
                await _reply_author(ctx, str(client.guild.members))
        await _reply_author(ctx, msg_str)

@client.command(name="member")
async def command_member(ctx, *args):
    """ handle command member"""
    # pylint: disable=consider-using-dict-items
    db = ScumLogDataManager(config.database_file)
    msg_str = ""
    if not _check_user_bot_role(ctx.author.name, 'admin', True):
        await ctx.reply("You don't have permission to invoke this command.")
        return

    if len(args) == 0:
        members = db.get_guild_member()
        msg_str = "Current members in database:\n"
        for member in members:
            msg_str += f"{member} - Discord Role: {members[member]['guild_role']}"
            msg_str += f" - Bot Role: {members[member]['bot_role']}\n"

    elif len(args) == 1:
        members = db.get_guild_member(args[0])
        if len(members) < 1:
            msg_str = "No members stored in Database"
        else:
            msg_str = "Current members in database:\n"
            for member in members:
                msg_str += f"{member} - Discord Role: {members[member]['guild_role']}"
                msg_str += f" - Bot Role: {members[member]['bot_role']}\n"

    elif len(args) == 2:
        # set bot_role of memeber
        member = db.get_guild_member(args[0])
        if len(member) < 1:
            if ctx.guild:
                for _member in ctx.guild.members:
                    if _member.name == args[0]:
                        msg_str = f"Member {args[0]} given bot role {args[1]}"
                        db.update_guild_member(_member.id,args[0],
                                                   ",".join(_member.roles),args[1])
                if len(msg_str) == 0:
                    msg_str = f"Member {args[0]} does not exist on Server."
            else:
                msg_str = f"Member {args[0]} not in database. Can't create member via DM."
        else:
            if member[args[0]]["bot_role"] == args[1]:
                msg_str = f"Member {args[0]} already has bot role {args[1]}"
            else:
                msg_str = f"Member {args[0]} given bot role {args[1]}"
                db.update_guild_member(member[args[0]]['id'],args[0],
                                       member[args[0]]['guild_role'],args[1])

    else:
        await _reply_author(ctx, "Too many arguments for command 'member'")

    if len(msg_str) > 0:
        await _reply_author(ctx, msg_str)
    else:
        await _reply_author(ctx, "No members in database!")
    # pylint: enable=consider-using-dict-items

async def handle_command_audit(ctx, args):
    """ handle command audit"""
    db = ScumLogDataManager(config.database_file)
    msg_str = ""
    local_timezone = ZoneInfo('Europe/Berlin')
    if len(args) == 0:
        audit = db.get_admin_audit()
        for a in audit:
            msg_str += f"{datetime.fromtimestamp(a['timestamp'],
                        local_timezone).strftime('%Y-%m-%d %H:%M:%S')}: "
            msg_str += f"{a['username']} invoked "
            msg_str += f"{a['type']}: {a['action']}\n"
    elif args[0] == "age":
        if "d" in args[1]:
            _days = int(args[1].split("d")[0])
            age = _get_date_for_age(_days)
        elif "m" in args[1]:
            _months = int(args[1].split("m")[0])
            age = _get_date_for_age(_months * 30)
        else:
            age = 0

        audit = db.get_admin_audit('age', datetime.timestamp(age))
        for a in audit:
            msg_str += f"{datetime.fromtimestamp(a['timestamp'],
                        local_timezone).strftime('%Y-%m-%d %H:%M:%S')}: "
            msg_str += f"{a['username']} invoked "
            msg_str += f"{a['type']}: {a['action']}\n"
    else:
        msg_str = "Command not supported!"

    if len(msg_str) > 0:
        if len(msg_str) > MAX_MESSAGE_LENGTH:
            chunks = []
            chunk = ""
            for line in msg_str.split("\n"):
                if len(chunk) + len(line) < MAX_MESSAGE_LENGTH:
                    chunk += f"{line}\n"
                else:
                    chunks.append(chunk)
                    chunk = f"{line}\n"

            for _chunk in chunks:
                await _reply_author(ctx, _chunk)
        else:
            await _reply_author(ctx, msg_str)
    else:
        await _reply_author(ctx, "No entries in audit!")

@client.command(name="audit")
async def command_audit(ctx, *args):
    """print audit log"""
    if ctx.guild:
        roles = []
        for role in ctx.author.roles:
            roles.append(role.name)

        if config.super_admin_role in roles or \
           _check_user_bot_role(ctx.author.name, 'admin', True):
            await handle_command_audit(ctx, args)
        else:
            await ctx.reply("You have no permission to execute this command!")

    else:
        if config.super_admin_user == ctx.author.name or \
           _check_user_bot_role(ctx.author.name, 'admin', True):
            await handle_command_audit(ctx, args)
        else:
            await ctx.reply("You have no permission to execute this command!")

async def handle_command_config(ctx, args):
    """ ** """
    db = ScumLogDataManager(config.database_file)
    if len(args) <= 0:
        msg = "Current config:\n"
        for cfg in config.config.items():
            msg += f"{cfg[0]}: {cfg[1]}\n"
        await _reply_author(ctx, msg)
        return

    if args[0] == "reply":
        if len(args) < 2:
            await _reply(ctx, "Missing arguments.")
        else:
            if args[1] == "private":
                config.config.update({"reply": "private"})
            else:
                config.config.update({"reply": "same_channel"})

    if args[0] == "publish_login":
        if len(args) < 2:
            await _reply(ctx, "Missing arguments.")
        else:
            if args[1].lower() == "true" or args[1] == "1":
                config.config.update({"publish_login": True})
            else:
                config.config.update({"publish_login": False})

    if args[0] == "publish_bunkers":
        if len(args) < 2:
            await _reply(ctx, "Missing arguments.")
        else:
            if args[1].lower() == "true" or args[1] == "1":
                config.config.update({"publish_bunkers": True})
            else:
                config.config.update({"publish_bunkers": False})

    if args[0] == "publish_kills":
        if len(args) < 2:
            await _reply(ctx, "Missing arguments.")
        else:
            if args[1].lower() == "true" or args[1] == "1":
                config.config.update({"publish_kills": True})
            else:
                config.config.update({"publish_kills": False})

    if args[0] == "publish_admin_log":
        if len(args) < 2:
            await _reply(ctx, "Missing arguments.")
        else:
            if args[1].lower() == "true" or args[1] == "1":
                config.config.update({"publish_admin_log": True})
            else:
                config.config.update({"publish_admin_log": False})

    logging.info(f"Updated config: {args[0]} = {config.config[args[0]]}")
    await _reply_author(ctx, f"Saved config: {args[0]} = {config.config[args[0]]}")
    db.save_config(config.config)

@client.command(name="config")
async def command_config(ctx, *args):
    """configure some settings on the bot"""
    if ctx.guild:
        roles = []
        for role in ctx.author.roles:
            roles.append(role.name)

        if config.admin_role in roles or \
           _check_user_bot_role(ctx.author.name, 'moderator', True):
            await handle_command_config(ctx, args)
        else:
            await ctx.reply("You do not have permission to execute this command.")

    else:
        if config.admin_user == ctx.author.name or \
           _check_user_bot_role(ctx.author.name, 'moderator', True):
            await handle_command_config(ctx, args)
        else:
            await ctx.reply("You do not have permission to execute this command.")


@client.command(name="lifetime")
async def command_lifetime(ctx, player: str = None):
    """Command to check server liftime of players"""
    msg_str = None

    if not _check_user_bot_role(ctx.author.name, "user") and not \
        _check_guild_roles(config.user_role):
        await ctx.reply("You do not have permission to invoke this command.")
        return

    db = ScumLogDataManager(config.database_file)
    if player:
        logging.info(f"Get server lifetime for player {player}")
        player_stat = db.get_player_status(player)
        if len(player_stat) > 0:
            lifetime = _convert_time(player_stat[0]["lifetime"])
            msg_str = f"Player {player} lives on server for {lifetime}."
        else:
            msg_str = f"Player {player} has no life on this server."
    else:
        logging.info("Getting all players that visited the server")
        player_stat = db.get_player_status()
        msg_str = "Following players have a liftime on this server:\n"
        for p in player_stat:
            lifetime = _convert_time(p["lifetime"])
            msg_str += f"{p['name']} lives for {lifetime} on this server.\n"

    await _reply(ctx, msg_str)
    db.close()

@client.command(name='bunkers')
async def command_bunkers(ctx, bunker: str = None):
    """Command to check Active bunkers"""
    msg_str = None

    if not _check_user_bot_role(ctx.author.name, "user") and not \
        _check_guild_roles(config.user_role):
        await ctx.reply("You do not have permission to invoke this command.")
        return

    db = ScumLogDataManager(config.database_file)
    if bunker:
        logging.info(f"Will get data for Bunker {bunker}")
        b = db.get_active_bunkers(bunker)
        if len(b) > 0:
            if b[0]["active"] == 0:
                msg_str = f"Bunker {bunker} is not active."
                if b[0]["next"] > 0:
                    _next = b[0]["timestamp"] + b[0]["next"]
                    msg_str += "\nWill be active @ "
                    msg_str += f"{datetime.fromtimestamp(_next).strftime('%d.%m.%Y - %H:%M:%S')}"
            else:
                msg_str =f"Bunker {bunker} is active.\n"
                msg_str += f"@ [Coordinates X={b[0]['coordinates']['x']} "
                msg_str += f"Y={b[0]['coordinates']['y']} "
                msg_str += f"Z={b[0]['coordinates']['z']}]"
                msg_str += f"(https://scum-map.com/en/map/place/{b[0]['coordinates']['x']}"
                msg_str += f",{b[0]['coordinates']['y']},3)"
        else:
            msg_str = f"Bunker {bunker} does not exist."
    else:
        logging.info("No bunker given, will get all active bunkers.")
        b = db.get_active_bunkers(None)
        if len(b) > 0:
            msg_str = "Following Bunkers are active.\n"
            for bunk in b:
                msg_str += f"Bunker {bunk['name']} is active.\n"
                msg_str += f"@ [Coordinates X={bunk['coordinates']['x']} "
                msg_str += f"Y={bunk['coordinates']['y']} "
                msg_str += f"Z={bunk['coordinates']['z']}]"
                msg_str += f"(https://scum-map.com/en/map/place/{b[0]['coordinates']['x']}"
                msg_str += f",{b[0]['coordinates']['y']},3)\n"
        else:
            msg_str = "No active bunkers found."

    await _reply(ctx, msg_str)
    db.close()

@client.command(name='online')
async def player_online(ctx, player: str = None):
    """Command to check if player is online"""
    message = ""

    if not _check_user_bot_role(ctx.author.name, "user") and not \
        _check_guild_roles(config.user_role):
        await ctx.reply("You do not have permission to invoke this command.")
        return

    local_timezone = ZoneInfo('Europe/Berlin')
    logging.info(f"Get status for player {player}")
    db = ScumLogDataManager(config.database_file)
    if player:
        player_status = db.get_player_status(player)

        if len(player_status) == 0:
            message = f"Error: Player {player} does not exists in Database"
        else:
            if len(player_status) > 1:
                message = f"Multiple players with Name {player} found.\n"
                for p in player_status:
                    if p["status"] == 0:
                        state = "offline"
                    else:
                        state = "online"
                    message += f"{player} is currently {p['status']}"
            else:
                if player_status[0]["status"] == 0:
                    state = "offline"
                else:
                    state = "online"
                message = f"Player: {player} is currently {state}."
    else:
        player_status = db.get_player_status()
        if len(player_status) > 0:
            message = "Follwoing Players are online:\n"
            for p in player_status:
                if p["status"] == 1:
                    login = datetime.fromtimestamp(p['login_timestamp'],
                                                    local_timezone).strftime('%d.%m.%Y %H:%M:%S')
                    message += f"{p['name']} is online since {login}\n"
        else:
            message = "No players are online at the moment."

    await _reply(ctx, message)
    db.close()

@client.command(name='lastseen')
async def player_lastseen(ctx, player: str):
    """Function to check last seen of a player"""
    message = ""

    if not _check_user_bot_role(ctx.author.name, "user") and not \
        _check_guild_roles(config.user_role):
        await ctx.reply("You do not have permission to invoke this command.")
        return

    local_timezone = ZoneInfo('Europe/Berlin')
    logging.info(f"Get status for player {player}")
    db = ScumLogDataManager(config.database_file)
    player_status = db.get_player_status(player)

    if len(player_status) == 0:
        message = f"Error: Player {player} does not exists in Database"
    else:
        if len(player_status) > 1:
            message = f"Multiple players with Name {player} found.\n"
            for p in player_status:
                if p["status"] == 0:
                    state = "offline"
                    lasstseen = datetime.fromtimestamp(p["logout_timestamp"],
                                                       local_timezone).strftime('%d.%m.%Y %H:%M:%S')
                else:
                    state = "online"
                    lasstseen = "now"
                message += f"Player: {player} is currently {state} and was last seen {lasstseen}."
        else:
            if player_status[0]["status"] == 0:
                state = "offline"
                lasstseen = datetime.fromtimestamp(player_status[0]["logout_timestamp"],
                                                   local_timezone).strftime('%Y-%m-%d %H:%M:%S')
            else:
                state = "online"
                lasstseen = "now"

            message = f"Player: {player} is currently {state} and was last seen {lasstseen}."

    await _reply(ctx, message)
    db.close()

@client.command(name=HELP_COMMAND)
async def bot_help(ctx):
    """Help command"""

    msg_str = f"Hi, {ctx.author}. My Name is {client.user}.\n"
    msg_str += "You can call me with following commands:\n"

    await _reply(ctx, msg_str)

    msg_str = "!online <player name> - I will tell you if the"
    msg_str += "player with <name> is online on the SCUM server\n"

    await _reply(ctx, msg_str)

    msg_str = "!lastseen <player name> - I will tell you when I have seen <playername>"
    msg_str += "on the SCUM Server\n"

    await _reply(ctx, msg_str)

    msg_str = "!bunkers <bunker name> - I will tell you if the <bunker name> is active.\n"
    msg_str += "But the <bunker name> is optional. Without I unveil the secret and give"
    msg_str += " you all active bunkers."

    await _reply(ctx, msg_str)

    msg_str = "I will also report bunker openening, kills and players joining to and disconnecting "
    msg_str += "from the SCUM Server."

    await _reply(ctx, msg_str)

@client.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    """Yeah, rolling a dice"""
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await _reply(ctx, ', '.join(dice))

@client.event
async def on_command_error(ctx, error):
    """Is called when commands have errors"""
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"'{error.param.name}' is a required argument.")
    else:
        # All unhandled errors will print their original traceback
        logging.error(f'Ignoring exception in command {ctx.command}:')
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

## Start the Program
config = ConfigManager()
client.run(config.token)
