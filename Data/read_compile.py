import netCDF4

filepath = 'ME4OH_EN411_OFAM3/data/en4.1.1/1993-2014/ofam3-jra55.all.EN.4.1.1.f.profiles.g10.199301.update.extra.anom.199301_201412.nc'
file2read = netCDF4.Dataset(filepath,'r')
print(file2read.variables)