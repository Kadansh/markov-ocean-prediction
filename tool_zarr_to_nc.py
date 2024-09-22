import xarray as xr

# Path to the Zarr file
filename = "prt_masked_data_cut10"
zarr_file_path = f'../data/{filename}.zarr'

# Open the Zarr file using xarray
ds = xr.open_zarr(zarr_file_path)

# Path to the output NetCDF file
nc_file_path = f'../data/{filename}.nc'

print("Starting process...")

# Save the dataset to a NetCDF file
ds.to_netcdf(nc_file_path)

print("Done!")
