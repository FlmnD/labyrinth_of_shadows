from enum import Enum
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
pygame.mixer.init()
pygame.mixer.music.set_volume(0.8)

WIDTH = len(MAZE[0]) * TILE_SIZE
HEIGHT = len(MAZE) * TILE_SIZE + 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Labyrinth of Shadows")

# Load images
wall_img = pygame.image.load("assets/wall.png").convert()
floor_img = pygame.image.load("assets/floor.png").convert()
shard_img = pygame.image.load("assets/glow_shard.png").convert_alpha()
gate_img = pygame.transform.scale(pygame.image.load(
    "assets/gate.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))
menu_background = pygame.image.load("assets/menu_background.png").convert()
menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))
win_screen = pygame.image.load("assets/win_screen.png").convert()
win_screen = pygame.transform.scale(win_screen, (WIDTH, HEIGHT))
key_img = pygame.transform.scale(pygame.image.load(
    "assets/key.png").convert_alpha(), (TILE_SIZE // (1.5), TILE_SIZE // (1.5)))

player_imgs = {
    "left": pygame.transform.scale(pygame.image.load("assets/character_left.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)),
    "right": pygame.transform.scale(pygame.image.load("assets/character_right.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)),
    "up": pygame.transform.scale(pygame.image.load("assets/character_up.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)),
    "down": pygame.transform.scale(pygame.image.load("assets/character.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))
}
enemy_img = pygame.transform.scale(pygame.image.load(
    "assets/enemy.png").convert_alpha(), (TILE_SIZE, TILE_SIZE))

cutscene_player_img = pygame.transform.scale(pygame.image.load(
    "assets/character.png").convert_alpha(), (150, 150))

wall_img = pygame.transform.scale(wall_img, (TILE_SIZE, TILE_SIZE))
floor_img = pygame.transform.scale(floor_img, (TILE_SIZE, TILE_SIZE))
shard_img = pygame.transform.scale(shard_img, (TILE_SIZE, TILE_SIZE))
shard_icon_img = pygame.transform.scale(
    shard_img, (TILE_SIZE // (1.5), TILE_SIZE // (1.5)))

button_font = pygame.font.Font('freesansbold.ttf', 36)
title_font = pygame.font.Font(
    'freesansbold.ttf', 48) 

start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
restart_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 50)
cutscene_images = [
    pygame.image.load(f"assets/intro_scene/{i}.png").convert() for i in range(1, 11)
]
pygame.mixer.music.load("assets/audio/menu_theme.mp3")

main_game_music = "assets/audio/level_audio.mp3"

# Sound effects
shard_collect_sound = pygame.mixer.Sound("assets/audio/shard_collect.ogg")
shard_collect_sound.set_volume(0.7)
hurt_sound = pygame.mixer.Sound("assets/audio/hurt.wav")
whoosh_sound = pygame.mixer.Sound("assets/audio/whoosh.wav")
walk_sound = pygame.mixer.Sound("assets/audio/player_walk.wav")

class GameState(Enum):
    MENU = 1
    START_GAME = 2
    WALK_TO_PC = 3
    COMPUTER_PROMPT = 4
    CUTSCENE = 5
    GAME = 6
    GAME_OVER = 7
    WIN = 8
    WIN_NEXT = 9

player_x, player_y = 4, 5
computer_pos = (15, 2)
state = GameState.MENU
cutscene_index = 0
pygame.mixer.music.play(-1)


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
    global state
    if player.health == 0:
        if state != GameState.GAME_OVER:
            pygame.mixer.music.pause()
            pygame.mixer.stop()
            state = GameState.GAME_OVER

def restart_game():
    global player, enemies, shards, shard_count
    player = Player(1, 1)
    enemies = [Enemy(18, 9), Enemy(1, 8), Enemy(18, 1)]
    shards = [Shard([player.x, player.y], [[e.x, e.y]
                    for e in enemies]) for _ in range(5)]
    shard_count = 0
    pygame.mixer.music.load(main_game_music)
    pygame.mixer.music.play(-1)

def show_centered_text(main_text, sub_text):
    font = pygame.font.Font('freesansbold.ttf', 36)
    main = font.render(main_text, True, (255, 255, 255))
    sub = font.render(sub_text, True, (255, 255, 255))
    screen.blit(main, main.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
    screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

def return_to_menu():
    global player_x, player_y, state, cutscene_index
    player_x, player_y = 4, 5  # Reset player to starting animation pos
    cutscene_index = 0         # Optional: Reset cutscene if needed
    state = GameState.WALK_TO_PC


player = Player(1, 1)
enemies = [Enemy(18, 9), Enemy(1, 8), Enemy(18, 1)]
player_pos = [0, 0]
enemy_pos = [[18, 9], [1, 8], [18, 1]]
shards = [Shard(player_pos, enemy_pos) for _ in range(5)]
shard_count = 0
GATE_POS = (18, 7)

walk_channel = pygame.mixer.Channel(1)

if math.dist((enemies[0].x, enemies[0].y), (enemies[1].x, enemies[1].y)) < 1.5:
    enemies[1] = Enemy(1, 7)

clock = pygame.time.Clock()
frame_count = 0

while True:
    if state == GameState.MENU or state == GameState.COMPUTER_PROMPT or state == GameState.WALK_TO_PC:
        screen.blit(menu_background, (0, 0))
    else:
        screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state == GameState.MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    state = GameState.START_GAME

        elif state == GameState.COMPUTER_PROMPT:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                state = GameState.CUTSCENE
                whoosh_sound.play()

        elif state == GameState.CUTSCENE:
            if event.type == pygame.MOUSEBUTTONDOWN:
                cutscene_index += 1
                if cutscene_index >= len(cutscene_images):
                    state = GameState.GAME
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(main_game_music)
                    pygame.mixer.music.play(-1)
        
        elif state == GameState.GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart_game()
                    state = GameState.GAME
                elif event.key == pygame.K_m:
                    restart_game()
                    pygame.mixer.music.load("assets/audio/menu_theme.mp3")
                    pygame.mixer.music.play(-1)
                    state = GameState.MENU
        
        elif state == GameState.WIN:
            if event.type == pygame.MOUSEBUTTONDOWN:
                state = GameState.WIN_NEXT
        
        elif state == GameState.WIN_NEXT:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                restart_game()
                pygame.mixer.music.load("assets/audio/menu_theme.mp3")
                pygame.mixer.music.play(-1)
                state = GameState.MENU
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    if state == GameState.MENU:
        screen.blit(menu_background, (0, 0))
        
        pygame.draw.rect(screen, (255, 255, 255), start_button_rect)
        text = button_font.render("START", True, (0, 0, 0))
        text_rect = text.get_rect(center=start_button_rect.center)
        screen.blit(text, text_rect)

        title_text = title_font.render(
            "Labyrinth of Shadows", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(title_text, title_rect)

    elif state == GameState.WALK_TO_PC:
        if frame_count % 3 == 0:
            if (player_x, player_y) != computer_pos:
                dx = computer_pos[0] - player_x
                dy = computer_pos[1] - player_y
                if abs(dx) > abs(dy):
                    player_x += 1 if dx > 0 else -1
                else:
                    player_y += 1 if dy > 0 else -1
            else:
                state = GameState.COMPUTER_PROMPT

        rect = pygame.Rect(player_x * TILE_SIZE, player_y *
                           TILE_SIZE, 150, 150)
        screen.blit(cutscene_player_img, rect)

    elif state == GameState.COMPUTER_PROMPT:
        rect = pygame.Rect(player_x * TILE_SIZE, player_y *
                           TILE_SIZE, 150, 150)
        screen.blit(cutscene_player_img, rect)
        font = pygame.font.Font('freesansbold.ttf', 24)
        prompt = font.render("Press E to enter", True, (255, 255, 255))
        screen.blit(prompt, (WIDTH // 2 - 100, HEIGHT - 100))

    elif state == GameState.CUTSCENE:
        screen.blit(pygame.transform.scale(
            cutscene_images[cutscene_index], (WIDTH, HEIGHT)), (0, 0))

    elif state == GameState.GAME:
        keys = pygame.key.get_pressed()

        moved = False

        if frame_count % 1 == 0:
            if keys[pygame.K_LEFT]:
                player.move(-1, 0, "left")
                moved = True
            elif keys[pygame.K_RIGHT]:
                player.move(1, 0, "right")
                moved = True
            elif keys[pygame.K_UP]:
                player.move(0, -1, "up")
                moved = True
            elif keys[pygame.K_DOWN]:
                player.move(0, 1, "down")
                moved = True
        
        if moved and not walk_channel.get_busy():
            walk_channel.play(walk_sound)

        if frame_count % 3 == 0:
            enemy_positions = {(e.x, e.y) for e in enemies}
            for enemy in enemies:
                enemy.move_towards(player, enemy_positions)
                enemy_positions = {(e.x, e.y) for e in enemies}

        for enemy in enemies:
            if (enemy.x, enemy.y) == (player.x, player.y):
                player.health = max(0, player.health - 10)
                hurt_sound.play()

        for shard in shards:
            if (shard.x, shard.y) == (player.x, player.y):
                shards.remove(shard)
                shard_count += 1
                shard_collect_sound.play()

        for y, row in enumerate(MAZE):
            for x, tile in enumerate(row):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE,
                                   TILE_SIZE, TILE_SIZE)
                screen.blit(wall_img if tile == "#" else floor_img, rect)

        screen.blit(gate_img, (GATE_POS[0] *
                    TILE_SIZE, GATE_POS[1] * TILE_SIZE))

        if (player.x, player.y) == GATE_POS and shard_count >= 5:
            font = pygame.font.Font('freesansbold.ttf', 24)
            prompt = font.render("Press E to enter", True, (255, 255, 255))
            screen.blit(prompt, (WIDTH // 2 - 100, HEIGHT - 100))

        if (player.x, player.y) == GATE_POS and shard_count >= 5:
            if keys[pygame.K_e]:
                pygame.mixer.music.pause()
                pygame.mixer.stop()
                state = GameState.WIN

        for shard in shards:
            shard.draw()

        player.draw()
        player.draw_health()

        font = pygame.font.Font('freesansbold.ttf', 24)
        shard_icon_x = 220
        shard_icon_y = HEIGHT - 50
        text = font.render(
            f"x {1 if shard_count == 5 else shard_count}", True, (255, 255, 255))
        screen.blit(shard_icon_img if shard_count < 5 else key_img, (shard_icon_x, shard_icon_y + 8))
        screen.blit(text, (shard_icon_x + TILE_SIZE // 2 + 10, HEIGHT - 30))

        for enemy in enemies:
            enemy.draw()

        game_over(player)

    elif state == GameState.GAME_OVER:
        show_centered_text(
            "GAME OVER!", "Press R to Restart | Press M for Menu")
    elif state == GameState.WIN:
        screen.blit(win_screen, (0, 0))
        font = pygame.font.Font('freesansbold.ttf', 36)

        text = font.render("YOU WIN!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        screen.blit(text, text_rect)

        click_text = font.render(
            "Click anywhere to continue", True, (255, 255, 255))
        click_rect = click_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        screen.blit(click_text, click_rect)

    elif state == GameState.WIN_NEXT:
        screen.blit(menu_background, (0, 0))
        show_centered_text(
            "What would you like to do?", "Press Q to Quit Game | Press M for Menu")
    elif state == GameState.START_GAME:
        return_to_menu()
        state = GameState.WALK_TO_PC

    pygame.display.flip()
    clock.tick(10)
    frame_count += 1
