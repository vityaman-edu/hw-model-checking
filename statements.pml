active proctype Controller() {
    byte state = 0;

    do
    :: state < 3 ->
        if
        :: true -> state = state + 1; printf("Incremented state to %d\n", state)
        :: true -> state = state + 2; printf("Jumped state to %d\n", state)
        fi
    :: state >= 3 ->
        printf("State reached threshold. Breaking loop.\n");
        break;
    od;

    printf("Process finished.\n");
}
