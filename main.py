


import pygame
import sys
import heapq
import math
import random

# Constants
TILE_SIZE = 40
MAX_HEALTH = 100
MAZE = [
    "####################",
    "#     #            #",
    "# ### # ########## #",
    "# #   #        #   #",
    "# # ##### #### # ###",
    "# #     #    #     #",
    "# ##### # ## #######",
    "#     # #  #       #",
    "### # # ## ####### #",
    "#   #        #     #",
    "####################",
]

# Initialize Pygame
pygame.init()
WIDTH = len(MAZE[0]) * TILE_SIZE
HEIGHT = len(MAZE) * TILE_SIZE + 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Maze Game")

# Load images
wall_img = pygame.image.load("assets/wall.png").convert()
floor_img = pygame.image.load("assets/floor.png").convert()
shard_img = pygame.image.load("assets/glow_shard.png").convert()
player_imgs = {
    "left": pygame.transform.scale(pygame.image.load("assets/character_left.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)),
    "right": pygame.transform.scale(pygame.image.load("assets/character_right.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)),
    "up": pygame.transform.scale(pygame.image.load("assets/character_up.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)),
    "down": pygame.transform.scale(pygame.image.load("assets/character.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))
}
enemy_img = pygame.transform.scale(pygame.image.load(
    "assets/enemy.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))
#healthbar_blank = pygame.image.load("assets/soul_bar.png").convert()
#healthbar_blank = pygame.transform.scale(healthbar_blank, (200, 20))

wall_img = pygame.transform.scale(wall_img, (TILE_SIZE, TILE_SIZE))
floor_img = pygame.transform.scale(floor_img, (TILE_SIZE, TILE_SIZE))
shard_img = pygame.transform.scale(shard_img, (TILE_SIZE, TILE_SIZE))


def can_move(x, y):
    return 0 <= x < len(MAZE[0]) and 0 <= y < len(MAZE) and MAZE[y][x] == " "


def a_star(start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}

    def h(pos):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        x, y = current
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (x + dx, y + dy)
            if not can_move(*neighbor):
                continue
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + h(neighbor)
                heapq.heappush(open_set, (f_score, neighbor))
    return []


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = player_imgs["down"]
        self.health = MAX_HEALTH

    def move(self, dx, dy, direction):
        new_x, new_y = self.x + dx, self.y + dy
        if can_move(new_x, new_y):
            self.x, self.y = new_x, new_y
            self.img = player_imgs[direction]

    def draw(self):
        rect = pygame.Rect(self.x * TILE_SIZE, self.y *
                           TILE_SIZE, TILE_SIZE, TILE_SIZE)
        screen.blit(self.img, rect)

    def draw_health(self):
        #screen.blit(healthbar_blank, (10, HEIGHT - 30))
        if self.health > 0:
            pygame.draw.rect(screen, (255, 0, 0), (12, HEIGHT -
                             28, (self.health / MAX_HEALTH) * 196, 16))


class Enemy:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move_towards(self, target, enemy_positions):
        path = a_star((self.x, self.y), (target.x, target.y))
        if path and len(path) > 0:
            next_pos = path[0]
            if next_pos == (target.x, target.y) or next_pos not in enemy_positions:
                self.x, self.y = next_pos

    def draw(self):
        rect = pygame.Rect(self.x * TILE_SIZE, self.y *
                           TILE_SIZE, TILE_SIZE, TILE_SIZE)
        screen.blit(enemy_img, rect)

class Shard:

    shard_positions = []

    def __init__(self, player_pos, enemy_pos):
        generate_pos()

    # Generate randomized glowshard positions
    def generate_pos(self, player_pos, enemy_pos):
        x = random.randint(0, len(MAZE))
        y = random.randint(0, len(MAZE[0]))

        # Make sure glowshards don't generate where players or enemies are or where other shards are
        while x != player_pos[0] and y != player_pos[0] and x != enemy_pos[0][0] and x != enemy_pos[1][0] and enemy_pos[1][1] != y and enemy_pos[0][1] != enemy_pos:
            x = random.randint(0, len(MAZE))
            y = random.randint(0, len(MAZE[0]))

        self.x = x
        self.y = y

    def draw(self):
        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        screen.blit(shard_img, rect)

# Create player and enemies
player = Player(1, 1)
enemies = [Enemy(18, 9), Enemy(1, 8)]

player_pos = [0, 0]
enemy_pos = [[18, 9], [1, 8]]


# Make sure enemies start at least 1 tile away from each other
if math.dist((enemies[0].x, enemies[0].y), (enemies[1].x, enemies[1].y)) < 1.5:
    enemies[1] = Enemy(1, 7)

# Game Loop
clock = pygame.time.Clock()
frame_count = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if frame_count % 1 == 0:  # Player moves every frame
        if keys[pygame.K_LEFT]:
            player.move(-1, 0, "left")
        elif keys[pygame.K_RIGHT]:
            player.move(1, 0, "right")
        elif keys[pygame.K_UP]:
            player.move(0, -1, "up")
        elif keys[pygame.K_DOWN]:
            player.move(0, 1, "down")

    if frame_count % 4 == 0:  # Enemies move less frequently
        enemy_positions = {(e.x, e.y) for e in enemies}
        for enemy in enemies:
            enemy.move_towards(player, enemy_positions)
            enemy_positions = {(e.x, e.y) for e in enemies}

    # Health reduction logic
    for enemy in enemies:
        if (enemy.x, enemy.y) == (player.x, player.y):
            player.health = max(0, player.health - 1)

    screen.fill((0, 0, 0))
    for y, row in enumerate(MAZE):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE,
                               TILE_SIZE, TILE_SIZE)
            screen.blit(wall_img if tile == "#" else floor_img, rect)

    player.draw()
    player.draw_health()
    for enemy in enemies:
        enemy.draw()


    pygame.display.flip()
    clock.tick(10)
    frame_count += 1



