import requests
import os
import sys


def download(nc, cookies):
    os.makedirs("download/", exist_ok=True)
    url = "https://s5phub.copernicus.eu/dhus/odata/v1/Products('" + nc.ncid + "')/$value"
    file_path = "download/" + nc.ncid + ".nc"

    r = requests.get(url, stream=True, cookies=cookies)
    total_size = int(r.headers['Content-Length'])

    if os.path.exists(file_path) and os.path.getsize(file_path) < total_size:
        temp_size = os.path.getsize(file_path)
    else:
        temp_size = 0

    headers = {'Range': 'bytes=%d-' % temp_size}
    r = requests.get(url, stream=True, cookies=cookies, headers=headers, timeout=15)
    if temp_size == 0:
        f = open(file_path, "wb")
    else:
        f = open(file_path, "ab")

    for chunk in r.iter_content(chunk_size=512):
        if chunk:
            temp_size += len(chunk)
            f.write(chunk)
            f.flush()

            # progress bar
            done = int(50 * temp_size / total_size)
            sys.stdout.write("\r" + nc.ncid + ".nc(" + nc.size + ")\t [%s%s] %d%%" % (
            '█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
            sys.stdout.flush()

    f.close()
    if temp_size == total_size:
        return True
    else:
        return False
