"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: Get files from git via HTTPS
"""
import modules.git.scum_gitea as gitea
import modules.git.scum_gitlab as gitlab
import modules.git.scum_http_request as generic

from modules.configmanager import ConfigManager as configmanager

class ScumGitConnector():
    """ Class to manage git connections """
    configuration: configmanager
    connector: object

    def __init__(self):
        """ Initialize object """
        self.configuration = configmanager()
        if self.configuration.git["protocol"] == "gitlab":
            self.connector = gitlab.ScumGitlab(self.configuration.git["url"],
                                               self.configuration.git["private_token"])
        elif self.configuration.git["protocol"] == "gitea":
            self.connector = gitea.ScumGitea(self.configuration.git["url"],
                                             self.configuration.git["private_token"])
        else:
            self.connector = generic.ScumGitHttp(self.configuration.git["url"],
                                                 self.configuration.git["username"],
                                                 self.configuration.git["password"])

    def get_file(self, filename) -> object:
        """ get a file from the git server """
        retval = None
        try:
            retval = self.connector.get_file(filename)
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print("Error: ", e)

        return retval
        # pylint: enable=broad-exception-caught
