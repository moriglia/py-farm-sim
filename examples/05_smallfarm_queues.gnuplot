#!/usr/bin/gnuplot

set terminal qt
set datafile separator ','
set key autotitle columnhead
plot "05_smallfarm_sautron_queue.csv" using 1:2 with lines, \
  "05_smallfarm_tenibres_queue.csv" using 1:2 with lines

pause -1
