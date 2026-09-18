import io
import math
import random
import struct
import sys
import wave

import pygame

pygame.init()
try:
    pygame.mixer.init()
    AUDIO_ENABLED = True
except pygame.error:
    AUDIO_ENABLED = False

WIDTH, HEIGHT = 960, 540
TILE = 40
FPS = 60
GRAVITY = 0.65
MOVE_SPEED = 4.8
JUMP_SPEED = -12.5

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Week 3 - Tilemap Adventure")
clock = pygame.time.Clock()
FONT = pygame.font.Font(None, 28)
BIG_FONT = pygame.font.Font(None, 56)

# # = solid tile, . = empty, C = coin, D = door/flag, E = patrol spawn, H = chase spawn.
TILEMAP = [
    "########################",
    "#......................#",
    "#......................#",
    "#........C.............#",
    "#....####..............#",
    "#................C.....#",
    "#.........#####........#",
    "#..C...................#",
    "#......####............#",
    "#......................#",
    "#.............C........#",
    "#....#####.............#",
    "#......................#",
    "#..C.............C....D#",
    "########################",
]

MAP_W = len(TILEMAP[0])
MAP_H = len(TILEMAP)


def tile_rect(tx, ty):
    return pygame.Rect(tx * TILE, ty * TILE, TILE, TILE)


