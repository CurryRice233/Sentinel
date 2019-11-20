from netCDF4 import Dataset
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


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
print(fh.groups['PRODUCT'].variables['time'])

lons = fh.groups['PRODUCT'].variables['longitude'][:][0, :, :]
lats = fh.groups['PRODUCT'].variables['latitude'][:][0, :, :]
no2 = fh.groups['PRODUCT'].variables['carbonmonoxide_total_column'][0, :, :]

#no2[fh.groups['PRODUCT'].variables['qa_value'][0,:,:]<0.75]=np.nan
#no2_units = fh.groups['PRODUCT'].variables['carbonmonoxide_total_column'].units

print(lons.shape)
print(lats.shape)
print(no2.shape)

print(lons)
print(lats)
print(no2)


fig = plt.figure(figsize=(20, 20))
m=Basemap(projection='cyl',llcrnrlat=30,llcrnrlon=-14,urcrnrlat=75,urcrnrlon=70)
#m=Basemap(projection='cyl')
m.drawcoastlines(color='blue')
m.drawcountries(color='blue')
x, y = m(lons, lats)
cf = m.contourf(x, y, np.squeeze(no2), levels=np.linspace(np.min(no2),np.max(no2),400))
print(np.min(no2))
print(np.max(no2))
cbar = m.colorbar(cf, location='right',size='3%' ,pad='2%')
plt.savefig('test.png')
plt.show()
