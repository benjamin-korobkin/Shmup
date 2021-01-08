# Pygame template
# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
# <http://creativecommons.org/licenses/by/3.0/>
# Art from Kenney.nl

# From bfxr, select 'Export Wav' when creating sound
import pygame
from pygame import image as img
import random
from pygame import sprite as spr
from os import path

img_dir = path.join(path.dirname(__file__), 'img')
sound_dir = path.join(path.dirname(__file__), 'sound')

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 600
FPS = 60
POWERUP_TIME = 6500

# Images and colors
# bg = img.load('bg.jpg')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Initialize pygame and create window
pygame.init()
pygame.mixer.init()  # Sound control
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Shmup!")
clock = pygame.time.Clock()

# Search through fonts on your machine and get closes match. Otherwise, include font file on your project.
font_name = pygame.font.match_font('arial')
def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)  # True -> anti-aliased text
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)  # set midtop of obj rect
    surface.blit(text_surface, text_rect)

def draw_shield_bar(surface, x, y, percentage):
    if percentage < 0:
        percentage = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (percentage / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)  # 2px thick line

def draw_lives(surface, x, y, lives, image):
    for life_num in range(lives):
        SPACE_GAP = 5
        image_rect = image.get_rect()
        image_rect.x = x + ((image_rect.width + SPACE_GAP) * life_num)
        image_rect.y = y
        surface.blit(image, image_rect)

def newMob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

class Player(spr.Sprite):
    def __init__(self):
        spr.Sprite.__init__(self)
        # scale the image. OG size is 99x75px. This is (approx) half that
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK) # Hid the black to make image transparent
        self.rect = self.image.get_rect()
        # Give a radius for smoother collision detection
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WINDOW_WIDTH / 2
        self.rect.bottom = WINDOW_HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 300  # in ms
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hidden_timer = pygame.time.get_ticks()
        self.power_level = 1
        self.power_timer = pygame.time.get_ticks()

    def update(self):
        # timeout for powerups
        if self.power_level > 1 and pygame.time.get_ticks() - self.power_timer > POWERUP_TIME:
            self.power_level -= 1
            self.power_timer = pygame.time.get_ticks()

        # un-hide if hidden
        if self.hidden and pygame.time.get_ticks() - self.hidden_timer > 1000:
            self.hidden = False
            self.rect.centerx = WINDOW_WIDTH / 2
            self.rect.bottom = WINDOW_HEIGHT - 10
        self.speedx = 0
        keystate = pygame.key.get_pressed()  # get all pressed keys
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power_level >= 1:
                bullet_default = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet_default)
                bullets.add(bullet_default)
                # shoot_sound.play()  # Sound is kind of annoying
            if self.power_level >= 2:
                bullet_right = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet_right)
                bullets.add(bullet_right)
            if self.power_level >= 3:
                bullet_left = Bullet(self.rect.left, self.rect.centery)
                all_sprites.add(bullet_left)
                bullets.add(bullet_left)

    def powerup(self):
        self.power_level += 1
        self.power_timer = pygame.time.get_ticks()


    def hide(self):
        # Temporarily hide player
        self.hidden = True
        self.hidden_timer = pygame.time.get_ticks()
        self.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT + 1000)  # Move the ship off screen

