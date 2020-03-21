from git import Repo
import datetime


def push_to_github():
    repo = Repo(".")
    remote = repo.remote()
    remote.pull()

    git = repo.git
    git.add("docs")
    git.commit("-m", "update by python script " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    remote.push()
