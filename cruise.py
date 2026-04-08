"""
Discrete cruise / manual driving model (see cruise.md).
"""
from __future__ import annotations

import sys
from typing import NamedTuple, Union

import pygame

DELTA_SPEED = 1
A_BRAKE = 8
A_ENGINE_LIMIT = A_BRAKE
V_MAX_USER = 16 * A_ENGINE_LIMIT
MAX_SPEED_WORLD = 4 * V_MAX_USER
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
    brake: float = 0.0

    @property
    def k_brake(self) -> float:
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
        brake = 1.0 if keys[pygame.K_s] else 0.0

        if keys[pygame.K_w]:
            if isinstance(t, Acceleration):
                t = Velocity(0)
            else:
                t = Acceleration(0)
        elif keys[pygame.K_a]:
            if isinstance(t, Acceleration):
                t = Acceleration(max(0, min(A_BRAKE, t.value - DELTA_SPEED)))
            else:
                t = Velocity(max(0, min(V_MAX_USER, t.value - DELTA_SPEED)))
        elif keys[pygame.K_d]:
            if isinstance(t, Acceleration):
                t = Acceleration(max(0, min(A_BRAKE, t.value + DELTA_SPEED)))
            else:
                t = Velocity(max(0, min(V_MAX_USER, t.value + DELTA_SPEED)))
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
    prev: Car | None
    engine_a_target: int
    x: int = 0
    velocity: int = 0
    acceleration: int = 0
    brake: float = 0.0

    @property
    def a_target_effective(self) -> int:
        return self.engine_a_target

    @property
    def a_output(self) -> int:
        return min(A_ENGINE_LIMIT, self.engine_a_target) - self.user.k_brake * A_BRAKE

    def _cruise_a_target(self) -> int:
        assert isinstance(self.user.target, Velocity)
        vt = self.user.target.value
        v = self.velocity
        if vt > v:
            a_t = max(0, vt - v)
        elif vt < v:
            a_t = int((v - vt) / A_BRAKE)
        else:
            a_t = 0

        if self.prev is not None:
            if (
                self.prev.velocity == self.velocity == 0
                and self.prev.user.k_brake == self.user.k_brake == 0.0
            ):
                a_t += 1

        return a_t

    def next(self) -> Car:
        if isinstance(self.user.target, Acceleration):
            a_t = self.user.target.value
        else:
            a_t = self._cruise_a_target()

        a_out = min(A_ENGINE_LIMIT, a_t) - self.user.k_brake * A_BRAKE
        a_current = a_out - self.env.resistance_acceleration
        v1 = min(MAX_SPEED_WORLD, max(0, self.velocity + a_current))
        x1 = self.x + v1
        return Car(
            user=self.user,
            env=self.env,
            prev=self,
            engine_a_target=a_t,
            x=x1,
            velocity=v1,
            acceleration=a_current,
            brake=self.user.k_brake,
        )


class State(NamedTuple):
    user: User
    car: Car
    env: Env

    def next(self) -> State:
        user = self.user.next()
        env = self.env.next()
        car_in = self.car._replace(user=user, env=env)
        car = car_in.next()
        return State(user=user, car=car, env=env)


def clear_terminal() -> None:
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def report(state: State) -> None:
    u, c, e = state.user, state.car, state.env
    clear_terminal()
    lines = [
        "=== Cruise simulation ===",
        f"User.target: {u.target!r}  k_brake={u.k_brake}",
        f"  a_target (manual): {u.a_target!r}   v_target (cruise): {u.v_target!r}",
        f"Car: x={c.x}  v={c.velocity}  a_current={c.acceleration}  car.brake={c.brake}",
        f"  engine_a_target (input)={c.engine_a_target}  a_output={c.a_output}  "
        f"(a_engine_limit={A_ENGINE_LIMIT}, a_brake={A_BRAKE})",
        f"Env: a_env={e.resistance_acceleration}  "
        f"(target cap A/D: MAX_SPEED_USER={V_MAX_USER}, DELTA_SPEED={DELTA_SPEED})",
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

    u0 = User(target=Acceleration(0), brake=0.0)
    env0 = Env(resistance_acceleration=2)
    car0 = Car(u0, env0, prev=None, engine_a_target=0, brake=0.0)
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
