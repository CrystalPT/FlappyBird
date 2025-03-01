import pygame
import sys
import random
import json
import os

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.25
FLAP_STRENGTH = -7
PIPE_SPEED = 6
PIPE_GAP = 400
PIPE_FREQUENCY = 1500  # milliseconds
GROUND_HEIGHT = 120

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 50)
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)


# Game state
class GameState:
    def __init__(self):
        self.score = 0
        self.high_score = 0
        self.tokens = 0
        self.total_tokens = 0
        self.current_bird = "Yellow Bird"
        self.current_pipe = "Green Pipe"
        self.current_background = "Day Sky"
        self.unlocked_birds = ["Yellow Bird"]
        self.unlocked_pipes = ["Green Pipe"]
        self.unlocked_backgrounds = ["Day Sky"]
        self.load_data()

    def load_data(self):
        try:
            if os.path.exists('flappy_data.json'):
                with open('flappy_data.json', 'r') as f:
                    data = json.load(f)
                    self.high_score = data.get('high_score', 0)
                    self.total_tokens = data.get('total_tokens', 0)
                    self.tokens = data.get('tokens', 0)
                    self.unlocked_birds = data.get('unlocked_birds', ["Yellow Bird"])
                    self.unlocked_pipes = data.get('unlocked_pipes', ["Green Pipe"])
                    self.unlocked_backgrounds = data.get('unlocked_backgrounds', ["Day Sky"])
                    self.current_bird = data.get('current_bird', "Yellow Bird")
                    self.current_pipe = data.get('current_pipe', "Green Pipe")
                    self.current_background = data.get('current_background', "Day Sky")
        except Exception:
            # If there's any error, just use defaults
            pass

    def save_data(self):
        data = {
            'high_score': self.high_score,
            'total_tokens': self.total_tokens,
            'tokens': self.tokens,
            'unlocked_birds': self.unlocked_birds,
            'unlocked_pipes': self.unlocked_pipes,
            'unlocked_backgrounds': self.unlocked_backgrounds,
            'current_bird': self.current_bird,
            'current_pipe': self.current_pipe,
            'current_background': self.current_background
        }
        try:
            with open('flappy_data.json', 'w') as f:
                json.dump(data, f)
        except Exception:
            # If there's an error, just continue
            pass

    def update_score(self, new_score):
        self.score = new_score
        # Add a token for every 10 points
        tokens_earned = new_score // 10
        new_tokens = tokens_earned - (self.total_tokens - self.tokens)
        if new_tokens > 0:
            self.tokens += new_tokens
            self.total_tokens += new_tokens

        if new_score > self.high_score:
            self.high_score = new_score

        self.save_data()


# Shop items
class ShopItems:
    def __init__(self):
        self.birds = {
            "Yellow Bird": {"price": 0, "color": YELLOW},
            "Red Bird": {"price": 5, "color": RED},
            "Blue Bird": {"price": 10, "color": BLUE},
            "Purple Bird": {"price": 15, "color": PURPLE}
        }

        self.pipes = {
            "Green Pipe": {"price": 0, "color": GREEN},
            "Blue Pipe": {"price": 8, "color": BLUE},
            "Orange Pipe": {"price": 12, "color": ORANGE},
            "Gray Pipe": {"price": 15, "color": GRAY}
        }

        self.backgrounds = {
            "Day Sky": {"price": 0, "color": SKY_BLUE},
            "Night Sky": {"price": 5, "color": (25, 25, 112)},  # Midnight Blue
            "Sunset": {"price": 5, "color": (255, 99, 71)},  # Tomato
            "Forest": {"price": 5, "color": (34, 139, 34)}  # Forest Green
        }


class Bird:
    def __init__(self, game_state, shop_items):
        self.x = WIDTH // 4
        self.y = HEIGHT // 2
        self.velocity = 0
        self.width = 30
        self.height = 24
        self.game_state = game_state
        self.shop_items = shop_items

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        # Apply gravity
        self.velocity += GRAVITY
        self.y += self.velocity

        # Keep bird within screen
        if self.y < 0:
            self.y = 0
            self.velocity = 0

    def draw(self):
        # Get bird color from current selection
        bird_color = self.shop_items.birds[self.game_state.current_bird]["color"]

        # Draw the bird
        bird_rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                                self.width, self.height)
        pygame.draw.rect(screen, bird_color, bird_rect)

        # Draw the eye
        pygame.draw.circle(screen, BLACK, (self.x + 10, self.y - 5), 3)

    def get_mask(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                           self.width, self.height)


