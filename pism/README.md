# PISM settings

## General settings

- The grid is periodic in the Y direction.
- PIK modifications (may not be important).

### Geothermal flux

The datasets in ALBMAPv1 have geothermal flux values of ~62 mW/m2 in
one and ~88 mW/m2 in the other. We set

```
    -bootstrapping.defaults.geothermal_flux 0.07
```
(the average).

## Stress balance

We use the SSA+SIA hybrid stress balance model.

### SSA

- Flow line mode (modification implemented for this project) (NB: try
  with and without and see if it improves condition numbers and
  performance).
- Calving front stress BC.

### SIA

- Turn off bed smoothing

### Basal strength

- Constant till friction angle because we suspect that presence or
  absence of sliding is driven by thermodynamics.

### Preconditioning of the SSA solver

- Consider using the redundant PC with LU as sub-PC.

## Climatic inputs

- Constant precipitation (0 m/yr) and near-surface air temperature
  (-15C).
- Precipitation computed using the orographic precipitation model.
- Precipitation is multiplied by a spatially-variable factor to
  eliminate positive precipitation downwind from the ridge.
- Near-surface air temperature and precipitation are re-interpreted as
  ice surface temperature and climatic mass balance (i.e.
  accumulation=precipitation, ablation=0).
- SMB is updated every 10 years (to reduce computational costs).

### Orographic precipitation

This model has about 15 parameters. We will need to tune it. To do
this we have to identify acceptable ranges for all the parameters we
can vary and (possibly) automate tuning.

**Note:** the spectral method used in the implementation implies that
*both* the topography (input) and the precipitation (output) are
periodic in space. We pad the grid to avoid issues with the
topography, but the support of the resulting precipitation field tends
to be larger and so requires more padding.

The amount of padding is set by

```
      -atmosphere.orographic_precipitation.grid_size_factor N
```

## Calving

Maximum ice extent is prescribed using a mask. Ice is removed when it
becomes floating *or* leaves the "maximum extent" area.
