"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: A Discord bot that will handle log files generated by a SCUM server
                  and will send various events to discord.
"""
import os
from dotenv import load_dotenv
from modules.datamanager import ScumLogDataManager

class ConfigManager():
    """Managing configuration"""

    token: str
    guild: str
    sftp_server: str
    sftp_port: str
    sftp_user: str
    sftp_password: str
    debug_channel: str
    log_feed_channel: str
    log_chat_global_channel: str
    log_chat_admin_channel: str
    log_chat_team_channel: str
    log_chat_local_channel: str
    log_directory: str
    database_file: str
    log_check_interval: str
    help_command: str
    experimental: str
    admin_user: str
    admin_role: str
    super_admin_role: str
    super_admin_user: str
    user_role: str
    language: str

    config: dict

    version="1.0.10"

    _DEFAULT_CONFIG = {
        "reply": "same_channel",
        "publish_login": False,
        "publish_bunkers": False,
        "publish_kills": False,
        "publish_admin_log": False,
        "publish_chat": False,
        "publish_chat_global": True,
        "publish_chat_team": True,
        "publish_chat_admin": True,
        "publish_chat_local": True
    }

    BOT_ROLES = [
        "deny",
        "user",
        "moderator",
        "admin",
        "owner"
    ]

    ENV_AVAILABLE_KEYS = [
        "DISCORD_GUILD",
        "SFTP_HOST",
        "SFTP_PORT",
        "SFTP_USERNAME",
        "DEBUG_CHANNEL",
        "SCUM_LOG_FEED_CHANNEL",
        "LOG_DIRECTORY",
        "DATABASE_FILE",
        "LOG_CHECK_INTERVAL",
        "BOT_HELP_COMMAND",
        "EXPERIMENTAL_ENABLE",
        "BOT_USER_ADMIN_ROLE",
        "BOT_ADMIN_ROLE",
        "BOT_ADMIN_USER",
        "BOT_SUPER_ADMIN_ROLE",
        "BOT_SUPER_ADMIN_USER",
        "BOT_USER_ROLE"
    ]


    def __init__(self):
        load_dotenv()

        self.token = os.getenv("DISCORD_TOKEN")
        self.guild = os.getenv("DISCORD_GUILD")
        self.sftp_server = os.getenv("SFTP_HOST")
        self.sftp_port = os.getenv("SFTP_PORT")
        self.sftp_user = os.getenv("SFTP_USERNAME")
        self.sftp_password = os.getenv("SFTP_PASSWORD")

        self.debug_channel = os.getenv("DEBUG_CHANNEL")
        self.log_feed_channel = os.getenv("SCUM_LOG_FEED_CHANNEL")
        self.log_chat_global_channel = os.getenv("SCUM_LOG_CHAT_GLOBAL_CHANNEL")
        self.log_chat_admin_channel = os.getenv("SCUM_LOG_CHAT_ADMIN_CHANNEL")
        self.log_chat_team_channel = os.getenv("SCUM_LOG_CHAT_TEAM_CHANNEL")
        self.log_chat_local_channel = os.getenv("SCUM_LOG_CHAT_LOCAL_CHANNEL")
        self.log_directory = os.getenv("LOG_DIRECTORY")
        self.database_file = os.getenv("DATABASE_FILE")
        self.log_check_interval = os.getenv("LOG_CHECK_INTERVAL")
        self.help_command = os.getenv("BOT_HELP_COMMAND")
        self.experimental = os.getenv("EXPERIMENTAL_ENABLE")

        self.language = os.getenv("BOT_LANGUAGE")

        if os.getenv("BOT_USER_ADMIN_ROLE") is not None:
            self.admin_role = os.getenv("BOT_USER_ADMIN_ROLE")
        elif os.getenv("BOT_ADMIN_ROLE") is not None:
            self.admin_role = os.getenv("BOT_ADMIN_ROLE")
        else:
            self.admin_role = None

        self.admin_user = os.getenv("BOT_ADMIN_USER")
        self.super_admin_role = os.getenv("BOT_SUPER_ADMIN_ROLE")
        self.super_admin_user = os.getenv("BOT_SUPER_ADMIN_USER")
        self.user_role = os.getenv("BOT_USER_ROLE")

        if self.experimental:
            if self.experimental == "1":
                self.experimental = True
            else:
                self.experimental = False

        if self.admin_role is None:
            self.admin_role = 'sbot_admin'

        if self.super_admin_role is None:
            self.super_admin_role = 'sbot_super_admin'

        if self.user_role is None:
            self.user_role = '@everyone'

        if self.log_check_interval is None:
            self.log_check_interval = 60.0
        else:
            self.log_check_interval = float(self.log_check_interval)

        if self.help_command is None:
            self.help_command = "buffi"

        if not self.admin_user:
            self.admin_user = "None"

        if not self.super_admin_user:
            self.super_admin_user = "None"

        if not self.language:
            self.language = "en"

        if self.log_chat_global_channel is None:
            self.log_chat_global_channel = self.log_feed_channel

        if self.log_chat_admin_channel is None:
            self.log_chat_admin_channel = self.log_feed_channel

        if self.log_chat_team_channel is None:
            self.log_chat_team_channel = self.log_feed_channel

        if self.log_chat_local_channel is None:
            self.log_chat_local_channel = self.log_feed_channel

        self._load_config(self.database_file)

    def _load_config(self, database_file) -> None:
        init = False
        db = ScumLogDataManager(database_file)
        _config = db.load_config()
        if len(_config) == 0:
            init = True
        if "reply" not in _config:
            _config.update({"reply": self._DEFAULT_CONFIG['reply']})
        if "publish_login" not in _config:
            _config.update({"publish_login": self._DEFAULT_CONFIG['publish_login']})
        if "publish_bunkers" not in _config:
            _config.update({"publish_bunkers": self._DEFAULT_CONFIG['publish_bunkers']})
        if "publish_kills" not in _config:
            _config.update({"publish_kills": self._DEFAULT_CONFIG['publish_kills']})
        if "publish_admin_log" not in _config:
            _config.update({"publish_admin_log": self._DEFAULT_CONFIG['publish_admin_log']})
        if "publish_chat" not in _config:
            _config.update({"publish_chat": self._DEFAULT_CONFIG['publish_chat']})
        if "publish_chat_global" not in _config:
            _config.update({"publish_chat_global": self._DEFAULT_CONFIG['publish_chat_global']})
        if "publish_chat_local" not in _config:
            _config.update({"publish_chat_local": self._DEFAULT_CONFIG['publish_chat_local']})
        if "publish_chat_team" not in _config:
            _config.update({"publish_chat_team": self._DEFAULT_CONFIG['publish_chat_team']})
        if "publish_chat_admin" not in _config:
            _config.update({"publish_chat_admin": self._DEFAULT_CONFIG['publish_chat_admin']})

        self.config = _config
        if init:
            db.save_config(self.config)
