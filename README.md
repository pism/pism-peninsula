# Modeling feedbacks between ice flow and orographic precipitation

This repository contains scripts that prepare input data and run PISM to
investigate feedbacks between ice flow and orographic precipitation.

## Input data

- [ALBMAPv1](https://doi.pangaea.de/10.1594/PANGAEA.734145)
  (geothermal flux, near-surface air temperature, accumulation rate)
- [BedMachine Antarctica](https://nsidc.org/data/nsidc-0756) (bed
  elevation, surface elevation, ice thickness)
- [ITS_LIVE](https://nsidc.org/apps/itslive/) (surface speeds)
- `precipitation.csv` (crudely digitized from a figure in the
  proposal) (precipitation from RACMO and a preliminary application of
  the LTOP model)

## Profile

The profile was picked "by hand", following the fastest ice flow above
Barilari Bay and along the Leppard glacier. It was then smoothed using
QGIS (Vector geometry/Smooth in the Processing toolbox) using default
parameters. The higher-resolution profile (`profile-500m`) was created
by placing points along the smoothed profile (Vector geometry/Points
along geometry).

See directories `profile-coarse` and `profile-500m`.

## Sampling raster data along the profile

CSV files in `data` were created using QGIS as well (Raster
analysis/Sample raster values). The processing toolbox supports batch
processing, making it easy to re-generate these after modifying the
profile.

See the directory `data`.

## Pre-processing data and running PISM

The script `preprocess.py` creates NetCDF files needed to run PISM.

See the directory `pism` for the run script and a discussion of
modeling choices.

## Other

The script `animate.py` can be used to visualize the changes in ice
geometry modeled by PISM.
