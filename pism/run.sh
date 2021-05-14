#!/bin/bash

set -x

N=$1
length=$2
outfile=$3

extra_vars="topg,usurf,mask,thk,velbar_mag,velbase_mag,dHdt,\
effective_precipitation,flux_mag,velbase,velsurf_mag,bmelt"

ssafd_opts="\
-stress_balance.sia.max_diffusivity 500 \
-stress_balance.ssa.fd.flow_line_mode \
-time_stepping.skip.enabled yes \
-time_stepping.skip.max 100 \
"

# preconditioner flags for the SSAFD solver
ssafd_pc="\
-ssafd_ksp_type gmres \
-ssafd_ksp_norm_type unpreconditioned \
-ssafd_ksp_pc_side right \
-ssafd_pc_type asm \
-ssafd_sub_pc_type lu\
"

# number of MG levels
M=6
# coarsening factor
C=2
# number of vertical levels
bp_Mz=$(echo "$C^($M - 1) + 1" | bc)

# Blatter solver options
bp_opts="\
-stress_balance.ice_free_thickness_standard 50 \
-stress_balance.blatter.use_eta_transform \
-stress_balance.blatter.coarsening_factor ${C} \
-time_stepping.adaptive_ratio 10 \
-blatter_Mz ${bp_Mz} \
"

# preconditioner flags for the Blatter solver
bp_pc="\
-bp_snes_ksp_ew  \
-bp_snes_ksp_ew_version 3  \
-bp_snes_monitor_ratio0 \
-bp_ksp_type gmres \
-bp_pc_type mg \
-bp_pc_mg_levels ${M} \
-bp_mg_levels_ksp_type richardson \
-bp_mg_levels_pc_type sor \
-bp_mg_coarse_ksp_type preonly \
-bp_mg_coarse_pc_type lu \
"

# use the SSAFD stress balance solver
stress_balance="-stress_balance.model ssa+sia ${ssafd_opts} ${ssafd_pc}"

# use the Blatter stress balance solver
stress_balance="-stress_balance.model blatter ${bp_opts} ${bp_pc}"

mpiexec -n $N pismr -i real_geometry.nc -bootstrap -My 3 -Mx 401 \
      -grid.periodicity y \
      -pik \
      -surface.models simple,cache \
      -surface.cache.update_interval 10 \
      -atmosphere.models uniform,orographic_precipitation,frac_P \
      -atmosphere.uniform.temperature 258.15 \
      -atmosphere.orographic_precipitation.wind_speed 15 \
      -atmosphere.orographic_precipitation.grid_size_factor 2 \
      -atmosphere.orographic_precipitation.scale_factor 0.6 \
      -atmosphere.frac_P.file precipitation_scaling.nc \
      -basal_resistance.pseudo_plastic.enabled \
      -basal_resistance.pseudo_plastic.q 0.5 \
      -stress_balance.sia.bed_smoother.range 0 \
      ${stress_balance} \
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
      -o ${outfile}.nc | tee log.txt

python3 ../animate.py ex_${outfile}.nc ${outfile}.mp4
