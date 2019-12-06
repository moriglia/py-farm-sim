#!/usr/bin/gnuplot

set terminal qt
set datafile separator ','
set key autotitle columnhead
set xlabel "Simulation time"
set ylabel "Capacity"
plot "20_multiple_lb_srv0_capacity.csv" using 1:2 with steps, \
  "20_multiple_lb_srv1_capacity.csv" using 1:2 with steps,\
  "20_multiple_lb_srv2_capacity.csv" using 1:2 with steps, \
  "20_multiple_lb_srv3_capacity.csv" using 1:2 with steps

pause -1
