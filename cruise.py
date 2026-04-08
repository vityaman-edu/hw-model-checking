import pygame
import math
import sys
import os

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_BLUE = (173, 216, 230)

CAR_RADIUS = 20
CAR_COLOR = GREEN
ROAD_LINE_COLOR = DARK_GRAY
ROAD_Y = SCREEN_HEIGHT // 2

G = 9.81
CAR_MASS = 800
DT = 1.0 / FPS

ENGINE_KONSTANT_K = 200
ENGINE_MAX_FORCE = 8000
MAX_TARGET_SPEED = 50.0
MIN_TARGET_SPEED = 0.0

BRAKE_MAX_FORCE = 15000

AIR_DRAG_K = 0.4
ROLLING_RESISTANCE_K = 70

WHEEL_RADIUS = 0.3

MAX_ROAD_ANGLE_DEGREES = 10
ROAD_ANGLE_STEP = 0.5


def sign(value):
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0


pygame.init()

pygame.display.set_caption("Автомобильная симуляция")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

running = True

car_x = SCREEN_WIDTH // 4
car_v = 0.0
target_engine_speed = 0.0
brake_input = 0.0
road_angle_degrees = 0.0
road_angle_radians = math.radians(road_angle_degrees)


def keyboard():
    global running
    global brake_input
    global target_engine_speed
    global road_angle_degrees
    global road_angle_radians

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                brake_input = 1.0
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                brake_input = 0.0

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        target_engine_speed += 0.5 * DT * FPS
        target_engine_speed = min(target_engine_speed, MAX_TARGET_SPEED)
    if keys[pygame.K_DOWN]:
        target_engine_speed -= 0.5 * DT * FPS
        target_engine_speed = max(target_engine_speed, MIN_TARGET_SPEED)

    if keys[pygame.K_RIGHT]:
        road_angle_degrees += ROAD_ANGLE_STEP
        road_angle_degrees = min(road_angle_degrees, MAX_ROAD_ANGLE_DEGREES)
        road_angle_radians = math.radians(road_angle_degrees)
    if keys[pygame.K_LEFT]:
        road_angle_degrees -= ROAD_ANGLE_STEP
        road_angle_degrees = max(road_angle_degrees, -MAX_ROAD_ANGLE_DEGREES)
        road_angle_radians = math.radians(road_angle_degrees)


def physics():
    global car_x
    global car_v
    global target_engine_speed
    global brake_input
    global road_angle_degrees
    global road_angle_radians

    F_engine = 0.0
    if target_engine_speed > car_v:
        F_engine_raw = ENGINE_KONSTANT_K * (target_engine_speed - car_v)
        F_engine = min(F_engine_raw, ENGINE_MAX_FORCE)

    F_brake = 0.0
    if car_v != 0:
        brake_magnitude = brake_input * BRAKE_MAX_FORCE
        F_brake = -sign(car_v) * brake_magnitude

    F_air_drag = 0.0
    if car_v != 0:
        F_air_drag = -sign(car_v) * AIR_DRAG_K * car_v**2

    F_rolling_resistance = 0.0
    if car_v != 0:
        F_rolling_resistance = -sign(car_v) * ROLLING_RESISTANCE_K * abs(car_v)

    F_gravity = -CAR_MASS * G * math.sin(road_angle_radians)

    F_net = F_engine + F_brake + F_air_drag + F_rolling_resistance + F_gravity

    acceleration = F_net / CAR_MASS

    car_v_old = car_v
    car_v += acceleration * DT

    if (abs(car_v) < 0.1 and sign(car_v_old) != sign(car_v)) or (
        abs(car_v) < 0.01 and F_net < 100 and F_net > -100
    ):
        car_v = 0.0

    car_x += car_v * DT * 50

    if car_x > SCREEN_WIDTH + CAR_RADIUS:
        car_x = -CAR_RADIUS

    if car_x < -CAR_RADIUS:
        car_x = SCREEN_WIDTH + CAR_RADIUS


def draw():
    screen.fill(LIGHT_BLUE)
    pygame.draw.line(screen, ROAD_LINE_COLOR, (0, ROAD_Y), (SCREEN_WIDTH, ROAD_Y), 5)
    pygame.draw.circle(screen, CAR_COLOR, (int(car_x), ROAD_Y), CAR_RADIUS)
    pygame.display.flip()
    clock.tick(FPS)


def debug():
    current_speed_kmh = car_v * 3.6
    target_speed_kmh = target_engine_speed * 3.6
    text_lines = [
        f"Текущая скорость: {current_speed_kmh:.1f} км/ч",
        f"Целевая скорость двигателя: {target_speed_kmh:.1f} км/ч",
        f"Угол дороги: {road_angle_degrees:.1f}°",
        f"Тормоз нажат: {'Да' if brake_input > 0 else 'Нет'}",
        "",
        "Управление:",
        "  [↑] [↓] - Изменить целевую скорость двигателя",
        "  [←] [→] - Изменить угол наклона дороги",
        "  [Space] - Тормоз на максимум",
        "  [Esc] - Выход",
    ]

    os.system("cls" if os.name == "nt" else "clear")
    for line in text_lines:
        print(line)


while running:
    keyboard()
    physics()
    draw()
    debug()

pygame.quit()
sys.exit()
