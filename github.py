from git import Repo
from git import Git
import datetime
import os


def push_to_github():
    git_ssh_identity_file = os.path.expanduser('~/.ssh/id_rsa')
    git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file
    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        repo = Repo(".")
        git = repo.git
        remote = repo.remote()
        remote.pull()

        git.add("docs")
        git.commit("-m", "update by python script " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        remote.push()

