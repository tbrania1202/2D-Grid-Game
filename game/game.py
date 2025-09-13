import pygame
import sys
import random
import asyncio

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
RED = (255, 0, 0)     # Opponent
PINK = (255, 100, 150)  # Life bar

# === Init Pygame ===
pygame.init()
screen = pygame.display.set_mode(
    (BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE + 40)
)
pygame.display.set_caption("Async Game Demo - Pure Async")
font = pygame.font.SysFont(None, 36)

# === Player State ===
player_pos = [BOARD_SIZE // 2, BOARD_SIZE // 2]  # start at center
life = INITIAL_LIFE

# === Items ===
items = []  # list of (x, y) positions

# === Opponent (async controlled) ===
opponent_pos = [0, 0]  # top-left corner initially


def draw_board():
    """Draw grid, player, items, opponent, and life bar."""
    screen.fill(BLACK)

    # Draw grid
    for x in range(0, BOARD_SIZE * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, BOARD_SIZE * CELL_SIZE))
    for y in range(0, BOARD_SIZE * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (BOARD_SIZE * CELL_SIZE, y))

    # Draw items
    for ix, iy in items:
        rect = pygame.Rect(
            ix * CELL_SIZE, iy * CELL_SIZE,
            CELL_SIZE, CELL_SIZE
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

    # Draw opponent
    rect = pygame.Rect(
        opponent_pos[0] * CELL_SIZE,
        opponent_pos[1] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )
    pygame.draw.rect(screen, RED, rect)

    # Draw life bar
    pygame.draw.rect(
        screen,
        PINK,
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


def check_opponent_collision():
    """Check if opponent touches player."""
    return (
        player_pos[0] == opponent_pos[0]
        and player_pos[1] == opponent_pos[1]
    )


# === Async Opponent Task ===
async def move_opponent():
    """Async task that moves opponent randomly every second."""
    while True:
        await asyncio.sleep(1)  # move every second
        direction = random.choice(["up", "down", "left", "right"])
        if direction == "up" and opponent_pos[1] > 0:
            opponent_pos[1] -= 1
        elif direction == "down" and opponent_pos[1] < BOARD_SIZE - 1:
            opponent_pos[1] += 1
        elif direction == "left" and opponent_pos[0] > 0:
            opponent_pos[0] -= 1
        elif direction == "right" and opponent_pos[0] < BOARD_SIZE - 1:
            opponent_pos[0] += 1


# === Async Item Spawner ===
async def spawn_items():
    """Spawn items periodically."""
    while True:
        await asyncio.sleep(ITEM_SPAWN_RATE / 1000)
        new_item = (
            random.randint(0, BOARD_SIZE - 1),
            random.randint(0, BOARD_SIZE - 1)
        )
        if new_item not in items and new_item != tuple(player_pos):
            items.append(new_item)


# === Main Async Game Loop ===
async def main():
    global life
    clock_interval = 1 / FPS
    last_life_tick = pygame.time.get_ticks()

    # Start background tasks
    asyncio.create_task(move_opponent())
    asyncio.create_task(spawn_items())

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player input
        handle_input()

        # Check collisions
        check_item_collision()
        if check_opponent_collision():
            print("Game Over! Opponent caught you.")
            running = False

        # Decrease life every 1 second
        now = pygame.time.get_ticks()
        if now - last_life_tick >= 1000:
            life -= 1
            last_life_tick = now
            if life <= 0:
                print("Game Over! Out of life.")
                running = False

        # Draw everything
        draw_board()

        # Async wait instead of clock.tick()
        await asyncio.sleep(clock_interval)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
