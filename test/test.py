from netCDF4 import Dataset
import netCDF4
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from os import listdir
import glob

print(listdir("./"))
print([f for f in glob.glob("*.nc")])
'''
my_example_nc_file = 'S5P_NRTI_L2__CO_____20191117T111514_20191117T112014_10854_01_010302_20191117T115316.nc'
fh = Dataset(my_example_nc_file, mode='r')
print(fh.variables.keys())


def walktree(top):
    values = top.groups.values()
    yield values
    for value in top.groups.values():
        for children in walktree(value):
            yield children


print(fh)

print(fh.groups)
print(fh.groups['PRODUCT'])
print(fh.groups['PRODUCT'].variables.keys())
print("time:\n"+str(fh.groups['PRODUCT'].variables['time']))
print("delta_time:\n"+str(fh.groups['PRODUCT'].variables['delta_time']))
print("time_utc:\n"+str(fh.groups['PRODUCT'].variables['time_utc']))

lons = fh.groups['PRODUCT'].variables['longitude'][:][0, :, :]
lats = fh.groups['PRODUCT'].variables['latitude'][:][0, :, :]
no2 = fh.groups['PRODUCT'].variables['carbonmonoxide_total_column'][0, :, :]
time = fh.groups['PRODUCT'].variables['delta_time']
time_utc = fh.groups['PRODUCT'].variables['time_utc'][:]
#no2[fh.groups['PRODUCT'].variables['qa_value'][0,:,:]<0.75]=np.nan
#no2_units = fh.groups['PRODUCT'].variables['carbonmonoxide_total_column'].units

print(lons.shape)
print(lats.shape)
print(no2.shape)
print(time_utc)
print(netCDF4.num2date(time[:], time.units))
print(time.units.split("since")[1].strip())
'''


'''
fig = plt.figure(figsize=(20, 20))
m=Basemap(projection='cyl',llcrnrlat=30,llcrnrlon=-14,urcrnrlat=75,urcrnrlon=70)
#m=Basemap(projection='cyl')
m.drawcoastlines(color='blue')
m.drawcountries(color='blue')
x, y = m(lons, lats)
cf = m.contourf(x, y, no2, levels=np.linspace(np.min(no2),np.max(no2),400))
print(np.min(no2))
print(np.max(no2))
cbar = m.colorbar(cf, location='right',size='3%' ,pad='2%')
plt.savefig('test.png')
plt.show()
'''

