import requests
import pickle
import os
import json
import datetime
from nc import Nc
import xml.etree.cElementTree as ET

units = {"B": 1, "KB": 10 ** 3, "MB": 10 ** 6, "GB": 10 ** 9, "TB": 10 ** 12}


# file size string to int
def parse_size(size):
    number, unit = [string.strip() for string in size.split()]
    return int(float(number) * units[unit])


# file size int to string
def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_cookies(username, password):
    login = requests.post("https://s5phub.copernicus.eu/dhus/login",
                          data={'login_username': username, 'login_password': password})
    cookies = {'dhusAuth': login.cookies['dhusAuth'], 'dhusIntegrity': login.cookies['dhusIntegrity']}
    f = open('./cookies', 'wb')
    pickle.dump(cookies, f)
    f.close()


def update_date_metadata():
    file_path = "docs/data/"
    dates = [name for name in os.listdir(file_path) if os.path.isdir(os.path.join(file_path, name))]
    dates.sort()
    metadata = open(file_path + "/metadata.json", "w")
    json.dump(dates, metadata)
    metadata.close()


def get_search_result(date, cookies):
    date = str(date.date())
    url = 'https://s5phub.copernicus.eu/dhus/search?start=0&rows=100&q=(' \
          'footprint:"Intersects(POLYGON((-29.812190777585087 26.577078786569615,69.10491090874537 26.577078786569615,69.10491090874537 71.10236152833656,-29.812190777585087 71.10236152833656,-29.812190777585087 26.577078786569615)))" ) ' \
          'AND ( (platformname:Sentinel-5 AND producttype:L2__NO2___))' \
          'AND ( beginPosition:[' + date + 'T00:00:00.000Z TO ' + date + 'T23:59:59.999Z] ' \
                                                                         'AND endPosition:[' + date + 'T00:00:00.000Z TO ' + date + 'T23:59:59.999Z] )'

    text = requests.get(url, cookies=cookies)
    tree = ET.ElementTree(ET.fromstring(text.text))
    root = tree.getroot()
    entries = root.findall("{http://www.w3.org/2005/Atom}entry")
    return entries


def get_files_by_date(search_date, cookies):
    result = {'files': [], 'count': 0, 'total_size': 0}

    entries = get_search_result(search_date, cookies)
    for entry in entries:
        date = entry.find('{http://www.w3.org/2005/Atom}date[@name="ingestiondate"]').text.split("T")[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        if date.date() == search_date.date():
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            ncid = entry.find('{http://www.w3.org/2005/Atom}id').text
            link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
            size = entry.find('{http://www.w3.org/2005/Atom}str[@name="size"]').text

            nc = Nc(title, ncid, link, size, date)
            # print(str(nc))
            result['files'].append(nc)
            result['total_size'] += parse_size(size)
            result['count'] += 1

    return result
