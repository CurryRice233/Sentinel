from git import Repo
from git import Git
import datetime


def push_to_github():
    git_ssh_cmd = 'ssh -i %s id_rsa'
    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        repo = Repo(".")
        remote = repo.remote()
        remote.pull()

        git = repo.git
        git.add("docs")
        git.commit("-m", "update by python script " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        remote.push()
