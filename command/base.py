"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: handler for commands
"""
import os
import gettext

from modules.configmanager import ConfigManager
from modules.output import Output

class Command:
    """Class to handle Online command"""
    config: ConfigManager
    logging: Output
    localedir: str
    translate: gettext.NullTranslations
    _ = None


    def __init__(self):
        self.config = ConfigManager()
        self.logging = Output()
        self.localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", 'locale')
        self.translate = gettext.translation('messages', self.localedir,
                                fallback=True, languages=[self.config.language])
        self.translate.install()
        self._ = self.translate.gettext

#    def handle_command(self) -> None:
#        """Virtual Function"""
