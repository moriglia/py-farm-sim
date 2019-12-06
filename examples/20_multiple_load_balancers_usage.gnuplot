#!/usr/bin/gnuplot

set terminal qt
set datafile separator ','
set key autotitle columnhead
set xlabel "Simulation time"
set ylabel "Utilization"
plot "20_multiple_lb_srv0_usage.csv" using 1:2 with lines, \
  "20_multiple_lb_srv1_usage.csv" using 1:2 with lines,\
  "20_multiple_lb_srv2_usage.csv" using 1:2 with lines, \
  "20_multiple_lb_srv3_usage.csv" using 1:2 with lines

pause -1
