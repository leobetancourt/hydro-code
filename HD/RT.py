import jax.numpy as jnp
from jax import Array
from jax.typing import ArrayLike
from jax import Array, jit
import matplotlib.pyplot as plt

import argparse
import os
import time
from dataclasses import dataclass

from hydro import Hydro, Lattice, Coords, run
from helpers import Boundary, cartesian_to_polar, create_csv_file, append_row_csv


@dataclass(frozen=True)
class RT(Hydro):
    g: float = -0.1
    
    def source(self, U: ArrayLike, X1, X2, t: float) -> Array:
        rho = U[..., 0]
        u, v = U[..., 1] / rho, U[..., 2] / rho
        zero = jnp.zeros_like(rho)
        
        # return jnp.array([
        #     zero,
        #     zero,
        #     rho * self.g,
        #     rho * (self.g * v)
        # ]).transpose((1, 2, 0))
        return jnp.zeros_like(U)
        
    def setup(self, X1: ArrayLike, X2: ArrayLike):
        t = 0
        x, y = X1, X2
        cs = self.c_s((2, 0, 0, 2.5), X1, X2, t)
        # velocity perturbation is 5% of characteristic sound speed
        v = (cs * 0.05) * (1 - jnp.cos(4 * jnp.pi * x)) * (1 - jnp.cos(4 * jnp.pi * y / 3))
        rho = jnp.zeros_like(x)
        rho = rho.at[y >= 0.75].set(2)
        rho = rho.at[y < 0.75].set(1)
        p = 2.5 + self.g * rho * (y - 0.75)
        
        return jnp.array([
            rho,
            jnp.zeros_like(x),
            rho * v,
            self.E((rho, 0, v, p), X1, X2, t)
        ]).transpose((1, 2, 0))
        

def sedov(hydro: Hydro, lattice: Lattice, radius: float = 0.1) -> Array:
    if lattice.coords == Coords.CARTESIAN:
        r, _ = cartesian_to_polar(lattice.X1, lattice.X2)
    else:
        r, _ = lattice.X1, lattice.X2
    U = jnp.zeros((*r.shape, 4))
    U = U.at[r < radius].set(jnp.array([1, 0, 0, 10]))
    U = U.at[r >= radius].set(jnp.array([1, 0, 0, (1e-4 / (hydro.gamma - 1))]))
    return U

def main():
    hydro = RT(gamma=5/3, nu=0, cfl=0.4, coords=Coords.CARTESIAN)
    zone_space = jnp.linspace(300000, 10000000, num=100).astype(int)
    nx1s = jnp.sqrt(zone_space / 3).astype(int)
    
    for i in range(len(nx1s)):
        nx1, nx2 = nx1s[i], nx1s[i] * 3
        lattice = Lattice(
            coords=Coords.CARTESIAN,
            bc_x1=(Boundary.PERIODIC, Boundary.PERIODIC),
            bc_x2=(Boundary.REFLECTIVE, Boundary.REFLECTIVE),
            nx1=nx1,
            nx2=nx2,
            x1_range=(0, 0.5),
            x2_range=(0, 1.5)
        )

        U = hydro.setup(lattice.X1, lattice.X2)

        iters = 100
        start_time = time.time()
        run(hydro, lattice, U, N=iters)
        end_time = time.time()
        
        OUT_PATH = f"./RT"
        os.makedirs(OUT_PATH, exist_ok=True)
        FILE_PATH = f"{OUT_PATH}/stats.csv"
        if not os.path.isfile(FILE_PATH):
            create_csv_file(FILE_PATH, ["index", "iters", "n_zones", "elapsed", "M_zones_per_sec"])
        elapsed = end_time - start_time
        print("Elapsed:", elapsed)
        n_zones = nx1 * nx2
        M_zones_per_sec = n_zones * iters / (elapsed * 1e6)
        append_row_csv(FILE_PATH, [i, iters, n_zones, elapsed, M_zones_per_sec])
        print("Mzones per second:", M_zones_per_sec)


if __name__ == "__main__":
    main()