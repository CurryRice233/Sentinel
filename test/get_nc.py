import requests
import xml.etree.cElementTree as ET

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


url = 'https://s5phub.copernicus.eu/dhus/search?q=(footprint:"Intersects(POLYGON((-29.812190777585087 26.577078786569615,69.10491090874537 26.577078786569615,69.10491090874537 71.10236152833656,-29.812190777585087 71.10236152833656,-29.812190777585087 26.577078786569615)))" ) AND ( (platformname:Sentinel-5 AND producttype:L2__NO2___))'
cookies = {'dhusAuth': '13907c0568f18567a221414d76456f78', 'dhusIntegrity': 'df611facece3196043f94bf0469cc851dafadf38'}
#print(requests.get(url, cookies=cookies).text)

#tree = ET.ElementTree(file='search2.xml')
text = requests.get(url, cookies=cookies)
text.raw.decode_content = True
tree = ET.fromstring(text.text)
root = tree.getroot()

'''
for child in root:
     print('child-tag是：',child.tag,',child.attrib：',child.attrib,',child.text：',child.text)
     for sub in child:
          print('sub-tag是：',sub.tag,',sub.attrib：',sub.attrib,',sub.text：',sub.text)
'''
entrys = root.findall("{http://www.w3.org/2005/Atom}entry")

total_size = 0
for entry in entrys:
    print('\n' + entry.find('{http://www.w3.org/2005/Atom}title').text)
    print(entry.find('{http://www.w3.org/2005/Atom}id').text)
    print(entry.find('{http://www.w3.org/2005/Atom}link').attrib['href'])
    size = entry.find('{http://www.w3.org/2005/Atom}str[@name="size"]').text
    print(size)
    total_size += parseSize(size)

print("\nTotal size: " + sizeof_fmt(total_size))
