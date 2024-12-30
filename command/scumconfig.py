"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 30.12.2024
    @CLicense: MIT
    @Description: handler for commands regarding scum server config
"""
import tempfile
import os

from datetime import datetime
from zoneinfo import ZoneInfo


from modules.gitconnector import GitLabConnector
from modules.sftpconnector import ScumSFTPConnector
from modules.configmanager import ConfigManager
from command.base import Command

# pylint: disable=too-few-public-methods, too-many-branches
class ServerConfig(Command):
    """Class to handle Online command"""
    git_connection: GitLabConnector
    sftp_connection: ScumSFTPConnector
    config: ConfigManager

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()

    def get_config_file(self):
        self.git_connection = GitLabConnector(self.config.git["url"],
                                              self.config.git["username"],
                                              self.config.git["password"],
                                              self.config.git["branch"],
                                              self.config.git["project"])
        
        git_file = self.git_connection.get_file(self.config.git["file"])
        print(git_file)
