import PISM

from PISM.util import convert

def grid(x_min, x_max, dx):
    "Allocate a flow-line grid."
    dy = dx

    x0 = (x_max + x_min) / 2.0
    y0 = 0.0

    Lx = (x_max - x_min) / 2.0
    Ly = 2.0 * dy
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
