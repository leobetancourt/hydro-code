from jax_hydro.helpers import plot_grid, print_progress_bar
from MHD.helpers import plot_grid as plot_MHD
import h5py
import os
from argparse import ArgumentParser
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300


parser = ArgumentParser(description="Create a movie from a .h5 file.")

parser.add_argument('-f', '--file', type=str, required=True,
                    help='The path to the .h5 file (required)')

parser.add_argument('-o', '--output', type=str, required=True,
                    choices=['density', 'log density', 'u', 'v', 'w',
                             'pressure', 'energy', 'Bx', 'By', 'Bz', 'div'],
                    help='The variable to plot: density, log density, u, v, pressure, energy, Bx, By, Bz or div (required)')

args = parser.parse_args()

# validate the file argument
if not args.file.endswith('.h5'):
    parser.error("The file name must end with '.h5'")

PATH = args.file
var = args.output

with h5py.File(PATH, "r") as f:
    coords = f.attrs["coords"]
    gamma = f.attrs["gamma"]
    x1 = f.attrs["x1"]
    x2 = f.attrs["x2"]

    if "x3" in f.attrs:
        x3 = f.attrs["x3"]

    tc = f["tc"][...]  # checkpoint times
    rho, momx1, momx2, En = f["rho"][...], f["momx1"][...], f["momx2"][...], f["E"][...]
    momx3, Bx, By, Bz = None, None, None, None
    if "Bx" in f:  # MHD
        momx3, Bx, By, Bz = f["momx3"], f["Bx"], f["By"], f["Bz"]

labels = {"density": r"$\rho$", "log density": r"$\log_{10} \Sigma$", "u": r"$u$",
          "v": r"$v$", "pressure": r"$P$", "energy": r"$E$", }

if var == "density":
    matrix = rho
elif var == "log density":
    matrix = np.log10(rho)
elif var == "u":
    matrix = momx1 / rho
elif var == "v":
    matrix = momx2 / rho
elif var == "energy":
    matrix = En

vmin, vmax = np.min(matrix), np.max(matrix)
if var == "log density":
    vmin, vmax = -3, 0.5
fig, ax, c, cb = plot_grid(
    matrix[0], labels[var], coords=coords, x1=x1, x2=x2, vmin=vmin, vmax=vmax)
ax.set_title(f"t = {0}")

fps = 24
FFMpegWriter = animation.writers['ffmpeg']
file = os.path.splitext(os.path.basename(PATH))[0]
metadata = dict(title=file, comment='')
writer = FFMpegWriter(fps=fps, metadata=metadata)
PATH = f"./visual/{file}"
if not os.path.exists(PATH):
    os.makedirs(PATH)
cm = writer.saving(fig, f"{PATH}/{var}.mp4", 600)

# tc /= 2 * np.pi
t_start = 0
diff_arr = np.absolute(tc - t_start)
idx_start = diff_arr.argmin()
t_end = 1
diff_arr = np.absolute(tc - t_end)
idx_end = len(tc)  # diff_arr.argmin()

with cm:
    for i in range(idx_start, idx_end):  # loop over checkpoints
        if Bx:  # MHD
            pass
            # plot_MHD(gamma, U, t=tc[i], plot=var, extent=[x1[0], x1[-1], x2[0], x2[-1]])
        else:  # HD
            if coords == "cartesian":
                c.set_data(matrix[i])
            elif coords == "polar":
                c.set_array(matrix[i].ravel())
            cb.update_normal(c)
            ax.set_title(f"t = {tc[i]:.2f}")
            fig.canvas.draw()
        writer.grab_frame()

        if var == "density":
            matrix = rho
        elif var == "log density":
            matrix = np.log10(rho)
        elif var == "u":
            matrix = momx1 / rho
        elif var == "v":
            matrix = momx2 / rho
        elif var == "energy":
            matrix = En

        print_progress_bar(i, len(tc), suffix="complete", length=50)

print("Movie saved to", PATH)
