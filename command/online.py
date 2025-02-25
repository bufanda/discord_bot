"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: handler for commands
"""
from datetime import datetime
from zoneinfo import ZoneInfo


from modules.datamanager import ScumLogDataManager
from command.base import Command

# pylint: disable=too-few-public-methods, too-many-branches
class Online(Command):
    """Class to handle Online command"""

    def handle_command(self, player: str) -> str:
        """handle online command"""
        message = ""
        local_timezone = ZoneInfo('Europe/Berlin')
        self.logging.info(f"Get status for player {player}")
        db = ScumLogDataManager(self.config.database_file)
        if player:
            player_status = db.get_player_status(player)

            if len(player_status) == 0:
                message = self._("Error: Player {player} does not exists in Database") \
                    .format(player=player)
            else:
                if len(player_status) > 1:
                    message = self._("Multiple players with Name {player} found.\n") \
                        .format(player=player)
                    for p in player_status:
                        if p["state"] == 1 and p["drone"] == 0:
                            state = "online"
                        else:
                            state = "offline"
                        message += self._("{player} is currently {status}") \
                            .format(player=player, status=state)
                else:
                    if player_status[0]["state"] == 1 and player_status[0]["drone"] == 0:
                        state = "online"
                    else:
                        state = "offline"
                    message += self._("{player} is currently {status}") \
                    .format(player=player, status=state)
        else:
            player_status = db.get_player_online_status()
            none_drone = 0
            for p in player_status:
                if p["state"] == 1 and p["drone"] == 0:
                    none_drone+=1
            if len(player_status) > 0 and none_drone > 0:
                message = self._("Follwoing Players are online:\n")
                for p in player_status:
                    if p["state"] == 1 and p["drone"] == 0:
                        login = datetime.fromtimestamp(p['login_timestamp'],
                                        local_timezone).strftime('%d.%m.%Y %H:%M:%S')
                        message += self._("{name} is online since {login}\n") \
                            .format(name=p['username'],login=login)
            else:
                message = self._("No players are online at the moment.")
        db.close()
        return message
