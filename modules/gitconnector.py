"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: Get files from git via HTTPS
"""
import shutil
import tempfile
import requests
import gitlab

class ScumGitConnector():
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

class GitLabConnector(ScumGitConnector):
    """ TBD """
    private_token: str

    def set_branch(self, branch: str):
        """ TBD """
        self.branch_name = branch

    def set_project(self, project: str):
        """" TBD """
        self.project_name = project

    def get_file(self, filename):
        """ TBD """
        retval = None
        self.repository_file = filename
        file_content = None
        try:
            gl = gitlab.Gitlab(self.repository_url, private_token=self.private_token)

            pl = gl.projects.list(search=self.project_name)

            project = None
            for p in pl:
                if p.name == self.project_name:
                    project = p
                    break
            if project is not None:
                # file_list = project.repository_tree()
                file_content = project.files.get(file_path=self.repository_file,
                                                ref=self.branch_name)
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print("Error:", e)
        finally:
            if file_content:
                retval = file_content.decode().decode('UTF-8')
        # pylint: enable=broad-exception-caught
        return retval

    def __init__(self, url: str, private_token: str, branch: str,
                 project: str, username: str = None, password: str = None):
        """ TBD """
        super().__init__(url, username, password)
        self.private_token = private_token
        self.set_branch(branch)
        self.set_project(project)
