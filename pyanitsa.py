import pygame
import os
import sys
import random

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Генерация игровой карты с помощью алгоритма пьяницы')

# процент "земли", когда заканчиваем
floor_ratio = 0.5
# массив с высотой и шириной карт при каждом уровне, но сейчас настроено как для 1 эл-та
level_size = [[164, 164]]

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

    def update(self, x, y, n, m):
        dx = x // tile_width
        dy = y // tile_height
        if 0 <= self.rect.y + y < m * tile_height and 0 <= self.rect.x + x < n * tile_height and \
                level_map[(self.rect.y + y) // tile_height][(self.rect.x + x) // tile_width] in ('.', '@'):
            self.rect = self.rect.move(x, y)
            self.x += dx
            self.y += dy

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

def generate_map(n, m):
    # инициализируем карту со стенами
    map = [['#' for x in range(m)] for y in range(n)]

    # выбираем случайную стартовую точку
    start_x = random.randint(0, n - 1)
    start_y = random.randint(0, m - 1)

    # делаем стартовую точку полом
    map[start_x][start_y] = '.'

    # количество клеток, которые нужно сделать полом
    floor_count = int(n * m * floor_ratio)

    # текущее количество клеток пола
    current_floor_count = 1

    # направления движения (вверх, вниз, влево, вправо)
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    while current_floor_count < floor_count:
        dx, dy = random.choice(directions)

        # вычисляем новые координаты
        new_x = start_x + dx
        new_y = start_y + dy

        # проверяем, что новые координаты внутри карты
        if 0 <= new_x < n and 0 <= new_y < m:
            # если новая клетка стена, делаем ее полом
            if map[new_x][new_y] == '#':
                map[new_x][new_y] = '.'
                current_floor_count += 1
        else:
            continue
        # обновляем стартовую точку
        start_x = new_x
        start_y = new_y

    return map

def load_level(n, m):
    karta = generate_map(n, m)
    return karta

# создание готовой карты
def generate_level(level):
    new_player = Player(0, 0)
    x, y = None, None
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

for level in range(10):
    load_music('labyrinth_1_music.ogg')
    screen.fill((255, 255, 255))
    N, M = level_size[0]
    level_map = load_level(N, M)
    player, level_x, level_y = generate_level(level_map)
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            key = pygame.key.get_pressed()
            if key[pygame.K_DOWN]:
                player.update(0, tile_height, N, M)
            if key[pygame.K_UP]:
                player.update(0, -tile_height, N, M)
            if key[pygame.K_LEFT]:
                player.update(-tile_width, 0, N, M)
            if key[pygame.K_RIGHT]:
                player.update(tile_width, 0, N, M)
            # выход при нажатии esc
            if key[pygame.K_ESCAPE]:
                run = False
                terminate()
            # cлед уровень при нажатии ctrl + s
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
    pygame.mixer.music.stop()

terminate()