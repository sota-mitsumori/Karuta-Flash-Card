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

card_directory = set/your/own/file/directory

# 画像の読み込み（仮に1から100までの画像があると仮定）
cards = [os.path.join(card_directory, f"torifuda ({i}).jpg") for i in range(1, 101)]

# スタート画面の画像
start_image = pygame.image.load(os.path.join(card_directory, "start_photo.webp"))
finish_image = pygame.image.load(os.path.join(card_directory, "finish_photo.jpg"))

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

def scale_image(image, width, height):
    return pygame.transform.scale(image, (width, height))

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
    display_message(text, font, BLACK, (rect.x + 65, rect.y + 10))

def main():
    global start_time, end_time, best_score, screen, WIDTH, HEIGHT
    running = True
    clock = pygame.time.Clock()
    current_card_index = 0
    random.shuffle(cards)  # 札をシャッフル
    is_fullscreen = False

    # Variables for swipe detection
    swipe_threshold = 20  # Minimum distance for a swipe to be considered
    swipe_start_pos = None

    current_card_rotation = 0

    #Button settings
    button_font = get_scaled_font(WIDTH // 20)
    button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                if not is_fullscreen:
                    WIDTH, HEIGHT = event.w, event.h
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

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
                        current_card_rotation = None

                        if current_card_index == len(cards):
                            # すべての札を表示し終えたら終了時刻を記録
                            end_time = time.time()

                            elapsed_time = end_time - start_time

                            # Update Best Score
                            if best_score is None or elapsed_time < best_score:
                                best_score = elapsed_time
                                save_best_score(best_score)


            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_time is None:
                    if button_rect.collidepoint(event.pos):
                        start_time = time.time()
                else:
                    swipe_start_pos = event.pos # Record the position where the mouse is pressed
                
            elif event.type == pygame.MOUSEBUTTONUP:
                if swipe_start_pos:
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

            

        screen.fill(WHITE)

        if start_time is None:
            start_image_rect = start_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(start_image, start_image_rect)
            draw_button(screen, "Start", button_font, button_rect, GRAY, DARK_GRAY, mouse_pos)
        elif current_card_index < len(cards):
            # 画像の表示
            card_image = pygame.image.load(cards[current_card_index])

            # Determine card rotation once per card display
            if current_card_rotation is None:
                current_card_rotation = 180 if random.choice([True, False]) else 0

            if current_card_rotation == 180:
                card_image = pygame.transform.rotate(card_image, 180)

            scaled_card_image = scale_image(card_image, WIDTH // 2, HEIGHT // 2)
            card_rect = scaled_card_image.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(card_image, card_rect)

            # Display Cards left
            cards_left = len(cards) - current_card_index
            display_message(f"Cards Left: {cards_left}", get_scaled_font(WIDTH // 30), BLACK, (10, 10))
        
        else:
            # 終了メッセージと経過時間の表示
            finish_image_rect = finish_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(finish_image, finish_image_rect)
            display_message("Finished!", get_scaled_font(WIDTH // 20), WHITE, (WIDTH // 2 - 100, HEIGHT // 2))
            if best_score is not None:
                display_message(f"Best Score: {best_score:.2f} s", get_scaled_font(WIDTH // 30), WHITE, (WIDTH // 2 - 100, HEIGHT // 2 + 80))

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
