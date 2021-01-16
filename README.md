# Modeling feedbacks between ice flow and orographic precipitation.

This repository contains scripts 

## Input data

- [ALBMAPv1](https://doi.pangaea.de/10.1594/PANGAEA.734145)
  (geothermal flux, near-surface air temperature, accumulation rate)
- [BedMachine Antarctica](https://nsidc.org/data/nsidc-0756) (bed
  elevation, surface elevation, ice thickness)
- [ITS_LIVE](https://nsidc.org/apps/itslive/) (surface speeds)

## Profile

The profile was picked "by hand", following the fastest flow above
Barilari Bay and along the Leppard glacier. It was then smoothed using
QGIS (Vector geometry/Smooth in the Processing toolbox) using default
parameters. The higher-resolution profile (`profile-500m`) was created
by placing points along the smoothed profile (Vector geometry/Points
along geometry).

## Sampling raster data along the profile

CSV files in `data` were created using QGIS as well (Raster
analysis/Sample raster values). The processing toolbox supports batch
processing, making it easy to re-generate these after modifying the
profile.

