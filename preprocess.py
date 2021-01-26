#!/usr/bin/env python3

import numpy as np
import PISM

import flowline

import matplotlib.pyplot as plt

def real_geometry(grid):

    def load(filename, prefix="data/"):
        data = np.genfromtxt(prefix + filename, delimiter=",", skip_header=1, usecols=(1,3))
        return data[:, 0], data[:, 1]

    x, b = load("bed.csv")
    _, H = load("thickness.csv")

    X = np.array(grid.x())

    b = np.interp(X, x, b)
    H = np.interp(X, x, H)
    
    geometry = PISM.Geometry(grid)

    bed = geometry.bed_elevation
    thickness = geometry.ice_thickness
    with PISM.vec.Access([bed, thickness]):
        for i, j in grid.points():
            bed[i, j] = b[i]
            thickness[i, j] = H[i]

    geometry.sea_level_elevation.set(0)
    geometry.ensure_consistency(0)
    
    return geometry

def synthetic_geometry(grid):
    geometry = PISM.Geometry(grid)

    bed = geometry.bed_elevation
    thickness = geometry.ice_thickness
    with PISM.vec.Access([bed, thickness]):
        for i, j in grid.points():
            xi = grid.x(i)
            b = flowline.bump(xi, x0=32e3, zmax=1625, zmin_l=-300, zmin_r=-650, sigma_l=7.5e3, sigma_r=20e3)
            s = flowline.bump(xi, x0=32e3, zmax=2000, zmin_l=-200, zmin_r=30, sigma_l=10e3, sigma_r=30e3)
            bed[i, j] = b
            thickness[i, j] = max(s - b, 0)

    geometry.sea_level_elevation.set(0)
    geometry.ensure_consistency(0)
    
    return geometry

# Create the flow line grid and ice geometry on this grid:
#
# - real (read from csv files)
# - synthetic (generated using formulas)

grid = flowline.grid(-25e3, 175e3, dx=500)

real = real_geometry(grid)
real.dump("real_geometry.nc")

synth = synthetic_geometry(grid)

synth.dump("synth_geometry.nc")

# Plot real and synthetic geometry

x = np.array(grid.x()) * 1e-3

def F(v):
    return v.numpy()[0, :]

fig, ax = plt.subplots()
fig.set_figwidth(10)
fig.set_figheight(5)

ax.set_title("Geometry")

ax.plot(x, F(real.ice_surface_elevation) - F(real.ice_thickness),
        color="lightblue", label="bottom surface")
ax.plot(x, F(real.ice_surface_elevation), color="blue", label="top surface")
ax.plot(x, F(real.bed_elevation), color="black", label="bed")

ax.plot(x, F(synth.bed_elevation), "--", color="black", label="synthetic bed")
ax.plot(x, F(synth.ice_surface_elevation), "--", color="blue", label="synthetic surface")

ax.legend()
fig.savefig("geometry.png")

# Run the orographic precipitation model

config = PISM.Context().config
config.set_number("atmosphere.orographic_precipitation.wind_speed", 10)
config.set_number("atmosphere.orographic_precipitation.water_vapor_scale_height", 2500)
config.set_number("atmosphere.orographic_precipitation.fallout_time", 1000)
config.set_number("atmosphere.orographic_precipitation.conversion_time", 1000)
config.set_flag("atmosphere.orographic_precipitation.truncate", True)
config.set_number("atmosphere.orographic_precipitation.background_precip_post", 0.04)
config.set_number("atmosphere.orographic_precipitation.grid_size_factor", 2)
config.set_number("atmosphere.orographic_precipitation.scale_factor", 0.78)

# The precipitation field from RACMO was computed using "real"
# topography, so we need to tune LTOP using real topography as well.
P = flowline.ltop(real)

# Plot results and compare to the figure in the proposal.

data = np.genfromtxt("precipitation.csv", delimiter=",", skip_header=1)
P_x = data[:,0]
RACMO = data[:, 1]
SB04 = data[:, 2]

fig, ax = plt.subplots()
fig.set_figwidth(10)
fig.set_figheight(5)

ax.set_title("Precipitation in m/year")
ax.grid()

ax.plot(x, P, label="PISM")
ax.plot(P_x + 35, RACMO, color="red", label="RACMO")
ax.plot(P_x + 35, SB04, color="green", label="SB04")

h = F(real.ice_surface_elevation)
h /= 0.25 * h.max()

ax.plot(x, h, "--", color="black", label="scaled surface elevation")

ax.legend()
fig.savefig("precipitation.png")

# Create a "climate" input file. We can use this with "-atmosphere
# given" to look at differences between runs with and without
# orographic precipitation feedbacks.

out = PISM.util.prepare_output("climate.nc")

P = PISM.IceModelVec2S(grid, "precipitation", PISM.WITHOUT_GHOSTS)
# this value will be replaced by the LTOP model
P.set(0.0)
P.metadata().set_string("units", "kg m-2 year-1")
P.write(out)

temp = PISM.IceModelVec2S(grid, "air_temp", PISM.WITHOUT_GHOSTS)
temp.set(-15.0)
temp.metadata().set_string("units", "Celsius")
temp.write(out)

out.close()

out = PISM.util.prepare_output("ocean.nc")

x_s = 35e3

TH_e = -2.2
TH_w = 0.23
TH = PISM.IceModelVec2S(grid, "theta_ocean", PISM.WITHOUT_GHOSTS)
TH.set(TH_w)

with PISM.vec.Access(TH):
    for i,j in grid.points():
        xi = grid.x(i)
        TH[i, j] = (xi > x_s) * TH_e

TH.metadata().set_string("units", "Celsius")
TH.write(out)

S_e = 34.84
S_w = 34.70

S = PISM.IceModelVec2S(grid, "salinity_ocean", PISM.WITHOUT_GHOSTS)
S.set(S_w)

with PISM.vec.Access(S):
    for i,j in grid.points():
        xi = grid.x(i)
        S[i, j] = (xi > x_s) * S_e

S.metadata().set_string("units", "g/kg")
S.write(out)

out.close()

# Prescribe maximum ice extent.

ice_extent_mask = PISM.IceModelVec2S(grid, "land_ice_area_fraction_retreat", PISM.WITHOUT_GHOSTS)
ice_extent_mask.metadata().set_string("units", "1")

x_min = 20e3
x_max = 150e3

with PISM.vec.Access(ice_extent_mask):
    for i,j in grid.points():
        xi = grid.x(i)
        ice_extent_mask[i, j] = xi > x_min and xi < x_max

ice_extent_mask.dump("ice_extent_mask.nc")

# Generate the spatially-variable precipitation factor used to remove
# the patch of positive precipitation downwind from the ridge.

frac_P = PISM.IceModelVec2S(grid, "frac_P", PISM.WITHOUT_GHOSTS)
frac_P.metadata().set_string("units", "1")

with PISM.vec.Access(frac_P):
    for i,j in grid.points():
        xi = grid.x(i)
        frac_P[i, j] = xi < 90e3

frac_P.dump("precipitation_scaling.nc")

