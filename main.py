import os

import requests
import socket
import time
import pickle
import datetime
import json

import utils
from download import download
from nc import Nc
import read
import bot
import github

username = 's5pguest'
password = 's5pguest'

utils.get_cookies(username, password)
cookies = pickle.load(open("./cookies", 'rb'))

# date = datetime.datetime.today() - datetime.timedelta(1)  # yesterday
date = datetime.datetime(2020, 3, 30)
result = utils.get_files_by_date(date, cookies)

print("\n" + str(date.date()) + ": " + str(result['files'].__len__()) + " files with total size: " + utils.sizeof_fmt(
    result['total_size']))

# download and read data
file_path = "docs/data/" + str(date.date())
os.makedirs(file_path, exist_ok=True)
utils.update_date_metadata()
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
for file in result['files']:
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

    msg += "\n[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] Downloaded " + str(i) + "/" + str(
        files_to_download.__len__()) + " files"


except Exception as e:
    msg += str(e)

try:
    github.push_to_github()
except Exception as e:
    msg += str(e)

if not bot.send_message(msg):
    msg = "\n[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]: Telegram bot can't send message." + msg

log = open("log.txt", "a+")
log.write("\n\n---" + date.strftime("%Y-%m-%d %H:%M:%S") + "---" + msg)
log.close()
