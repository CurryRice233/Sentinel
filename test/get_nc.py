import requests
import pickle
import os
import xml.etree.cElementTree as ET
from nc import Nc


units = {"B": 1, "KB": 10 ** 3, "MB": 10 ** 6, "GB": 10 ** 9, "TB": 10 ** 12}


def parseSize(size):
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


def downloadNC(ncid, cookies):
    r = requests.get("https://s5phub.copernicus.eu/dhus/odata/v1/Products('" + ncid + "')/$value", stream=True, cookies=cookies)
    f = open(ncid + ".nc", "wb")
    for chunk in r.iter_content(chunk_size=512):
        if chunk:
            f.write(chunk)
    print('downloaded '+ncid)


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
for entry in entrys:
    title = '\n' + entry.find('{http://www.w3.org/2005/Atom}title').text
    ncid = entry.find('{http://www.w3.org/2005/Atom}id').text
    link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
    size = entry.find('{http://www.w3.org/2005/Atom}str[@name="size"]').text
    total_size += parseSize(size)
    count += 1

print("\n" + str(count) + " Files Total size: " + sizeof_fmt(total_size))

downloadNC("70ff2e67-2f91-4919-985e-e2880df493d9", cookies)
