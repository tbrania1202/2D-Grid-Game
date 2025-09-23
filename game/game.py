import pygame
import sys
import random
import asyncio
import threading
import time
import multiprocessing as mp
import psutil

# === Config ===
BOARD_SIZE = 12
CELL_SIZE = 50
FPS = 10
INITIAL_LIFE = 30
ITEM_SPAWN_RATE = 2000  # ms
SPAWN_ITEM_EVENT = pygame.USEREVENT + 1  # custom event ID
ASYNC_OPPONENT_SLEEP = 1
THREAD_OPPONENT_SLEEP = 1
PROCESS_OPPONENT_SLEEP = 1

# === Colors ===
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)      # Player
GREEN = (0, 255, 0)     # Item
RED = (255, 0, 0)       # Async Opponenta
ORANGE = (255, 165, 0)  # Thread Opponent
PURPLE = (160, 32, 240)  # Process Opponent
PINK = (255, 100, 150)

# === Player State ===
player_pos = [BOARD_SIZE // 2, BOARD_SIZE // 2]
life = INITIAL_LIFE

# === Items ===
items = []

# === Opponents ===
corners = [
    [0, 0],
    [0, BOARD_SIZE - 1],
    [BOARD_SIZE - 1, 0],
    [BOARD_SIZE - 1, BOARD_SIZE - 1]
]
async_opponents = [[0, 0]]
thread_opponents = [[BOARD_SIZE-1, BOARD_SIZE-1]]
process_opponents = [[0, BOARD_SIZE-1]]

# === Process management ===
process_queues = []
processes = []


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
    # Async opponents
    for pos in async_opponents:
        rect = pygame.Rect(
            pos[0] * CELL_SIZE,
            pos[1] * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(screen, RED, rect)
    # Thread opponents
    for pos in thread_opponents:
        rect = pygame.Rect(
            pos[0] * CELL_SIZE,
            pos[1] * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(screen, ORANGE, rect)
    # Process opponents
    for pos in process_opponents:
        rect = pygame.Rect(
            pos[0] * CELL_SIZE,
            pos[1] * CELL_SIZE,
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
        (BOARD_SIZE * CELL_SIZE - 150, BOARD_SIZE * CELL_SIZE + 8)
    )

    # === System Stats ===
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    threads = threading.active_count()
    processes_count = len(processes)
    stats_text = f"CPU: {cpu}%  MEM: {mem}%  "
    stats_text += f"Threads: {threads}  Procs: {processes_count}"
    text = font.render(stats_text, True, WHITE)
    screen.blit(text, (10, BOARD_SIZE * CELL_SIZE + 40))

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


def check_item_collision(loop):
    global life

    # Player collision
    for i, (ix, iy) in enumerate(items):
        if player_pos[0] == ix and player_pos[1] == iy:
            items.pop(i)
            life += 5
            return

    # Async opponents
    for pos in async_opponents:
        for i, (ix, iy) in enumerate(items):
            if pos[0] == ix and pos[1] == iy:
                items.pop(i)
                new_pos = random.choice(corners)
                async_opponents.append(new_pos)
                loop.create_task(move_single_async_opponent(new_pos))
                return

    # Thread opponents
    for pos in thread_opponents:
        for i, (ix, iy) in enumerate(items):
            if pos[0] == ix and pos[1] == iy:
                items.pop(i)
                new_pos = random.choice(corners)
                thread_opponents.append(new_pos)
                t = threading.Thread(
                    target=move_single_thread_opponent,
                    args=(new_pos,),
                    daemon=True
                )
                t.start()
                return

    # Process opponents
    for pos in process_opponents:
        for i, (ix, iy) in enumerate(items):
            if pos[0] == ix and pos[1] == iy:
                items.pop(i)
                new_pos = random.choice(corners)
                process_opponents.append(new_pos)
                q = mp.Queue()
                p = mp.Process(
                    target=process_opponent_worker,
                    args=(q, [new_pos], BOARD_SIZE),
                    daemon=True
                )
                p.start()
                process_queues.append(q)
                processes.append(p)
                return


def check_collisions():
    for pos in async_opponents + thread_opponents + process_opponents:
        if player_pos == pos:
            print("Game Over! Opponent caught you.")
            return True
    return False


# === Async Opponents ===
async def move_single_async_opponent(pos):
    while True:
        await asyncio.sleep(ASYNC_OPPONENT_SLEEP)
        direction = random.choice(["up", "down", "left", "right"])
        if direction == "up" and pos[1] > 0:
            pos[1] -= 1
        elif direction == "down" and pos[1] < BOARD_SIZE - 1:
            pos[1] += 1
        elif direction == "left" and pos[0] > 0:
            pos[0] -= 1
        elif direction == "right" and pos[0] < BOARD_SIZE - 1:
            pos[0] += 1


# === Thread Opponents ===
def move_single_thread_opponent(pos):
    while True:
        time.sleep(THREAD_OPPONENT_SLEEP)
        direction = random.choice(["up", "down", "left", "right"])
        if direction == "up" and pos[1] > 0:
            pos[1] -= 1
        elif direction == "down" and pos[1] < BOARD_SIZE - 1:
            pos[1] += 1
        elif direction == "left" and pos[0] > 0:
            pos[0] -= 1
        elif direction == "right" and pos[0] < BOARD_SIZE - 1:
            pos[0] += 1


# === Process Opponent Worker ===
def process_opponent_worker(queue, start_positions, board_size):
    positions = start_positions[:]
    while True:
        time.sleep(PROCESS_OPPONENT_SLEEP)
        new_positions = []
        for pos in positions:
            direction = random.choice(["up", "down", "left", "right"])
            if direction == "up" and pos[1] > 0:
                pos[1] -= 1
            elif direction == "down" and pos[1] < board_size - 1:
                pos[1] += 1
            elif direction == "left" and pos[0] > 0:
                pos[0] -= 1
            elif direction == "right" and pos[0] < board_size - 1:
                pos[0] += 1
            new_positions.append(pos)
        positions = new_positions
        queue.put(positions)


# === Main Async Game Loop ===
async def main():
    global life

    clock_interval = 1 / FPS
    last_life_tick = pygame.time.get_ticks()
    elapsed_time = 0

    # Initialize Pygame
    pygame.init()
    global screen, font
    screen = pygame.display.set_mode(
        (BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE + 120)
    )
    pygame.display.set_caption("Game Demo - Multiple Opponents")
    font = pygame.font.SysFont(None, 36)
    pygame.time.set_timer(SPAWN_ITEM_EVENT, ITEM_SPAWN_RATE)

    loop = asyncio.get_running_loop()

    # Start play timer
    pygame.time.get_ticks()

    # Start async opponents
    for pos in async_opponents:
        loop.create_task(move_single_async_opponent(pos))

    # Start thread opponents
    for pos in thread_opponents:
        t = threading.Thread(
            target=move_single_thread_opponent,
            args=(pos,),
            daemon=True
        )
        t.start()

    # Start process opponents
    for pos in process_opponents:
        q = mp.Queue()
        p = mp.Process(
            target=process_opponent_worker,
            args=(q, [pos], BOARD_SIZE),
            daemon=True
        )
        p.start()
        process_queues.append(q)
        processes.append(p)

    running = True
    while running:
        # Handle pygame events
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
        check_item_collision(loop)

        # Receive process opponent updates
        for idx, q in enumerate(process_queues):
            try:
                while not q.empty():
                    updates = q.get_nowait()
                    if idx < len(process_opponents):
                        process_opponents[idx:idx+len(updates)] = updates
            except Exception:
                pass

        if check_collisions():
            running = False

        # Life countdown
        now = pygame.time.get_ticks()
        if now - last_life_tick >= 1000:
            last_life_tick = now
            life -= 1
            elapsed_time += 1
            if life <= 0:
                print("Game Over! Out of life.")
                running = False

        draw_board()

        # Draw play timer (after board)
        timer_text = font.render(f"Time: {elapsed_time}s", True, WHITE)
        screen.blit(
            timer_text,
            (BOARD_SIZE * CELL_SIZE - 150, BOARD_SIZE * CELL_SIZE + 90)
        )
        # screen.blit(timer_text, (10, BOARD_SIZE * CELL_SIZE + 90))
        pygame.display.flip()

        await asyncio.sleep(clock_interval)

    pygame.quit()
    sys.exit()


# === Entry Point ===
if __name__ == "__main__":
    mp.set_start_method("spawn")
    asyncio.run(main())
