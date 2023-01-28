import pygame
import os
import sys
import random
from time import sleep


pygame.init()

size = width, height = 1280, 720
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

SCORE = 0
score2 = SCORE
FPS = 50
lives = 4
V = 5

GRAVITY = 0.5

all_sprites = pygame.sprite.Group()
all_pipis = pygame.sprite.Group()
all_specialpipis = pygame.sprite.Group()
all_bombs = pygame.sprite.Group()
all_hearts = pygame.sprite.Group()
stars = pygame.sprite.Group()
new_lvl = pygame.sprite.Group()

all_score = 0


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)

    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


# начальный экран
def start_screen():
    pygame.mixer.music.load("data/start.mp3")
    pygame.mixer.music.play(-1)

    fon = pygame.transform.scale(load_image('start.jpg'), (width, height))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame\
                    .QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    pygame.mixer.music.pause()
                    return
        pygame.display.flip()
        clock.tick(FPS)


# экран проигрыша
def loose_screen():

    pygame.mixer.music.load("data/loose.mp3")

    clock = pygame.time.Clock()

    subsurf = pygame.surface.Surface((1280, 720))
    all_sprites = pygame.sprite.Group()

    spamton = pygame.sprite.Group()
    sprite = pygame.sprite.Sprite()
    all_sprites.add(sprite)
    image = load_image('lostpic.png')
    sprite.image = image
    sprite.rect = image.get_rect()

    x = 0 - sprite.rect.width
    pygame.mixer.music.play(-1)

    mh = pygame.sprite.Sprite()

    images = [pygame.transform.scale(load_image('spamton_defeat/6.png'),
                                     (load_image('spamton_defeat/6.png').get_width() * 3,
                                     load_image('spamton_defeat/6.png').get_height() * 3)),
              pygame.transform.scale(load_image('spamton_defeat/7.png'),
                                     (load_image('spamton_defeat/7.png').get_width() * 3,
                                     load_image('spamton_defeat/7.png').get_height() * 3))]

    spamton.add(mh)

    mh.image = images[0]
    mh.rect = images[0].get_rect()
    mh.rect.x = 1000
    mh.rect.y = 20

    c = 0
    running = True
    timer = 0

    with open('data/top_result.txt', 'r+') as file:
        n = int(file.read())
        if all_score > n:
            f = open('data/top_result.txt', 'w')
            f.write(str(all_score))
            f.close()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.draw(subsurf)
        spamton.draw(subsurf)
        screen.blit(subsurf, (x, 0))

        if x < 1280 - sprite.rect.width:
            x += 10
        if timer % 5 == 0:
            if c == 0:
                mh.image = images[0]
                c = 1
            else:
                mh.image = images[1]
                c = 0

        pygame.display.flip()
        clock.tick(50)
        timer += 1
    pygame.quit()


screen_rect = (0, 0, width, height)


# рассыпающиеся звёзды
class Particle(pygame.sprite.Sprite):

    fire = [pygame.transform.scale(load_image("star.png"), (load_image("star.png").get_width() / 30,
                                                            load_image("star.png").get_height() / 30))]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(stars)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

        self.gravity = GRAVITY

    def update(self):

        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        if not self.rect.colliderect(screen_rect):
            self.kill()


# генерация звёзд
def create_particles(position):
    particle_count = 20
    numbers = range(-5, 6)

    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


# падающие объекты, которые надо поймать
class Pipis(pygame.sprite.Sprite):

    image = load_image("pipis.png")

    def __init__(self):
        super().__init__(all_pipis)
        self.sprite = pygame.sprite.Sprite()
        self.image = pygame.transform.scale(Pipis.image, (Pipis.image.get_width() * 1.5,
                                                          Pipis.image.get_height() * 1.5))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = random.randint(0 + self.image.get_width(), 1280 - self.image.get_width())
        self.rect.y = 0
        self.f = True

    def update(self, v):
        self.rect = self.rect.move(0, v)

        if self.f:
            if pygame.sprite.collide_mask(self, mh):
                self.f = False
                sound = pygame.mixer.Sound("data/gotcha.mp3")
                pygame.mixer.music.set_volume(0.5)
                sound.play()
                return True
        else:
            return False

    def explode(self):
        self.image = load_image('no.png')


