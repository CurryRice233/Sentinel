from git import Repo
import datetime
import subprocess


def push_to_github():
    repo = Repo(".")
    git = repo.git
    remote = repo.remote()
    remote.pull()

    git.add("docs")
    git.commit("-m", "update by python script " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    remote.push()

