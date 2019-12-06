#!/usr/bin/gnuplot

set terminal qt
set datafile separator ','
set key autotitle columnhead
set xlabel "Simulation time"
set ylabel "Queue"
plot "20_multiple_lb_srv0.csv" using 1:2 with lines, \
  "20_multiple_lb_srv1.csv" using 1:2 with lines, \
  "20_multiple_lb_srv2.csv" using 1:2 with lines, \
  "20_multiple_lb_srv3.csv" using 1:2 with lines

pause -1
