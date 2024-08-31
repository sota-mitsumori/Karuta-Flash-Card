import pygame
import sys
import random
import time
import os

# Pygameの初期化
pygame.init()

# 画面サイズ
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("百人一首札流しゲーム")

# フォントの設定
def get_scaled_font(size):
    return pygame.font.Font(None, int(size))

# 色の設定
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# 画像の読み込み（仮に1から100までの画像があると仮定）
cards = [f"torifuda ({i}).jpg" for i in range(1, 101)]

# スタート画面の画像
start_image = pygame.image.load("start_photo.webp")
finish_image = pygame.image.load("finish_photo.jpg")

# ストップウォッチ
start_time = None
end_time = None

# Best Score File
best_score_file = "best_score.txt"

# Load Best Score
def load_best_score():
    if os.path.exists(best_score_file):
        with open(best_score_file, "r") as file:
            try:
                return float(file.read().strip())
            except ValueError:
                return None
    return None

# Store Best Score
def save_best_score(score):
    with open(best_score_file, "w") as file:
        file.write(f"{score:.2f}")

# Load 初期　best score
best_score = load_best_score()

def display_message(message, font, color, position):
    text = font.render(message, True, color)
    text_rect = text.get_rect(topleft=position)
    screen.blit(text, text_rect)

def toggle_fullscreen(is_fullscreen):
    if is_fullscreen:
        pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        return False
    else:
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        return True

def draw_button(screen, text, font, rect, color, hover_color, mouse_pos):
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, rect)
    else:
        pygame.draw.rect(screen, color, rect)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

