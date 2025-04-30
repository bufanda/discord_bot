"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 29.04.2025
    @CLicense: MIT
    @Description: Thread to handle log file loading
"""
import time

from modules.datamanager import ScumLogDataManager
from modules.configmanager import ConfigManager
from modules.sftpconnector import ScumSFTPConnector

class LogFileHandler():

    timer: int
    config: ConfigManager = ConfigManager()
    lp = ScumSFTPConnector
    db: ScumLogDataManager

    def __init__ (self):
        self.timer = 0
        self.db = ScumLogDataManager(self.config.database_file)

    def _message_lines(self, msgs):
        lines = []
        for m in msgs[file_key]:
            if not isinstance(m,set):
                for mm in str.split(m,"\n"):
                    lines.append(m)

    def handle_login(self, msgs, file_key):
        lines = self._message_lines(msgs)
        return lines
        
    def handle_kills(self, msgs, file_key):
        lines = self._message_lines(msgs)
        return lines

    def handle_bunkers(self, msgs, file_key):
        lines = self._message_lines(msgs)
        return lines

    def handle_fame(self, msgs, file_key):
        lines = self._message_lines(msgs)
        return lines

    def handle_admin_log(self, msgs, file_key):
        lines = self._message_lines(msgs)
        return lines

    def handle_chat(self, msgs, file_key):
        lines = self._message_lines(msgs)
        return lines

    def _parse_logfiles(self):
        """Load logfiles and store lines in database"""
        msgs = self.lp.scum_log_parse()
        if len(msgs) > 0:
            for file_key in msgs:
                if "login" in file_key:
                    self.handle_login(msgs, file_key)
                elif "kill" in file_key and "event" not in file_key:
                    self.handle_kills(msgs, file_key)
                elif "gameplay" in file_key:
                    self.handle_bunkers(msgs, file_key)
                elif "famepoints" in file_key:
                    self.handle_fame(msgs, file_key)
                elif "admin" in file_key:
                    self.handle_admin_log(msgs, file_key)
                elif "chat" in file_key:
                    self.handle_chat(msgs, file_key)


    def run_thread(self):
        while True:
            time.sleep(1)
            self.timer += 1
            if self.timer%60 == 0:
                self._parse_logfiles()
