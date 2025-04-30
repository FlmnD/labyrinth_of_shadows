import pygame
import sys

# Constants
TILE_SIZE = 40
MAZE = [
    "##########",
    "#        #",
    "# ###### #",
    "# #    # #",
    "#   #  # #",
    "# # #  # #",
    "# #    # #",
    "# ###### #",
    "#        #",
    "##########",
]

# Initialize Pygame
pygame.init()
WIDTH = len(MAZE[0]) * TILE_SIZE
HEIGHT = len(MAZE) * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Maze Game")

# Load images
wall_img = pygame.image.load("assets/wall.png").convert()
floor_img = pygame.image.load("assets/floor.png").convert()
player_img = pygame.image.load("assets/character.png").convert_alpha()

# Resize to tile size
wall_img = pygame.transform.scale(wall_img, (TILE_SIZE, TILE_SIZE))
floor_img = pygame.transform.scale(floor_img, (TILE_SIZE, TILE_SIZE))
player_img = pygame.transform.scale(player_img, (TILE_SIZE, TILE_SIZE))

# Player position in grid
player_pos = [1, 1]


def draw_maze():
    for y, row in enumerate(MAZE):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE,
                               TILE_SIZE, TILE_SIZE)
            if tile == "#":
                screen.blit(wall_img, rect)
            else:
                screen.blit(floor_img, rect)


def draw_player():
    rect = pygame.Rect(player_pos[0] * TILE_SIZE,
                       player_pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    screen.blit(player_img, rect)


def can_move(x, y):
    if 0 <= x < len(MAZE[0]) and 0 <= y < len(MAZE):
        return MAZE[y][x] == " "
    return False


# Game Loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    new_x, new_y = player_pos
    if keys[pygame.K_LEFT]:
        player_img = pygame.image.load("assets/character_left.png").convert_alpha()
        new_x -= 1
    elif keys[pygame.K_RIGHT]:
        player_img = pygame.image.load(
            "assets/character_right.png").convert_alpha()
        new_x += 1
    elif keys[pygame.K_UP]:
        player_img = pygame.image.load(
            "assets/character_up.png").convert_alpha()
        new_y -= 1
    elif keys[pygame.K_DOWN]:
        player_img = pygame.image.load(
            "assets/character.png").convert_alpha()
        new_y += 1

    player_img = pygame.transform.scale(player_img, (TILE_SIZE, TILE_SIZE))

    if can_move(new_x, new_y):
        player_pos = [new_x, new_y]

    screen.fill((0, 0, 0))  # Clear screen
    draw_maze()
    draw_player()
    pygame.display.flip()
    clock.tick(10)
