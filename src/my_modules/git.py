from pathlib import Path
from subprocess import check_output


class InvalidGitDirectory(FileNotFoundError):
    """Exception raised when Git object is initiated in a non git-project directory"""


class Git:
    """A class to interact with Git repositories and retrieve Git-related information.

    This class provides methods to access Git repository information such as remote URLs
    and current branch names. It validates that operations are performed within a Git repository.
    """

    def __init__(self) -> None:
        """Initialize the Git object.

        Validates that the current directory is a Git repository by checking for the presence
        of a .git directory. Raises InvalidGitDirectory if not in a Git repository.
        """
        self._ensure_git_project()

    def _ensure_git_project(self):
        """Validate that the current directory is a Git repository.

        Checks for the presence of a .git directory in the current working directory.
        Raises InvalidGitDirectory exception if not found.

        Raises:
            InvalidGitDirectory: If the current directory is not a Git repository.
        """
        if not Path("./.git").exists():
            raise InvalidGitDirectory

    @property
    def remote_url(self) -> str:
        """Get the remote URL of the Git repository.

        Returns the URL of the 'origin' remote for the current Git repository.

        Returns:
            str: The URL of the origin remote.

        Raises:
            subprocess.CalledProcessError: If the git command fails or origin remote doesn't exist.
        """
        return check_output("git remote get-url origin".split(), text=True).strip()

    @property
    def current_branch(self) -> str:
        """Get the current branch name of the Git repository.

        Returns the name of the currently checked out branch in the Git repository.

        Returns:
            str: The name of the current branch.

        Raises:
            subprocess.CalledProcessError: If the git command fails or no branch is checked out.
        """
        return check_output("git branch --show-current".split(), text=True).strip()
