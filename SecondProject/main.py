import pygame
import sys
import os
import math

pygame.init()
FPS = 72
size = WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
goblin_hp = 0.80
zombie_hp = 0.85
skeleton_hp = 0.65


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print(f'Файл с изображением "{fullname} не найден"')
        raise SystemExit(message)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


all_sprites = SpriteGroup()
tiles_group = SpriteGroup()
mobs_group = SpriteGroup()
bullets_group = SpriteGroup()


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('wall', x, y)
            elif level[y][x] == '*':
                Tile('path', x, y)
            elif level[y][x] == ',':
                Tile('t_place', x, y)
            elif level[y][x] == '!':
                Tile('g_down', x, y)
            elif level[y][x] == '?':
                Tile('g_up', x, y)
            elif level[y][x] == '|':
                Tile('tower', x, y)
    return x, y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    text = 'Press any button to start the game!'
    font = pygame.font.Font(None, 60)
    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    output = font.render(text, True, pygame.Color('white'))
    screen.blit(output, (630, 700))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {
    'wall': load_image('grass.png', None),
    'path': load_image('path.png', None),
    't_place': load_image('stone.png', None),
    'g_up': load_image('g_up.png', None),
    'g_down': load_image('g_down.png', None),
    'tower': load_image('tower.png'),
    'zombie': load_image('zombie.png'),
    'skeleton': load_image('skeleton.png'),
    'goblin': load_image('goblin.png'),
    'ct1': load_image('choosert_tile.png', ),
    'ct2': load_image('choosett_tile.png'),
    't_tower': load_image('t_tower.png'),
    'r_tower': load_image('r_tower.png'),
    'rt': load_image('r_tower2.png'),
    'bullet': load_image('bullet.png'),
    'rocket': load_image('r.png'),
    'r2': load_image('r2.png'),
    'explosion': load_image('explosion.png'),
    'heart': load_image('heart_9.png'),
    'dat': load_image('dat_tower.png'),
    'dr': load_image('dr_tower.png'),
    'dr2': load_image('dr_tower2.png'),
    'adr': load_image('adr_tower.png'),
    'adr2': load_image('adr_tower2.png'),
    'at': load_image('at_tower.png'),
    'm': load_image('money.png'),
    'u': load_image('up.png')
}
tile_width = tile_height = 120


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


def get_cell(mouse_pos):
    cell_x = mouse_pos[0] // 120
    cell_y = mouse_pos[1] // 120
    if cell_x < 0 or cell_x >= WIDTH or cell_y < 0 or cell_y >= HEIGHT:
        return None
    return cell_x, cell_y


b_places = [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 1), (7, 1), (8, 1), (11, 2), (12, 2), (13, 2),
            (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 7), (7, 7), (8, 7), (11, 6), (12, 6), (13, 6)]
u_places = []


