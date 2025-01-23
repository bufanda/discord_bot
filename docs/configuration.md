# Configuration

## configure env-file
```bash
DISCORD_TOKEN = "<discord-token>"
DISCORD_GUILD = "<server-name>"

SCUM_LOG_FEED_CHANNEL = "<channel-id>" # Default Channel where bot will post all messages

SCUM_LOG_CHAT_ADMIN_CHANNEL = "<channel-id>" # Channel to post admin chat messages - if not defined default channel will be used

SCUM_LOG_CHAT_TEAM_CHANNEL = "<channel-id>" # Channel to post team chat messages - if not defined default channel will be used

SCUM_LOG_CHAT_GLOBAL_CHANNEL = "<channel-id>" # Channel to post global chat messages - if not defined default channel will be used

SCUM_LOG_CHAT_LOCAL_CHANNEL = "<channel-id>" # Channel to post local chat messages - if not defined default channel will be used

DATABASE_FILE = "/app/db.sqlite3"

SFTP_HOST = # SFTP-Host
SFTP_PORT = # SFTP-Port
SFTP_USERNAME = # SFTP-User
SFTP_PASSWORD = # SFTP-Passwort
LOG_DIRECTORY = # Path to logfiles
LOG_CHECK_INTERVAL = 60 # Interval in which bot will check server log files (default: 60 seconds)
RESTART_SCHEDULE = # Comma seperated times in HH:MM when server restarts happen
                  # Users will be set as offline in bot database

BOT_HELP_COMMAND = # Command to print bot help (default: buffi)

BOT_USER_ROLE = # user role who can invoke user commands. Set to @everyone for global access
BOT_USER_ADMIN_ROLE = # Admin role that is allowed to modify bot runtime configuration (default: sbot_admin)
                     # Role has to be created on server (deprecated).

BOT_ADMIN_ROLE = # Admin role that is allowed to modify bot runtime configuration (default: sbot_admin)
                     # Role has to be created on server.

BOT_ADMIN_USER = # User who can invoke config command via DM

BOT_SUPER_ADMIN_ROLE = # Users with super admin role can invoke audit command
BOT_SUPER_ADMIN_USER = # Super admin who can invoke audit command via DM

EXPERIMENTAL_ENABLE = # Enable experimental and debug features (default: disabled)
                     # Valid value to enable => 1

BOT_LANGUAGE = "en" # set languge bot should use for chat messages currently supported: en, de

SCUM_CONFIG_GIT_PROJECT = # Project on git server (gitlab)
SCUM_CONFIG_GIT_BRANCH = # Branch on git server (gitlab)
SCUM_CONFIG_GIT_HOST = # Host on git server (gitlab)
SCUM_CONFIG_GIT_FILE = # Full path filename on git server for default
                       # file to copy in case file isn't given with copy command (gitlab)

SCUM_CONFIG_GIT_TOKEN = # Authorization Token git server (gitlab)
SCUM_CONFIG_GIT_DESTINATION = # Default destination for config file on scum server (full path and filename)

```
