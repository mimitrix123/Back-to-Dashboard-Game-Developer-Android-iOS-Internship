import random
import sys

import pygame

# Window
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
BACKGROUND = (20, 24, 35)
WHITE = (245, 245, 245)
PLAYER_COLOR = (80, 170, 255)
OBJECT_COLORS = [(255, 100, 100), (255, 190, 70), (110, 220, 140), (190, 120, 255)]

# Gameplay
PLAYER_WIDTH, PLAYER_HEIGHT = 110, 22
PLAYER_SPEED = 8
OBJECT_SIZE = 28
OBJECT_SPEED_MIN, OBJECT_SPEED_MAX = 3, 7
SPAWN_INTERVAL_MS = 650


class FallingObject:
    def __init__(self):
        self.rect = pygame.Rect(
            random.randint(0, WIDTH - OBJECT_SIZE),
            -OBJECT_SIZE,
            OBJECT_SIZE,
            OBJECT_SIZE,
        )
        self.speed = random.randint(OBJECT_SPEED_MIN, OBJECT_SPEED_MAX)
        self.color = random.choice(OBJECT_COLORS)

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=7)


def draw_text(screen, font, text, position):
    surface = font.render(text, True, WHITE)
    screen.blit(surface, position)


def reset_game():
    player = pygame.Rect(
        WIDTH // 2 - PLAYER_WIDTH // 2,
        HEIGHT - 55,
        PLAYER_WIDTH,
        PLAYER_HEIGHT,
    )
    objects = []
    score = 0
    missed = 0
    return player, objects, score, missed


def main():
    pygame.init()
    pygame.display.set_caption("Catch the Falling Objects")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 34)
    title_font = pygame.font.Font(None, 56)
    small_font = pygame.font.Font(None, 26)

    player, objects, score, missed = reset_game()
    game_over = False

    SPAWN_OBJECT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_OBJECT, SPAWN_INTERVAL_MS)

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == SPAWN_OBJECT and not game_over:
                objects.append(FallingObject())

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
                player, objects, score, missed = reset_game()
                game_over = False

        keys = pygame.key.get_pressed()

        if not game_over:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.x += PLAYER_SPEED

            # Keep the player inside the screen.
            player.x = max(0, min(WIDTH - PLAYER_WIDTH, player.x))

            for obj in objects[:]:
                obj.update()

                if obj.rect.colliderect(player):
                    score += 1
                    objects.remove(obj)
                elif obj.rect.top > HEIGHT:
                    missed += 1
                    objects.remove(obj)

            # A simple difficulty increase as the score grows.
            if score and score % 10 == 0:
                for obj in objects:
                    obj.speed = min(obj.speed + 0.002 * dt, 12)

            if missed >= 5:
                game_over = True

        screen.fill(BACKGROUND)

        # Header
        draw_text(screen, font, f"Score: {score}", (20, 18))
        draw_text(screen, font, f"Missed: {missed}/5", (WIDTH - 145, 18))

        # Instructions
        draw_text(
            screen,
            small_font,
            "Move: ← → or A/D   |   Catch the falling objects",
            (20, HEIGHT - 28),
        )

        # Game objects
        pygame.draw.rect(screen, PLAYER_COLOR, player, border_radius=8)
        for obj in objects:
            obj.draw(screen)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))

            title = title_font.render("GAME OVER", True, WHITE)
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 45))
            screen.blit(title, title_rect)

            draw_text(
                screen,
                font,
                f"Final Score: {score}",
                (WIDTH // 2 - 75, HEIGHT // 2 + 5),
            )
            draw_text(
                screen,
                small_font,
                "Press R to play again or close the window to exit.",
                (WIDTH // 2 - 170, HEIGHT // 2 + 45),
            )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
