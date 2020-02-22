import os
import pickle
import requests
import xml.etree.cElementTree as ET
import sqlite3
import glob
import datetime
import json

import utils
from download import download
from nc import Nc
import dao
import read

url = 'https://s5phub.copernicus.eu/dhus/search?start=0&rows=50&q=(footprint:"Intersects(POLYGON((-29.812190777585087 26.577078786569615,69.10491090874537 26.577078786569615,69.10491090874537 71.10236152833656,-29.812190777585087 71.10236152833656,-29.812190777585087 26.577078786569615)))" ) AND ( (platformname:Sentinel-5 AND producttype:L2__NO2___))'
username = 's5pguest'
password = 's5pguest'

# get search list with cookies
if not os.path.exists('./cookies'):
    utils.get_cookies(username, password)
cookies = pickle.load(open("./cookies", 'rb'))
text = requests.get(url, cookies=cookies)

if text.status_code == 401:
    utils.get_cookies(username, password)
    cookies = pickle.load(open("./cookies", 'rb'))
    text = requests.get(url, cookies=cookies)

# text to class nc
tree = ET.ElementTree(ET.fromstring(text.text))
root = tree.getroot()
entries = root.findall("{http://www.w3.org/2005/Atom}entry")

total_size = 0
count = 0
files = []
for entry in entries:
    title = entry.find('{http://www.w3.org/2005/Atom}title').text
    ncid = entry.find('{http://www.w3.org/2005/Atom}id').text
    link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
    size = entry.find('{http://www.w3.org/2005/Atom}str[@name="size"]').text
    date = datetime.datetime.strptime(entry.find('{http://www.w3.org/2005/Atom}date[@name="ingestiondate"]').text,
                                      '%Y-%m-%dT%H:%M:%S.%fZ')
    nc = Nc(title, ncid, link, size, date)
    # print(str(nc))
    files.append(nc)
    total_size += utils.parse_size(size)
    count += 1

print("\n" + str(count) + " Total files size: " + utils.sizeof_fmt(total_size))

# download and read data
date = datetime.datetime.today() - datetime.timedelta(0)
file_path = "display/data/" + str(date.date())
os.makedirs(file_path, exist_ok=True)
if os.path.exists(file_path + "/metadata.json"):
    with open(file_path + "/metadata.json") as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            data = {}
else:
    data = {}

total_size = 0
count = 0
for file in files:
    if file.date.date() == date.date() and file.ncid not in data:
        total_size += utils.parse_size(file.size)
        count += 1

print("Will download " + str(count) + " files with " + utils.sizeof_fmt(total_size))

metadata = open(file_path + "/metadata.json", "w")
for file in files:
    if file.date.date() == date.date() and file.ncid not in data:
        if download(file, cookies):
            read.save_to_csv("download/" + file.ncid + ".nc", file_path + "/" + file.ncid + ".csv")
            os.remove("download/" + file.ncid + ".nc")
            data.update({file.ncid: {"size": file.size}})
            json.dump(data, metadata)
            break

metadata.close()

'''# download nc file
conn = sqlite3.connect('./download.db')
dao.create_download_table(conn)

total_size = 0
count = 0
for file in files:
    if not dao.exist_nc(conn, file.ncid) and file.date.date() == datetime.datetime.today() - datetime.timedelta(day=1):
        total_size += utils.parse_size(file.size)
        count += 1
print("Will download " + str(count) + " files with " + utils.sizeof_fmt(total_size))
for file in files:
    if not dao.exist_nc(conn, file.ncid) and file.date.date() == datetime.datetime.today() - datetime.timedelta(day=1):
        print("Start to download " + file.ncid + "(" + file.size + ")")
        if download(file, cookies):
            dao.insert_nc(conn, file)
            print("\t" + file.ncid + "(" + file.size + ") Downloaded!")
            break
conn.close()

# read all nc files in directory download
ncs = [f for f in glob.glob("download/*.nc")]
for nc in ncs:
    read.save_to_csv(nc)
    os.remove(nc)'''
