import pygame as pg
import sys
import random

# Initialize Pygame
pg.init()

# Screen dimensions and grid size
GRID_SIZE = 30
GRID_WIDTH = 10  # 10 blocks wide
GRID_HEIGHT = 20  # 20 blocks high
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE
SIDE_PANEL_WIDTH = 6 * GRID_SIZE
TOTAL_WIDTH = SCREEN_WIDTH + 2 * SIDE_PANEL_WIDTH
TEXT_MARGIN = 20  # Margin between texts and top of the screen

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

# Shapes and colors
SHAPES = [
    [[1, 1, 0], [0, 1, 1], [0, 0, 0]],  # S-shape
    [[0, 1, 1], [1, 1, 0], [0, 0, 0]],  # Z-shape
    [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],  # I-shape
    [[1, 1], [1, 1]],  # O-shape
    [[1, 0, 0], [1, 1, 1], [0, 0, 0]],  # J-shape
    [[0, 0, 1], [1, 1, 1], [0, 0, 0]],  # L-shape
    [[0, 1, 0], [1, 1, 1], [0, 0, 0]]   # T-shape
]
SHAPE_COLORS = [RED, GREEN, BLUE, CYAN, YELLOW, MAGENTA, ORANGE]

# Game variables
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
current_shape = None
current_color = None
next_shape = None
next_color = None
hold_shape = None
hold_color = None
can_hold = True
current_x, current_y = 3, 0
fall_time = 0
fall_speed = 300  # Speed of falling pieces in milliseconds
fast_fall_speed = 50  # Speed when down key is pressed
clock = pg.time.Clock()
game_over = False  # Initialize game_over variable here

# Font settings
game_over_font = pg.font.SysFont(None, 50)  # Increased font size for game over message
small_font = pg.font.SysFont(None, 30)  # Smaller font for next shape and hold shape text

# Piece generation bag
piece_bag = []

def refill_bag():
    global piece_bag
    piece_bag = list(range(len(SHAPES)))
    random.shuffle(piece_bag)

def get_next_piece():
    global piece_bag
    if not piece_bag:
        refill_bag()
    shape_index = piece_bag.pop()
    return SHAPES[shape_index], SHAPE_COLORS[shape_index]

