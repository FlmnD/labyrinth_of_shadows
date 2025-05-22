#TODO: key formation, gate opening, make the game harder, classes, sound effects/music, restart button, music on / off, second level with sword, main menu


import pygame
import sys
import math
import random

# Constants
TILE_SIZE = 60
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
shard_img = pygame.image.load("assets/glow_shard.png").convert_alpha()
gate_img = pygame.transform.scale(pygame.image.load(
    "assets/gate.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))

player_imgs = {
    "left": pygame.transform.scale(pygame.image.load("assets/character_left.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)),
    "right": pygame.transform.scale(pygame.image.load("assets/character_right.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)),
    "up": pygame.transform.scale(pygame.image.load("assets/character_up.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)),
    "down": pygame.transform.scale(pygame.image.load("assets/character.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))
}
enemy_img = pygame.transform.scale(pygame.image.load(
    "assets/enemy.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))

wall_img = pygame.transform.scale(wall_img, (TILE_SIZE, TILE_SIZE))
floor_img = pygame.transform.scale(floor_img, (TILE_SIZE, TILE_SIZE))
shard_img = pygame.transform.scale(shard_img, (TILE_SIZE, TILE_SIZE))
shard_icon_img = pygame.transform.scale(
    shard_img, (TILE_SIZE // (1.5), TILE_SIZE // (1.5)))


def can_move(x, y):
    return 0 <= x < len(MAZE[0]) and 0 <= y < len(MAZE) and MAZE[y][x] == " "


def distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def cost(pos, g_score_dict, goal):
    g = g_score_dict.get(pos, float('inf'))
    h = distance(pos, goal)
    return g + h


def get_path(start, goal):
    open_set = [start]
    came_from = {}
    g_score = {start: 0}

    while open_set:
        min_score = float('inf')
        current = None
        for pos in open_set:
            score = cost(pos, g_score, goal)
            if score < min_score:
                min_score = score
                current = pos

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        open_set.remove(current)
        x = current[0]
        y = current[1]

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for direction in directions:
            dx = direction[0]
            dy = direction[1]
            neighbor = (x + dx, y + dy)
            nx = neighbor[0]
            ny = neighbor[1]

            if not can_move(nx, ny):
                continue

            tentative_g_score = g_score[current] + 1
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                if neighbor not in open_set:
                    open_set.append(neighbor)

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
        if self.health > 0:
            pygame.draw.rect(screen, (86, 91, 92), (12, HEIGHT - 28, 196, 16))
            pygame.draw.rect(screen, (54, 187, 201), (12,
                             HEIGHT - 28, (self.health / MAX_HEALTH) * 196, 16))


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move_towards(self, target, enemy_positions):
        path = get_path((self.x, self.y), (target.x, target.y))
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
        self.generate_pos(player_pos, enemy_pos)

    def generate_pos(self, player_pos, enemy_pos):
        while True:
            x = random.randint(0, len(MAZE[0]) - 1)
            y = random.randint(0, len(MAZE) - 1)
            if ((x, y) != tuple(player_pos) and
                (x, y) != tuple(enemy_pos[0]) and
                (x, y) != tuple(enemy_pos[1]) and
                (x, y) not in Shard.shard_positions and
                    MAZE[y][x] == " "):
                self.x = x
                self.y = y
                Shard.shard_positions.append((x, y))
                break

    def draw(self):
        rect = pygame.Rect(self.x * TILE_SIZE, self.y *
                           TILE_SIZE, TILE_SIZE, TILE_SIZE)
        screen.blit(shard_img, rect)


def game_over(player):
    if player.health == 0:
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
        font = pygame.font.Font('freesansbold.ttf', 30)
        text = font.render(f"GAME OVER!", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 75, HEIGHT // 2))


player = Player(1, 1)
enemies = [Enemy(18, 9), Enemy(1, 8), Enemy(18, 1)]
player_pos = [0, 0]
enemy_pos = [[18, 9], [1, 8], [18, 1]]
shards = [Shard(player_pos, enemy_pos) for _ in range(5)]
shard_count = 0
GATE_POS = (18, 7)

if math.dist((enemies[0].x, enemies[0].y), (enemies[1].x, enemies[1].y)) < 1.5:
    enemies[1] = Enemy(1, 7)

clock = pygame.time.Clock()
frame_count = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if frame_count % 1 == 0:
        if keys[pygame.K_LEFT]:
            player.move(-1, 0, "left")
        elif keys[pygame.K_RIGHT]:
            player.move(1, 0, "right")
        elif keys[pygame.K_UP]:
            player.move(0, -1, "up")
        elif keys[pygame.K_DOWN]:
            player.move(0, 1, "down")

    if frame_count % 3 == 0:
        enemy_positions = {(e.x, e.y) for e in enemies}
        for enemy in enemies:
            enemy.move_towards(player, enemy_positions)
            enemy_positions = {(e.x, e.y) for e in enemies}

    for enemy in enemies:
        if (enemy.x, enemy.y) == (player.x, player.y):
            player.health = max(0, player.health - 10)

    for shard in shards:
        if (shard.x, shard.y) == (player.x, player.y):
            shards.remove(shard)
            shard_count += 1

    screen.fill((0, 0, 0))
    for y, row in enumerate(MAZE):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE,
                               TILE_SIZE, TILE_SIZE)
            screen.blit(wall_img if tile == "#" else floor_img, rect)

    screen.blit(gate_img, (GATE_POS[0] * TILE_SIZE, GATE_POS[1] * TILE_SIZE))

    if (player.x, player.y) == GATE_POS and shard_count >= 5:
        font = pygame.font.Font('freesansbold.ttf', 24)
        prompt = font.render("Press E to enter", True, (255, 255, 255))
        screen.blit(prompt, (WIDTH // 2 - 100, HEIGHT - 100))

    if (player.x, player.y) == GATE_POS and shard_count >= 5:
        if keys[pygame.K_e]:
            print("Entering gate!")



    for shard in shards:
        shard.draw()

    player.draw()
    player.draw_health()

    font = pygame.font.Font('freesansbold.ttf', 24)
    # text = font.render(f"Shard count: {shard_count}", True, (255, 255, 255))
    # screen.blit(text, (10, HEIGHT - 70))

    shard_icon_x = 220
    shard_icon_y = HEIGHT - 50
    text = font.render(f"x {shard_count}", True, (255, 255, 255))
    screen.blit(shard_icon_img, (shard_icon_x, shard_icon_y + 8))
    screen.blit(text, (shard_icon_x + TILE_SIZE // 2 + 10, HEIGHT - 30))

    for enemy in enemies:
        enemy.draw()

    game_over(player)
    pygame.display.flip()
    clock.tick(10)
    frame_count += 1
