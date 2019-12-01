#!/usr/bin/gnuplot

set terminal qt
set datafile separator ','
set key autotitle columnhead
plot "10_multiple_lb_wr_timeouts.csv" using 1:2 with lines, \
  "10_multiple_lb_wr_fullqueues.csv" using 1:2 with lines

pause -1
