# markov-ocean-prediction
A location prediction for floating particles on the ocean surface, based on Markov chains.

## Packages
This code is based on two packages:
1. [pygtm](https://github.com/philippemiron/pygtm) - which you will need to download locally. <br>
I have added here the package with the modded `dataset2.py` file, but the only difference is the oversmapling value. <br>
Available at folder `modded-pygtm`.
2. [parcels](https://github.com/OceanParcels/Parcels) - which can be installed with pip.

## Guide
I wrote a 2-part guide to complement the tutorials provided by Miron for using the pygtm package and using the Markov prediction. <br>
__Note__ that the reading of NC files is different here, as the structure of the NC file for this example was different from the files created by the parcels script added here. 

## Data files
Data files are not provided, please ask if you need them for validation or help. <br>
__Note__ that NC files might have different structs and might require different handling in the code.

## How To Use

In order to use these codes with ease, please read below.

We need to run several files to make a map prediction using Markov.

### Steps:
1. Run a script that creates particles over the ocean - such as: <br>
    `parcels_creator_300m_on_mask.py` <br>
    This code is without parallelization.

    `MPI_parcels_creator_300m_on_mask.py` <br>
    This code is with parallelization with MPI.
   
   To run it, you will need to have MPI installed and run the following:  <br>
   `mpiexec -np ### python MPI_parcels_creator_300m_on_mask.py` <br>
   __! Replace ### with the number of cores you would like to use.__

    <ins>Details about some parameters:</ins> <br>
    * 'cut_n' - splices the area of data over the ocean. The bigger it is, the less data there is (jump value).
    * 'nend' - should match the biggest value in the file name of the u,v,vorticity files. Can be smaller for testing purposes.
    * 'output_zarr_name' =  the file name / folder name of the output from this code

2. Convert using a script the zarr file to an nc file: <br>
    `tool_zarr_to_nc.py`  - Use this one for zarr files created without MPI or with MPI with 1 processing unit <br>
   `tool_zarr_to_nc_MPI` - Use this one for zarr files created with MPI with more than 1 processing unit <br>

    <ins>Details about some parameters:</ins> <br>
    * 'filename' - change file name to match the folder name in output_zarr_name
    * 'zarr_file_path' - looks for the predfined path in the output_zarr_name, change if needed

From here you can choose to animate the particles flow (3,4) and / or create a markov prediction (5)

3. Plot the particles and vorticity if you'd like AND animate: <br>
    `cmap_vorticity_plot_300.py`  <br>
    Note that at function plot_vorticity at comment: <br>
    `# Plot current location` <br>
    You have two options - using a cmap or a single color. Choose your preference.

    <ins>Details about some parameters: </ins><br>
    * 'parcels_file_name' - should match 'filename' from tool_zarr_to_nc.py, will also be the name of the mp4 and gif files.

4. Animate without remaking the frames / use in case of an error in cmap_vorticity_plot_300.py before the animation is completed: <br>
    `tool_traj_only_animation.py`

    <ins>Details about some parameters: </ins><br>
    * 'parcels_file_name' - should match 'filename' from tool_zarr_to_nc.py, will also be the name of the mp4 and gif files.

5. Create Markov prediction map using: <br>
    `markov_pushforward_map.py`

    Details about some parameters:
    * 'Med_particle' - should match 'parcels_file_name' 
    * 'files_n' - should match or be lower then the total amount of files available of the  u,v,vorticity files
    * 'T' - change based on the relevant autocorrelation value on average for the area in question
    * 'x0','y0' - change to select starting location
    * 'output_dir' - change output location of the frames
    * 'output_file' - change output file (frame) name if you'd like
    * 'output_anim' - gif and mp4 location
