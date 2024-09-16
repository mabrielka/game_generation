import pygame
import os
import sys
import random

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Генерация игровой карты с помощью лабиринта алгоритмом прима и клеточным аппаратом')

# количество раз обрубания тупиков
KOEFF_smoothing = 4
# количество раз сглаживания
KOEFF_num_сellular_automaton = 3
# количество клеток которые должны окружать стену чтобы она стала полом
KOEFF_сellular_automaton = 4
# массив с высотой и шириной карт при каждом уровне, но сейчас настроено как для 1 эл-та
level_size = [[64, 64]]

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
tile_images = {'wall': load_image('black_kirpich.jpg', 0), 'empty': load_image('travka.png', 0)}
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

def get_unvis_points(karta):
    n_ = len(karta)
    m_ = len(karta[0])
    for i in range(n_):
        for j in range(m_):
            if i % 2 != 0 & j % 2 != 0:
                if karta[i][j] == '*':
                    return [i, j]

def get_neighbors(a, b, karta):
    n = len(karta)
    m = len(karta[0])
    list = []
    # вверх
    if b >= 2 and karta[a][b - 2] == '#':
        list.append([a, b - 2])
    # вниз
    if b < m - 2 and karta[a][b + 2] == '#':
        list.append([a, b + 2])
    # вправо
    if a < n - 2 and karta[a + 2][b] == '#':
        list.append([a + 2, b])
    # влево
    if a >= 2 and karta[a - 2][b] == '#':
        list.append([a - 2, b])
    return list

def generation_labyrinth(n_, m_):
    # создание основы для лабиринта с толстыми стенками
    # . - посещенные и гарантированные пути
    # # - стенки алгоритма
    n, m = 2 * n_ + 1, 2 * m_ + 1
    karta = [['#' for _ in range(m)] for __ in range(n)]
    x, y  = None, None
    x = min(random.randint(0, (n // 2)) * 2 + 1, n - 2)
    y = min(random.randint(0, (m // 2)) * 2 + 1, m - 2)
    karta[x][y] = '.'
    list = get_neighbors(x, y, karta)

    while list:
        ind = random.randint(0, len(list) - 1)
        x, y = list[ind][0], list[ind][1]
        if karta[x][y] == '.':
            list.pop(ind)
            continue
        list.pop(ind)

        karta[x][y] = '.'

        directions = [0, 1, 2, 3]
        random.shuffle(directions)
        while(directions):
            dir = directions.pop()
            if dir == 0 and x + 2 < n and karta[x + 2][y] == '.':
                karta[x + 1][y] = '.'
                break
            elif dir == 1 and x - 2 >= 0 and karta[x - 2][y] == '.':
                karta[x - 1][y] = '.'
                break
            elif dir == 2 and y - 2 >= 0 and karta[x][y - 2] == '.':
                karta[x][y - 1] = '.'
                break
            elif dir == 3 and y + 2 < m and karta[x][y + 2] == '.':
                karta[x][y + 1] = '.'
                break
        list += get_neighbors(x, y, karta)

    return karta

def deadends_remover(karta):
    w = len(karta[0])
    h = len(karta)
    for _ in range(1):
        deadends = []
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                if karta[i][j] == '.':
                    neighbors = 0
                    if j > 1 and karta[i][j - 1] == '.':
                        neighbors += 1
                    if j < w - 2 and karta[i][j + 1] == '.':
                        neighbors += 1
                    if i > 1 and karta[i - 1][j] == '.':
                        neighbors += 1
                    if i < h - 2 and karta[i + 1][j] == '.':
                        neighbors += 1
                    if neighbors <= 1:
                        deadends.append([i, j])
        for i in deadends:
            a, b = i[0], i[1]
            karta[a][b] = '#'
    return karta

def beautifuler(karta):
    w = len(karta[0])
    h = len(karta)
    for _ in range(KOEFF_num_сellular_automaton):
        news = []
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                if karta[i][j] == '#':
                    neighbors = 0
                    for a in range(-1, 2):
                        for b in range(-1, 2):
                            neighbor_x = i - a
                            neighbor_y = j - b
                            if 0 <= neighbor_x < h and 0 <= neighbor_y < w:
                                if karta[neighbor_x][neighbor_y] == '.':
                                    neighbors += 1
                    if neighbors >= KOEFF_сellular_automaton:
                        news.append([i, j])
        for i in news:
            karta[i[0]][i[1]] = '.'
    return karta

def load_level(n, m):
    karta = generation_labyrinth(n, m)
    for _ in range(KOEFF_smoothing):
        karta = deadends_remover(karta)
    karta = beautifuler(karta)
    karta = deadends_remover(karta)
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
