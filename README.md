# Hydro Code



A GPU-acccelerated Godunov hydrodynamics code written in [JAX](https://github.com/jax-ml/jax).

This code supports newtonian hydrodynamics up to 2D and compiles on CPU/GPU/TPU from the same Python code base. See [just-in-time compilation](https://jax.readthedocs.io/en/latest/jit-compilation.html).

https://github.com/user-attachments/assets/4a9abd93-4475-446b-8e73-1dcc3d937822

## Quick-start

Install with:

```bash
cd hydro-code
python setup.py
```

Run a configuration script:

```bash
hydrocode run configs/RayleighTaylor.py --nx 1000 --gamma-ad 1.4
```
Command line arguments `nx` and `gamma-ad` are dynamically parsed from the config class (a subclass of `Hydro`). See the `configs/` directory for examples.

## Notes

This code was adapted from Weiqun Zhang's [How To Write A Hydrodynamics Code](http://duffell.org/media/hydro.pdf). 
