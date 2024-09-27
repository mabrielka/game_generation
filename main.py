import pygame
import os
import sys
import random

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('Генерация игровой карты с помощью алгоритма пьяницы')

# количество раз сглаживания
KOEFF_num_сellular_automaton = 1
# количество клеток которые должны окружать стену чтобы она стала полом
KOEFF_сellular_automaton = 5
keys_num = 3

# процент "земли", когда заканчиваем
floor_ratio = 0.5
# массив с высотой и шириной карт при каждом уровне, но сейчас настроено как для 1 эл-та
level_size = [[21, 21]]

# установка размера объектов / ячеек карты
tile_width = tile_height = 32

def terminate():
    pygame.quit()
    sys.exit()

# функция для загрузки изображений
def load_image(name, colorkey=None, size_1=tile_width, size_2=tile_width):
    fullname = os.path.join('pictures', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
        image = resize_image(image, size_1, size_2)
    else:
        image = image.convert_alpha()
    return image

def resize_image(image, num1, num2):
    image = pygame.transform.scale(image, (num1, num2))
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

def show_screen(filename):
    screen.fill((0, 0, 0))
    w, h = pygame.display.get_surface().get_size()
    fon = load_image(filename, 0, 3 * tile_width * level_size[0][0] // 2, tile_height * level_size[0][1])
    screen.blit(fon, (w // 2 - 625, h // 2 - 400))
    load_music('заставка.ogg')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                pygame.mixer.music.stop()
                return
        pygame.display.flip()

# загрузка изображений
tile_images = {'wall': load_image('water.jpg', 0),
               'empty': load_image('trava.png', 0),
               'wall_l': load_image('black_kirpich_3.png', 0),
               'empty_l': load_image('travka.png', 0),
               'stone': load_image('камень.png', -1),
               'tree': load_image('дерево.png', -1),
                'krya': load_image('trava.png', 0),
                 'castle': load_image('замок.png', -1)}
player_image = load_image('рыцарь.png', -1)
key_image = load_image('ключ.png', -1)

def remove_key():
    for key in key_group:
        if player.rect.collidepoint(key.rect.center):
            x = key.rect.x // tile_width
            y = key.rect.y // tile_height
            key.kill()
            Tile('empty', x, y)

# класс базовых объектов карты
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

# класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, num):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.x = pos_x
        self.y = pos_y
        self.in_castle = False
        self.keys = num

    def update(self, x, y, n, m):
        dx = x // tile_width
        dy = y // tile_height
        if 0 <= self.rect.y + y < m * tile_height and 0 <= self.rect.x + x < n * tile_height and \
                level_map[(self.rect.y + y) // tile_height][(self.rect.x + x) // tile_width] in ('.', '@', '*', '1', '0'):
            self.rect = self.rect.move(x, y)
            if level_map[(self.rect.y) // tile_height][
                (self.rect.x) // tile_width] == '1':
                # сбор ключа
                remove_key()
                self.keys -= 1
                level_map[(self.rect.y) // tile_height][(self.rect.x) // tile_width] = '.'
                self.in_castle = False
            # если герой наступил на красный бонус
            elif level_map[(self.rect.y) // tile_height][
                (self.rect.x) // tile_width] == '*':
                # наступил на замок
                self.in_castle = True
            elif level_map[(self.rect.y) // tile_height][
                (self.rect.x) // tile_width] == '0':
                # крякающая точка
                play_sound('krya.ogg')
                self.in_castle = False
            else:
                self.in_castle = False
            self.x += dx
            self.y += dy

class Key(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(key_group, all_sprites)
        self.image = key_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.x = pos_x
        self.y = pos_y

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
key_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

def generate_map(n, m):
    map = [['#' for x in range(m)] for y in range(n)]

    start_x = random.randint(0, n - 1)
    start_y = random.randint(0, m - 1)

    map[start_x][start_y] = '.'
    floor_count = int(n * m * floor_ratio)
    current_floor_count = 1
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    while current_floor_count < floor_count:
        dx, dy = random.choice(directions)
        new_x = start_x + dx
        new_y = start_y + dy

        if 0 <= new_x < n and 0 <= new_y < m:
            if map[new_x][new_y] == '#':
                map[new_x][new_y] = '.'
                current_floor_count += 1
        else:
            continue
        start_x = new_x
        start_y = new_y
    return map

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
    karta = generate_map(n, m)
    karta = beautifuler(karta)
    flag = 0
    keys = keys_num
    castle = 1
    trees = n * m // 15
    stones = 10
    while castle != 0 and keys != 0:
        for i in range(n):
            for j in range(m):
                if karta[i][j] == '.' and flag == 0:
                    karta[i][j] = '@'
                    flag = 1
                elif karta[i][j] == '.' and random.random() < 0.02 and keys > 0:
                    karta[i][j] = '1'
                    keys -= 1
                elif karta[i][j] == '.' and random.random() < 0.05 and trees > 0:
                    karta[i][j] = ')'
                    trees -= 1
                elif karta[i][j] == '.' and random.random() < 0.05 and stones > 0:
                    karta[i][j] = '('
                    stones -= 1
                elif karta[i][j] == '.' and random.random() < 0.02 and castle > 0:
                    karta[i][j] = '*'
                    castle -= 1
                elif karta[i][j] == '.' and random.random() < 0.15:
                    karta[i][j] = '0'
    return karta

# создание готовой карты
def generate_level(level):
    new_player, key, x, y = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y, keys_num)
            elif level[y][x] == '1':
                Tile('empty', x, y)
                key = Key(x, y)
            elif level[y][x] == ')':
                Tile('empty', x, y)
                Tile('tree', x, y)
            elif level[y][x] == '(':
                Tile('empty', x, y)
                Tile('stone', x, y)
            elif level[y][x] == '*':
                Tile('empty', x, y)
                Tile('castle', x, y)
            elif level[y][x] == '0':
                Tile('empty', x, y)
    return new_player, key, x, y

show_screen('заставка.jpg')

# main
for level in range(1):
    load_music('labyrinth_1_music.ogg')
    screen.fill((255, 255, 255))
    N, M = level_size[0]
    level_map = load_level(N, M)
    player, keys, level_x, level_y = generate_level(level_map)
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
            if player.keys == 0 and player.in_castle == True:
                run = False
                break
        screen.fill((0, 0, 0))
        tiles_group.draw(screen)
        player_group.draw(screen)
        key_group.draw(screen)
        pygame.display.flip()
    if player.keys == 0 and player.in_castle == True:
        player.kill()
        break
    player.kill()
    pygame.mixer.music.stop()

show_screen('между.jpg')

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

def generation_labyrinth(N, M):
    # создание основы для лабиринта с толстыми стенками
    # * - непосещенные точки
    # . - посещенные и гарантированные пути
    # # - гарантированные стенки алгоритма
    if N%2 == 0:
        N += 1
    if M%2 == 0:
        M += 1
    n = (N - 1) // 2
    m = (M - 1) // 2
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
    return karta

def load_labyrinth(n, m):
    karta = generation_labyrinth(n, m)
    karta[1][1] = '@'
    karta[-1][-2] = '.'
    return karta

def generate_labyrinth(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty_l', x, y)
            elif level[y][x] == '#':
                Tile('wall_l', x, y)
            elif level[y][x] == '@':
                Tile('empty_l', x, y)
                new_player = Player(x, y, 0)
    return new_player, x, y

for level in range(1):
    load_music('подземелье.ogg')
    n, m = level_size[0]
    level_map = load_labyrinth(n, m)
    player, level_x, level_y = generate_labyrinth(level_map)
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            key = pygame.key.get_pressed()
            if key[pygame.K_DOWN]:
                player.update(0, tile_height, n, m)
            if key[pygame.K_UP]:
                player.update(0, -tile_height, n, m)
            if key[pygame.K_LEFT]:
                player.update(-tile_width, 0, n, m)
            if key[pygame.K_RIGHT]:
                player.update(tile_width, 0, n, m)
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
    pygame.mixer.music.stop()

show_screen('победа.jpg')

pygame.quit()
terminate()