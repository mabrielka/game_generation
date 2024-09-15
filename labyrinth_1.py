import pygame
import os
import sys
import random

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Лабиринт 1')

def terminate():
    pygame.quit()
    sys.exit()

# установка размера объектов / ячеек карты
tile_width = tile_height = 10

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
tile_images = {'wall': load_image('black_kirpich.jpg', 0), 'empty': load_image('travka.png', 0)}
player_image = load_image('vorona.png', -1)

def start_screen():
    screen.fill((0, 0, 0))
    w, h = pygame.display.get_surface().get_size()
    fon = load_image('заставка_1.jpg')
    screen.blit(fon, (w // 2 - 625, h // 2 - 400))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()

def between_screen():
    screen.fill((0, 0, 0))
    w, h = pygame.display.get_surface().get_size()
    fon = load_image('заставка_1_2.jpg')
    screen.blit(fon, (w // 2 - 630, h // 2 - 400))
    play_sound('winner_1_2.ogg')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()

def winner_screen():
    screen.fill((0, 0, 0))
    w, h = pygame.display.get_surface().get_size()
    fon = load_image('заставка_1_3.jpg')
    play_sound('winner_1_3.ogg')
    screen.blit(fon, (w // 2 - 625, h // 2 - 400))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()

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
        if 0 <= self.rect.y + y < 85 * tile_height and 0 <= self.rect.x + x < 50 * tile_width and \
                level_map[(self.rect.y + y) // tile_height][(self.rect.x + x) // tile_width] in ('.', '@'):
            self.rect = self.rect.move(x, y)
            self.x += dx
            self.y += dy

start_screen()

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

def get_unvis_points(karta):
    n_ = len(karta)
    m_ = len(karta[0])
    for i in range(n_):
        for j in range(m_):
            if i % 2 != 0 & j % 2 != 0:
                if karta[i][j] == '*':
                    return [i, j]

def get_unvis_neighbors(a, b, karta):
    n_ = (len(karta) - 1) / 2
    m_ = (len(karta[0]) - 1) / 2
    list = []
    # вверх
    if b > 2:
        if karta[a][b - 2] == '*':
            list.append([a, b-2])
    # вниз
    if b < 2 * m_ - 2:
        if karta[a][b + 2] == '*':
            list.append([a,  b + 2])
    # вправо
    if a < 2 * n_ - 2:
        if karta[a + 2][b] == '*':
            list.append([a + 2, b])
    # влево
    if a > 2:
        if karta[a - 2][b] == '*':
            list.append([a - 2, b])
    return list

def generation_labyrinth(n, m):
    # создание основы для лабиринта с толстыми стенками
    # * - непосещенные точки
    # . - посещенные и гарантированные пути
    # # - гарантированные стенки алгоритма
    karta = [['#' for _ in range(2 * m + 1)] for __ in range(2 * n + 1)]
    for i in range(n):
        for j in range(m):
            karta[2 * i + 1][2 * j + 1] = '*'

    karta[1][1] = '.'
    not_visited = n * m - 1
    stack = [[1, 1]]

    while not_visited > 0:
        current = [stack[-1][0], stack[-1][1]]
        neighbours = get_unvis_neighbors(current[0], current[1], karta)
        if len(neighbours) != 0:
            rand_neighbour = random.choice(neighbours)
            diff_n = current[0] - rand_neighbour[0]
            diff_m = current[1] - rand_neighbour[1]
            if diff_n > 0:
                karta[- diff_n + 1 + current[0]][current[1]] = '.'
            elif diff_n < 0:
                karta[- diff_n - 1 + current[0]][current[1]] = '.'
            elif diff_m < 0:
                karta[current[0]][- diff_m - 1 + current[1]] = '.'
            elif diff_m > 0:
                karta[current[0]][- diff_m + 1 + current[1]] = '.'
            karta[rand_neighbour[0]][rand_neighbour[1]] = '.'
            stack.append(rand_neighbour)
            not_visited -= 1
        elif len(stack) != 0:
            stack.pop()
        else:
            unvisited = get_unvis_points(karta)
            stack.append(unvisited)
    return karta

def load_level(n, m):
    karta = generation_labyrinth(n, m)
    karta[1][1] = '@'
    karta[-1][-2] = '.'
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

level_size = [[], [5, 5], [10, 10], [10, 10], [10, 15], [15, 15],
              [20, 15], [20, 20], [20, 20], [22, 25], [22, 30]]

for level in range(1, 11):
    load_music('labyrinth_1_music.ogg')
    n, m = level_size[level]
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
            # победа при нажатии ctrl + F10
            if key[pygame.K_F10]:
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
    between_screen()

winner_screen()
terminate()