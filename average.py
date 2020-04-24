import pandas as pd
import datetime


def calculate_average(date, zone):
    data = pd.read_csv("docs/data/" + date.strftime("%Y-%m-%d") + "/data.csv", names=["lat", "lon", "data"])
    data = data[(zone.p1.lon >= data.lon) & (data.lon >= zone.p2.lon)
                & (zone.p1.lat >= data.lat) & (data.lat >= zone.p2.lat)]
    return data["data"].mean()


def in_zone(lon, lat, zone):
    if zone.p1.lon >= lon >= zone.p2.lon and zone.p1.lat >= lat >= zone.p2.lat:
        return True
    return False


class Zone:
    def __init__(self, p1, p2):
        self.p1 = Point(max(p1.lon, p2.lon), max(p1.lat, p2.lat))
        self.p2 = Point(min(p1.lon, p2.lon), min(p1.lat, p2.lat))


class Point:
    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat


madrid = Zone(Point(40.716939, -3.199185), Point(40.100123, -4.082764))
date = datetime.datetime.strptime("2020-03-23", '%Y-%m-%d')
result = {}
for i in range(7):
    result[str(date.strftime("%Y-%m-%d"))] = calculate_average(date, madrid)
    date = date + datetime.timedelta(1)


print(result)