import requests
import pickle
import os
import json

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
    metadata = open(file_path + "/metadata.json", "w")
    json.dump(dates, metadata)
    metadata.close()


update_date_metadata()
