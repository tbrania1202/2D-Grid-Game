import pygame
import sys

# === Config ===
BOARD_SIZE = 10      # n x n board
CELL_SIZE = 50       # pixel size of each cell
FPS = 10             # frames per second

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# === Init Pygame ===
pygame.init()
screen = pygame.display.set_mode(
    (BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE)
)
pygame.display.set_caption("Async Game Demo - Step 1")
clock = pygame.time.Clock()

# === Player State ===
player_pos = [BOARD_SIZE // 2, BOARD_SIZE // 2]  # start at center


def draw_board():
    """Draw grid and player."""
    screen.fill(BLACK)

    # Draw grid lines
    for x in range(0, BOARD_SIZE * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, BOARD_SIZE * CELL_SIZE))
    for y in range(0, BOARD_SIZE * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (BOARD_SIZE * CELL_SIZE, y))

    # Draw player
    rect = pygame.Rect(
        player_pos[0] * CELL_SIZE,
        player_pos[1] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )
    pygame.draw.rect(screen, BLUE, rect)

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


# === Main Loop ===
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    handle_input()
    draw_board()
    clock.tick(FPS)
