from abc import abstractmethod
import math
from typing import Self, override

import pygame

PYGAME_FPS = 60
PYGAME_WIDTH = 1024 + 512
PYGAME_HEIGHT = 256
PYGAME_COLOR_BG = (0, 0, 0)
PYGAME_COLOR_PLAYER = (127, 255, 127)
PYGAME_COLOR_ENEMY = (127, 127, 255)
PYGAME_Y_CENTER = PYGAME_HEIGHT // 2
PYGAME_R_ENTITY = 8

SIM_CAR_A_FORWARD = 4
SIM_CAR_A_BRAKE = 6
SIM_CAR_A_MAX = SIM_CAR_A_BRAKE // 2


class Entity:
    @abstractmethod
    def next(self) -> Self:
        raise NotImplementedError

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        raise NotImplementedError


class CarControl(Entity):
    def __init__(
        self,
        k_accel: float = 0.0,
        k_brake: float = 0.0,
    ) -> None:
        self.k_accel = k_accel
        self.k_brake = k_brake

    @property
    def a(self) -> int:
        a_forward = int(self.k_accel * SIM_CAR_A_FORWARD)
        a_brake = int(self.k_brake * SIM_CAR_A_BRAKE)
        return min(SIM_CAR_A_MAX, a_forward - a_brake)

    @override
    def next(self) -> "CarControl":
        return CarControl(
            k_accel=self.k_accel,
            k_brake=self.k_brake,
        )

    @override
    def draw(self, surface: pygame.Surface) -> None:
        pass


class CarKeyboard(CarControl):
    def __init__(
        self,
        btn_accel_inc: int,
        btn_accel_dec: int,
        btn_brake: int,
        k_accel: float = 0.0,
        k_brake: float = 0.0,
    ) -> None:
        super().__init__(k_accel, k_brake)
        self.btn_accel_inc = btn_accel_inc
        self.btn_accel_dec = btn_accel_dec
        self.btn_brake = btn_brake

    @override
    def next(self) -> "CarKeyboard":
        step = 0.05

        keys = pygame.key.get_pressed()

        k_brake = 1.0 if keys[self.btn_brake] else 0.0

        if keys[self.btn_accel_inc]:
            k_accel = min(1.0, self.k_accel + step)
        elif keys[self.btn_accel_dec]:
            k_accel = max(0.0, self.k_accel - step)
        else:
            k_accel = self.k_accel

        return CarKeyboard(
            btn_accel_inc=self.btn_accel_inc,
            btn_accel_dec=self.btn_accel_dec,
            btn_brake=self.btn_brake,
            k_accel=k_accel,
            k_brake=k_brake,
        )

    @override
    def draw(self, surface: pygame.Surface) -> None:
        pass


class Car(Entity):
    def __init__(
        self,
        c: CarControl,
        x: int,
        v: int,
        color: tuple[int, int, int],
    ) -> None:
        self.c = c
        self.x = x
        self.v = v
        self.color = color

    @property
    def a(self) -> int:
        return self.c.a

    @override
    def next(self) -> "Car":
        assert 0 <= self.v
        return Car(
            c=self.c.next(),
            x=self.x + self.v,
            v=max(0, self.v + self.a),
            color=self.color,
        )

    @override
    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(
            surface,
            self.color,
            (self.x % PYGAME_WIDTH, PYGAME_Y_CENTER),
            PYGAME_R_ENTITY,
        )

        self.c.draw(surface)


class Cruise(Entity):
    def __init__(self, prev: Car | None, this: Car, that: Car) -> None:
        self.prev = prev or this
        self.this = this
        self.that = that

    @override
    def next(self) -> "Cruise":
        assert self.this.x < self.that.x

        d = max(0, self.that.x - self.this.x - self.this.v - 16)
        a_smooth = 1.0 * SIM_CAR_A_BRAKE
        v_target = max(0, math.sqrt(2 * a_smooth * d) - a_smooth / 2)
        a_req = v_target - self.this.v

        k_accel = max(0.0, min(1.0, +a_req / SIM_CAR_A_FORWARD))
        k_brake = max(0.0, min(1.0, -a_req / SIM_CAR_A_BRAKE))

        return Cruise(
            prev=self.this,
            this=Car(
                c=CarControl(k_accel=k_accel, k_brake=k_brake),
                x=self.this.x,
                v=self.this.v,
                color=self.this.color,
            ).next(),
            that=self.that.next(),
        )

    @override
    def draw(self, surface: pygame.Surface) -> None:
        self.this.draw(surface)
        self.that.draw(surface)


def draw(surface: pygame.Surface, e: Entity) -> None:
    surface.fill(PYGAME_COLOR_BG)
    e.draw(surface)
    pygame.display.flip()


def is_running() -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True


def main() -> None:
    pygame.init()

    pygame.display.set_caption("Cruise")
    surface = pygame.display.set_mode((PYGAME_WIDTH, PYGAME_HEIGHT))

    clock = pygame.time.Clock()

    world = Cruise(
        prev=None,
        this=Car(
            c=CarKeyboard(
                btn_accel_inc=pygame.K_w,
                btn_accel_dec=pygame.K_s,
                btn_brake=pygame.K_a,
            ),
            x=10,
            v=1,
            color=(255, 0, 0),
        ),
        that=Car(
            c=CarKeyboard(
                btn_accel_inc=pygame.K_UP,
                btn_accel_dec=pygame.K_DOWN,
                btn_brake=pygame.K_LEFT,
            ),
            x=256,
            v=1,
            color=(0, 0, 255),
        ),
    )

    try:
        while is_running():
            draw(surface, world)
            world = world.next()
            clock.tick(PYGAME_FPS)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
