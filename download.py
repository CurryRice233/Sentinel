import requests
import os
import sys


def download(nc, cookies):
    os.makedirs("download/", exist_ok=True)
    url = "https://s5phub.copernicus.eu/dhus/odata/v1/Products('" + nc.ncid + "')/$value"
    file_path = "download/" + nc.ncid + ".nc"

    r = requests.get(url, stream=True, cookies=cookies)
    # total_size = int(r.headers['Content-Length'])
    total_size = float(r.headers.get('content-length', len(r.content)))

    if os.path.exists(file_path) and os.path.getsize(file_path) < total_size:
        temp_size = os.path.getsize(file_path)
    else:
        temp_size = 0

    headers = {'Range': 'bytes=%d-%d' % (temp_size, total_size - 1)}
    r = requests.get(url, stream=True, cookies=cookies, headers=headers, timeout=10)
    if temp_size == 0:
        f = open(file_path, "wb")
    else:
        f = open(file_path, "ab")

    for chunk in r.iter_content(chunk_size=1024 * 1024):
        if chunk:
            f.seek(temp_size)
            f.truncate()
            f.write(chunk)
            f.flush()
            temp_size += len(chunk)

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
