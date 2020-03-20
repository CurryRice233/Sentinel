from netCDF4 import Dataset
import pandas
import numpy
import datetime


def save_to_csv(file, save_path):
    nc = Dataset(file, mode='r')
    # print(nc.groups['PRODUCT'].variables.keys())
    lons = nc.groups['PRODUCT'].variables['longitude'][:].flatten()
    lats = nc.groups['PRODUCT'].variables['latitude'][:][0, :, :].flatten()
    no2 = nc.groups['PRODUCT'].variables['nitrogendioxide_tropospheric_column'][0, :, :].flatten()
    time = datetime.datetime.strptime(nc.groups['PRODUCT'].variables['delta_time'].units.split("since")[1].strip(),
                                      '%Y-%m-%d %H:%M:%S')
    # print(str(len(lons))+" / "+str(len(lats))+" / "+str(len(no2)))
    data = pandas.DataFrame({'Longitude': lons, 'Latitude': lats, 'Data': no2})
    data['Data'].replace('', numpy.nan, inplace=True)
    data.dropna(subset=['Data'], inplace=True)
    data["Data"] = data["Data"] * 1000000
    data = data[data.Data > 50]
    data.to_csv(save_path, index=False, mode='a', header=False)
    nc.close()