def draw_grid(surface, grid):
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            color = WHITE if grid[y][x] == 0 else grid[y][x]
            pg.draw.rect(surface, color, (x * GRID_SIZE + SIDE_PANEL_WIDTH, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
            pg.draw.rect(surface, BLACK, (x * GRID_SIZE + SIDE_PANEL_WIDTH, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pg.draw.line(surface, BLACK, (x + SIDE_PANEL_WIDTH, 0), (x + SIDE_PANEL_WIDTH, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pg.draw.line(surface, BLACK, (SIDE_PANEL_WIDTH, y), (SIDE_PANEL_WIDTH + SCREEN_WIDTH, y))

def draw_shape(surface, shape, color, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pg.draw.rect(surface, color, (off_x + x * GRID_SIZE, off_y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
                pg.draw.rect(surface, BLACK, (off_x + x * GRID_SIZE, off_y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

def check_collision(grid, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                if x + off_x < 0 or x + off_x >= len(grid[0]) or y + off_y >= len(grid):
                    return True
                if y + off_y >= 0 and grid[y + off_y][x + off_x]:
                    return True
    return False

def merge_shape(grid, shape, offset, color):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                grid[y + off_y][x + off_x] = color

def remove_full_lines(grid):
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    while len(new_grid) < len(grid):
        new_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
    return new_grid

def rotate_shape(shape):
    return [list(row) for row in zip(*shape[::-1])]

def draw_next_shape(surface, shape, color):
    offset = (SCREEN_WIDTH + SIDE_PANEL_WIDTH + GRID_SIZE, GRID_SIZE + TEXT_MARGIN)
    draw_text(surface, "Next Shape", small_font, WHITE, (SCREEN_WIDTH + SIDE_PANEL_WIDTH + GRID_SIZE, TEXT_MARGIN))
    draw_shape(surface, shape, color, offset)

def draw_hold_shape(surface, shape, color):
    if shape:
        offset = (GRID_SIZE, GRID_SIZE + TEXT_MARGIN)
        draw_text(surface, "Hold Shape", small_font, WHITE, (GRID_SIZE, TEXT_MARGIN))
        draw_shape(surface, shape, color, offset)

def draw_text(surface, text, font, color, pos):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def draw_game_over(surface):
    game_over_text = game_over_font.render("Game Over", True, RED)  # Render game over message
    game_over_rect = game_over_text.get_rect(center=(TOTAL_WIDTH // 2, SCREEN_HEIGHT // 2))  # Center the text
    surface.blit(game_over_text, game_over_rect)  # Draw game over message

def main():
    global grid, current_shape, current_color, next_shape, next_color, hold_shape, hold_color, can_hold, current_x
    global current_y, fall_time, fall_speed, fast_fall_speed, clock, game_over  # Declare game_over variable as global
    
    # Initialize the first pieces
    refill_bag()
    current_shape, current_color = get_next_piece()
    next_shape, next_color = get_next_piece()

    screen = pg.display.set_mode((TOTAL_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Tetris")

    while True:
        screen.fill(BLACK)
        draw_grid(screen, grid)
        draw_shape(screen, current_shape, current_color, (current_x * GRID_SIZE + SIDE_PANEL_WIDTH, current_y * GRID_SIZE))
        draw_next_shape(screen, next_shape, next_color)  # Drawing next shape
        draw_hold_shape(screen, hold_shape, hold_color)  # Drawing hold shape
        if game_over:
            draw_game_over(screen)  # Drawing game over text
        
        pg.display.flip()

        fall_time += clock.get_rawtime()
        clock.tick()

        keys = pg.key.get_pressed()
        if keys[pg.K_DOWN]:
            speed = fast_fall_speed
        else:
            speed = fall_speed

        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    new_x = current_x - 1
                    if not check_collision(grid, current_shape, (new_x, current_y)):
                        current_x = new_x
                elif event.key == pg.K_RIGHT:
                    new_x = current_x + 1
                    if not check_collision(grid, current_shape, (new_x, current_y)):
                        current_x = new_x
                elif event.key == pg.K_DOWN:
                    new_y = current_y + 1
                    if not check_collision(grid, current_shape, (current_x, new_y)):
                        current_y = new_y
                elif event.key == pg.K_UP:
                    new_shape = rotate_shape(current_shape)
                    if not check_collision(grid, new_shape, (current_x, current_y)):
                        current_shape = new_shape
                elif event.key == pg.K_c and can_hold:
                    if hold_shape:
                        hold_shape, current_shape = current_shape, hold_shape
                        hold_color, current_color = current_color, hold_color
                    else:
                        hold_shape, hold_color = current_shape, current_color
                        current_shape, current_color = next_shape, next_color
                        next_shape, next_color = get_next_piece()
                    current_x, current_y = 3, 0
                    can_hold = False
                elif event.key == pg.K_r and game_over:  # Restart game if 'r' key is pressed and game is over
                    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
                    current_shape, current_color = get_next_piece()
                    next_shape, next_color = get_next_piece()
                    hold_shape = None
                    hold_color = None
                    can_hold = True
                    current_x, current_y = 3, 0
                    fall_time = 0
                    game_over = False

        if not game_over:
            if fall_time > speed:
                fall_time = 0
                current_y += 1
                if check_collision(grid, current_shape, (current_x, current_y)):
                    current_y -= 1
                    merge_shape(grid, current_shape, (current_x, current_y), current_color)
                    grid = remove_full_lines(grid)
                    current_shape, current_color = next_shape, next_color
                    next_shape, next_color = get_next_piece()
                    current_x, current_y = 3, 0
                    can_hold = True
                    if check_collision(grid, current_shape, (current_x, current_y)):
                        game_over = True

if __name__ == "__main__":
    main()
