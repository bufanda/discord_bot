"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: Get files from git via HTTPS
"""
import requests
import gitlab
import shutil
import tempfile

class ScumGitConnector():
    repository_url: str
    repository_password: str
    repository_username: str
    repository_file: str
    temporary_file: str

    def __init__(self, url: str, username: str, password: str, branch: str = None, project: str = None):
        self.repository_password = password
        self.repository_username = username
        self.repository_url = url
        self.temporary_file = tempfile.NamedTemporaryFile()

    def __del__(self):
        self.clean_up()

    def get_file(self, filename) -> tempfile.NamedTemporaryFile:
        self.repository_file = filename
        with requests.get(self.repository_url, stream=True) as r:
            with open(self.temporary_file, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        return self.temporary_file

    def clean_up(self):
        del self.temporary_file

class GitLabConnector(ScumGitConnector):
    branch_name: str
    project_name: str

    def set_branch(self, branch: str):
        self.branch_name = branch

    def set_project(self, project: str):
        self.project_name = project

    def get_file(self, filename) -> tempfile.NamedTemporaryFile:
        self.repository_file = filename
        try:
            gl = gitlab.Gitlab(self.repository_url, http_password=self.repository_password, \
                               http_username=self.repository_username)
            pl = gl.projects.list() # gl.projects.list(search=self.project_name)
            print(pl)
            print(gl.api_url)
            print(gl.namespaces.list())
            print(gl.groups.list())
            project = None
            for p in pl:
                if p.name == self.project_name:
                    project = p
                    break
            if project is not None:
                project.files.raw(file_path=self.repository_file, ref=self.branch_name, streamed=True, action=self.temporary_file.write)
        except Exception as e:
            print("Error:", e)
        finally:
            return self.temporary_file

    def __init__(self, url: str, username: str, password: str, branch: str, project: str):
        super().__init__(url, username, password)
        self.set_branch(branch)
        self.set_project(project)