class zombie(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, mobs_group)
        self.x = 1
        self.frames = []
        self.cut_sheet(tile_images['zombie'], 3, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(self.x, 480)
        self.count = 0
        self.hp = 100 * zombie_hp
        self.pos = self.x
        self.dead = False

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        global balance, t_balance
        if not self.dead:
            if self.count % 10 == 0:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(self.x, 0)
            self.pos += self.x
            self.count += 1
            if self.hp <= 0:
                self.__del__()
                self.dead = True
            if self.dead:
                balance += 30
                t_balance += 30
                self.pos = 0

    def __del__(self):
        self.kill()
        del self


class skeleton(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, mobs_group)
        self.x = 2
        self.frames = []
        self.dead = False
        self.cut_sheet(tile_images['skeleton'], 9, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(self.x, 480)
        self.count = 0
        self.hp = 100 * skeleton_hp
        self.pos = self.x

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        global balance, t_balance
        if not self.dead:
            if self.count % 10 == 0:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(self.x, 0)
            self.pos += self.x
            self.count += 1
            if self.hp <= 0:
                self.__del__()
                self.dead = True
            if self.dead:
                balance += 20
                t_balance += 20
                self.pos = 0

    def __del__(self):
        self.kill()
        del self


class goblin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, mobs_group)
        self.x = 3
        self.dead = False
        self.frames = []
        self.cut_sheet(tile_images['goblin'], 8, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(self.x, 480)
        self.count = 0
        self.hp = 100 * goblin_hp
        self.pos = self.x

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        global balance, t_balance
        if not self.dead:
            if self.count % 10 == 0:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(self.x, 0)
            self.pos += self.x
            self.count += 1
            if self.hp <= 0:
                self.__del__()
                self.dead = True
            if self.dead:
                balance += 15
                t_balance += 15
                self.pos = 0

    def __del__(self):
        self.kill()
        del self


def spawn(m_type):
    if m_type == 'zombie':
        z = zombie()
        mobs.append(z)
        mobs_x.append(z.pos)
    if m_type == 'skeleton':
        s = skeleton()
        mobs.append(s)
        mobs_x.append(s.pos)
    if m_type == 'goblin':
        g = goblin()
        mobs.append(g)


class choose_tiles1(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images['ct1']
        self.rect = self.image.get_rect().move(x - 120, y - 60)

    def __del__(self):
        self.kill()


class choose_tiles2(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images['ct2']
        self.rect = self.image.get_rect().move(x, y - 60)

    def __del__(self):
        self.kill()


class t_tower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images['t_tower']
        self.rect = self.image.get_rect().move(x - 60, y - 60)
        self.x = x
        self.y = y
        self.count = 1
        self.dmg = 40
        self.speed = 72 / 2

    def shoot(self, angle):
        if self.count % self.speed == 0 and mobs_x:
            bul = bullet(self.x - 60, self.y - 60, angle, self.dmg)

    def update(self):
        if mobs_x:
            self.image = tile_images['t_tower']
            rel_x = first - self.x
            rel_y = 480 - self.y
            angle = math.atan2(rel_y, rel_x)
            angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
            self.image = pygame.transform.rotate(self.image, int(angle))
            self.rect = self.image.get_rect(center=(self.x, self.y))
            self.count += 1
            self.shoot(angle)

    def __del__(self):
        self.kill()


class at_tower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images['at']
        self.rect = self.image.get_rect().move(x - 60, y - 60)
        self.x = x
        self.y = y
        self.count = 1
        self.dmg = 90
        self.speed = 72 / 3

    def shoot(self, angle):
        if self.count % self.speed == 0 and mobs_x:
            bul = bullet(self.x - 60, self.y - 60, angle, self.dmg)

    def update(self):
        if mobs_x:
            self.image = tile_images['at']
            rel_x = first - self.x
            rel_y = 480 - self.y
            angle = math.atan2(rel_y, rel_x)
            angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
            self.image = pygame.transform.rotate(self.image, int(angle))
            self.rect = self.image.get_rect(center=(self.x, self.y))
            self.count += 1
            self.shoot(angle)

    def __del__(self):
        self.kill()


class dat_tower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images['dat']
        self.rect = self.image.get_rect().move(x - 60, y - 60)
        self.x = x
        self.y = y
        self.count = 1
        self.dmg = 150
        self.speed = 72 / 4

    def shoot(self, angle):
        if self.count % self.speed == 0 and mobs_x:
            bul = bullet(self.x - 60, self.y - 60, angle, self.dmg)

    def update(self):
        if mobs_x:
            self.image = tile_images['dat']
            rel_x = first - self.x
            rel_y = 480 - self.y
            angle = math.atan2(rel_y, rel_x)
            angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
            self.image = pygame.transform.rotate(self.image, int(angle))
            self.rect = self.image.get_rect(center=(self.x, self.y))
            self.count += 1
            self.shoot(angle)

    def __del__(self):
        self.kill()


class r_tower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images['r_tower']
        self.x = x
        self.y = y
        self.rect = self.image.get_rect().move(x - 60, y - 60)
        self.count = 1
        self.speed = 72 * 3
        self.dmg = 300

    def update(self):
        self.image = tile_images['r_tower']
        if mobs_x:
            rel_x = first - self.x
            rel_y = 480 - self.y
            angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
            self.image = pygame.transform.rotate(self.image, int(angle))
            self.rect = self.image.get_rect(center=(self.x, self.y))
            self.count += 1
            self.shoot(angle)

    def shoot(self, angle):
        if self.count % self.speed == 0 and mobs_x:
            bul = Rocket(self.x - 60, self.y - 60, angle, self.dmg)

    def __del__(self):
        self.kill()


class dr_tower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images['dr']
        self.rect = self.image.get_rect().move(x - 60, y - 60)
        self.x = x
        self.y = y
        self.count = 1
        self.dmg = 450
        self.speed = 72 * 2

    def shoot(self, angle):
        if self.count % self.speed == 0 and mobs_x:
            bul = bullet(self.x - 60, self.y - 60, angle, self.dmg)

    def update(self):
        if mobs_x:
            self.image = tile_images['dr']
            rel_x = first - self.x
            rel_y = 480 - self.y
            angle = math.atan2(rel_y, rel_x)
            angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
            self.image = pygame.transform.rotate(self.image, int(angle))
            self.rect = self.image.get_rect(center=(self.x, self.y))
            self.count += 1
            self.shoot(angle)

    def __del__(self):
        self.kill()


class adr_tower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images['adr']
        self.rect = self.image.get_rect().move(x - 60, y - 60)
        self.x = x
        self.y = y
        self.dmg = 600
        self.count = 1
        self.speed = round(72 * 1.5)

    def shoot(self, angle):
        if self.count % self.speed == 0 and mobs_x:
            bul = bullet(self.x - 60, self.y - 60, angle, self.dmg)

    def update(self):
        if mobs_x:
            self.image = tile_images['adr']
            rel_x = first - self.x
            rel_y = 480 - self.y
            angle = math.atan2(rel_y, rel_x)
            angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
            self.image = pygame.transform.rotate(self.image, int(angle))
            self.rect = self.image.get_rect(center=(self.x, self.y))
            self.count += 1
            self.shoot(angle)

    def __del__(self):
        self.kill()


class explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(tile_images['explosion'], 1, 4)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x + 60, y + 60)
        self.count = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if self.count % 3 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.frames[-1] == self.frames[self.cur_frame]:
                self.kill()
        self.count += 1


class bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, damage):
        super().__init__(all_sprites, bullets_group)
        self.image = tile_images['bullet']
        self.image = pygame.transform.rotate(self.image, int(angle))
        self.rect = self.image.get_rect().move(x, y)
        self.x = x
        self.y = y
        self.x1 = (max(mobs_x) - x) / 3
        self.y1 = (480 - y) / 5
        self.dmg = damage

    def update(self):
        self.x += self.x1
        self.y += self.y1
        self.rect = self.image.get_rect().move(self.x, self.y)
        for m in mobs:
            if pygame.sprite.spritecollide(m, bullets_group, True):
                if mobs_x:
                    mobs[mobs_x.index(max(mobs_x))].hp -= self.dmg
        if not mobs_x:
            self.kill()


class heart(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = tile_images['heart']
        self.rect = self.image.get_rect().move(x, y)


class Rocket(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, damage):
        super().__init__(all_sprites, bullets_group)
        self.image = tile_images['rocket']
        self.image = pygame.transform.rotate(self.image, int(angle))
        self.rect = self.image.get_rect().move(x, y)
        self.x = x
        self.y = y
        self.x1 = (max(mobs_x) - x) / 3
        self.y1 = (480 - y) / 5
        self.dmg = damage

    def update(self):
        self.x += self.x1
        self.y += self.y1
        self.rect = self.image.get_rect().move(self.x, self.y)
        for m in mobs:
            if pygame.sprite.spritecollide(m, bullets_group, True):
                if mobs_x:
                    exp = explosion(self.x, self.y)
                    mobs[mobs_x.index(max(mobs_x))].hp -= self.dmg
        if not mobs_x:
            self.kill()


class Tower(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images['tower']
        self.rect = self.image.get_rect().move(1700, 420)


class up_button(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = tile_images['u']
        self.rect = self.image.get_rect().move(x, y)


def new_wave():
    global z_limit, s_limit, g_limit, killed, wave, zc, sc, gc, nw, goblin_hp, zombie_hp, skeleton_hp
    z_limit += 3
    s_limit += 2
    g_limit += 3
    zc = 0
    sc = 0
    wave += 1
    gc = 0
    killed = 0
    goblin_hp += 0.20
    zombie_hp += 0.30
    skeleton_hp += 0.15
    nw = True


start_screen()
types = []
output = None
nw = False
t_count = 0
count = 1
z_limit = 3
s_limit = 8
g_limit = 5
zc = 0
sc = 0
gc = 0
killed = 0
tower_hp = 3
running = True
k = False
k1 = False
k2 = False
level_x, level_y = generate_level(load_level("map.map"))
z = Tower()
i = None
i1 = None
t = []
mobs = []
towers = []
mobs_x = []
u = False
wave = 0
show = False
rg = False
balance = 300
t_balance = 300
buttons = []
upping = False
hearts = [heart(1800, 60), heart(1850, 60), heart(1750, 60)]
new_wave()
while running:
    screen.fill(pygame.Color('Black'))
    tiles_group.draw(screen)
    all_sprites.draw(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:
            g = get_cell(event.pos)
            if g in b_places and not rg:
                k2 = False
                click_pos = event.pos
                if i and i1:
                    k1 = True
                k = True
                if not k1:
                    cg = get_cell(event.pos)
                    center = ((g[0] + 1) * 120 - 60, (g[1] + 1) * 120 - 60)
                k = True
            elif g in u_places and not rg:
                type = types[u_places.index(g)]
                ti = u_places.index(g)
                tt = towers[u_places.index(g)]
                if type == 1:
                    text_c = 'cost: 250'
                    cost = 250
                if type == 2:
                    text_c = 'cost: 400'
                    cost = 400
                if type == 3:
                    text_c = 'cost 600'
                    cost = 600
                if type == 4:
                    text_c = 'cost 900'
                    cost = 900
                s_center = ((g[0] + 1) * 120, (g[1] + 1) * 120 - 60)
                font = pygame.font.SysFont('Comic Sans MS', 20)
                output_c = font.render(text_c, True, pygame.Color('white'))
                show = True
                upb = up_button(center[0], center[1])
                buttons.append(upb)
                rg = True
                continue
            if rg:
                if event.pos[0] in range(s_center[0], s_center[0] + 120) and \
                        event.pos[1] in range(s_center[1] + 30, s_center[1] + 70) \
                        and balance - cost >= 0 and type == 1:
                    x = tt.x
                    y = tt.y + 10
                    tt.kill()
                    types[ti] = 3
                    for u in buttons:
                        u.kill()
                    balance -= cost
                    show = False
                    i2 = at_tower(x, y)
                    rg = False
                if event.pos[0] in range(s_center[0], s_center[0] + 120) and \
                        event.pos[1] in range(s_center[1] + 30, s_center[1] + 70) \
                        and type == 2:
                    if balance - cost >= 0:
                        x = tt.x
                        y = tt.y + 10
                        tt.kill()
                        balance -= cost
                        types[ti] = 4
                        for u in buttons:
                            u.kill()
                        show = False
                        i2 = dr_tower(x, y)
                        rg = False
                if event.pos[0] in range(s_center[0], s_center[0] + 120) and \
                        event.pos[1] in range(s_center[1] + 30, s_center[1] + 70) \
                        and type == 3:
                    if balance - cost >= 0:
                        x = tt.x
                        balance -= cost
                        types[ti] = 5
                        y = tt.y + 10
                        tt.kill()
                        for u in buttons:
                            u.kill()
                        show = False
                        i2 = dat_tower(x, y)
                        rg = False
                if event.pos[0] in range(s_center[0], s_center[0] + 120) and \
                        event.pos[1] in range(s_center[1] + 30, s_center[1] + 70) \
                        and type == 4:
                    if balance - cost >= 0:
                        balance -= cost
                        x = tt.x
                        y = tt.y + 10
                        tt.kill()
                        types[ti] = 6
                        for u in buttons:
                            u.kill()
                        show = False
                        i2 = adr_tower(x, y)
                        rg = False
                else:
                    for u in buttons:
                        u.kill()
                    show = False
                    rg = False
    if show:
        screen.blit(output_c, (s_center[0] + 10, s_center[1] - 30))
    if count % 170 == 0:
        if zc < z_limit:
            spawn('zombie')
            zc += 1
    if count % 120 == 0:
        if sc < s_limit:
            spawn('skeleton')
            sc += 1
    if count % 100 == 0:
        if gc < g_limit:
            spawn('goblin')
            gc += 1
    if tower_hp == 2:
        hearts[-1].kill()
    elif tower_hp == 1:
        hearts[-1].kill()
    elif tower_hp == 0:
        hearts[-1].kill()
    b_text = f'balance: {balance}'
    b_font = pygame.font.SysFont('Comic Sans MS', 20)
    b_output = b_font.render(b_text, True, pygame.Color('white'))
    screen.blit(b_output, (20, 20))
    if k:
        if i and i1:
            i.__del__()
            i1.__del__()
            i = None
            i1 = None
        if k1:
            if click_pos[0] in range(center[0] + 10, center[0] + 150) and \
                    click_pos[1] in range(center[1] - 60, center[1] + 60):
                if balance - 100 >= 0:
                    balance -= 100
                    i2 = t_tower(center[0], center[1])
                    k2 = True
                    towers.append(i2)
                    b_places.remove(cg)
                    types.append(1)
                    u_places.append(cg)
            elif click_pos[0] in range(center[0] - 120, center[0] - 10) and \
                    click_pos[1] in range(center[1] - 60, center[1] + 60):
                if balance - 100 >= 0:
                    balance -= 100
                    i2 = r_tower(center[0], center[1])
                    k2 = True
                    b_places.remove(cg)
                    types.append(2)
                    towers.append(i2)
                    u_places.append(cg)
            else:
                k = False
                i = None
                i1 = None
                continue
            k1 = False
        if not k2:
            i = choose_tiles1(center[0], center[1])
            i1 = choose_tiles2(center[0], center[1])
        k = False
    all_sprites.update()
    mobs_x = []
    if nw:
        text = 'NEW WAVE'
        text1 = f'WAVE {wave}'
        font = pygame.font.SysFont('Comic Sans MS', 200)
        font1 = pygame.font.SysFont('Comic Sans MS', 150)
        output = font.render(text, True, pygame.Color('white'))
        output1 = font1.render(text1, True, pygame.Color('White'))
        screen.blit(output, (360, 300))
        screen.blit(output1, (600, 500))
        t_count += 1
        if t_count % 150 == 0 and t_count != 0:
            t_count = 0
            nw = False
    for mob in mobs:
        if mob.hp <= 0:
            mobs.remove(mob)
            killed += 1
            continue
        mobs_x.append(mob.pos)
        first = max(mobs_x)
    if pygame.sprite.spritecollide(z, mobs_group, True):
        tower_hp -= 1
    if tower_hp <= 0:
        z.kill()
        terminate()
    if killed == z_limit + g_limit + s_limit:
        new_wave()
    pygame.display.flip()
    count += 1
    clock.tick(FPS)