class Mob(spr.Sprite):
    def __init__(self):
        spr.Sprite.__init__(self)
        self.image_og = random.choice(meteor_images)
        self.image_og.set_colorkey(BLACK)
        self.image = self.image_og.copy()  # Copy so we can smoothly rotate original
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()  # Time last updated image, goes by clock
        self.spawn()

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # If enemy goes off bottom or sides, randomize its location at the top
        if self.rect.top > WINDOW_HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WINDOW_WIDTH + 20:
            self.spawn()

    def spawn(self):
        self.rect.x = random.randrange(WINDOW_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedx = random.randrange(-2, 2)
        self.speedy = random.randrange(1, 8)

    def rotate(self):
        now = pygame.time.get_ticks()
        # Current time - time last update. e.g now=1000, last_update=900, it's been 100ms
        # If I understand correctly, this updates every 50ms
        if now - self.last_update > 50:
            self.last_update = now
            self.rotation = (self.rotation + self.rotation_speed) % 360
            # We rotate the original of the image bc img info is lost every rotation
            new_image = pygame.transform.rotate(self.image_og, self.rotation)
            # Need to recenter image for proper rotation
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

class Bullet(spr.Sprite):
    def __init__(self, x, y):
        spr.Sprite.__init__(self)
        self.image = laser_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        #  remove it moves off screen
        if self.rect.bottom < 0:
            self.kill()

class Powerup(spr.Sprite):
    def __init__(self, center):
        spr.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 5

    def update(self):
        self.rect.y += self.speedy
        #  remove if it moves off screen
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class Explosion(spr.Sprite):
    def __init__(self, center, size):
        spr.Sprite.__init__(self)
        self.size = size
        self.image = explosion_animation[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        EXPLOSION_FPS = 30
        self.frame_rate = EXPLOSION_FPS

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_animation[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_animation[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

def show_game_over_scrn():
    screen.blit(background, background_rect)
    draw_text(screen, "SHMUP!", 64, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
    draw_text(screen, "Press any key to begin", 18, WINDOW_WIDTH / 2, WINDOW_HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)  # He says this is to control speed of the loop
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                waiting = False
                pygame.quit()
            if e.type == pygame.KEYUP:  # pygame.KEYDOWN is too fast
                waiting = False

# Load all graphics
background = img.load(path.join(img_dir, "space_background.png")).convert()
background_rect = background.get_rect()
player_img = img.load(path.join(img_dir, "playerShip1_blue.png")).convert()
mini_plyr_img = pygame.transform.scale(player_img, (25, 19))
mini_plyr_img.set_colorkey(BLACK)
# meteor_img = pygame.image.load(path.join(img_dir, "meteorBrown_med1.png")).convert()
laser_img = img.load(path.join(img_dir, "laserRed16.png")).convert()
meteor_images = []
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_big2.png', 'meteorBrown_med1.png', 'meteorBrown_med2.png',
               'meteorBrown_small1.png', 'meteorBrown_small2.png', 'meteorBrown_tiny1.png']
for image in meteor_list:
    meteor_images.append(img.load(path.join(img_dir, image)).convert())

explosion_animation = {}
explosion_animation['large'] = []
explosion_animation['small'] = []
explosion_animation['player'] = []
for i in range(9):
    filename = 'explosions/regularExplosion0{}.png'.format(i)
    image = img.load(path.join(img_dir, filename)).convert()
    image.set_colorkey(BLACK)
    LARGE_EXPLOSION_SCALE = 48
    img_lg = pygame.transform.scale(image, (LARGE_EXPLOSION_SCALE, LARGE_EXPLOSION_SCALE))
    explosion_animation['large'].append(img_lg)
    SMALL_EXPLOSION_SCALE = 32
    img_sm = pygame.transform.scale(image, (SMALL_EXPLOSION_SCALE, SMALL_EXPLOSION_SCALE))
    explosion_animation['small'].append(img_sm)
    filename = 'explosions/sonicExplosion0{}.png'.format(i)
    image = img.load(path.join(img_dir, filename)).convert()
    image.set_colorkey(BLACK)
    explosion_animation['player'].append(image)

powerup_images = {}
powerup_images['shield'] = img.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = img.load(path.join(img_dir, 'bolt_gold.png')).convert()

# Load all sounds - relies on pygame.mixer.init() above
shoot_sound = pygame.mixer.Sound(path.join(sound_dir, 'Laser_Shoot.wav'))
shield_sound = pygame.mixer.Sound(path.join(sound_dir, 'Shield_up.wav'))
powerup_sound = pygame.mixer.Sound(path.join(sound_dir, 'Powerup.wav'))
explosion_sounds = []
for sound in ['Explosion.wav', 'Explosion2.wav']:
    explosion_sounds.append(pygame.mixer.Sound(path.join(sound_dir, sound)))
for es in explosion_sounds:
    es.set_volume(0.4)
player_die_sound = pygame.mixer.Sound(path.join(sound_dir, 'rumble.ogg'))
pygame.mixer.music.load(path.join(sound_dir, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.3)

pygame.mixer.music.play(loops=-1)  # Infinite loop
# Game loop
game_over = True
game_running = True
while game_running:
    if game_over:
        show_game_over_scrn()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = spr.Group()
        bullets = spr.Group()
        powerups = spr.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            newMob()
        score = 0

    # Keep loop running at the right speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False

    # Update
    all_sprites.update()

    #  *******COLLISIONS*******
    # Check if bullet hit mob
    hits = spr.groupcollide(mobs, bullets, True, True)  # delete both bullet and mob if collision
    for hit in hits:
        score += 100 - hit.radius  # get more points for hitting smaller objects
        random.choice(explosion_sounds).play()
        explosion = Explosion(hit.rect.center, 'large')
        all_sprites.add(explosion)
        if random.random() > 0.955:
            powerup = Powerup(hit.rect.center)
            all_sprites.add(powerup)
            powerups.add(powerup)
        newMob()

    # Check if mob hit player. returns a list (hits)
    hits = spr.spritecollide(player, mobs, True, spr.collide_circle)  # control if it gets deleted
    for hit in hits:
        player.shield -= hit.radius * 2
        explosion = Explosion(hit.rect.center, 'small')
        all_sprites.add(explosion)
        newMob()
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100
            player.power_level = 1

    # Check if player caught powerup
    hits = spr.spritecollide(player, powerups, True)  # make sprite disappear
    for hit in hits:
        if hit.type == 'shield':
            player.shield += 20  # random.randrange(10, 30)
            shield_sound.play()
            if player.shield > 100:
                player.shield = 100
        if hit.type == 'gun':
            powerup_sound.play()
            player.powerup()

    #  If player died and explosion has finished playing
    if player.lives == 0 and not death_explosion.alive():
        game_over = True

    # Draw / render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WINDOW_WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WINDOW_WIDTH - 100, 5, player.lives, mini_plyr_img)
    # *after* drawing everything, flip the display
    pygame.display.flip()  # This means show everything to the player

pygame.quit()