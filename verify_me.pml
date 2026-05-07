byte n = 0;

active [2] proctype Adder() {
    byte temp;

    temp = n;
    temp = temp + 1;
    n = temp;
}

init {
    _nr_pr == 1;

    printf("Final value of n is %d\n", n);
    assert(n == 2);
}
