#!/bin/bash

set -x

N=$1
length=$2
outfile=$3

stress_balance=ssa+sia

ssafd_pc="-ssafd_ksp_type gmres -ssafd_ksp_norm_type unpreconditioned -ssafd_ksp_pc_side right -ssafd_pc_type asm -ssafd_sub_pc_type lu"

extra_vars="topg,usurf,mask,thk,velbar_mag,velbase_mag,dHdt,effective_precipitation,flux_mag,velbase,velsurf_mag,bmelt"

mpiexec -n $N pismr -i real_geometry.nc -bootstrap -My 3 -Mx 401 \
      -grid.periodicity y \
      -geometry.flow_line_mode \
      -pik \
      -time_stepping.skip.enabled yes \
      -time_stepping.skip.max  100 \
      -surface.models simple,cache \
      -surface.cache.update_interval 10 \
      -atmosphere.models uniform,orographic_precipitation,frac_P \
      -atmosphere.uniform.temperature 258.15 \
      -atmosphere.orographic_precipitation.wind_speed 15 \
      -atmosphere.orographic_precipitation.grid_size_factor 2 \
      -atmosphere.orographic_precipitation.scale_factor 0.6 \
      -atmosphere.frac_P.file precipitation_scaling.nc \
      -basal_resistance.pseudo_plastic.q 0.5 \
      -stress_balance.sia.bed_smoother.range 0 \
      -stress_balance.model ${stress_balance} ${ssafd_pc} \
      -stress_balance.sia.max_diffusivity 500 \
      -basal_yield_stress.mohr_coulomb.till_phi_default 20 \
      -bootstrapping.defaults.geothermal_flux 0.075 \
      -geometry.front_retreat.prescribed.file ice_extent_mask.nc \
      -ocean th \
      -ocean.th.file ocean.nc \
      -calving.methods eigen_calving  \
      -calving.eigen_calving.K 1e10 \
      -output.extra.file ex_${outfile}.nc \
      -output.extra.vars ${extra_vars} \
      -output.extra.times 10 \
      -y ${length} \
      -o ${outfile}.nc

python animate.py ex_${outfile}.nc ${outfile}.mp4
