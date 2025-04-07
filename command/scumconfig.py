"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 30.12.2024
    @CLicense: MIT
    @Description: handler for commands regarding scum server config
"""
from modules.gitconnector import ScumGitConnector
from modules.sftpconnector import ScumSFTPConnector
from modules.configmanager import ConfigManager
from command.base import Command

# pylint: disable=too-few-public-methods, too-many-branches
class ServerConfig(Command):
    """Class to handle Online command"""
    git_connection: ScumGitConnector
    sftp_connection: ScumSFTPConnector
    config: ConfigManager

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()

    def get_config_file(self, filename : str = None) -> object:
        """ get config file from git server """
        git_file = None
        self.git_connection = ScumGitConnector()

        if filename:
            git_file = self.git_connection.get_file(filename)
        else:
            git_file = self.git_connection.get_file(self.config.git["file"])

        return git_file

    def copy_file_to_server(self, content: object, destination: str = None):
        """ copy the file to the scum server config directory """
        self.sftp_connection = ScumSFTPConnector(self.config.sftp_server,
                                                 self.config.sftp_port,
                                                 self.config.sftp_user,
                                                 self.config.sftp_password,
                                                 logdirectoy=self.config.log_directory,
                                                 database=self.config.database_file,
                                                 debug_callback=None)

        if destination:
            self.sftp_connection.put_file(content, destination)
        else:
            self.sftp_connection.put_file(content, self.config.git["config_destination"])
