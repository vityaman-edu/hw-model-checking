"""
Discrete cruise / manual driving model (see cruise.md).
"""
from __future__ import annotations

import sys
from typing import NamedTuple, Union

import pygame

DELTA_SPEED = 1
A_BRAKE = 8
MAX_SPEED_USER = 8 * DELTA_SPEED
MAX_SPEED_WORLD = 24 * DELTA_SPEED
SCREEN_W = 800
SCREEN_H = 400
CAR_R = 15
BG_COLOR = (28, 28, 28)
CAR_COLOR = (230, 230, 230)
CAR_PREV_COLOR = (72, 72, 72)
Y_CENTER = SCREEN_H // 2
FPS = 60


class Acceleration(NamedTuple):
    value: int = 0


class Velocity(NamedTuple):
    value: int = 0


Target = Union[Velocity, Acceleration]


class User(NamedTuple):
    target: Target
    brake: int = 0

    @property
    def k_brake(self) -> int:
        return self.brake

    @property
    def a_target(self) -> int | None:
        if isinstance(self.target, Acceleration):
            return self.target.value
        return None

    @property
    def v_target(self) -> int | None:
        if isinstance(self.target, Velocity):
            return self.target.value
        return None

    def next(self) -> User:
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        t = self.target
        brake = 1 if keys[pygame.K_s] else 0

        if keys[pygame.K_w]:
            if isinstance(t, Acceleration):
                t = Velocity(0)
            else:
                t = Acceleration(0)
        elif keys[pygame.K_a]:
            if isinstance(t, Acceleration):
                t = Acceleration(max(0, min(MAX_SPEED_USER, t.value - DELTA_SPEED)))
            else:
                t = Velocity(max(0, min(MAX_SPEED_USER, t.value - DELTA_SPEED)))
        elif keys[pygame.K_d]:
            if isinstance(t, Acceleration):
                t = Acceleration(max(0, min(MAX_SPEED_USER, t.value + DELTA_SPEED)))
            else:
                t = Velocity(max(0, min(MAX_SPEED_USER, t.value + DELTA_SPEED)))
        else:
            t = self.target

        return User(target=t, brake=brake)


class Env(NamedTuple):
    resistance_acceleration: int = 2

    def next(self) -> Env:
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        ra = self.resistance_acceleration
        if keys[pygame.K_q]:
            ra -= DELTA_SPEED
        if keys[pygame.K_e]:
            ra += DELTA_SPEED
        return Env(resistance_acceleration=max(0, ra))


class Car(NamedTuple):
    user: User
    env: Env
    prev: Car | None = None
    x: int = 0
    velocity: int = 0
    acceleration: int = 0
    brake: int = 0

    @property
    def a_target_effective(self) -> int:
        if isinstance(self.user.target, Acceleration):
            return max(0, self.user.target.value)
        raise NotImplementedError("velocity field is dummy (always 0)")

    @property
    def a_output(self) -> int:
        return self.a_target_effective - self.user.brake * A_BRAKE

    def next(self) -> Car:
        a_current = self.a_output - self.env.resistance_acceleration
        v1 = min(MAX_SPEED_WORLD, max(0, self.velocity + a_current))
        x1 = self.x + v1
        return Car(
            user=self.user,
            env=self.env,
            prev=self._replace(prev=None),
            x=x1,
            velocity=v1,
            acceleration=a_current,
            brake=self.user.brake,
        )


class State(NamedTuple):
    user: User
    car: Car
    env: Env

    def next(self) -> State:
        user = self.user.next()
        env = self.env.next()
        car = self.car.next()._replace(user=user, env=self.env)
        return State(user=user, car=car, env=env)


def clear_terminal() -> None:
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def report(state: State) -> None:
    u, c, e = state.user, state.car, state.env
    clear_terminal()
    lines = [
        "=== Cruise simulation ===",
        f"User.target: {u.target!r}  brake(k_brake)={u.k_brake}",
        f"  a_target (manual): {u.a_target!r}   v_target (cruise): {u.v_target!r}",
        f"Car: x={c.x}  velocity(dummy)={c.velocity}  step_speed={c.acceleration}  "
        f"a_current={c.acceleration}  brake={c.brake}",
        f"Engine: a_target_effective={c.a_target_effective}  a_output={c.a_output}",
        f"Env: resistance_acceleration={e.resistance_acceleration}  "
        f"(target cap A/D: MAX_SPEED={MAX_SPEED_USER}, DELTA_SPEED={DELTA_SPEED})",
        "Keys: A/D target  W mode  S brake  Q/E env resistance",
    ]
    print("\n".join(lines))


def draw(screen: pygame.Surface, state: State) -> None:
    screen.fill(BG_COLOR)

    if state.car.prev is not None:
        x_prev = state.car.prev.x % SCREEN_W
        pygame.draw.circle(screen, CAR_PREV_COLOR, (int(x_prev), Y_CENTER), CAR_R)

    x_curr = state.car.x % SCREEN_W
    pygame.draw.circle(screen, CAR_COLOR, (int(x_curr), Y_CENTER), CAR_R)

    pygame.display.flip()


def is_running() -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Cruise")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()

    u0 = User(target=Acceleration(0), brake=0)
    env0 = Env(resistance_acceleration=2)
    car0 = Car(u0, env0)
    state = State(u0, car0, env0)

    try:
        while is_running():
            report(state)
            draw(screen, state)
            state = state.next()
            clock.tick(FPS)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
