from pathlib import Path
from subprocess import check_output


class Git:
    def __init__(self, remote_url: str = "", current_branch: str = "main") -> None:
        self._remote_url = remote_url
        self._current_branch = current_branch
        self._ensure_git_repo()

    def _ensure_git_repo(self):
        if not any([self._remote_url, self._current_branch, Path(".git").exists()]):
            raise EnvironmentError("Not a valid git project.")

    @property
    def remote_url(self) -> str:
        return (
            self._remote_url
            or check_output(["git", "remote", "get-url", "origin"], text=True).strip()
        )

    @property
    def current_branch(self) -> str:
        return (
            self._current_branch
            or check_output(["git", "branch", "--show-current"], text=True).strip()
        )

    @property
    def name(self) -> str:
        return self._remote_url.split("/")[-1].rstrip(".git") or Path().absolute().stem

    def __str__(self) -> str:
        return f"Git(name={self.name}, url={self.remote_url}, branch={self.current_branch})"

    def __repr__(self) -> str:
        return str(self)


if __name__ == "__main__":
    Git()