# New: Draw Settings Menu
def draw_settings_menu(card_rotation_option, screen, WIDTH, HEIGHT):
    screen.fill(WHITE)
    settings_font = get_scaled_font(WIDTH // 20)
    
    # Title
    display_message("Settings", settings_font, BLACK, (WIDTH // 2 - 100, HEIGHT // 4))
    
    # Option: Card Rotation
    display_message("Card Rotation:", settings_font, BLACK, (WIDTH // 4, HEIGHT // 2 - 50))
    
    # Rotation Buttons
    rotation_options = ["0 degrees", "180 degrees", "Random"]
    rotation_buttons = []
    button_width, button_height = 160, 40
    spacing = 180
    start_x = WIDTH // 2 - (spacing * (len(rotation_options) - 1)) // 2
    y_pos = HEIGHT // 2
    
    for i, option in enumerate(rotation_options):
        rect = pygame.Rect(start_x + i * spacing, y_pos, button_width, button_height)
        rotation_buttons.append((rect, option))
        pygame.draw.rect(screen, GRAY, rect)
        text_surface = settings_font.render(option, True, BLACK)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
    
    # Back Button
    back_button_rect = pygame.Rect(WIDTH // 2 - 50, y_pos + 100, 100, 50)
    pygame.draw.rect(screen, GRAY, back_button_rect)
    back_text = settings_font.render("Back", True, BLACK)
    back_text_rect = back_text.get_rect(center=back_button_rect.center)
    screen.blit(back_text, back_text_rect)
    
    pygame.display.flip()
    
    return rotation_buttons, back_button_rect

# New: Handle Settings Input
def handle_settings_input(event, rotation_buttons, back_button_rect):
    global card_rotation_option, settings_menu_open
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = event.pos
        for rect, option in rotation_buttons:
            if rect.collidepoint(mouse_pos):
                card_rotation_option = option
                return
        if back_button_rect.collidepoint(mouse_pos):
            settings_menu_open = False

# Initialize Settings Variables
settings_menu_open = False
card_rotation_option = "0 degrees"  # Default rotation option

def main():
    global start_time, end_time, best_score, screen, WIDTH, HEIGHT, settings_menu_open, card_rotation_option
    running = True
    clock = pygame.time.Clock()
    current_card_index = 0
    random.shuffle(cards)  # 札をシャッフル
    is_fullscreen = False

    # Variables for swipe detection
    swipe_threshold = 20  # Minimum distance for a swipe to be considered
    swipe_start_pos = None

    #Button settings
    button_font = get_scaled_font(WIDTH // 20)
    start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
    settings_button_rect = pygame.Rect(WIDTH - 150, 10, 120, 40)

    # Settings Menu Buttons (initialized later)
    rotation_buttons = []
    back_button_rect = None

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                if not is_fullscreen and not settings_menu_open:
                    WIDTH, HEIGHT = event.w, event.h
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    # Update button positions
                    start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
                    settings_button_rect = pygame.Rect(WIDTH - 150, 10, 120, 40)
            
            if settings_menu_open:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Handle settings menu input
                    handle_settings_input(event, rotation_buttons, back_button_rect)
            else:
                if event.type == pygame.KEYDOWN:
                    #　Toggle Full Screen                
                    if event.key == pygame.K_f:
                        is_fullscreen = toggle_fullscreen(is_fullscreen)

                    elif event.key == pygame.K_SPACE:
                        if start_time is None:
                            # スタート
                            start_time = time.time()
                        elif current_card_index < len(cards):
                            # 次の札を表示
                            current_card_index += 1

                            if current_card_index == len(cards):
                                # すべての札を表示し終えたら終了時刻を記録
                                end_time = time.time()

                                elapsed_time = end_time - start_time

                                # Update Best Score
                                if best_score is None or elapsed_time < best_score:
                                    best_score = elapsed_time
                                    save_best_score(best_score)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not start_time:
                        if start_button_rect.collidepoint(event.pos):
                            start_time = time.time()
                    elif current_card_index < len(cards):
                        swipe_start_pos = event.pos  # Record the position where the mouse is pressed
                    # Check if settings button is clicked
                    if settings_button_rect.collidepoint(event.pos):
                        settings_menu_open = True
                        # Initialize settings menu buttons
                        rotation_buttons, back_button_rect = draw_settings_menu(card_rotation_option, screen, WIDTH, HEIGHT)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if swipe_start_pos and not settings_menu_open:
                        swipe_end_pos = event.pos  # Record the position where the mouse button is released
                        swipe_distance = swipe_end_pos[0] - swipe_start_pos[0]

                        if abs(swipe_distance) > swipe_threshold:
                            # Detect a swipe and show the next card if swiping to the right
                            if swipe_distance > 0 and start_time is not None and current_card_index < len(cards):
                                current_card_index += 1

                                if current_card_index == len(cards):
                                    end_time = time.time()
                                    elapsed_time = end_time - start_time
                                    if best_score is None or elapsed_time < best_score:
                                        best_score = elapsed_time
                                        save_best_score(best_score)
                    swipe_start_pos = None  # Reset swipe start position

        if settings_menu_open:
            # Settings menu is already drawn and handled within the event loop
            # So we just need to keep the settings menu on the screen
            # and prevent other drawings
            draw_settings_menu(card_rotation_option, screen, WIDTH, HEIGHT)
            # Note: To avoid redrawing multiple times, you can optimize this
        else:
            screen.fill(WHITE)

            if start_time is None:
                # Start Screen
                start_image_rect = start_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                screen.blit(start_image, start_image_rect)
                draw_button(screen, "Start", button_font, start_button_rect, GRAY, DARK_GRAY, mouse_pos)
                draw_button(screen, "Settings", button_font, settings_button_rect, GRAY, DARK_GRAY, mouse_pos)
            elif current_card_index < len(cards):
                # Game Screen: Display current card
                try:
                    card_image = pygame.image.load(cards[current_card_index])
                except pygame.error:
                    print(f"Error loading image: {cards[current_card_index]}")
                    card_image = pygame.Surface((WIDTH // 2, HEIGHT // 2))
                    card_image.fill(GRAY)

                # Apply rotation based on the selected option
                if card_rotation_option == "0 degrees":
                    rotated_card_image = card_image
                elif card_rotation_option == "180 degrees":
                    rotated_card_image = pygame.transform.rotate(card_image, 180)
                elif card_rotation_option == "Random":
                    rotated_card_image = pygame.transform.rotate(card_image, random.choice([0, 180]))

                card_rect = rotated_card_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(rotated_card_image, card_rect)

                # Display Cards left
                cards_left = len(cards) - current_card_index
                display_message(f"Cards Left: {cards_left}", get_scaled_font(WIDTH // 30), BLACK, (10, 10))

                # Draw Settings Button
                draw_button(screen, "Settings", button_font, settings_button_rect, GRAY, DARK_GRAY, mouse_pos)
            else:
                # Finished Screen
                finish_image_rect = finish_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                screen.blit(finish_image, finish_image_rect)
                display_message("Finished!", get_scaled_font(WIDTH // 20), WHITE, (WIDTH // 2 - 100, HEIGHT // 2))
                if best_score is not None:
                    display_message(f"Best Score: {best_score:.2f} s", get_scaled_font(WIDTH // 30), WHITE, (WIDTH // 2 - 100, HEIGHT // 2 + 80))

                # Draw Settings Button
                draw_button(screen, "Settings", button_font, settings_button_rect, GRAY, DARK_GRAY, mouse_pos)

            # 経過時間を右上に表示
            if start_time is not None:
                if end_time is None:
                    elapsed_time = time.time() - start_time
                    display_message(f"Time: {elapsed_time:.2f} s", get_scaled_font(WIDTH // 30), BLACK, (WIDTH - 150, 10))
                else:
                    elapsed_time = end_time - start_time
                    display_message(f"Time: {elapsed_time:.2f} s", get_scaled_font(WIDTH // 30), WHITE, (WIDTH // 2 - 100, HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
