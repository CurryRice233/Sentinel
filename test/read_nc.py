from netCDF4 import Dataset
import datetime
import pandas


my_example_nc_file = 'S5P_NRTI_L2__CO_____20191117T111514_20191117T112014_10854_01_010302_20191117T115316.nc'


def save_to_csv(file):
    nc = Dataset(file, mode='r')
    lons = nc.groups['PRODUCT'].variables['longitude'][:].flatten()
    lats = nc.groups['PRODUCT'].variables['latitude'][:][0, :, :].flatten()
    no2 = nc.groups['PRODUCT'].variables['carbonmonoxide_total_column'][0, :, :].flatten()
    time = datetime.datetime.strptime(nc.groups['PRODUCT'].variables['delta_time'].units.split("since")[1].strip(), '%Y-%m-%d %H:%M:%S')

    print(len(lons))
    print(len(lats))
    print(len(no2))
    data = pandas.DataFrame({'Longitude': lons, 'Latitude': lats, 'Data': no2})
    data.to_csv(str(time.date())+".csv", index=False)


save_to_csv(my_example_nc_file)
