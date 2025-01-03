# SCUM Discord Bot

preliminary readme

## Supported commands

    * !online <user> - Returns if a user is online or not. <user> is optional.
    * !lastseen <user> - Returns if a user is online or not and lasst seen time if offline.
    * !bunkers <bunker> - Returns if bunker is active. <bunker> is optional.
    * !lifetime <user> - Returns the lifetime of a player on the Server. <user> is optional.
    * !config <config key> <config value> - configure some bot setting during runtime. (Only for role BOT_USER_ADMIN_ROLE and user BOT_ADMIN_USER)
      valid keys and values:
        -> reply: private or same_channel - when private will respond via DM. same_channel reply to same channel.
        -> publish_login: 0 = disable, 1 = enable. When enabled will report logins to SCUM_LOG_FEED_CHANNEL
        -> publish_bunkers: 0 = disable, 1 = enable. When enabled will report bunker activations to SCUM_LOG_FEED_CHANNEL
        -> publish_kills: 0 = disable, 1 = enable. When enabled will report kills to SCUM_LOG_FEED_CHANNEL
        -> publish_admin_log: 0 = disable, 1 = enable. When enabled Admin action will be published in SCUM_LOG_FEED_CHANNEL
        -> publish_chat: 0 = disabel, 1 = enable. When enabled chat messages will be posted in configured channels
        -> publish_chat_globa: default enabled - but if <publish_chat = disabled> it's disabled too.
        -> publish_chat_team: default enabled - but if <publish_chat = disabled> it's disabled too.
        -> publish_chat_admin: default enabled - but if <publish_chat = disabled> it's disabled too.
        -> publish_chat_local: default enabled - but if <publish_chat = disabled> it's disabled too.
      - BOT_ADMIN_USER can contact the bot in DM to execute config command
    * !audit age <age> - Audit Admin log
       -> <age> can be in days or month (e.g. !audit 14d, !audit 3m)
       -> Can only be called by users with role CONFIG_SUPER_ADMIN_ROLE
       -> Can be used via DM by user BOT_SUPER_ADMIN_USER
    * !debug <cmd> - Debug commands, when enabled no rights restrictions are applied!!!
        - dump_all - Dumps config, member database and environment
    * !offline <name> or all - set's a player in offline state in bot database. If `all` is used all 
      players will be set to offline state

## configure env-file
```
DISCORD_TOKEN = "<discord-token>"
DISCORD_GUILD = "<server-name>"

SCUM_LOG_FEED_CHANNEL = "<channel-id>" # Default Channel where bot will post all messages

SCUM_LOG_CHAT_ADMIN_CHANNEL = "<channel-id>" # Channel to post admin chat messages - if not defined default channel will be used

SCUM_LOG_CHAT_TEAM_CHANNEL = "<channel-id>" # Channel to post team chat messages - if not defined default channel will be used

SCUM_LOG_CHAT_GLOBAL_CHANNEL = "<channel-id>" # Channel to post global chat messages - if not defined default channel will be used

SCUM_LOG_CHAT_LOCAL_CHANNEL = "<channel-id>" # Channel to post local chat messages - if not defined default channel will be used

DATABASE_FILE = "/app/db.sqlite3"

SFTP_HOST= # SFTP-Host
SFTP_PORT= # SFTP-Port
SFTP_USERNAME= # SFTP-User
SFTP_PASSWORD= # SFTP-Passwort
LOG_DIRECTORY= # Path to logfiles
LOG_CHECK_INTERVAL= 60 # Interval in which bot will check server log files (default: 60 seconds)
RESTART_SCHEDULE= # Comma seperated times in HH:MM when server restarts happen
                  # Users will be set as offline in bot database
                  
BOT_HELP_COMMAND= # Command to print bot help (default: buffi)

BOT_USER_ROLE= # user role who can invoke user commands. Set to @everyone for global access
BOT_USER_ADMIN_ROLE= # Admin role that is allowed to modify bot runtime configuration (default: sbot_admin)
                     # Role has to be created on server (deprecated).

BOT_ADMIN_ROLE= # Admin role that is allowed to modify bot runtime configuration (default: sbot_admin)
                     # Role has to be created on server.

BOT_ADMIN_USER= # User who can invoke config command via DM

BOT_SUPER_ADMIN_ROLE= # Users with super admin role can invoke audit command
BOT_SUPER_ADMIN_USER= # Super admin who can invoke audit command via DM

EXPERIMENTAL_ENABLE= # Enable experimental and debug features (default: disabled)
                     # Valid value to enable => 1

BOT_LANGUAGE=en # set languge bot should use for chat messages currently supported: en, de
```

## Build and run docker
```bash
    docker build -t scum_bot .
    docker run --name scum_bot -d -v ".env:/app/.env" -v "db.sqlite3:/app/db.sqlite3" scum_bot
```

# Build language catalog

Extract phrases from source code:
```bash
python setup.py extract_messages --output-file locale/messages.pot --input-dirs ./
```

Prepare/Update template:
```bash
python setup.py update_catalog -l de -i locale/messages.pot -o locale/de/LC_MESSAGES/messages.po
```

Compile catalog:
```bash
cd locale/de/LC_MESSAGES
msgfmt.py messages.po
```
