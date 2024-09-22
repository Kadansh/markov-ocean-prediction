import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)



# Imports
from parcels import FieldSet, ParticleSet, JITParticle, AdvectionRK4, StatusCode
import numpy as np
import netCDF4 as nc
from datetime import timedelta
import os
from mpi4py import MPI  # Added MPI for parallel execution
import progressbar
import time  # Added to simulate progress for each rank

# MPI initialization
comm = MPI.COMM_WORLD
size = comm.Get_size()  # Total number of processors
rank = comm.Get_rank()  # Rank of this processor

# Loading grid file
uv_grd = '/indian/vickyverma/EMedCrocoC/INPUT/EMed300m_grd.nc'
ds_uv_grd = nc.Dataset(uv_grd, 'r')
grd_mask = ds_uv_grd['mask_psi'][:]
lon_mask = ds_uv_grd['lon_psi'][:]
lat_mask = ds_uv_grd['lat_psi'][:]

# Loading data for u and v
uv_data_zero = '/southern/kadanshinyuk/markov-pushforward/300m/data/rvort_winter/z_EMed300m_his.00000.nc'
ds_uv_data = nc.Dataset(uv_data_zero, 'r')

filenames = {'U': {'lon': uv_grd, 'lat': uv_grd, 'data': uv_data_zero},
             'V': {'lon': uv_grd, 'lat': uv_grd, 'data': uv_data_zero}}

variables = {'U': 'u', 'V': 'v'}
dimensions = {'U': {'lon': 'lon_psi', 'lat': 'lat_psi', 'time': 'time'},
              'V': {'lon': 'lon_psi', 'lat': 'lat_psi', 'time': 'time'}}

indices = {'U': {'lon': range(1599), 'lat': range(2173)},
           'V': {'lon': range(1599), 'lat': range(2173)}}

# Main change from regular version is here - allow_time_extrapolation is set to True and we are cutting the data to chunks.
fieldset = FieldSet.from_nemo(filenames, variables, dimensions, indices, allow_time_extrapolation=True, chunksize='auto') #384 / 'auto'

# Create particles
grd_mask = ds_uv_grd['mask_psi'][:]
lon_mask = ds_uv_grd['lon_psi'][:]
lat_mask = ds_uv_grd['lat_psi'][:]
land_mask = (grd_mask == 1)

lon_water = np.where(land_mask, lon_mask, np.nan)
lat_water = np.where(land_mask, lat_mask, np.nan)

cut_n = 10
cut_lon_water = lon_water[::cut_n, ::cut_n]
cut_lat_water = lat_water[::cut_n, ::cut_n]

[lons, lats] = [cut_lon_water, cut_lat_water]

# Calculate cycles
nstart = 0
# nend = 1252
nend = 400
ncycle = nend - nstart + 3

# Setting the ParticleSet (JITParticle works with MPI)
# Filter out NaN values from lons and lats, happens because of the chunking
valid_mask = ~np.isnan(cut_lon_water) & ~np.isnan(cut_lat_water)

# Apply the mask to filter out invalid lon/lat pairs
valid_lons = cut_lon_water[valid_mask]
valid_lats = cut_lat_water[valid_mask]

print(valid_lons.shape, valid_lats.shape)

# Use valid_lons and valid_lats in ParticleSet
pset = ParticleSet(fieldset, JITParticle, lon=valid_lons, lat=valid_lats)

# Execute with MPI support
output_zarr_name = '../data/11092024_test_400.zarr'
output_file = pset.ParticleFile(name=output_zarr_name, outputdt=timedelta(hours=2))

# Kernel for out-of-bounds particles
def CheckOutOfBounds(particle, fieldset, time):
    if particle.state == StatusCode.ErrorOutOfBounds:
        particle.delete()

# Execute the particle simulation
pset.execute([AdvectionRK4, CheckOutOfBounds], runtime=timedelta(hours=ncycle),
                dt=timedelta(seconds=30), output_file=output_file)
