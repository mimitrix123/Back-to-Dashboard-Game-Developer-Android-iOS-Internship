import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 960, 540
FPS = 60
GRAVITY = 0.65
MOVE_SPEED = 5
JUMP_SPEED = -13

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Week 2 - Platformer Level")
clock = pygame.time.Clock()

FONT = pygame.font.Font(None, 30)
BIG_FONT = pygame.font.Font(None, 54)

# Level geometry: x, y, width, height
STATIC_PLATFORMS = [
    pygame.Rect(0, 490, 960, 50),
    pygame.Rect(40, 400, 190, 20),
    pygame.Rect(300, 330, 180, 20),
    pygame.Rect(560, 420, 170, 20),
    pygame.Rect(760, 300, 160, 20),
    pygame.Rect(470, 210, 170, 20),
]

class MovingPlatform:
    def __init__(self, x, y, w, h, left, right, speed=2):
        self.rect = pygame.Rect(x, y, w, h)
        self.left = left
        self.right = right
        self.speed = speed
        self.direction = 1
        self.dx = 0

    def update(self):
        old_x = self.rect.x
        self.rect.x += self.speed * self.direction
        if self.rect.left <= self.left:
            self.rect.left = self.left
            self.direction = 1
        elif self.rect.right >= self.right:
            self.rect.right = self.right
            self.direction = -1
        self.dx = self.rect.x - old_x

    def draw(self):
        pygame.draw.rect(screen, (90, 170, 240), self.rect, border_radius=5)

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.collected = False

    def rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def draw(self):
        if not self.collected:
            pygame.draw.circle(screen, (255, 215, 45), (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, (255, 245, 140), (int(self.x), int(self.y)), self.radius - 3, 2)

class Enemy:
    def __init__(self, x, y, left, right):
        self.rect = pygame.Rect(x, y, 38, 34)
        self.left = left
        self.right = right
        self.speed = 2.2
        self.direction = 1

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= self.left:
            self.rect.left = self.left
            self.direction = 1
        elif self.rect.right >= self.right:
            self.rect.right = self.right
            self.direction = -1

    def draw(self):
        pygame.draw.rect(screen, (220, 70, 75), self.rect, border_radius=7)
        pygame.draw.circle(screen, (255, 255, 255), (self.rect.x + 11, self.rect.y + 10), 4)
        pygame.draw.circle(screen, (255, 255, 255), (self.rect.x + 27, self.rect.y + 10), 4)

def make_level():
    moving = [
        MovingPlatform(110, 270, 120, 18, 70, 370, 2.0),
        MovingPlatform(650, 180, 120, 18, 600, 900, 2.4),
    ]
    coins = [
        Coin(135, 365), Coin(355, 295), Coin(620, 385),
        Coin(820, 265), Coin(555, 175), Coin(260, 235),
        Coin(735, 145),
    ]
    enemy = Enemy(330, 296, 300, 442)
    return moving, coins, enemy

def reset_player():
    return pygame.Rect(80, 350, 34, 40), 0.0, 0.0

def draw_player(player):
    pygame.draw.rect(screen, (75, 220, 120), player, border_radius=6)
    pygame.draw.circle(screen, (255, 255, 255), (player.x + 10, player.y + 11), 4)
    pygame.draw.circle(screen, (255, 255, 255), (player.x + 24, player.y + 11), 4)

def draw_text(text, pos, font=FONT):
    screen.blit(font.render(text, True, (245, 245, 245)), pos)

def main():
    moving_platforms, coins, enemy = make_level()
    player, vx, vy = reset_player()
    lives = 3
    score = 0
    on_ground = False
    standing_platform = None
    game_over = False
    won = False

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and (game_over or won):
                moving_platforms, coins, enemy = make_level()
                player, vx, vy = reset_player()
                lives, score = 3, 0
                game_over, won = False, False

        if not game_over and not won:
            keys = pygame.key.get_pressed()
            vx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) * MOVE_SPEED
            vx -= (keys[pygame.K_LEFT] or keys[pygame.K_a]) * MOVE_SPEED

            if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and on_ground:
                vy = JUMP_SPEED
                on_ground = False

            for platform in moving_platforms:
                platform.update()
            enemy.update()

            # Carry the player with a moving platform while standing on it.
            if standing_platform is not None and on_ground:
                player.x += standing_platform.dx

            player.x += vx
            player.x = max(0, min(WIDTH - player.width, player.x))

            vy += GRAVITY
            old_bottom = player.bottom
            player.y += vy
            on_ground = False
            standing_platform = None

            platforms = STATIC_PLATFORMS + [p.rect for p in moving_platforms]

            # Resolve vertical landing only when falling.
            if vy >= 0:
                for platform in platforms:
                    if player.right > platform.left and player.left < platform.right:
                        if old_bottom <= platform.top and player.bottom >= platform.top:
                            player.bottom = platform.top
                            vy = 0
                            on_ground = True
                            if any(platform is p.rect for p in moving_platforms):
                                standing_platform = next(p for p in moving_platforms if p.rect is platform)
                            break

            # Head bump against platforms.
            if vy < 0:
                for platform in platforms:
                    if player.right > platform.left and player.left < platform.right:
                        if player.top <= platform.bottom <= player.bottom:
                            player.top = platform.bottom
                            vy = 0
                            break

            # Collect coins.
            for coin in coins:
                if not coin.collected and player.colliderect(coin.rect()):
                    coin.collected = True
                    score += 1

            # Enemy contact costs one life and respawns player.
            if player.colliderect(enemy.rect):
                lives -= 1
                player, vx, vy = reset_player()
                on_ground = False
                standing_platform = None
                if lives <= 0:
                    game_over = True

            # Falling off the level costs a life.
            if player.top > HEIGHT:
                lives -= 1
                player, vx, vy = reset_player()
                on_ground = False
                standing_platform = None
                if lives <= 0:
                    game_over = True

            if score == len(coins):
                won = True

        screen.fill((25, 32, 52))

        # Simple sky bands.
        pygame.draw.rect(screen, (35, 45, 70), (0, 0, WIDTH, 490))

        for platform in STATIC_PLATFORMS:
            pygame.draw.rect(screen, (105, 75, 50), platform, border_radius=5)
        for platform in moving_platforms:
            platform.draw()

        for coin in coins:
            coin.draw()

        enemy.draw()
        draw_player(player)

        draw_text(f"Coins: {score}/{len(coins)}", (20, 18))
        draw_text(f"Lives: {lives}", (20, 50))
        draw_text("Move: A/D or ←/→   Jump: W/↑/Space", (260, 18))

        if game_over or won:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 165))
            screen.blit(overlay, (0, 0))
            message = "LEVEL COMPLETE!" if won else "GAME OVER"
            title = BIG_FONT.render(message, True, (255, 255, 255))
            screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
            draw_text("Press R to restart", (WIDTH // 2 - 85, HEIGHT // 2 + 25))

        pygame.display.flip()

if __name__ == "__main__":
    main()
