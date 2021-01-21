"""
Helper functions for flow-line simulations.
"""

import PISM
from PISM.util import convert

import numpy as np

def bump(x, x0=0, zmin_l=-300, zmin_r=50, zmax=2000, sigma_l=10e3, sigma_r=25e3):
    """Evaluate a Gaussian 'bump' at location x.

    The bump is centered at x0 with the height zmax.

    The left part rises from zmin_l to zmax over the span controlled
    using sigma_l. (Similar for the right side.)

    """
    A_l = zmax - zmin_l
    A_r = zmax - zmin_r

    left  = zmin_l + A_l * np.exp(-(((x - x0) ** 2 / (2 * sigma_l ** 2))))
    right = zmin_r + A_r * np.exp(-(((x - x0) ** 2 / (2 * sigma_r ** 2))))

    return ((x <= x0) * left + (x > x0) * right)

def grid(x_min, x_max, dx):
    "Allocate a flow-line grid."
    dy = dx

    x0 = (x_max + x_min) / 2.0
    y0 = 0.0

    Lx = (x_max - x_min) / 2.0
    Ly = dy
    Mx = int((x_max - x_min) / dx) + 1
    My = 3

    return PISM.IceGrid_Shallow(PISM.Context().ctx,
                                Lx, Ly,
                                x0, y0,
                                Mx, My,
                                PISM.CELL_CORNER, PISM.Y_PERIODIC)

def ltop(geometry):
    """Run the LTOP model on a given ice geometry and return precipitation
    in m/year.

    """

    grid = geometry.ice_thickness.grid()
    config = grid.ctx().config()

    model = PISM.AtmosphereOrographicPrecipitation(grid, PISM.AtmosphereUniform(grid))

    model.init(geometry)
    model.update(geometry, 0, 1)

    My = int(grid.My()) // 2

    # convert to m/year and extract the middle "row"
    year = convert(1, "year", "second")
    water_density = config.get_number("constants.fresh_water.density")

    return year * model.mean_precipitation().numpy()[My,:] / water_density
