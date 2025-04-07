"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: Get files from git via HTTPS
"""
import gitea

class ScumGitea():
    """ TBD """
    repository_url: str
    repo: str
    owner: str
    repository_file: str
    private_token: str
    base_url: str
    branch_name: str = "master"

    def __init__(self, url: str, private_token: str,
                 branch: str = None):
        """ TBD """
        self.private_token = private_token
        _url = url.split("/")
        self.repository_url = url
        self.repo = _url[-1]
        self.owner = _url[-2]
        self.base_url = _url[0] + "//" + _url[-3]

        if branch:
            self.branch_name = branch

    def __del__(self):
        self.clean_up()

    def get_file(self, filename) -> object:
        """ get a file from git """
        result = False
        file_content = None
        try:
            session = gitea.Gitea(gitea_url=self.repository_url,
                                  token_text=self.private_token, verify=False)

            file_content = session.requests_get(f"/repos/{self.owner}/{self.repo}/media/{filename}")
        except gitea.NotFoundException as e:
            print("Error:", e)
        finally:
            if file_content:
                result = file_content.content
        # pylint: enable=broad-exception-caught

        return result

    def clean_up(self):
        """ clean up memory """
