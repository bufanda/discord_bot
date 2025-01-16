"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: handler for commands
"""
from modules.datamanager import ScumLogDataManager
from command.base import Command

# pylint: disable=too-few-public-methods, too-many-branches
class PlayerMangement(Command):
    """Class to handle Online command"""
    db_connection: ScumLogDataManager

    def __init__(self):
        super().__init__()
        self.db_connection = ScumLogDataManager(self.config.database_file)

    def handle_command(self, kwargs: list ) -> str:
        """handle online command"""
        subcommand = kwargs[0]
        player = kwargs[1]
        message = ""
        self.logging.info(f"manage Player {player} with sub-command {subcommand}")
        if subcommand == "delete":
            if (self._remove_player(player)):
                message = self._("Player {player} was removed successfully from database.").format(player=player)
            else:
                message = self._("Player {player} couldn't be removed from database. Do they exist?").format(player=player)
        elif subcommand == "lifetime":
            if (self._update_player_lifetime(player, int(kwargs[2]))):
                message = self._("Lifetime for player {player} was set to {lifetime}")\
                    .format(player=player, lifetime=kwargs[2])
            else:
                message = self._("Lifetime for player {player} couldn't be updated. Do they exist?")\
                    .format(player=player,)

        return message

    def _remove_player(self, player: str) -> bool:
        p = self.db_connection.get_player_status(player)
        if p is None or len(p) == 0:
            return False
        else:
            self.db_connection.delete_player(player)
            return True


    def _update_player_lifetime(self, player: str, new_lifetime: int) -> bool:
        p = self.db_connection.get_player_status(player)
        if p is not None:
            return self.db_connection.update_player_lifetime(player, new_lifetime)
        else:
            return False

    def close(self):
        self.db_connection.close()
