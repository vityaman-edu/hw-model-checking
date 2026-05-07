byte global_counter;

active [2] proctype Calculator() {
    byte local_value = 5;

    local_value = local_value + _pid;

    global_counter = global_counter + 1;

    printf("PID %d: local_value = %d, global_counter = %d\n",
            _pid, local_value, global_counter);
}
