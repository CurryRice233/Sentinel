from netCDF4 import Dataset
import datetime
import pandas
import numpy

my_example_nc_file = '70ff2e67-2f91-4919-985e-e2880df493d9.nc'


def save_to_csv(file):
    nc = Dataset(file, mode='r')
    print(nc.groups['PRODUCT'].variables.keys())
    lons = nc.groups['PRODUCT'].variables['longitude'][:].flatten()
    lats = nc.groups['PRODUCT'].variables['latitude'][:][0, :, :].flatten()
    no2 = nc.groups['PRODUCT'].variables['nitrogendioxide_tropospheric_column'][0, :, :].flatten()
    time = datetime.datetime.strptime(nc.groups['PRODUCT'].variables['delta_time'].units.split("since")[1].strip(), '%Y-%m-%d %H:%M:%S')

    print(len(lons))
    print(len(lats))
    print(len(no2))
    data = pandas.DataFrame({'Longitude': lons, 'Latitude': lats, 'Data': no2})
    data['Data'].replace('', numpy.nan, inplace=True)
    data.dropna(subset=['Data'], inplace=True)
    data.to_csv(str(time.date()) + ".csv", index=False)


save_to_csv(my_example_nc_file)
