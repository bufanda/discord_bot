"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: handler for commands
"""
from datetime import datetime
from zoneinfo import ZoneInfo


from modules.datamanager import ScumLogDataManager
from modules.mytime import mytime
from command.base import Command


# pylint: disable=too-few-public-methods, too-many-branches, line-too-long
class Lifetime(Command):
    """Class to handle Online command"""

    def handle_command(self, player: str) -> str:
        """ some text """
        msg_str = None
        db = ScumLogDataManager(self.config.database_file)
        if player:
            self.logging.info(f"Get server lifetime for player {player}")
            player_stat = db.get_player_status(player)
            if len(player_stat) > 0:
                lifetime = mytime.convert_time(player_stat[0]["lifetime"])
                msg_str = self._("Player {player} lives on server for {lifetime}.").format(player=player, lifetime=lifetime)
            else:
                msg_str = self._("Player {player} has no life on this server.").format(player=player)
        else:
            self.logging.info("Getting all players that visited the server")
            player_stat = db.get_player_status()
            msg_str = self._("Following players have a liftime on this server:\n")
            for p in player_stat:
                lifetime = mytime.convert_time(p["lifetime"])
                msg_str += self._("{name} lives for {lifetime} on this server.\n").format(name=p['name'], lifetime=lifetime)
        db.close()

        return msg_str
