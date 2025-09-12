import pygame
import sys
import random

# === Config ===
BOARD_SIZE = 10       # n x n board
CELL_SIZE = 50        # pixel size of each cell
FPS = 10              # frames per second
INITIAL_LIFE = 30     # starting life (seconds)
ITEM_SPAWN_RATE = 2000  # in milliseconds (every 2 seconds)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)    # Player
GREEN = (0, 255, 0)   # Item
RED = (255, 0, 0)     # Life bar

# === Init Pygame ===
pygame.init()
screen = pygame.display.set_mode(
    (BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE + 40)
)
pygame.display.set_caption("Async Game Demo - Step 2")
clock = pygame.time.Clock()

# === Player State ===
player_pos = [BOARD_SIZE // 2, BOARD_SIZE // 2]  # start at center
life = INITIAL_LIFE

# === Items ===
items = []  # list of (x, y) positions

# Setup custom timers
LIFE_EVENT = pygame.USEREVENT + 1
ITEM_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(LIFE_EVENT, 1000)   # decrease life every second
pygame.time.set_timer(ITEM_EVENT, ITEM_SPAWN_RATE)  # spawn items


def draw_board():
    """Draw grid, player, items, and life bar."""
    screen.fill(BLACK)

    # Draw grid
    for x in range(0, BOARD_SIZE * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, BOARD_SIZE * CELL_SIZE))
    for y in range(0, BOARD_SIZE * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (BOARD_SIZE * CELL_SIZE, y))

    # Draw items
    for ix, iy in items:
        rect = pygame.Rect(
            ix * CELL_SIZE,
            iy * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(screen, GREEN, rect)

    # Draw player
    rect = pygame.Rect(
        player_pos[0] * CELL_SIZE,
        player_pos[1] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )
    pygame.draw.rect(screen, BLUE, rect)

    # Draw life bar
    pygame.draw.rect(
        screen,
        RED,
        (10, BOARD_SIZE * CELL_SIZE + 10, life * 5, 20)
    )

    pygame.display.flip()


def handle_input():
    """Move player with WASD keys."""
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player_pos[1] > 0:
        player_pos[1] -= 1
    elif keys[pygame.K_s] and player_pos[1] < BOARD_SIZE - 1:
        player_pos[1] += 1
    elif keys[pygame.K_a] and player_pos[0] > 0:
        player_pos[0] -= 1
    elif keys[pygame.K_d] and player_pos[0] < BOARD_SIZE - 1:
        player_pos[0] += 1


def check_item_collision():
    """Check if player collected an item."""
    global life
    for i, (ix, iy) in enumerate(items):
        if player_pos[0] == ix and player_pos[1] == iy:
            items.pop(i)
            life += 5  # increase life when item collected
            break


# === Main Loop ===
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == LIFE_EVENT:
            life -= 1
            if life <= 0:
                print("Game Over!")
                running = False

        elif event.type == ITEM_EVENT:
            # Spawn random item if space is free
            new_item = (
                random.randint(0, BOARD_SIZE - 1),
                random.randint(0, BOARD_SIZE - 1)
                )
            if new_item not in items and new_item != tuple(player_pos):
                items.append(new_item)

    handle_input()
    check_item_collision()
    draw_board()
    clock.tick(FPS)

pygame.quit()
sys.exit()
