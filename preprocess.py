#!/usr/bin/env python3

import numpy as np
import PISM

import formulas
import flowline

def real_geometry(grid):

    def load(filename, prefix="profile/"):
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
            b = formulas.bump(xi, x0=30e3, zmax=1600, zmin_l=-200, zmin_r=-500, sigma_l=4e3, sigma_r=25e3)
            s = formulas.bump(xi, x0=35e3, zmax=2000, zmin_l=-300, zmin_r=30, sigma_l=10e3, sigma_r=30e3)
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

synth = synthetic_geometry(grid)

synth.dump("geometry.nc")

# Plot real and synthetic geometry

x = np.array(grid.x()) * 1e-3

def F(v):
    return v.numpy()[0, :]

fig = figure(plot_width=900, plot_height=500, title="Geometry",
             tooltips=[("x", "@x"), ("y", "@y")])

fig.line(x, F(real.ice_surface_elevation) - F(real.ice_thickness),
         line_width=2, line_color="lightblue", legend_label="bottom surface")
fig.line(x, F(real.ice_surface_elevation), line_width=2, line_color="blue", legend_label="top surface")
fig.line(x, F(real.bed_elevation), line_width=2, line_color="black", legend_label="bed")


fig.line(x, F(synth.bed_elevation),
         line_width=2, line_color="black", line_dash="dashed", legend_label="synthetic bed")
fig.line(x, F(synth.ice_surface_elevation),
         line_width=2, line_color="blue", line_dash="dashed", legend_label="synthetic surface")

show(fig)


# Run the orographic precipitation model

config = PISM.Context().config
config.set_number("atmosphere.orographic_precipitation.wind_speed", 15)
config.set_number("atmosphere.orographic_precipitation.water_vapor_scale_height", 2000)
config.set_number("atmosphere.orographic_precipitation.fallout_time", 1000)
config.set_number("atmosphere.orographic_precipitation.conversion_time", 1000)
config.set_flag("atmosphere.orographic_precipitation.truncate", True)
config.set_number("atmosphere.orographic_precipitation.background_precip_post", 0.0)
config.set_number("atmosphere.orographic_precipitation.grid_size_factor", 20)
config.set_number("atmosphere.orographic_precipitation.scale_factor", 1.3)

P = flowline.ltop(real)


# Plot results and compare to the figure in the proposal.

x = np.array(grid.x()) * 1e-3

data = np.genfromtxt("precipitation.csv", delimiter=",", skip_header=1)
P_x = data[:,0]
RACMO = data[:, 1]
SB04 = data[:, 2]

fig = figure(plot_width=900, plot_height=500, title="Precipitation in m/year",
             tooltips=[("x", "@x"), ("y", "@y")])
fig.line(x, P, line_width=2, legend_label="PISM")
fig.line(P_x + 35, RACMO, line_width=2, line_color="red", legend_label="RACMO")
fig.line(P_x + 35, SB04, line_width=2, line_color="green", legend_label="SB04")

h = F(real.ice_surface_elevation)
h /= 0.25 * h.max()

fig.line(x, h,
         line_width=2, line_color="black", line_dash="dashed", legend_label="scaled surface elevation")

show(fig)

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

# Prescribe maximum ice extent.

ice_extent_mask = PISM.IceModelVec2S(grid, "land_ice_area_fraction_retreat", PISM.WITHOUT_GHOSTS)
ice_extent_mask.metadata().set_string("units", "1")

x_min = 0e3
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

