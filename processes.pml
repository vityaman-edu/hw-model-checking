proctype Worker(byte id) {
    printf("Worker %d is executing with PID: %d\n", id, _pid);
}

active proctype AutoWorker() {
    printf("I am the auto-started worker, PID: %d\n", _pid);
}

init {
    printf("Init block started, PID: %d\n", _pid);
    run Worker(10);
    run Worker(20);
}
