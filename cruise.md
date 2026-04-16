# Cruise Control

## Theoretic Model

There is a user. User has 2 variables:
- `k_brake:  float in [0, 1]` - intent to stop.
- `a_target: int | None` - acceleration it wants car to move with.
- `v_target: int | None` - velocity it wants car to move with.

The `a_target` is used only when user rides a car as it is own. If
croise control system is on, `a_target` should be disabled, so
user can't set it. Instead it uses `v_target`, but still can stop a
car via `k_brake`.

There is a parameter `a_brake` is an inversed acceleration of
brakes. There is a `a_engine_limit`, so engine can't produce
an acceleration higher that this one. An engine produces
`a_output = max(0, min(a_engine_limit, a_target) - k_brake * a_brake)`.

Also environment inversed acceleration `a_env` exists, so it also
makes car slower, and it is unknown for a user and a croise control
system.

Current velocity `v1` is computed as `v1 = v0 + a_current`, where
`a_current = max(0, a_output - a_env)`.

Current position `x1` is computed as `x1 = x0 + v1`.

How cruise control system works.

It remembers previous car state `prev`.
It knowns current car `velocity` and `v_target`, so it sets `a_target`
input for `a_output` formula to `max(0, v_target - velocity)` if
`v_target > velocity` or `(velocity - v_target) / a_brake` if
`v_target < velocity`.

Also here is the trick if user wants low `v_target` and `a_resistance` is
higher than `a_target` is computed without this knowledge, so car will not
move. To fix it, when `prev.velocity == self.velocity == 0` and
`prev.k_brake = self.k_brake = 0`, then `k_accel` is incremented by 1,
so car now also stores its `a_target` computed at previous state.

## Python Model

Implement a Python model of the "Theoretic Model" in a single file.
Use `pygame`. Do not use `pygame.font`, because it is not working.
Prefer printing output to the terminal, doing a clean before each print.

Use `NamedTuple` to declare objects:
- `User(Target: Velocity | Acceleration = Acceleration(0), Brake = 0)`
- `Env(ResistanceAcceleration = 2)`
- `Car(User, Env, X = 0, Velocity = 0, Acceleration = 0, Brake = 0)`
- `State(User, Car, Env)`

Each object could have readonly properties to expose intermiate calculation
results for diagnostics.

Make a `T.next(self): T` method on each object that will compute
its next values based on current and produce a copy.

The `User.next(self): T` should use `pygame` functionality to get target
value diff from a keyboard.

Keyboard:
`A` - Decrease `Target` by `DELTA_SPEED`.
`D` - Increase `Target` by `DELTA_SPEED`.
`W` - Switch between `Velocity` and `Acceleration` targets and reset to `0`.
`S` - Stop, while is pressed, so `Brake = 1`, otherwise `Brake = 0`.
`Q` - Decrease `Env.ResistanceAcceleration` by `DELTA_SPEED`.
`E` - Increase `Env.ResistanceAcceleration` by `DELTA_SPEED`.

Draw a screen with dark-dark gray background and light-light gray circle (car).

Car should move from left to right horizontally and when out of the screen
(at right), it wraps (at left side).

Also include a separate function to print the report about a state, including
intermidiate results.

You should have a `while True` loop with `report`, `draw` and `state = state.next()`.

## nuXmv Model

TODO: Stage 3.
