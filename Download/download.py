import requests
import pickle
import os
import xml.etree.cElementTree as ET
import sqlite3
import glob
from netCDF4 import Dataset
import datetime
import pandas
import numpy


class Nc(object):
    def __init__(self, title, ncid, link, size, date):
        self.title = title
        self.ncid = ncid
        self.link = link
        self.size = size
        self.date = date

    def __str__(self):
        return '\n' + self.title + '\n' + self.ncid + '\n' + self.link + '\n' + self.size + '\n' + str(self.date)


units = {"B": 1, "KB": 10 ** 3, "MB": 10 ** 6, "GB": 10 ** 9, "TB": 10 ** 12}


def parse_size(size):
    number, unit = [string.strip() for string in size.split()]
    return int(float(number) * units[unit])


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_cookies():
    login = requests.post("https://s5phub.copernicus.eu/dhus/login",
                          data={'login_username': 's5pguest', 'login_password': 's5pguest'})
    cookies = {'dhusAuth': login.cookies['dhusAuth'], 'dhusIntegrity': login.cookies['dhusIntegrity']}
    f = open('./cookies', 'wb')
    pickle.dump(cookies, f)
    f.close()


def download_nc(nc, cookies):
    r = requests.get("https://s5phub.copernicus.eu/dhus/odata/v1/Products('" + nc.ncid + "')/$value", stream=True,
                     cookies=cookies)
    os.makedirs("cache/", exist_ok=True)
    f = open("cache/" + nc.ncid + ".nc", "wb")
    for chunk in r.iter_content(chunk_size=512):
        if chunk:
            f.write(chunk)
    print('downloaded ' + nc.ncid)


url = 'https://s5phub.copernicus.eu/dhus/search?start=0&rows=50&q=(footprint:"Intersects(POLYGON((-29.812190777585087 26.577078786569615,69.10491090874537 26.577078786569615,69.10491090874537 71.10236152833656,-29.812190777585087 71.10236152833656,-29.812190777585087 26.577078786569615)))" ) AND ( (platformname:Sentinel-5 AND producttype:L2__NO2___))'

if not os.path.exists('./cookies'):
    get_cookies()
cookies = pickle.load(open("./cookies", 'rb'))
text = requests.get(url, cookies=cookies)

if text.status_code == 401:
    get_cookies()
    cookies = pickle.load(open("./cookies", 'rb'))
    text = requests.get(url, cookies=cookies)

tree = ET.ElementTree(ET.fromstring(text.text))
root = tree.getroot()

entrys = root.findall("{http://www.w3.org/2005/Atom}entry")

total_size = 0
count = 0
files = []
for entry in entrys:
    title = entry.find('{http://www.w3.org/2005/Atom}title').text
    ncid = entry.find('{http://www.w3.org/2005/Atom}id').text
    link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
    size = entry.find('{http://www.w3.org/2005/Atom}str[@name="size"]').text
    date = datetime.datetime.strptime(entry.find('{http://www.w3.org/2005/Atom}date[@name="ingestiondate"]').text,
                                      '%Y-%m-%dT%H:%M:%S.%fZ')
    nc = Nc(title, ncid, link, size, date)
    print(str(nc))
    files.append(nc)
    total_size += parse_size(size)
    count += 1

print("\n" + str(count) + " Files Total size: " + sizeof_fmt(total_size))

# download_nc("70ff2e67-2f91-4919-985e-e2880df493d9", cookies)

conn = sqlite3.connect('./download.db')
cursor = conn.cursor()
cursor.execute(""" CREATE TABLE IF NOT EXISTS download (
                        ncid text PRIMARY KEY NOT NULL,
                        title text,
                        link text,
                        size integer,
                        date timestamp
                        ) """)

for file in files:
    rs = cursor.execute("SELECT * FROM download WHERE ncid = ?", [file.ncid])
    if len(rs.fetchall()) == 0 and file.date.date() == datetime.datetime.today().date():
        download_nc(file, cookies)
        cursor.execute("INSERT INTO download (ncid,title,link,size,date) VALUES (?,?,?,?,?) ", [file.ncid, file.title,
                                                                                                file.link, file.size,
                                                                                                file.date])

print(cursor.execute("SELECT * FROM download").fetchall())


def save_to_csv(file):
    nc = Dataset(file, mode='r')
    print(nc.groups['PRODUCT'].variables.keys())
    lons = nc.groups['PRODUCT'].variables['longitude'][:].flatten()
    lats = nc.groups['PRODUCT'].variables['latitude'][:][0, :, :].flatten()
    no2 = nc.groups['PRODUCT'].variables['nitrogendioxide_tropospheric_column'][0, :, :].flatten()
    time = datetime.datetime.strptime(nc.groups['PRODUCT'].variables['delta_time'].units.split("since")[1].strip(),
                                      '%Y-%m-%d %H:%M:%S')

    print(len(lons))
    print(len(lats))
    print(len(no2))
    data = pandas.DataFrame({'Longitude': lons, 'Latitude': lats, 'Data': no2})
    data['Data'].replace('', numpy.nan, inplace=True)
    data.dropna(subset=['Data'], inplace=True)
    data.to_csv(str(time.date()) + ".csv", index=False, mode='a')


ncs = [f for f in glob.glob("cache/*.nc")]
print(ncs)
for nc in ncs:
    save_to_csv(nc)
