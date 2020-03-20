import os
import pickle

import requests
import socket
import time
import xml.etree.cElementTree as ET
import datetime
import json

import utils
from download import download
from nc import Nc
import read
import bot

url = 'https://s5phub.copernicus.eu/dhus/search?start=100&rows=100&q=(footprint:"Intersects(POLYGON((-29.812190777585087 26.577078786569615,69.10491090874537 26.577078786569615,69.10491090874537 71.10236152833656,-29.812190777585087 71.10236152833656,-29.812190777585087 26.577078786569615)))" ) AND ( (platformname:Sentinel-5 AND producttype:L2__NO2___))'
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
    date = entry.find('{http://www.w3.org/2005/Atom}date[@name="ingestiondate"]').text.split("T")[0]
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    nc = Nc(title, ncid, link, size, date)
    # print(str(nc))
    files.append(nc)
    total_size += utils.parse_size(size)
    count += 1

print("\n" + str(count) + " Total files size: " + utils.sizeof_fmt(total_size))

# download and read data
date = datetime.datetime.today() - datetime.timedelta(1)  # yesterday
file_path = "docs/data/" + str(date.date())
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
files_to_download = []
for file in files:
    if file.date.date() == date.date() and file.ncid not in data:
        files_to_download.append(file)
        total_size += utils.parse_size(file.size)

print("Will download " + str(len(files_to_download)) + " files with " + utils.sizeof_fmt(total_size) + " (" + str(
    date.date()) + ")")

msg = ""
i = 0
MAX_RETRIES = 5
WAIT_SECONDS = 5
try:
    for file in files_to_download:

        for j in range(MAX_RETRIES):
            try:
                is_downloaded = download(file, cookies)
                break
            except requests.exceptions.ConnectionError:
                msg += "\n[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "](" + str(
                    j) + " retry):<" + file.ncid + "> Connection Error."
            except socket.timeout:
                msg += "\n[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "](" + str(
                    j) + " retry):<" + file.ncid + "> Time out."
            time.sleep(WAIT_SECONDS)
        else:
            is_downloaded = False

        if is_downloaded:
            i += 1
            print("  (" + str(i) + "/" + str(files_to_download.__len__()) + ")")
            read.save_to_csv("download/" + file.ncid + ".nc", file_path + "/data.csv")
            os.remove("download/" + file.ncid + ".nc")
            data.update({file.ncid: {"size": file.size}})
            metadata = open(file_path + "/metadata.json", "w")
            json.dump(data, metadata)
            metadata.close()
        else:
            msg += "\n[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "](All tries failed):" + file.ncid

    msg += "\n[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] Downloaded " + str(i) + "/" + str(files_to_download.__len__()) + " files"


except Exception as e:
    msg += str(e)

bot.send_message(msg)
log = open("log.txt", "a+")
log.write("\n\n---" + date.strftime("%Y-%m-%d %H:%M:%S") + "---" + msg)
log.close()
