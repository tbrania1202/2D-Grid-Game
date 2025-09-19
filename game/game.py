import pygame
import sys
import random
import asyncio
import threading
import time
import multiprocessing as mp
import psutil  # for system stats

# === Config ===
BOARD_SIZE = 10
CELL_SIZE = 50
FPS = 10
INITIAL_LIFE = 30
ITEM_SPAWN_RATE = 2000  # ms
SPAWN_ITEM_EVENT = pygame.USEREVENT + 1  # custom event ID

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)      # Player
GREEN = (0, 255, 0)     # Item
RED = (255, 0, 0)       # Async Opponent
ORANGE = (255, 165, 0)  # Thread Opponent
PURPLE = (160, 32, 240)  # Process Opponent
PINK = (255, 100, 150)

# === Player State ===
player_pos = [BOARD_SIZE // 2, BOARD_SIZE // 2]
life = INITIAL_LIFE

# === Items ===
items = []

# === Opponents ===
async_opponent = [0, 0]               # red
thread_opponent = [BOARD_SIZE-1, BOARD_SIZE-1]  # orange
process_opponent = [0, BOARD_SIZE-1]  # purple


# === Draw Functions ===
def draw_board():
    screen.fill(BLACK)
    for x in range(0, BOARD_SIZE * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, BOARD_SIZE * CELL_SIZE))
    for y in range(0, BOARD_SIZE * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (BOARD_SIZE * CELL_SIZE, y))
    # Items
    for ix, iy in items:
        rect = pygame.Rect(
            ix * CELL_SIZE,
            iy * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(screen, GREEN, rect)
    # Player
    rect = pygame.Rect(
        player_pos[0] * CELL_SIZE,
        player_pos[1] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )
    pygame.draw.rect(screen, BLUE, rect)
    # Opponents
    rect = pygame.Rect(
        async_opponent[0] * CELL_SIZE,
        async_opponent[1] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )
    pygame.draw.rect(screen, RED, rect)
    rect = pygame.Rect(
        thread_opponent[0] * CELL_SIZE,
        thread_opponent[1] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )
    pygame.draw.rect(screen, ORANGE, rect)
    rect = pygame.Rect(
        process_opponent[0] * CELL_SIZE,
        process_opponent[1] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )
    pygame.draw.rect(screen, PURPLE, rect)
    # Life bar
    pygame.draw.rect(
        screen,
        PINK,
        (10, BOARD_SIZE * CELL_SIZE + 10, life * 5, 20)
    )
    text = font.render(f"Life: {life}", True, WHITE)
    screen.blit(
        text,
        (BOARD_SIZE * CELL_SIZE - 120, BOARD_SIZE * CELL_SIZE + 8)
    )

    # === System Stats ===
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    threads = threading.active_count()
    stats_text = font.render(
        f"CPU: {cpu}%  MEM: {mem}%  Threads: {threads}", True, WHITE
    )
    screen.blit(stats_text, (10, BOARD_SIZE * CELL_SIZE + 40))

    pygame.display.flip()


def handle_input():
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
    global life
    for i, (ix, iy) in enumerate(items):
        if player_pos[0] == ix and player_pos[1] == iy:
            items.pop(i)
            life += 5
            break


def check_collisions():
    if player_pos == async_opponent:
        print("Game Over! Async Opponent caught you.")
        return True
    if player_pos == thread_opponent:
        print("Game Over! Thread Opponent caught you.")
        return True
    if player_pos == process_opponent:
        print("Game Over! Process Opponent caught you.")
        return True
    return False


# === Async Opponent ===
async def move_async_opponent():
    while True:
        await asyncio.sleep(1)
        direction = random.choice(["up", "down", "left", "right"])
        if direction == "up" and async_opponent[1] > 0:
            async_opponent[1] -= 1
        elif direction == "down" and async_opponent[1] < BOARD_SIZE - 1:
            async_opponent[1] += 1
        elif direction == "left" and async_opponent[0] > 0:
            async_opponent[0] -= 1
        elif direction == "right" and async_opponent[0] < BOARD_SIZE - 1:
            async_opponent[0] += 1


# === Thread Opponent ===
def move_thread_opponent():
    while True:
        time.sleep(1.5)
        direction = random.choice(["up", "down", "left", "right"])
        if direction == "up" and thread_opponent[1] > 0:
            thread_opponent[1] -= 1
        elif direction == "down" and thread_opponent[1] < BOARD_SIZE - 1:
            thread_opponent[1] += 1
        elif direction == "left" and thread_opponent[0] > 0:
            thread_opponent[0] -= 1
        elif direction == "right" and thread_opponent[0] < BOARD_SIZE - 1:
            thread_opponent[0] += 1


# === Process Opponent Worker ===
def process_opponent_worker(queue, start_pos, board_size):
    pos = start_pos[:]
    while True:
        time.sleep(2)
        direction = random.choice(["up", "down", "left", "right"])
        if direction == "up" and pos[1] > 0:
            pos[1] -= 1
        elif direction == "down" and pos[1] < board_size - 1:
            pos[1] += 1
        elif direction == "left" and pos[0] > 0:
            pos[0] -= 1
        elif direction == "right" and pos[0] < board_size - 1:
            pos[0] += 1
        queue.put(pos)


# === Main Async Game Loop ===
async def main():
    global life, process_opponent

    clock_interval = 1 / FPS
    last_life_tick = pygame.time.get_ticks()

    # Initialize Pygame
    pygame.init()
    global screen, font
    screen = pygame.display.set_mode(
        (BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE + 80)
    )
    pygame.display.set_caption("Game Demo - System Stats Added")
    font = pygame.font.SysFont(None, 36)
    pygame.time.set_timer(SPAWN_ITEM_EVENT, ITEM_SPAWN_RATE)

    # Start async opponent
    asyncio.create_task(move_async_opponent())

    # Start thread opponent
    t = threading.Thread(target=move_thread_opponent, daemon=True)
    t.start()

    # Start process opponent
    q = mp.Queue()
    p = mp.Process(
        target=process_opponent_worker,
        args=(q, process_opponent, BOARD_SIZE),
        daemon=True
    )
    p.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == SPAWN_ITEM_EVENT:
                new_item = (
                    random.randint(0, BOARD_SIZE - 1),
                    random.randint(0, BOARD_SIZE - 1)
                )
                if new_item not in items and new_item != tuple(player_pos):
                    items.append(new_item)

        handle_input()
        check_item_collision()

        # Receive process opponent updates
        try:
            while not q.empty():
                process_opponent = q.get_nowait()
        except Exception:
            pass

        if check_collisions():
            running = False

        # Life countdown
        now = pygame.time.get_ticks()
        if now - last_life_tick >= 1000:
            life -= 1
            last_life_tick = now
            if life <= 0:
                print("Game Over! Out of life.")
                running = False

        draw_board()
        await asyncio.sleep(clock_interval)

    pygame.quit()
    sys.exit()

# === Entry Point ===
if __name__ == "__main__":
    mp.set_start_method("spawn")
    asyncio.run(main())
