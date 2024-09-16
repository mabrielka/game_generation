import numpy as np
import pygame
import os
import sys
import random

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Лабиринт построенный по тупому - просто во все стороны идем, с какой-то вероятностью генерируем точку')

probability = 0.5
min_norm = 0.2
max_norm = 0.8

def terminate():
    pygame.quit()
    sys.exit()

# установка размера объектов / ячеек карты
tile_width = tile_height = 4

# функция для загрузки изображений
def load_image(name, colorkey=None):
    fullname = os.path.join('pictures', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
        image = resize_image(image, tile_width)
    else:
        image = image.convert_alpha()
    return image

def resize_image(image, num):
    image = pygame.transform.scale(image, (num, num))
    return image

# функция для произведения фоновой музыки в формате ogg
def load_music(name):
    fullname = os.path.join('music', name)
    pygame.mixer.music.load(fullname)
    pygame.mixer.music.play()

# функция для произведения звуков в формате ogg
def play_sound(name):
    fullname = os.path.join('music', name)
    sound = pygame.mixer.Sound(fullname)
    sound.play()

# загрузка изображений
tile_images = {'wall': load_image('water.jpg', 0), 'empty': load_image('trava.png', 0)}
player_image = load_image('vorona.png', -1)

# класс базовых объектов карты
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

# класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.x = pos_x
        self.y = pos_y

    def update(self, x, y):
        dx = x // tile_width
        dy = y // tile_height
        if 0 <= self.rect.y + y < m * tile_height and 0 <= self.rect.x + x < n * tile_width and \
                level_map[(self.rect.y + y) // tile_height][(self.rect.x + x) // tile_width] in ('.', '@'):
            self.rect = self.rect.move(x, y)
            self.x += dx
            self.y += dy

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

def generate_island_map(n, m):
    # # - вода
    # . - земля
    map_matrix = [['#' for _ in range(m)] for _ in range(n)]
    x, y = n // 2, m // 2
    x = x + random.randint(-n // 4, n // 4)
    y = y + random.randint(-m // 4, m // 4)
    x = max(0, min(x, n - 1))
    y = max(0, min(y, m - 1))

    list = [[x, y]]
    map_matrix[x][y] = '.'
    sum = 1
    while list:
        x, y = list.pop(0)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < m and map_matrix[nx][ny] == '#':
                if random.random() < probability:
                    map_matrix[nx][ny] = '.'
                    sum += 1
                    list.append([nx, ny])
    for i in range(1, n - 1):
        for j in range(1, m - 1):
            mid_sum = 0
            if map_matrix[i + 1][j] == '.':
                mid_sum += 1
            if map_matrix[i - 1][j] == '.':
                mid_sum += 1
            if map_matrix[i][j - 1] == '.':
                mid_sum += 1
            if map_matrix[i][j + 1] == '.':
                mid_sum += 1
            if mid_sum >= 3:
                map_matrix[i][j] = '.'
                sum += 1
    map_matrix[x][y] = '@'
    if sum / (n * m) < min_norm or sum / (n * m) > max_norm:
        map_matrix = generate_island_map(n, m)
    return map_matrix

def load_level(n, m):
    karta = generate_island_map(n, m)
    return karta

# создание готовой карты
def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y

level_size = [[100, 120]]

for level in range(1, 11):
    n, m = level_size[0]
    level_map = load_level(n, m)
    player, level_x, level_y = generate_level(level_map)
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            key = pygame.key.get_pressed()
            if key[pygame.K_DOWN]:
                player.update(0, tile_height)
            if key[pygame.K_UP]:
                player.update(0, -tile_height)
            if key[pygame.K_LEFT]:
                player.update(-tile_width, 0)
            if key[pygame.K_RIGHT]:
                player.update(tile_width, 0)\
            # выход при нажатии esc
            if key[pygame.K_ESCAPE]:
                run = False
                terminate()
            # победа при нажатии ctrl + s
            if key[pygame.K_s]:
                run = False
                break
            if player.y >= level_y or player.x >= level_x:
                run = False
        screen.fill((0, 0, 0))
        tiles_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
    player.kill()

terminate()