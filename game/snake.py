import pygame as pg
import sys
import random

# Initialize Pygame
pg.init()

# Screen dimensions and grid size
GRID_SIZE = 30
GRID_WIDTH = 20
GRID_HEIGHT = 20
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE
TOTAL_WIDTH = SCREEN_WIDTH
TOTAL_HEIGHT = SCREEN_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Font settings
game_over_font = pg.font.SysFont(None, 50)

# Snake settings
snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
snake_dir = (1, 0)  # Start moving right
snake_color = GREEN

# Apple settings
def spawn_apple():
    while True:
        position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if position not in snake:
            return position

apple = spawn_apple()
apple_color = RED

# Game variables
clock = pg.time.Clock()
speed = 10  # Snake speed
game_over = False  # Initialize game_over variable here

def draw_snake(surface):
    for segment in snake:
        pg.draw.rect(surface, snake_color, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_apple(surface):
    pg.draw.rect(surface, apple_color, (apple[0] * GRID_SIZE, apple[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_game_over(surface):
    game_over_text = game_over_font.render("Game Over", True, RED)
    game_over_rect = game_over_text.get_rect(center=(TOTAL_WIDTH // 2, TOTAL_HEIGHT // 2))
    surface.blit(game_over_text, game_over_rect)

def main():
    global snake, snake_dir, apple, game_over

    screen = pg.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
    pg.display.set_caption("Snake Game")

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP and snake_dir != (0, 1):
                    snake_dir = (0, -1)
                elif event.key == pg.K_DOWN and snake_dir != (0, -1):
                    snake_dir = (0, 1)
                elif event.key == pg.K_LEFT and snake_dir != (1, 0):
                    snake_dir = (-1, 0)
                elif event.key == pg.K_RIGHT and snake_dir != (-1, 0):
                    snake_dir = (1, 0)
                elif event.key == pg.K_r and game_over:
                    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
                    snake_dir = (1, 0)
                    apple = spawn_apple()
                    game_over = False

        if not game_over:
            new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])

            # Check for collisions with walls
            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
                game_over = True

            # Check for collisions with itself
            if new_head in snake:
                game_over = True

            if not game_over:
                snake.insert(0, new_head)
                if new_head == apple:
                    apple = spawn_apple()
                else:
                    snake.pop()

        screen.fill(BLACK)  # Solid background color
        draw_snake(screen)
        draw_apple(screen)
        if game_over:
            draw_game_over(screen)

        pg.display.flip()
        clock.tick(speed)

if __name__ == "__main__":
    main()