def load_level():
    solids = []
    coins = []
    door = None
    patrol_spawn = (120, 360)
    chase_spawn = (700, 320)

    for y, row in enumerate(TILEMAP):
        for x, cell in enumerate(row):
            if cell == "#":
                solids.append(tile_rect(x, y))
            elif cell == "C":
                coins.append(Coin(x * TILE + TILE // 2, y * TILE + TILE // 2))
            elif cell == "D":
                door = tile_rect(x, y)
            elif cell == "E":
                patrol_spawn = (x * TILE + 3, y * TILE - 34)
            elif cell == "H":
                chase_spawn = (x * TILE + 3, y * TILE - 34)

    return solids, coins, door, patrol_spawn, chase_spawn


def make_tone(frequency, duration=0.10, volume=0.18):
    """Create a tiny WAV tone in memory so the project needs no audio assets."""
    if not AUDIO_ENABLED:
        return None

    sample_rate = 22050
    frames = int(sample_rate * duration)
    raw = bytearray()
    for i in range(frames):
        envelope = 1.0 - (i / frames)
        sample = int(32767 * volume * envelope * math.sin(2 * math.pi * frequency * i / sample_rate))
        raw.extend(struct.pack("<h", sample))

    data = io.BytesIO()
    with wave.open(data, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(raw)

    data.seek(0)
    return pygame.mixer.Sound(file=data)


class Coin:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.collected = False

    @property
    def rect(self):
        return pygame.Rect(self.x - 9, self.y - 9, 18, 18)

    def draw(self):
        if not self.collected:
            pygame.draw.circle(screen, (255, 215, 45), (self.x, self.y), 9)
            pygame.draw.circle(screen, (255, 245, 150), (self.x, self.y), 5, 2)


class Enemy:
    def __init__(self, x, y, mode, left, right):
        self.rect = pygame.Rect(x, y, 32, 34)
        self.mode = mode
        self.left = left
        self.right = right
        self.speed = 1.8 if mode == "patrol" else 2.15
        self.direction = 1

    def update(self, player):
        if self.mode == "patrol":
            self.rect.x += self.speed * self.direction
            if self.rect.left <= self.left:
                self.rect.left = self.left
                self.direction = 1
            elif self.rect.right >= self.right:
                self.rect.right = self.right
                self.direction = -1
        else:
            # Chase only when the player is reasonably close.
            if abs(player.centerx - self.rect.centerx) < 300:
                self.direction = 1 if player.centerx > self.rect.centerx else -1
                self.rect.x += self.speed * self.direction
                self.rect.x = max(self.left, min(self.right - self.rect.width, self.rect.x))

    def draw(self):
        body = (220, 75, 75) if self.mode == "patrol" else (170, 80, 220)
        pygame.draw.rect(screen, body, self.rect, border_radius=7)
        pygame.draw.circle(screen, (255, 255, 255), (self.rect.x + 9, self.rect.y + 10), 3)
        pygame.draw.circle(screen, (255, 255, 255), (self.rect.x + 23, self.rect.y + 10), 3)


def draw_tilemap(solids):
    screen.fill((22, 29, 48))
    for rect in solids:
        pygame.draw.rect(screen, (70, 91, 110), rect)
        pygame.draw.rect(screen, (100, 125, 145), rect, 1)


def move_player(player, vx, vy, solids):
    player.x += int(vx)
    for block in solids:
        if player.colliderect(block):
            if vx > 0:
                player.right = block.left
            elif vx < 0:
                player.left = block.right

    vy += GRAVITY
    player.y += int(vy)
    on_ground = False
    for block in solids:
        if player.colliderect(block):
            if vy > 0:
                player.bottom = block.top
                vy = 0
                on_ground = True
            elif vy < 0:
                player.top = block.bottom
                vy = 0

    return vy, on_ground


def draw_player(player):
    pygame.draw.rect(screen, (70, 215, 125), player, border_radius=6)
    pygame.draw.circle(screen, (255, 255, 255), (player.x + 9, player.y + 10), 3)
    pygame.draw.circle(screen, (255, 255, 255), (player.x + 24, player.y + 10), 3)


def draw_door(rect, unlocked):
    color = (80, 210, 120) if unlocked else (190, 85, 70)
    pygame.draw.rect(screen, color, rect.inflate(-8, -4), border_radius=5)
    pygame.draw.circle(screen, (255, 225, 90), (rect.right - 13, rect.centery), 3)


def draw_hud(score, total, lives):
    screen.blit(FONT.render(f"Coins: {score}/{total}", True, (245, 245, 245)), (15, 12))
    screen.blit(FONT.render(f"Lives: {lives}", True, (245, 245, 245)), (15, 42))
    screen.blit(FONT.render("Move: A/D or ←/→   Jump: W/↑/Space", True, (245, 245, 245)), (270, 12))


def main():
    solids, coins, door, patrol_spawn, chase_spawn = load_level()
    player = pygame.Rect(80, 430, 30, 38)
    spawn = player.topleft
    lives = 3
    score = 0
    won = False
    game_over = False
    on_ground = False

    patrol = Enemy(patrol_spawn[0], patrol_spawn[1], "patrol", 80, 500)
    chase = Enemy(chase_spawn[0], chase_spawn[1], "chase", 520, 860)

    coin_sound = make_tone(880, 0.09, 0.20)
    hit_sound = make_tone(160, 0.18, 0.20)
    finish_sound = make_tone(1200, 0.25, 0.22)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and (won or game_over):
                solids, coins, door, patrol_spawn, chase_spawn = load_level()
                player = pygame.Rect(80, 430, 30, 38)
                lives, score = 3, 0
                won, game_over, on_ground = False, False, False
                patrol = Enemy(patrol_spawn[0], patrol_spawn[1], "patrol", 80, 500)
                chase = Enemy(chase_spawn[0], chase_spawn[1], "chase", 520, 860)

        if not won and not game_over:
            keys = pygame.key.get_pressed()
            vx = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                vx -= MOVE_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                vx += MOVE_SPEED
            vy = getattr(main, "vy", 0.0)

            if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and on_ground:
                vy = JUMP_SPEED
                on_ground = False

            vy, on_ground = move_player(player, vx, vy, solids)
            main.vy = vy

            patrol.update(player)
            chase.update(player)

            for coin in coins:
                if not coin.collected and player.colliderect(coin.rect):
                    coin.collected = True
                    score += 1
                    if coin_sound:
                        coin_sound.play()

            if player.colliderect(patrol.rect) or player.colliderect(chase.rect):
                lives -= 1
                if hit_sound:
                    hit_sound.play()
                player.topleft = spawn
                main.vy = 0.0
                on_ground = False
                if lives <= 0:
                    game_over = True

            unlocked = score == len(coins)
            if unlocked and door and player.colliderect(door):
                won = True
                if finish_sound:
                    finish_sound.play()

        draw_tilemap(solids)
        unlocked = score == len(coins)
        if door:
            draw_door(door, unlocked)
        for coin in coins:
            coin.draw()
        patrol.draw()
        chase.draw()
        draw_player(player)
        draw_hud(score, len(coins), lives)

        if not unlocked:
            screen.blit(FONT.render("Collect all coins to unlock the door.", True, (255, 225, 120)), (270, 45))
        else:
            screen.blit(FONT.render("Door unlocked! Reach the finish.", True, (120, 240, 150)), (270, 45))

        if won or game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))
            title = "LEVEL COMPLETE!" if won else "GAME OVER"
            text = BIG_FONT.render(title, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 25)))
            sub = FONT.render("Press R to restart", True, (245, 245, 245))
            screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

        pygame.display.flip()


if __name__ == "__main__":
    main()
