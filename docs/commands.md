# Bot Commands

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
    * !copy_server_config <source_config_file> - Allows to copy a config file from gitlab to Scum Server
    * !pm <sub-command> <player> <additional args> - Player Management in Database of Bot.
      Sub-Commands:
        -> delete <player> - delete player info from bot database
        -> lifetime <player> <lifetime> - set lifetime in seconds for player in database (future plan
        to make it more human usable)
