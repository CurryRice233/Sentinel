def create_download_table(cursor):
    cursor.execute(""" CREATE TABLE IF NOT EXISTS download (
                        ncid text PRIMARY KEY NOT NULL,
                        title text,
                        link text,
                        size integer,
                        date timestamp
                        ) """)


def exist_nc(cursor, ncid):
    rs = cursor.execute("SELECT * FROM download WHERE ncid = ?", [ncid])
    return not len(rs.fetchall()) == 0


def insert_nc(cursor, file):
    cursor.execute("INSERT INTO download (ncid,title,link,size,date) VALUES (?,?,?,?,?) ", [file.ncid, file.title,
                                                                                            file.link, file.size,
                                                                                            file.date])
