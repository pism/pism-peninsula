import numpy as np

def bump(x, x0=0, zmin_l=-300, zmin_r=50, zmax=2000, sigma_l=10e3, sigma_r=25e3):
    """Evaluate a Gaussian 'bump' at location x.

    The bump is centered at x0 with the height zmax.

    The left part rises from zmin_l to zmax over the span controlled
    using sigma_l. (Similar for the right side.)

    """
    A_l = zmax - zmin_l
    A_r = zmax - zmin_r

    left  = zmin_r + A_r * np.exp(-(((x - x0) ** 2 / (2 * sigma_r ** 2))))
    right = zmin_l + A_l * np.exp(-(((x - x0) ** 2 / (2 * sigma_l ** 2))))

    return ((x <= x0) * left + (x > x0) * right)
