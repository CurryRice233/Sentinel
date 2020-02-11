class Nc(object):
    def __init__(self, title, ncid, link, size, date):
        self.title = title
        self.ncid = ncid
        self.link = link
        self.size = size
        self.date = date

    def __str__(self):
        return '\n' + self.title + '\n' + self.ncid + '\n' + self.link + '\n' + self.size + '\n' + str(self.date)
