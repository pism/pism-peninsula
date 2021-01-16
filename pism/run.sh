#!/bin/bash

set -x

length=1500
stress_balance=sia

ssafd_pc="-ssafd_ksp_type gmres -ssafd_ksp_norm_type unpreconditioned -ssafd_ksp_pc_side right -ssafd_pc_type asm -ssafd_sub_pc_type lu"

extra_vars="topg,usurf,mask,thk,velbar_mag,velbase_mag,dHdt,effective_precipitation,flux_mag,velbase"

mpiexec -n 16 pismr -i geometry.nc -bootstrap -My 3 -Mx 101 \
      -grid.periodicity y \
      -geometry.flow_line_mode \
      -pik \
      -surface.models simple,cache \
      -surface.cache.update_interval 10 \
      -atmosphere.models uniform,orographic_precipitation,frac_P \
      -atmosphere.uniform.temperature 258.15 \
      -atmosphere.orographic_precipitation.wind_speed 15 \
      -atmosphere.orographic_precipitation.grid_size_factor 2 \
      -atmosphere.orographic_precipitation.scale_factor 0.6 \
      -atmosphere.frac_P.file precipitation_scaling.nc \
      -stress_balance.sia.bed_smoother.range 0 \
      -stress_balance.model ${stress_balance} ${ssafd_pc} \
      -basal_yield_stress.mohr_coulomb.till_phi_default 20 \
      -bootstrapping.defaults.geothermal_flux 0.075 \
      -geometry.front_retreat.prescribed.file ice_extent_mask.nc \
      -calving.methods float_kill \
      -output.extra.file ex.nc \
      -output.extra.vars ${extra_vars} \
      -output.extra.times 10 \
      -y ${length} \
      -o output.nc
