byte counter = 0;

active [2] proctype SafeIncrement() {
    byte temp;

    d_step {
        temp = counter;
        temp = temp + 1;
        counter = temp;
    }

    printf("PID %d updated counter to %d\n", _pid, counter);
}