class Pipe:
    def __init__(self, x, game_state, shop_items):
        self.x = x
        self.height = random.randint(150, 400)
        self.top_pipe_rect = pygame.Rect(self.x, 0, 50, self.height - PIPE_GAP // 2)
        self.bottom_pipe_rect = pygame.Rect(self.x, self.height + PIPE_GAP // 2,
                                            50, HEIGHT - self.height - PIPE_GAP // 2 - GROUND_HEIGHT)
        self.passed = False
        self.game_state = game_state
        self.shop_items = shop_items

    def update(self):
        self.x -= PIPE_SPEED
        self.top_pipe_rect.x = self.x
        self.bottom_pipe_rect.x = self.x

    def draw(self):
        # Get pipe color from current selection
        pipe_color = self.shop_items.pipes[self.game_state.current_pipe]["color"]

        pygame.draw.rect(screen, pipe_color, self.top_pipe_rect)
        pygame.draw.rect(screen, pipe_color, self.bottom_pipe_rect)

    def collide(self, bird):
        bird_mask = bird.get_mask()
        return bird_mask.colliderect(self.top_pipe_rect) or bird_mask.colliderect(self.bottom_pipe_rect)


class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), hover_color=(150, 150, 150)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border

        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos, click):
        return self.rect.collidepoint(mouse_pos) and click


def draw_floor():
    floor_rect = pygame.Rect(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)
    pygame.draw.rect(screen, (222, 184, 135), floor_rect)  # Sand color


def draw_background(game_state, shop_items):
    # Get background color
    bg_color = shop_items.backgrounds[game_state.current_background]["color"]

    screen.fill(bg_color)

    # Draw clouds if not night sky
    if game_state.current_background != "Night Sky":
        cloud_color = WHITE
        if game_state.current_background == "Sunset":
            cloud_color = (255, 218, 185)  # Peach for sunset clouds

        pygame.draw.ellipse(screen, cloud_color, (50, 50, 80, 40))
        pygame.draw.ellipse(screen, cloud_color, (200, 80, 100, 50))
        pygame.draw.ellipse(screen, cloud_color, (300, 40, 70, 35))
    else:
        # Draw stars for night sky
        for _ in range(30):
            x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT // 2)
            pygame.draw.circle(screen, WHITE, (x, y), 1)


