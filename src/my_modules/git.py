from pathlib import Path
from subprocess import check_output


class Git:
    def __init__(self) -> None:
        self._ensure_git_repo()

    def _ensure_git_repo(self):
        if not Path(".git").exists():
            raise EnvironmentError("Not a valid git project.")

    @property
    def remote_url(self) -> str:
        return check_output(["git", "remote", "get-url", "origin"], text=True).strip()

    @property
    def current_branch(self) -> str:
        return check_output(["git", "branch", "--show-current"], text=True).strip()

    @property
    def name(self) -> str:
        return Path().absolute().stem

    def __str__(self) -> str:
        return f"Git(name={self.name}, url={self.remote_url}, branch={self.current_branch})"

    def __repr__(self) -> str:
        return str(self)


if __name__ == "__main__":
    Git()