# счёт игры
class Score(pygame.sprite.Sprite):
    image = load_image('score.png')

    def __init__(self):
        super().__init__(all_sprites)
        pygame.font.init()
        self.sprite = pygame.sprite.Sprite()
        self.img = Pipis.image
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.score = 0

    def update(self, num):
        self.score = num

    def draw(self):
        font = pygame.font.Font('Comic Sans MS.ttf', 20)
        text = font.render(str(self.score), True, '#ff74e6')
        screen.blit(text, (40, 40))


# жизни игрока
class Hearts(pygame.sprite.Sprite):

    image = pygame.transform.scale(pygame.image.load('data/hearts/4.png'),
                                   (pygame.image.load('data/hearts/4.png').get_width() * 4,
                                    pygame.image.load('data/hearts/4.png').get_height() * 4))

    def __init__(self):
        super().__init__(all_hearts)
        self.sprite = pygame.sprite.Sprite()
        self.img = Hearts.image
        self.rect = self.image.get_rect()
        self.rect.x = 120
        self.rect.y = -10

    def update(self, number):
        if number == 4:
            self.image = pygame.transform.scale(load_image('hearts/4.png'),
                                                (load_image('hearts/4.png').get_width() * 4,
                                                 load_image('hearts/4.png').get_height() * 4))
        elif number == 3:
            self.image = pygame.transform.scale(load_image('hearts/3.png'),
                                                (load_image('hearts/4.png').get_width() * 4,
                                                 load_image('hearts/4.png').get_height() * 4))
        elif number == 2:
            self.image = pygame.transform.scale(load_image('hearts/2.png'),
                                                (load_image('hearts/4.png').get_width() * 4,
                                                 load_image('hearts/4.png').get_height() * 4))
        elif number == 1:
            self.image = pygame.transform.scale(load_image('hearts/1.png'),
                                                (load_image('hearts/4.png').get_width() * 4,
                                                 load_image('hearts/4.png').get_height() * 4))
        elif number == 0:
            self.image = pygame.transform.scale(load_image('hearts/0.png'),
                                                (load_image('hearts/4.png').get_width() * 4,
                                                 load_image('hearts/4.png').get_height() * 4))
            return True
        return False


# особые падающие объекты, восстанавливающие одну жизнь
class Special(pygame.sprite.Sprite):

    image = load_image("special_pipis.png")

    def __init__(self):
        super().__init__(all_specialpipis)
        self.sprite = pygame.sprite.Sprite()
        self.image = pygame.transform.scale(Special.image,
                                            (Special.image.get_width() * 1.5,
                                             Special.image.get_height() * 1.5))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = random.randint(0 + self.image.get_width(), 1280 - self.image.get_width())
        self.rect.y = 0
        self.f = True

    def update(self, v):
        self.rect = self.rect.move(0, v)

        if self.f:
            if pygame.sprite.collide_mask(self, mh):
                self.f = False
                wow = pygame.mixer.Sound("data/wow.mp3")
                pygame.mixer.music.set_volume(0.5)
                wow.play()
                return True
        else:
            return False

    def get_coords(self):
        return (self.rect.x, self.rect.y)

    def explode(self):
        self.image = load_image('no.png')


# падающие бомбы, отнимающие жизнь
class Bomb(pygame.sprite.Sprite):

    image = load_image("bomb.png")

    def __init__(self):
        super().__init__(all_bombs)
        self.sprite = pygame.sprite.Sprite()
        self.image = pygame.transform.scale(load_image("bomb.png"),
                                            (load_image("bomb.png").get_width() * 1.5,
                                             load_image("bomb.png").get_height() * 1.5))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = random.randint(0 + self.image.get_width(), 1280 - self.image.get_width())
        self.rect.y = 0
        self.f = True

    def update(self, v):
        self.rect = self.rect.move(0,  v)

        if self.f:
            if pygame.sprite.collide_mask(self, mh):
                self.f = False
                boom = pygame.mixer.Sound("data/boom.mp3")
                pygame.mixer.music.set_volume(0.1)
                boom.play()
                return True
        else:
            return False

    def explode(self):
        self.image = load_image('no.png')


