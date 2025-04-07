"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: Get files from git via HTTPS
"""
import shutil
import tempfile
import requests

class ScumGitHttp():
    """ TBD """
    repository_url: str
    repository_password: str
    repository_username: str
    repository_file: str
    temporary_file: tempfile._TemporaryFileWrapper
    branch_name: str = None
    project_name: str = None

    def __init__(self, url: str, username: str, password: str,
                 branch: str = None, project: str = None):
        """ TBD """
        self.repository_password = password
        self.repository_username = username
        self.repository_url = url
        self.temporary_file = tempfile.NamedTemporaryFile()
        if branch:
            self.branch_name = branch
        if project:
            self.project_name = project

    def __del__(self):
        self.clean_up()

    def get_file(self, filename) -> tempfile.NamedTemporaryFile:
        """ get a file from git """
        self.repository_file = filename
        with requests.get(self.repository_url, stream=True, timeout=15) as r:
            with open(self.temporary_file, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        return self.temporary_file

    def clean_up(self):
        """ clean up memory """
        del self.temporary_file
