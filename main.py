import pygame as pg
import random

from pygame.locals import (
    K_UP,
    K_RIGHT,
    K_DOWN,
    K_LEFT,
    K_w,
    K_d,
    K_s,
    K_a,
    K_ESCAPE,
    QUIT,
    KEYDOWN,
    RLEACCEL
)

pg.mixer.init()

pg.init()

clock = pg.time.Clock()
fps = 60

# Events
SPAWN_ENEMY_CAR = pg.USEREVENT + 1
pg.time.set_timer(SPAWN_ENEMY_CAR, 1000)

SPAWN_FUEL = pg.USEREVENT + 1
pg.time.set_timer(SPAWN_FUEL, 10000)

# Game constants
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 200
PLAYER_SPEED = 2
PLAYER_MAX_SPEED = 7
ENEMY_MAX_CAR_SPEED = 10
MAX_FUEL = 100
FUEL_LIFETIME_MS = 5000
FUEL_INCREASE = 50

# Game objects
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
enemies = pg.sprite.Group()
all_sprites = pg.sprite.Group()
fuel_tanks = pg.sprite.Group()

# images
interface_img = pg.image.load("graphics/ui.png").convert_alpha()
bg_img = pg.image.load("graphics/bg.png").convert_alpha()
tree_img = pg.image.load("graphics/tree.png").convert_alpha()
road_img = pg.image.load("graphics/road.png").convert_alpha()


screen.blit(bg_img, (0, 0))

for i in range(4):
    randx = random.randint(0, 36)
    randy = random.randint(0, 177)
    rect = tree_img.get_rect()
    rect.x = randx
    rect.y = randy
    screen.blit(tree_img, rect)

for i in range(4):
    randx = random.randint(0, 36)
    randy = random.randint(0, 177)
    rect = tree_img.get_rect()
    rect.x = randx + 204
    rect.y = randy
    screen.blit(tree_img, rect)

class PlayerCar(pg.sprite.Sprite):
    def __init__(self):
        super(PlayerCar, self).__init__()
        self.surf = pg.image.load("graphics/car-player.png").convert_alpha()
        self.rect = self.surf.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.speed = PLAYER_SPEED
        self.fuel = MAX_FUEL

    def update(self, pressed_keys):
        speed_increased = False
        if pressed_keys[K_w] or pressed_keys[K_UP]:
            speed_increased = True
            self.rect.move_ip(0, -self.speed)
            if self.rect.y < 0:
                self.rect.y = 0
        if pressed_keys[K_d] or pressed_keys[K_RIGHT]:
            speed_increased = True
            self.rect.move_ip(self.speed, 0)
            if self.rect.x + self.rect.width > SCREEN_WIDTH - 125:
                self.rect.x = SCREEN_WIDTH - self.rect.width - 125
        if pressed_keys[K_s] or pressed_keys[K_DOWN]:
            speed_increased = True
            self.rect.move_ip(0, self.speed)
            if self.rect.y + self.rect.height > SCREEN_HEIGHT:
                self.rect.y = SCREEN_HEIGHT - self.rect.height
        if pressed_keys[K_a] or pressed_keys[K_LEFT]:
            speed_increased = True
            self.rect.move_ip(-self.speed, 0)
            if self.rect.x < 63:
                self.rect.x = 63

        # Increase/decrease velocity based on if key was pressed
        if speed_increased:
            self.speed += 0.05
            if self.speed > PLAYER_MAX_SPEED:
                self.speed = PLAYER_MAX_SPEED
        else:
            self.speed -= 0.1
            if self.speed < PLAYER_SPEED:
                self.speed = PLAYER_SPEED
        # Decrease fuel amount
        self.fuel -= 0.05

    def increase_fuel(self):
        self.fuel = min(MAX_FUEL, self.fuel + FUEL_INCREASE)

    def draw(self, screen):
        screen.blit(self.surf, self.rect)

class EnemyCar(pg.sprite.Sprite):
    def __init__(self):
        super(EnemyCar, self).__init__()
        self.surf = pg.image.load("graphics/car-enemy.png").convert_alpha()
        self.rect = self.surf.get_rect(
            center=(
                random.randint((63 + 8), (63 + 136 - 8)),
                random.randint(SCREEN_HEIGHT, SCREEN_HEIGHT + 100)
            )
        )
        self.speed = random.randint(1, ENEMY_MAX_CAR_SPEED)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < -22:
            self.kill()


class Fuel(pg.sprite.Sprite):
    def __init__(self):
        super(Fuel, self).__init__()
        self.surf = pg.image.load("graphics/fuel.png").convert_alpha()
        self.rect = self.surf.get_rect(
            center=(
                random.randint((63 + 8), (63 + 136 - 8)),
                random.randint(0, SCREEN_HEIGHT-8)
            )
        )
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FUEL_LIFETIME_MS:
            self.kill()

# Game state
running = True
road_y = 0
player_car = PlayerCar()



while running:
    for event in pg.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False
        if event.type == SPAWN_ENEMY_CAR:
            new_enemy_car = EnemyCar()
            enemies.add(new_enemy_car)
            all_sprites.add(new_enemy_car)
        if event.type == SPAWN_FUEL:
            print("Creating fuel")
            new_fuel = Fuel()
            fuel_tanks.add(new_fuel)
            all_sprites.add(new_fuel)

    # draw the road
    screen.blit(road_img, (61, road_y-SCREEN_HEIGHT))
    screen.blit(road_img, (61, road_y-SCREEN_HEIGHT+108))
    screen.blit(road_img, (61, road_y))
    screen.blit(road_img, (61, road_y+108))
    # update road position
    if road_y > SCREEN_HEIGHT:
        road_y = 0
    road_y += 1

    pressed_keys = pg.key.get_pressed()
    player_car.update(pressed_keys)
    enemies.update()

    # check for collision between player and fuel tanks
    for fuel in fuel_tanks:
        if player_car.rect.colliderect(fuel.rect):
            player_car.increase_fuel()
            fuel.kill()

    # draw all game objects
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)
    player_car.draw(screen)

    screen.blit(interface_img, (0, 0))
    # draw speed
    pg.draw.rect(screen, (255, 0, 0), (SCREEN_WIDTH - 43, 80, (player_car.speed * (21/PLAYER_MAX_SPEED)), 9))
    # draw fuel gage
    pg.draw.rect(screen, (255, 0, 0), (SCREEN_WIDTH - 61, 50, (player_car.fuel * (57/MAX_FUEL)), 9))
    pg.display.update()
    clock.tick(fps)
