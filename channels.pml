chan data_bus = [2] of { byte };

active proctype Producer() {
    byte value = 10;
    printf("Producer: Sending %d\n", value);
    data_bus ! value;

    value = 20;
    printf("Producer: Sending %d\n", value);
    data_bus ! value;
}

active proctype Consumer() {
    byte received;

    data_bus ? received;
    printf("Consumer: Received %d\n", received);

    data_bus ? received;
    printf("Consumer: Received %d\n", received);
}