# игрок
class Main_Spamton(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__(all_sprites)
        self.standing = [load_image('spamton_staystill/stay1.png'),
                         load_image('spamton_staystill/stay1.png'),
                         load_image('spamton_staystill/stay2.png'),
                         load_image('spamton_staystill/stay2.png')]
        self.g = 0
        self.sprite = pygame.sprite.Sprite()
        self.image = pygame.transform.scale(self.standing[0],
                                            (self.standing[0].get_width() * 2.5,
                                             self.standing[0].get_height() * 2.5))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 0
        self.rect.y = 720 - self.image.get_height() - 80
        pygame.mixer.music.load("data/theme.mp3")
        pygame.mixer.music.play(-1)

    def move(self, coords):
        self.rect.x = coords[0]
        self.rect.y = coords[1]
        self.rect.move(coords[0], coords[1])

    def get_coords(self):
        return (self.rect.x, self.rect.y)

    def width(self):
        return self.image.get_width()

    def change_sprite(self):
        if self.g < 3:
            self.g += 1

        else:
            self.g = 0
        self.image = pygame.transform.scale(self.standing[self.g],
                                            (self.standing[self.g].get_width() * 2.5,
                                             self.standing[self.g].get_height() * 2.5))


def new_level(c):
    imgs = [load_image('LEVEL.png'), load_image('no.png')]
    sprite = pygame.sprite.Sprite()
    new_lvl.add(sprite)
    sprite.image = imgs[c]
    sprite.rect = sprite.image.get_rect()
    new_lvl.draw(screen)
    pygame.display.flip()
    sleep(1)


start_screen()

player_score = Score()
background = load_image('background.jpg')
rect = background.get_rect()
mh = Main_Spamton()

go_left = False
go_right = False
c = 0
live_score = Hearts()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                go_right = True
            if event.key == pygame.K_LEFT:
                go_left = True
        if event.type == pygame.KEYUP:
            go_left, go_right = False, False

    if go_right:
        if mh.get_coords()[0] == 1280:
            mh.move((0 - mh.width(), mh.get_coords()[1]))
        else:
            mh.move((mh.get_coords()[0] + 25, mh.get_coords()[1]))

    if go_left:
        if mh.get_coords()[0] == 0 - mh.width():
            mh.move((1280, mh.get_coords()[1]))
        else:
            mh.move((mh.get_coords()[0] - 25, mh.get_coords()[1]))

    if SCORE != score2:
        player_score.update(SCORE)
        score2 = SCORE

    for i in all_pipis:
        if i.update(V):
            SCORE += 5
            all_score += 5
            i.explode()

    for i in all_specialpipis:
        if i.update(V):
            SCORE += 15
            all_score += 15
            i.explode()
            create_particles(i.get_coords())
            if lives < 4:
                lives += 1

    for i in all_bombs:
        if i.update(V):
            SCORE -= 15
            all_score -= 15
            i.explode()
            lives -= 1
    for i in stars:
        i.update()

    pygame.display.update()
    screen.blit(background, rect)
    all_sprites.draw(screen)
    all_pipis.draw(screen)
    all_specialpipis.draw(screen)
    all_bombs.draw(screen)
    stars.draw(screen)
    player_score.draw()


    for i in all_hearts:
        if i.update(lives):
            loose_screen()
            break

    all_hearts.draw(screen)
    pygame.display.flip()
    mh.change_sprite()

    if SCORE >= 100:
        # новый уровень
        new_level(0)

        V += 5
        SCORE = 0


    clock.tick(30)
    c += 1
    if c % 20 == 0:
        num = random.choice([0, 0, 1, 2, 2])
        if num == 0:
            pipis = Pipis()
        elif num == 1:
            pipis = Special()
        elif num == 2:
            pipis = Bomb()

pygame.quit()
