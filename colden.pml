#define SPEAKER_VOLUME_MAX 2
#define ENGINE_TICKS_BEFORE_STOP_MAX 4

mtype:SpeakerRequest = {
    SPEAKER_BEEP
};

mtype:EngineRequest = {
    ENGINE_START,
    ENGINE_STOP
};

mtype:EngineState = {
    ENGINE_STOPPED,
    ENGINE_RUNNING,
    ENGINE_RUNNING_LOW
};

bool CoolingIsLow = false;
byte SpeakerVolume = 0;
bool EngineIsRunning = false;

proctype Cooling() {
    do
    :: true ->
        CoolingIsLow = false;
    :: true ->
        CoolingIsLow = true;
    od
}

proctype Speaker(chan self) {
    // Turn the Light On 🥀

    do
    :: self ? SPEAKER_BEEP ->
        SpeakerVolume = SPEAKER_VOLUME_MAX;
    :: empty(self) && 0 < SpeakerVolume ->
        SpeakerVolume = SpeakerVolume - 1;
    :: empty(self) && 0 == SpeakerVolume ->
        SpeakerVolume = 0;
    od
}

proctype User(chan engine) {
    do
    :: true ->
        engine ! ENGINE_START;
    :: true ->
        engine ! ENGINE_STOP;
    :: true ->
        skip;
    od
}

proctype Engine(chan self; chan speaker) {
    mtype:EngineState state;
    bool isLow;
    bool isStart;
    bool isStop;
    byte ticksBeforeStop;

    state = ENGINE_STOPPED;
    ticksBeforeStop = ENGINE_TICKS_BEFORE_STOP_MAX;

    do
    :: true ->
        isLow = CoolingIsLow;
        isStart = false;
        isStop = false;

        if
        :: self ? ENGINE_START ->
            isStart = true;
        :: self ? ENGINE_STOP ->
            isStop = true;
        :: empty(self) ->
            skip;
        fi

        assert(!(isStart && isStop));

        if
        :: (state == ENGINE_STOPPED) ->
            assert(ticksBeforeStop == ENGINE_TICKS_BEFORE_STOP_MAX);

            if
            :: isStart && isLow ->
                speaker ! SPEAKER_BEEP;
                state = ENGINE_STOPPED;
            :: isStart && !isLow ->
                EngineIsRunning = true;
                state = ENGINE_RUNNING;
            :: !isStart ->
                state = ENGINE_STOPPED;
            fi
        :: (state == ENGINE_RUNNING) ->
            assert(ticksBeforeStop == ENGINE_TICKS_BEFORE_STOP_MAX);

            if
            :: !isStop && isLow ->
                speaker ! SPEAKER_BEEP;
                state = ENGINE_RUNNING_LOW;
            :: !isStop && !isLow ->
                state = ENGINE_RUNNING;
            :: isStop ->
                EngineIsRunning = false;
                state = ENGINE_STOPPED;
            fi
        :: (state == ENGINE_RUNNING_LOW) ->
            assert(0 < ticksBeforeStop && ticksBeforeStop <= ENGINE_TICKS_BEFORE_STOP_MAX);

            ticksBeforeStop = ticksBeforeStop - 1;

            if
            :: ticksBeforeStop == 0 ->
                isStop = true;
            :: else ->
                skip;
            fi

            if
            :: !isStop && isLow ->
                state = ENGINE_RUNNING_LOW;
            :: !isStop && !isLow ->
                ticksBeforeStop = ENGINE_TICKS_BEFORE_STOP_MAX;
                state = ENGINE_RUNNING;
            :: isStop ->
                EngineIsRunning = false;
                ticksBeforeStop = ENGINE_TICKS_BEFORE_STOP_MAX;
                state = ENGINE_STOPPED;
            fi
        fi
    od
}

init {
    chan speaker = [1] of { mtype:SpeakerRequest };
    chan engine = [1] of { mtype:EngineRequest };

    run Cooling();
    run Speaker(speaker);
    run User(engine);
    run Engine(engine, speaker);
}

ltl p1 {
    [] (
        (EngineIsRunning &&
         CoolingIsLow &&
         0 == SpeakerVolume) ->
        (<> (!CoolingIsLow ||    // Consider: `CoolingIsLow; !CoolingIsLow; isLow = CoolingIsLow`
             !EngineIsRunning || // Consider: `CoolingIsLow; c ! ENGINE_STOP`
             0 < SpeakerVolume))
    );
}

ltl p2 {
    [] (
        (EngineIsRunning && CoolingIsLow) ->
        (<> (!CoolingIsLow || !EngineIsRunning))
    );
}

ltl p3 {
    [] (
        (!EngineIsRunning && CoolingIsLow) -> (!EngineIsRunning U CoolingIsLow)
    );
}
