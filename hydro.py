import numpy as np
import matplotlib.pyplot as plt
from HD.HD_1D import HD_1D
from HD.HD_2D import HD_2D, Boundary
from Binary import Binary

from MHD.MHD import MHD

if __name__ == "__main__":

    sim = Binary(gamma=5/3, resolution=(300, 300))
    sim.run(T=20, plot="density", filename="binary", save_interval=0.04)

    # sim = MHD(gamma=2, resolution=(800, 1, 1), xrange=(-1, 1))
    # sim.shock_tube()
    # sim.run(T=0.2, plot="By", filename="BW", save_interval=0.01)

    # sim = MHD(gamma=5/3, resolution=(400, 600, 1), xrange=(-0.5, 0.5), yrange=(-0.75, 0.75))
    # sim.set_bcs((Boundary.PERIODIC, Boundary.PERIODIC),
    #             (Boundary.PERIODIC, Boundary.PERIODIC),
    #             (Boundary.PERIODIC, Boundary.PERIODIC))
    # sim.spherical_blast()
    # sim.run(T=1, plot="density", filename="MHD blast", save_interval=0.01)
    
    # sim = MHD(gamma=5/3, resolution=(512, 512, 1), xrange=(0, 1), yrange=(0, 1))
    # sim.set_bcs((Boundary.PERIODIC, Boundary.PERIODIC),
    #             (Boundary.PERIODIC, Boundary.PERIODIC),
    #             (Boundary.PERIODIC, Boundary.PERIODIC))
    # sim.orszag_tang()
    # sim.run(T=1, plot="pressure", filename="Orszag-Tang", save_interval=0.01)
    
    # sim = HD_2D(gamma=5/3, nu=0, resolution=(300, 450), xrange=(-1, 1), yrange=(-1.5, 1.5), solver="hll")
    # sim.set_bcs((Boundary.OUTFLOW, Boundary.OUTFLOW), 
    #             (Boundary.OUTFLOW, Boundary.OUTFLOW))
    # sim.sheer()
    # sim.run(T=1, plot="v", filename="sheer1", save_interval=0.01)
