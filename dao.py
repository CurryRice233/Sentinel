import sqlite3
import nc


def create_download_table(conn):
    cursor = conn.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS download (
                        ncid text PRIMARY KEY NOT NULL,
                        title text,
                        link text,
                        size integer,
                        date timestamp
                        ) """)


def exist_nc(conn, ncid):
    cursor = conn.cursor()
    rs = cursor.execute("SELECT * FROM download WHERE ncid = ?", [ncid])
    return not len(rs.fetchall()) == 0


def insert_nc(conn, file):
    conn.execute("INSERT INTO download (ncid,title,link,size,date) VALUES (?,?,?,?,?) ",
                 (file.ncid, file.title, file.link, file.size, file.date))
    conn.commit()
