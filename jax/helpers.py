import jax.numpy as jnp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


class Boundary:
    OUTFLOW = "outflow"
    REFLECTIVE = "reflective"
    PERIODIC = "periodic"
    
class Coords:
    CARTESIAN = "cartesian"
    POLAR = "polar"


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # print new line on complete
    if iteration == total:
        print()


def plot_grid(lattice, matrix, label, vmin=None, vmax=None):
    x1, x2 = lattice.x1, lattice.x2
    extent = [x1[0], x1[-1], x2[0], x2[-1]]

    if lattice.coords == Coords.CARTESIAN:
        fig, ax = plt.subplots()
        if vmin is None:
            vmin, vmax = np.min(matrix), np.max(matrix)
        c = ax.imshow(np.transpose(matrix), cmap="magma", interpolation='nearest',
                      origin='lower', extent=extent, vmin=vmin, vmax=vmax)
    elif lattice.coords == Coords.POLAR:
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        if vmin is None:
            vmin, vmax = np.min(matrix), np.max(matrix)
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylim(0, np.max(x1))
        ax.set_facecolor("black")
        circle_r = np.min(x1) - (x1[1] - x1[0]) / 2
        circle = Circle((0, 0), radius=circle_r, transform=ax.transData._b,
                        color='blue', fill=False, linewidth=1)
        ax.add_patch(circle)
        R, Theta = np.meshgrid(x1, x2, indexing="ij")
        c = ax.pcolormesh(Theta, R, matrix, shading='auto',
                          cmap="magma", vmin=vmin, vmax=vmax)

    cb = plt.colorbar(c, ax=ax, label=label)

    return fig, ax, c, cb


def cartesian_to_polar(x, y):
    r = jnp.sqrt(x ** 2 + y ** 2)
    theta = jnp.arctan2(y, x)
    return r, theta


def linspace_cells(min, max, num):
    interfaces = jnp.linspace(min, max, num + 1)
    centers = (interfaces[:-1] + interfaces[1:]) / 2

    return centers, interfaces


def logspace_cells(min, max, num):
    interfaces = jnp.logspace(jnp.log10(min), jnp.log10(max), num + 1)
    centers = (interfaces[:-1] + interfaces[1:]) / 2

    return centers, interfaces


def add_ghost_cells(arr, num_g, axis=0):
    if axis == 0:
        # add ghost cells to the first coordinate direction
        return jnp.vstack((jnp.repeat(arr[:1, :, :], num_g, axis), arr, jnp.repeat(
            arr[-1:, :, :], num_g, axis)))
    elif axis == 1:
        # add ghost cells to the second coordinate direction
        return jnp.hstack((jnp.repeat(arr[:, :1, :], num_g, axis), arr, jnp.repeat(
            arr[:, -1:, :], num_g, axis)))


def apply_bcs(lattice, U):
    g = lattice.num_g
    bc_x1, bc_x2 = lattice.bc_x1, lattice.bc_x2
    if bc_x1[0] == Boundary.OUTFLOW:
        U = U.at[:g, :, :].set(U[g:(g+1), :, :])
    elif bc_x1[0] == Boundary.REFLECTIVE:
        U = U.at[:g, :, :].set(jnp.flip(U[g:(2*g), :, :], axis=0))
        # invert x1 momentum
        U = U.at[:g, :, 1].set(-jnp.flip(U[g:(2*g), : 1], axis=0))
    elif bc_x1[0] == Boundary.PERIODIC:
        U = U.at[:g, :, :].set(U[(-2*g):(-g), :, :])

    if bc_x1[1] == Boundary.OUTFLOW:
        U = U.at[-g:, :, :].set(U[-(g+1):-g, :, :])
    elif bc_x1[1] == Boundary.REFLECTIVE:
        U = U.at[-g:, :, :].set(jnp.flip(U[-(2*g):-g, :, :], axis=0))
        # invert x1 momentum
        U = U.at[-g:, :, 1].set(-jnp.flip(U[-(2*g):-g, : 1], axis=0))
    elif bc_x1[1] == Boundary.PERIODIC:
        U = U.at[-g:, :, :].set(U[g:(2*g), :, :])

    if bc_x2[0] == Boundary.OUTFLOW:
        U = U.at[:, :g, :].set(U[:, g:(g+1), :])
    elif bc_x2[0] == Boundary.REFLECTIVE:
        U = U.at[:, :g, :].set(jnp.flip(U[:, g:(2*g), :], axis=1))
        # invert x2 momentum
        U = U.at[:, :g, 2].set(-jnp.flip(U[:, g:(2*g), 2], axis=1))
    elif bc_x2[0] == Boundary.PERIODIC:
        U = U.at[:, :g, :].set(U[:, (-2*g):(-g), :])

    if bc_x2[1] == Boundary.OUTFLOW:
        U = U.at[:, -g:, :].set(U[:, -(g+1):-g, :])
    elif bc_x2[1] == Boundary.REFLECTIVE:
        U = U.at[:, -g:, :].set(jnp.flip(U[:, -(2*g):-g, :], axis=1))
        # invert x2 momentum
        U = U.at[:, -g:, 2].set(-jnp.flip(U[:, -(2*g):-g, 2], axis=1))
    elif bc_x2[1] == Boundary.PERIODIC:
        U = U.at[:, -g:, :].set(U[:, g:(2*g), :])

    return U


def get_prims(hydro, U, X1, X2):
    rho = U[:, :, 0]
    u, v = U[:, :, 1] / rho, U[:, :, 2] / rho
    e = U[:, :, 3]
    p = hydro.P((rho, u, v, e), X1, X2)
    return rho, u, v, p


def U_from_prim(hydro, lattice, prims):
    rho, u, v, p = prims
    e = hydro.E(prims, lattice.X1, lattice.X2)
    return jnp.array([rho, rho * u, rho * v, e]).transpose((1, 2, 0))


def F_from_prim(hydro, lattice, prims):
    rho, u, v, p = prims
    e = hydro.E(prims, lattice.X1, lattice.X2)
    return jnp.array([
        rho * u,
        rho * (u ** 2) + p,
        rho * u * v,
        (e + p) * u
    ]).transpose((1, 2, 0))


def G_from_prim(hydro, lattice, prims):
    rho, u, v, p = prims
    e = hydro.E(prims, lattice.X1, lattice.X2)
    return jnp.array([
        rho * v,
        rho * u * v,
        rho * (v ** 2) + p,
        (e + p) * v
    ]).transpose((1, 2, 0))