def draw_menu(game_state):
    # Draw title
    title_text = title_font.render("FLAPPY BIRD", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

    # Draw high score
    high_score_text = font.render(f"High Score: {game_state.high_score}", True, BLACK)
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, 180))

    # Draw tokens
    tokens_text = font.render(f"Tokens: {game_state.tokens}", True, BLACK)
    screen.blit(tokens_text, (WIDTH // 2 - tokens_text.get_width() // 2, 220))


def draw_shop(game_state, shop_items, selected_tab):
    # Draw shop title
    shop_title = title_font.render("SHOP", True, BLACK)
    screen.blit(shop_title, (WIDTH // 2 - shop_title.get_width() // 2, 30))

    # Draw tokens
    tokens_text = font.render(f"Tokens: {game_state.tokens}", True, BLACK)
    screen.blit(tokens_text, (WIDTH // 2 - tokens_text.get_width() // 2, 80))

    # Draw tabs
    y_pos = 130

    # Draw items based on selected tab
    items_to_display = []
    if selected_tab == "Birds":
        items_to_display = shop_items.birds
    elif selected_tab == "Pipes":
        items_to_display = shop_items.pipes
    else:
        items_to_display = shop_items.backgrounds

    for i, (item_name, item_data) in enumerate(items_to_display.items()):
        # Item rectangle
        item_rect = pygame.Rect(50, y_pos + i * 60, WIDTH - 100, 50)

        # Check if item is unlocked
        is_unlocked = False
        if selected_tab == "Birds":
            is_unlocked = item_name in game_state.unlocked_birds
        elif selected_tab == "Pipes":
            is_unlocked = item_name in game_state.unlocked_pipes
        else:
            is_unlocked = item_name in game_state.unlocked_backgrounds

        # Check if item is currently selected
        is_selected = False
        if selected_tab == "Birds":
            is_selected = item_name == game_state.current_bird
        elif selected_tab == "Pipes":
            is_selected = item_name == game_state.current_pipe
        else:
            is_selected = item_name == game_state.current_background

        # Draw item background
        if is_selected:
            pygame.draw.rect(screen, (200, 255, 200), item_rect)  # Light green for selected
        elif is_unlocked:
            pygame.draw.rect(screen, (220, 220, 220), item_rect)  # Light gray for unlocked
        else:
            pygame.draw.rect(screen, (180, 180, 180), item_rect)  # Darker gray for locked

        pygame.draw.rect(screen, BLACK, item_rect, 2)  # Border

        # Draw color sample
        color_rect = pygame.Rect(item_rect.x + 10, item_rect.y + 10, 30, 30)
        pygame.draw.rect(screen, item_data["color"], color_rect)
        pygame.draw.rect(screen, BLACK, color_rect, 1)

        # Draw item name
        name_text = font.render(item_name, True, BLACK)
        screen.blit(name_text, (item_rect.x + 50, item_rect.y + 15))

        # Draw price or status
        if is_unlocked:
            if is_selected:
                status_text = small_font.render("SELECTED", True, (0, 100, 0))
            else:
                status_text = small_font.render("OWNED", True, BLACK)
        else:
            status_text = small_font.render(f"Price: {item_data['price']} tokens", True, BLACK)

        screen.blit(status_text, (item_rect.x + item_rect.width - status_text.get_width() - 10, item_rect.y + 15))


def shop_screen(game_state, shop_items):
    tab_buttons = [
        Button(50, 120, 100, 40, "Birds"),
        Button(WIDTH // 2 - 50, 120, 100, 40, "Pipes"),
        Button(WIDTH - 150, 120, 100, 40, "Backgrounds")
    ]

    back_button = Button(10, 10, 80, 30, "Back")
    selected_tab = "Birds"

    running = True
    while running:
        click = False
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True

        # Update buttons
        back_button.update(mouse_pos)
        if back_button.check_click(mouse_pos, click):
            running = False

        for button in tab_buttons:
            button.update(mouse_pos)
            if button.check_click(mouse_pos, click):
                selected_tab = button.text

        # Check for item clicks
        if click:
            y_pos = 130
            items_to_check = []

            if selected_tab == "Birds":
                items_to_check = shop_items.birds
            elif selected_tab == "Pipes":
                items_to_check = shop_items.pipes
            else:
                items_to_check = shop_items.backgrounds

            for i, (item_name, item_data) in enumerate(items_to_check.items()):
                item_rect = pygame.Rect(50, y_pos + i * 60, WIDTH - 100, 50)

                if item_rect.collidepoint(mouse_pos):
                    # Check if already unlocked
                    is_unlocked = False
                    if selected_tab == "Birds":
                        is_unlocked = item_name in game_state.unlocked_birds
                    elif selected_tab == "Pipes":
                        is_unlocked = item_name in game_state.unlocked_pipes
                    else:
                        is_unlocked = item_name in game_state.unlocked_backgrounds

                    # If unlocked, select it
                    if is_unlocked:
                        if selected_tab == "Birds":
                            game_state.current_bird = item_name
                        elif selected_tab == "Pipes":
                            game_state.current_pipe = item_name
                        else:
                            game_state.current_background = item_name
                        game_state.save_data()
                    # Otherwise try to purchase
                    elif game_state.tokens >= item_data["price"]:
                        game_state.tokens -= item_data["price"]

                        if selected_tab == "Birds":
                            game_state.unlocked_birds.append(item_name)
                            game_state.current_bird = item_name
                        elif selected_tab == "Pipes":
                            game_state.unlocked_pipes.append(item_name)
                            game_state.current_pipe = item_name
                        else:
                            game_state.unlocked_backgrounds.append(item_name)
                            game_state.current_background = item_name

                        game_state.save_data()

        # Draw
        draw_background(game_state, shop_items)
        draw_floor()

        # Draw shop content
        draw_shop(game_state, shop_items, selected_tab)

        # Draw buttons
        back_button.draw()
        for button in tab_buttons:
            button.draw()

        pygame.display.flip()
        clock.tick(FPS)


def main_menu(game_state, shop_items):
    play_button = Button(WIDTH // 2 - 100, 260, 200, 50, "Play")
    shop_button = Button(WIDTH // 2 - 100, 330, 200, 50, "Shop")
    quit_button = Button(WIDTH // 2 - 100, 400, 200, 50, "Quit")

    running = True
    while running:
        click = False
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True

        # Update buttons
        play_button.update(mouse_pos)
        shop_button.update(mouse_pos)
        quit_button.update(mouse_pos)

        if play_button.check_click(mouse_pos, click):
            game_loop(game_state, shop_items)
        if shop_button.check_click(mouse_pos, click):
            shop_screen(game_state, shop_items)
        if quit_button.check_click(mouse_pos, click):
            pygame.quit()
            sys.exit()

        # Draw
        draw_background(game_state, shop_items)
        draw_floor()
        draw_menu(game_state)

        # Draw buttons
        play_button.draw()
        shop_button.draw()
        quit_button.draw()

        pygame.display.flip()
        clock.tick(FPS)


def game_loop(game_state, shop_items):
    bird = Bird(game_state, shop_items)
    pipes = []
    game_state.score = 0
    last_pipe = pygame.time.get_ticks()
    game_active = True

    # Calculate tokens earned markers
    tokens_at_score = []
    for i in range(10, 101, 10):  # Show markers for every 10 points up to 100
        tokens_at_score.append(i)

    while True:
        current_time = pygame.time.get_ticks()
        click = False

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
                    bird.flap()
                if event.key == pygame.K_SPACE and not game_active:
                    return  # Return to main menu
                if event.key == pygame.K_ESCAPE:
                    return  # Return to main menu

            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                if game_active:
                    bird.flap()
                else:
                    return  # Return to main menu

        if game_active:
            # Update
            bird.update()

            # Generate new pipes
            if current_time - last_pipe > PIPE_FREQUENCY:
                pipes.append(Pipe(WIDTH, game_state, shop_items))
                last_pipe = current_time

            # Update pipes and check for scoring
            pipes_to_remove = []
            for pipe in pipes:
                pipe.update()

                # Check if bird passed the pipe
                if pipe.x + 50 < bird.x and not pipe.passed:
                    pipe.passed = True
                    game_state.score += 1

                    # Check if token earned (every 10 points)
                    if game_state.score in tokens_at_score:
                        tokens_at_score.remove(game_state.score)

                # Remove pipes that are off screen
                if pipe.x + 50 < 0:
                    pipes_to_remove.append(pipe)

                # Check for collisions
                if pipe.collide(bird):
                    game_active = False
                    game_state.update_score(game_state.score)

            # Remove old pipes
            for pipe in pipes_to_remove:
                pipes.remove(pipe)

            # Check for ground collision
            if bird.y + bird.height // 2 > HEIGHT - GROUND_HEIGHT:
                game_active = False
                game_state.update_score(game_state.score)

        # Draw
        draw_background(game_state, shop_items)

        # Draw pipes
        for pipe in pipes:
            pipe.draw()

        # Draw floor
        draw_floor()

        # Draw bird
        bird.draw()

        # Draw score
        score_text = font.render(f'Score: {game_state.score}', True, BLACK)
        screen.blit(score_text, (10, 10))

        # Draw tokens
        tokens_text = font.render(f'Tokens: {game_state.tokens}', True, BLACK)
        screen.blit(tokens_text, (10, 50))

        # Draw high score
        high_score_text = font.render(f'High Score: {game_state.high_score}', True, BLACK)
        screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

        # Show next token milestone
        if tokens_at_score and game_active:
            next_token_text = small_font.render(f'Next token at: {tokens_at_score[0]} points', True, BLACK)
            screen.blit(next_token_text, (10, 90))

        # Game over text
        if not game_active:
            game_over_text = font.render('Game Over!', True, BLACK)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))

            final_score_text = font.render(f'Final Score: {game_state.score}', True, BLACK)
            screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2))

            if game_state.score == game_state.high_score and game_state.score > 0:
                new_high_text = font.render('New High Score!', True, (255, 0, 0))
                screen.blit(new_high_text, (WIDTH // 2 - new_high_text.get_width() // 2, HEIGHT // 2 + 40))

            back_text = font.render('Press SPACE or Click to continue', True, BLACK)
            screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT // 2 + 80))

        # Update display
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    game_state = GameState()
    shop_items = ShopItems()
    main_menu(game_state, shop_items)