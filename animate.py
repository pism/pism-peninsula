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

def update(ax, data, index, variables):
    year = 365 * 86400

    x = data.variables["x"][:] * 1e-3
    t = data.variables["time"][index]

    ax.cla()

    for v in variables:
        y = data.variables[v][index, 1, :]
        ax.plot(x, y, label=v)

    ax.set_ylim(ymin=-600, ymax=2100)

    ax.set_title(f"Time: {t / year}")
    ax.legend()

    ax.grid(True)

if __name__ == "__main__":
    data = netCDF4.Dataset("ex.nc")

    N = len(data.variables["time"])

    variables = ["usurf", "topg"]

    writer = FFMpegWriter(fps=15, metadata={"title" : "Flowline run"})

    fig, ax = plt.subplots()

    with writer.saving(fig, "evolution.mp4", 100):
        for i in range(N):
            update(ax, data, i, variables)
            writer.grab_frame()
