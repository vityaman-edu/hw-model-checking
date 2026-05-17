spin -a colden.pml
clang -O3 -o pan pan.c
./pan -m100000 -a -f -N "p1"
./pan -m100000 -a -f -N "p2"
./pan -m100000 -a -f -N "p3"
