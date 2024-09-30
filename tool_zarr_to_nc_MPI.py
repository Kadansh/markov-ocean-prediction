### This version is intended to convert zarr files created with MPI

import xarray as xr

# Base filename
filename = "testing-4"
zarr_file_pattern = f'/southern/kadanshinyuk/parcels/data/290924-19/{filename}.zarr/proc*.zarr'

# Open all Zarr files using xarray
ds = xr.open_mfdataset(zarr_file_pattern, engine='zarr', parallel=True, concat_dim='trajectory', combine='nested')

# Path to the output NetCDF file
nc_file_path = f'../data/{filename}.nc'

print("Starting process...")

# Save the combined dataset to a NetCDF file
ds.to_netcdf(nc_file_path)

print("Done!")
