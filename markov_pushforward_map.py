# Imports

import sys
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import cmocean
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from datetime import datetime as dt, timedelta as td # Used for the date and time conversion to datenum

sys.path.insert(0, '../')
from pygtm.physical import physical_space
from pygtm.matrix import matrix_space
# from pygtm.dataset import trajectory # This is the original version of dateset with no oversampling
from pygtm.dataset2 import trajectory as trajectory2 # This is the oversampeling version of dataset 


# Functions
# Convert a stripped date to a datenum using datetime as dt
def datenum(stripped_date):
    days = 365 + d.toordinal()
    hours = (stripped_date - dt.fromordinal(d.toordinal())).total_seconds()/(24*60*60)
    return days + hours

d = dt.strptime('29/01/2018 01:00','%d/%m/%Y %H:%M')
start_time = datenum(d)

# Print for example
# print(start_time)


# Reverse function for your comfort and validation, using datetime as dt and timedelta as td
def numdate(num):
    days = num - 365
    whole_days = int(days)
    fractional_days = days - whole_days
    date = dt.fromordinal(whole_days)
    time_delta = td(seconds=fractional_days * 24 * 60 * 60)
    return date + time_delta

# Print for example
num = 737088.0416666666
reveresed_date = numdate(num)
# print(reveresed_date)


# Data load

# Loading the file and reading the dataset for the particle locations
# Med_particle = '../Data/EMed300m_his_prt_data_bc_winter.nc'
Med_particle = '../Data/prt_masked_data_cut10.nc'

# Creating a dataset
ds_Med_particle = nc.Dataset(Med_particle)

# Reading and naming the variables 
lon_par = ds_Med_particle['lon'][:]
lat_par = ds_Med_particle['lat'][:]
id_par = ds_Med_particle['trajectory'][:] # Acts as an ID as the data matches - if something changes with this field it needs to be reevaluated
time_par = ds_Med_particle['time'][:]

# For the time list - we will create a list starting from 0 and raising by 2/24 at each step, with a length of 418. 
# Starting with the start time defined above

files_n = 203
#### 629

time_jump = (2/24) 
time_list = np.arange(0, files_n) * time_jump + start_time

# Print the following to see the list created
# print(time_list)

# Create empty lists to store data
d_id = []
x = []
y = []
t = []


# Loop through each particle - through the 10,000
for i in range(time_par[:, 0].size):
    # Append trajectory ID
    result = np.full(files_n, id_par[i])
    d_id.append(result.tolist())
    
    # Append longitude
    x.append(lon_par[i].tolist())
    
    # Append latitude
    y.append(lat_par[i].tolist())
    
    # Append corresponding times (using the same list for all particles)
    t.append(time_list)

# Concatenate lists to create arrays
d_id = np.concatenate(d_id)
x = np.concatenate(x)
y = np.concatenate(y)
t = np.concatenate(t) # Acts as an ID as the data matches - if something changes with this field this usage needs to be reevaluated

# Print sizes for debugging, they should all be the same size
print(d_id.size, x.size, y.size, t.size)


# Parameters

T = 1  # transition time [days] 
spatial_dis = 60
# changes area of view and calculation, currently set to 
lon = [31, 37] 
lat = [31, 37]

# create the grid and bins
d = physical_space(lon, lat, spatial_dis)

# creates segments ready to plot with add_collection()
data = trajectory2(x,y,t,d_id)
data.create_segments(T)

# create matrix object
tm = matrix_space(d)
tm.fill_transition_matrix(data)

# Choose location
x0 = 32.9 # initial location  lon
y0 = 32.9 # initial location   lats

el_id = d.find_element(x0, y0) #find matching bin for that initial location, getting "bin i"
print(el_id)

# setting the initial density (this always sum to 1)
density = np.zeros(len(d.bins))
density[el_id] = 1
density /= np.sum(density) # if there is more than 1 initial bin this normalize the distribution
# print(density.size)

# Plot

