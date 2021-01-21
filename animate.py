#!/usr/bin/python3

"""This script can be used to visualize the evolution of ice geometry
in a flow-line simulation.

"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
import netCDF4
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

def update(ax, data, index):
    year = 365 * 86400

    x = data.variables["x"][:] * 1e-3
    t = data.variables["time"][index]

    ax[0].cla()
    ax[1].cla()
    ax_b.cla()

    speed = data.variables["velsurf_mag"][index, 1, :]
    bmelt = data.variables["bmelt"][index, 1, :]
    topg = data.variables["topg"][index, 1, :]
    usurf = data.variables["usurf"][index, 1, :]
    thk = data.variables["thk"][index, 1, :]
    surface = np.ma.array(data=usurf, mask=(thk < 1))
    basal_topography = np.ma.array(data=(usurf-thk), mask=(thk < 1))
    basal_melt = np.ma.array(data=-bmelt, mask=(thk < 1))
    speed = np.ma.array(data=speed, mask=(thk < 10))
    ax[0].plot(x, speed, label="Speed (m/yr)")
    ax_b.plot(x, basal_melt, color="k", label="Basal melt")
    ax[1].plot(x, topg, label="Bed")
    ax[1].plot(x, surface, label="surface")
    ax[1].plot(x, basal_topography, label="ice bottom")
    ax[0].set_ylim(ymin=0, ymax=500)
    ax[1].set_ylim(ymin=-750, ymax=2200)
    ax[0].set_ylabel("Speed (m/r)")
    ax_b.set_ylabel("Melt rate (m/r)")
    ax[1].set_ylabel("Elevation (m)")
    ax[1].legend()

    ax[0].set_title(f"Time: {t / year}")


if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("FILE", nargs=1, help="Input file", default=None)
    parser.add_argument("OUTFILE", nargs=1, help="Output file", default=None)
    options = parser.parse_args()

    infile = options.FILE[-1]
    outfile= options.OUTFILE[-1]
    data = netCDF4.Dataset(infile)

    N = len(data.variables["time"])

    writer = FFMpegWriter(fps=15, metadata={"title" : "Flowline run"})

    fig, ax = plt.subplots(
        2,
        1,
        sharex="col",
        figsize=[6.2, 4.0],
        clear=True,
    )
    fig.subplots_adjust(wspace=0.025)
    ax_b = ax[0].twinx()

    with writer.saving(fig, outfile, 100):
        for i in range(N):
            update(ax, data, i)
            writer.grab_frame()
