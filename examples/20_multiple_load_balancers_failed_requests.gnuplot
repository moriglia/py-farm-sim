#!/usr/bin/gnuplot

set terminal qt
set datafile separator ','
set key autotitle columnhead
set xlabel "Simulation time"
set ylabel "Failures"
plot "20_multiple_lb_wr_timeouts.csv" using 1:2 with lines, \
  "20_multiple_lb_wr_fullqueues.csv" using 1:2 with lines

pause -1
