class Nc(object):
    def __init__(self, title, ncid, link, size):
        self.title = title
        self.ncid = ncid
        self.link = link
        self.size = size

    def __str__(self):
        print('\n' + self.title + '\n' + self.ncid + '\n' + self.link + '\n' + self.size)