# simple function to fix the axis and make plot prettier
def geo_map(ax):
    # ticks
    ax.set_xticks([31,32,33,34,35,36,37], crs=ccrs.PlateCarree())
    ax.set_yticks([31,32,33,34,35,36,37], crs=ccrs.PlateCarree())
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.tick_params(axis='x', labelsize=7) 
    ax.tick_params(axis='y', labelsize=7)  


    # add land and coastline
    ax.add_feature(cfeature.LAND, facecolor='silver', zorder=1)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.25, zorder=1)


# Create frames

# We will need to import os for this
import os

# Create the output directory if it does not exist
output_dir = f'../Images/pushforward_anim_play/{el_id}'
os.makedirs(output_dir, exist_ok=True)

for i in range(1, 55): # why 35? it excludes it in the range.
    duration = i
    evolved_density = tm.push_forward(density, int(duration / T))
    
    fig = plt.figure(figsize=(4, 3), dpi=300)


    # density heatmap
    ax1 = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(), aspect='equal')
    # p1 = ax1.pcolormesh(d.vx, d.vy, d.vector_to_matrix(evolved_density), vmin=0, vmax=0.06, cmap=cmocean.cm.amp, transform=ccrs.PlateCarree())
    p1 = ax1.pcolormesh(d.vx, d.vy, d.vector_to_matrix(evolved_density), vmin=0, vmax=0.06, cmap="ocean_r", transform=ccrs.PlateCarree())
    # p1 = ax1.pcolormesh(d.vx, d.vy, percent_density, vmin=0, vmax=10, cmap="Spectral_r", transform=ccrs.PlateCarree())


    # ax1.scatter(np.array(lon_par[:,0]), np.array(lat_par[:,0]), s=0.1, color='grey', alpha=0.005 , transform=ccrs.PlateCarree())
    ax1.set_extent([31, 37, 31, 37], crs=ccrs.PlateCarree())


    # mark the x0,y0 location
    ax1.scatter(x0, y0, color='b', marker='+',linewidths=0.5, transform=ccrs.PlateCarree())

    # colorbar
    cb = fig.colorbar(p1)

    # tick positions and formatting
    ticks = cb.get_ticks()
    ticks = ticks * 100 # move to percentage

    cb.ax.set_yticklabels(['{:.2f}'.format(t) for t in ticks], fontsize=7)

    #     ticks = cb.get_ticks()
    #     cb.ax.set_yticklabels(['{:.4f}'.format(t) for t in ticks], fontsize=7)
    cb.ax.tick_params(which='major', length=3, width=0.5, pad=0.05)

    # label
    cb.set_label('Probabilities after %d days [%%]' % (duration), size=7, labelpad=2)

    # add x,y ticks and land-sea
    geo_map(ax1)

    
    #Save file
    output_file = os.path.join(output_dir, 'density_pushforward_%02d.png' % i)
    #     print('Created file:', output_file)
    plt.savefig(output_file, dpi=300)
    plt.close()  
print("Done")


#Animate GIF and MP4

# We will need to import imageio for this to create a gif - you can use other measure you know of to animate if you'd like
import imageio.v2 as imageio

# Directory containing PNG files - output_dir

# Get a list of PNG files in the directory
files = [file for file in os.listdir(output_dir) if file.endswith('.png')]
files.sort()  # Sort files in alphabetical order

# Create a list to store images
images = []

# Read images from files and append to the list
for file in files:
    img_path = os.path.join(output_dir, file)
    images.append(imageio.imread(img_path))

# Save the animation
output_anim = f'../Images/pushforward_anim_play/prediction_for_bin_{el_id}.gif'
imageio.mimsave(output_anim, images, duration=1.6, loop=0)  # Adjust duration as needed

print('Done GIF')

# Save the animation as MP4
# output_file = f'../Images/pushforward_anim_play/prediction_for_bin_{el_id}.mp4'
imageio.mimsave(output_anim, images, fps=10)  # Adjust fps (frames per second) as needed
print('Done MP4')


