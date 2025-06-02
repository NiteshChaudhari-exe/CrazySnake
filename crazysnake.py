import math
import pygame
import random
import os
import pickle

# --- SETTINGS & GLOBALS ---
pygame.init()
width, height = 800, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Crazy Snake')

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
gray = (100, 100, 100)

snake_block = 20
init_speed = 10
speed_increase = 1

font_style = pygame.font.SysFont(None, 50)
score_font = pygame.font.SysFont(None, 35)
clock = pygame.time.Clock()

# --- SETTINGS & GLOBALS ---
controls = {
    "start": pygame.K_SPACE,
    "quit": pygame.K_q,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "pause": pygame.K_p
}
music_on = True
sound_on = True

# --- MUSIC & SOUND ---
def play_sound(event):
    if not sound_on:
        return
    # Example: pygame.mixer.Sound('eat.wav').play()
    pass

def play_music():
    if music_on:
        # Example: pygame.mixer.music.load('background.mp3')
        # pygame.mixer.music.play(-1)
        pass

# --- SNAKE CLASS ---
class Snake:
    def __init__(self):
        self.body = [[width // 2, height // 2]]
        self.length = 1
        self.dx = 0
        self.dy = 0
        self.last_dir = None

    def move(self):
        head = [self.body[-1][0] + self.dx, self.body[-1][1] + self.dy]
        self.body.append(head)
        if len(self.body) > self.length:
            del self.body[0]

    def grow(self):
        self.length += 1

    def draw(self):
        for b in self.body:
            pygame.draw.rect(window, white, [b[0], b[1], snake_block, snake_block])  # Snake is now white

    def check_collision(self):
        head = self.body[-1]
        # Check wall collision
        if head[0] < 0 or head[0] >= width or head[1] < 0 or head[1] >= height:
            return True
        # Check self collision
        if head in self.body[:-1]:
            return True
        return False

    # Python
    def get_head(self):
        return self.body[-1]

# --- FOOD CLASS ---
class Food:
    def __init__(self):
        self.relocate([])

    def relocate(self, snake_list):
        while True:
            self.x = round(random.randrange(0, width - snake_block) / snake_block) * snake_block
            self.y = round(random.randrange(0, height - snake_block) / snake_block) * snake_block
            if [self.x, self.y] not in snake_list:
                break

    def draw(self):
        pygame.draw.rect(window, green, [self.x, self.y, snake_block, snake_block])  # Normal food is green

# --- OBSTACLES ---
class Obstacle:
    def __init__(self, avoid=None):
        if avoid is None:
            avoid = []
        while True:
            self.x = round(random.randrange(0, width - snake_block) / snake_block) * snake_block
            self.y = round(random.randrange(0, height - snake_block) / snake_block) * snake_block
            if [self.x, self.y] not in avoid:
                break
    def draw(self):
        pygame.draw.rect(window, gray, [self.x, self.y, snake_block, snake_block])

# --- POWER-UPS ---
class PowerUp:
    def __init__(self, kind=None, blink=False):
        # kind: 'slow' (red, slows snake) or 'bonus' (blue, +5 points)
        if kind is None:
            self.type = random.choice(['slow', 'bonus'])
        else:
            self.type = kind
        self.x = round(random.randrange(0, width - snake_block) / snake_block) * snake_block
        self.y = round(random.randrange(0, height - snake_block) / snake_block) * snake_block
        self.blink = blink
        self.blink_state = True
        self.blink_timer = pygame.time.get_ticks()

    def draw(self):
        # Red for slow, Blue for bonus (blinking if needed)
        if self.type == 'slow':
            color = red
        else:  # 'bonus'
            # Blinking effect
            if self.blink:
                now = pygame.time.get_ticks()
                if now - self.blink_timer > 250:
                    self.blink_state = not self.blink_state
                    self.blink_timer = now
                color = blue if self.blink_state else white
            else:
                color = blue
        pygame.draw.rect(window, color, [self.x, self.y, snake_block, snake_block])

# --- LEADERBOARD ---
def load_leaderboard():
    if os.path.exists("leaderboard.txt"):
        with open("leaderboard.txt", "r") as f:
            # Now each line is "name,score"
            entries = []
            for line in f:
                parts = line.strip().split(",", 1)
                if len(parts) == 2:
                    name, score = parts
                    entries.append((name, int(score)))
            return entries
    return []

def save_leaderboard(entries):
    with open("leaderboard.txt", "w") as f:
        for name, score in entries:
            f.write(f"{name},{score}\n")

def update_leaderboard(name, score):
    entries = load_leaderboard()
    entries.append((name, score))
    # Sort by score descending, keep only top 3
    entries = sorted(entries, key=lambda x: x[1], reverse=True)[:3]
    save_leaderboard(entries)
    return entries

def draw_leaderboard():
    entries = load_leaderboard()
    # Increased height to fit top 3 scores more comfortably
    leaderboard_rect = pygame.Rect(width // 2 - 170, height - 180, 340, 150)
    # Draw the board background and border
    pygame.draw.rect(window, (20, 20, 40), leaderboard_rect, border_radius=16)
    pygame.draw.rect(window, (80, 200, 255), leaderboard_rect, 4, border_radius=16)
    # Draw the "Leaderboard" title just above the board, in black
    leaderboard_title = font_style.render("Leaderboard", True, black)
    # Move the title just above the rectangle (10px above)
    window.blit(leaderboard_title, (leaderboard_rect.x + 60, leaderboard_rect.y - 40))
    trophy = "🏆"
    for idx, (name, score) in enumerate(entries[:3]):
        color = (255, 215, 0) if idx == 0 else (192, 192, 192) if idx == 1 else (205, 127, 50)
        pos_y = leaderboard_rect.y + 35 + idx * 32  # More vertical space between entries
        score_text = f"{trophy if idx == 0 else ''} {idx+1}. {name} - {score}"
        msg = score_font.render(score_text, True, color)
        window.blit(msg, (leaderboard_rect.x + 30, pos_y))

# --- HIGH SCORE ---
def load_high_score():
    if os.path.exists("high_score.txt"):
        with open("high_score.txt", "r") as f:
            return int(f.read())
    return 0

def save_high_score(score):
    with open("high_score.txt", "w") as f:
        f.write(str(score))

# --- SCORE DISPLAY ---
def draw_score(score, high_score):
    value = score_font.render(f"Score: {score}  High Score: {high_score}", True, yellow)
    window.blit(value, [0, 0])

# --- ACHIEVEMENTS ---
def check_achievements(score):
    achievements = []
    if score >= 10:
        achievements.append("Score 10!")
    if score >= 25:
        achievements.append("Score 25!")
    if score >= 50:
        achievements.append("Score 50!")
    return achievements

def draw_achievement_popup(achievement):
    popup = pygame.Surface((400, 80), pygame.SRCALPHA)
    popup.fill((0, 0, 0, 180))
    msg = font_style.render(f"Achievement: {achievement}", True, yellow)
    popup.blit(msg, (20, 20))
    window.blit(popup, (width // 2 - 200, height // 2 - 40))
    pygame.display.update()
    pygame.time.delay(1200)

def draw_achievements(achievements):
    y = height - 100
    for ach in achievements:
        msg = score_font.render(ach, True, yellow)
        window.blit(msg, [10, y])
        y += 30

# --- SETTINGS MENU ---
def settings_menu():
    global music_on, sound_on
    running = True
    back_button_rect = pygame.Rect(width // 3, 300, 200, 40)
    while running:
        window.fill(black)
        msg = font_style.render("Settings", True, white)
        window.blit(msg, [width // 3, 50])
        music_msg = score_font.render(f"Music: {'On' if music_on else 'Off'} (M)", True, yellow)
        sound_msg = score_font.render(f"Sound: {'On' if sound_on else 'Off'} (S)", True, yellow)
        back_msg = score_font.render("Back", True, gray)
        window.blit(music_msg, [width // 3, 150])
        window.blit(sound_msg, [width // 3, 200])
        # Draw back button rectangle
        pygame.draw.rect(window, gray, back_button_rect, border_radius=8)
        window.blit(back_msg, [width // 3 + 60, 305])
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    music_on = not music_on
                if event.key == pygame.K_s:
                    sound_on = not sound_on
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    running = False
    # Show main menu after back
    window.fill(black)
    pygame.display.update()

# --- TWO PLAYER MODE (SIMPLE) ---
class Snake2(Snake):
    def __init__(self):
        super().__init__()
        self.body = [[width // 4, height // 2]]
        self.dx = 0
        self.dy = 0
        self.last_dir = None

    def draw(self):
        for b in self.body:
            pygame.draw.rect(window, red, [b[0], b[1], snake_block, snake_block])

# --- MAIN GAME CLASS MODIFICATIONS ---
class Game:
    def __init__(self, two_player=False):
        self.difficulty = "Normal"  # Default
        self.set_difficulty_params()
        self.high_score = load_high_score()
        self.reset()
        self.two_player = two_player
        if two_player:
            self.snake2 = Snake2()
        self.obstacles = [Obstacle(avoid=self.snake.body + [[self.food.x, self.food.y]]) for _ in range(self.obstacle_count)]
        self.powerup = None
        self.powerup_timer = 0
        self.achievements = []

    def set_difficulty_params(self):
        if self.difficulty == "Easy":
            self.snake_speed = 7
            self.obstacle_count = 3
        elif self.difficulty == "Normal":
            self.snake_speed = 10
            self.obstacle_count = 7
        else:  # Hard
            self.snake_speed = 14
            self.obstacle_count = 12

    def reset(self):
        self.snake = Snake()
        if hasattr(self, 'two_player') and self.two_player:
            self.snake2 = Snake2()
        self.food = Food()
        self.score = 0
        self.set_difficulty_params()
        self.paused = False
        self.obstacles = [Obstacle(avoid=self.snake.body + [[self.food.x, self.food.y]]) for _ in range(self.obstacle_count)]
        self.powerup = None
        self.powerup_timer = 0
        self.achievements = []

    def welcome_screen(self):
        """
        Display a welcome/introduction screen before showing the main menu.
        """
        intro_lines = [
            "Welcome to Crazy Snake!",
            "",
            "Eat food to grow and score points.",
            "Avoid obstacles and yourself.",
            "Collect power-ups for special effects.",
            "",
            "Press any key or click to continue..."
        ]
        window.fill(black)
        # Draw a simple logo/title
        title = font_style.render("Crazy Snake", True, green)
        window.blit(title, (width // 2 - title.get_width() // 2, height // 6))
        # Draw intro/instructions
        for i, line in enumerate(intro_lines):
            color = yellow if i == 0 else white
            msg = score_font.render(line, True, color)
            window.blit(msg, (width // 2 - msg.get_width() // 2, height // 3 + i * 40))
        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

    def start_screen(self):
        self.welcome_screen()
        button_width, button_height = 200, 60
        button_gap = 20
        menu_items = ["Play", "Settings", "Scores", "Credits", "Exit"]
        menu_count = len(menu_items)
        total_height = menu_count * button_height + (menu_count - 1) * button_gap
        start_y = (height - total_height) // 2
        start_x = (width - button_width) // 2

        button_rects = [
            pygame.Rect(start_x, start_y + (button_height + button_gap) * i, button_width, button_height)
            for i in range(menu_count)
        ]
        show_leaderboard = False
        show_credits = False
        selected_idx = 0
        tips = [
            "Tip: Eat food to grow and score points!",
            "Tip: Avoid obstacles and yourself.",
            "Tip: Collect power-ups for special effects.",
            "Tip: Press ESC to close popups.",
            "Tip: Use arrow keys or mouse to navigate.",
            "Tip: Change difficulty before playing!"
        ]
        tip_idx = 0
        tip_timer = pygame.time.get_ticks()

        # --- Animated circles state ---
        circle_count = 5
        circle_states = []
        for i in range(circle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.2, 0.6)
            radius = random.randint(60, 90)
            base_x = width // 2 + random.randint(-200, 200)
            base_y = 150 + 80 * i
            color_phase = random.uniform(0, 2 * math.pi)
            circle_states.append({
                "angle": angle,
                "speed": speed,
                "radius": radius,
                "base_x": base_x,
                "base_y": base_y,
                "color_phase": color_phase
            })

        pygame.mouse.set_visible(True)
        while True:
            # Draw vertical gradient background
            for y in range(height):
                blend = y / height
                r = int(30 * (1 - blend) + 0 * blend)
                g = int(30 * (1 - blend) + 120 * blend)
                b = int(60 * (1 - blend) + 120 * blend)
                pygame.draw.line(window, (r, g, b), (0, y), (width, y))

            # Animated moving and color-changing circles
            t = pygame.time.get_ticks() / 1000.0
            for i, state in enumerate(circle_states):
                state["angle"] += state["speed"] * 15
                x = int(state["base_x"] + 120 * math.cos(state["angle"] + t * 0.4 + i))
                y = int(state["base_y"] + 60 * math.sin(state["angle"] + t * 0.3 + i))
                phase = state["color_phase"] + t * 0.9
                r = int(100 + 100 * math.sin(phase))
                g = int(150 + 100 * math.sin(phase + 2))
                b = int(200 + 55 * math.sin(phase + 4))
                color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 60)
                surface = pygame.Surface((state["radius"]*2, state["radius"]*2), pygame.SRCALPHA)
                pygame.draw.circle(surface, color, (state["radius"], state["radius"]), state["radius"])
                window.blit(surface, (x - state["radius"], y - state["radius"]))

            # Animated Title (pulsing)
            title_scale = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() / 400)
            title_font = pygame.font.SysFont(None, int(60 * title_scale))
            title = title_font.render("Crazy Snake", True, green)
            window.blit(title, (width // 2 - title.get_width() // 2, height // 8))

            # High Score Display
            high_score = load_high_score()
            hs_msg = score_font.render(f"High Score: {high_score}", True, yellow)
            window.blit(hs_msg, (width // 2 - hs_msg.get_width() // 2, height // 8 + 60))

            # Draw Buttons with Hover and Keyboard Effects
            mouse_pos = pygame.mouse.get_pos()
            hovered_button = None
            for idx, rect in enumerate(button_rects):
                is_hover = rect.collidepoint(mouse_pos)
                is_selected = idx == selected_idx
                color = (
                    (0, 255, 100) if (is_hover or is_selected) and menu_items[idx] == "Play" else
                    (255, 255, 180) if (is_hover or is_selected) and menu_items[idx] == "Settings" else
                    (120, 220, 255) if (is_hover or is_selected) and menu_items[idx] == "Scores" else
                    (200, 200, 200) if (is_hover or is_selected) and menu_items[idx] == "Credits" else
                    (255, 100, 100) if (is_hover or is_selected) and menu_items[idx] == "Exit" else
                    green if menu_items[idx] == "Play" else
                    yellow if menu_items[idx] == "Settings" else
                    (80, 200, 255) if menu_items[idx] == "Scores" else
                    gray if menu_items[idx] == "Credits" else
                    red
                )
                pygame.draw.rect(window, color, rect, border_radius=12)
                msg = font_style.render(menu_items[idx], True, black)
                window.blit(msg, (rect.x + (button_width - msg.get_width()) // 2, rect.y + 10))
                if is_hover:
                    hovered_button = idx

            # Settings Preview Icons
            music_icon = "♪" if music_on else "✖"
            sound_icon = "🔊" if sound_on else "✖"
            music_msg = score_font.render(f"Music: {music_icon}", True, yellow)
            sound_msg = score_font.render(f"Sound: {sound_icon}", True, yellow)
            window.blit(music_msg, (20, 20))
            window.blit(sound_msg, (20, 60))

            # Difficulty Display (clickable)
            diff_rect = pygame.Rect(width - 220, 20, 180, 50)
            pygame.draw.rect(window, (80, 200, 255), diff_rect, border_radius=8)
            diff_msg = score_font.render(f"Difficulty: {self.difficulty}", True, black)
            window.blit(diff_msg, (width - 210, 32))

            # Custom Cursor (snake head)
            mx, my = pygame.mouse.get_pos()
            pygame.draw.circle(window, green, (mx, my), 10)
            pygame.draw.circle(window, black, (mx + 4, my - 3), 2)
            pygame.draw.circle(window, black, (mx - 4, my - 3), 2)

            # Dynamic Tip at the bottom
            if pygame.time.get_ticks() - tip_timer > 4000:
                tip_idx = (tip_idx + 1) % len(tips)
                tip_timer = pygame.time.get_ticks()
            tip_msg = score_font.render(tips[tip_idx], True, white)
            window.blit(tip_msg, (width // 2 - tip_msg.get_width() // 2, height - 40))

            # Show leaderboard popup if toggled
            if show_leaderboard:
                background = window.copy()
                small = pygame.transform.smoothscale(background, (width // 5, height // 5))
                blur = pygame.transform.smoothscale(small, (width, height))
                window.blit(blur, (0, 0))
                overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 60))
                window.blit(overlay, (0, 0))

                entries = load_leaderboard()
                leaderboard_rect = pygame.Rect(width // 2 - 170, height // 2 - 120, 340, 150)
                pygame.draw.rect(window, (20, 20, 40), leaderboard_rect, border_radius=16)
                pygame.draw.rect(window, (80, 200, 255), leaderboard_rect, 4, border_radius=16)
                leaderboard_title = font_style.render("Scores", True, white)
                window.blit(leaderboard_title, (leaderboard_rect.x + 60, leaderboard_rect.y - 40))
                trophy = "🏆"
                leaderboard_font = pygame.font.SysFont(None, 32)
                for idx, (name, score) in enumerate(entries[:3]):
                    color = (255, 215, 0) if idx == 0 else (192, 192, 192) if idx == 1 else (205, 127, 50)
                    pos_y = leaderboard_rect.y + 35 + idx * 32
                    score_text = f"{trophy if idx == 0 else ''} {idx+1}. {name} - {score}"
                    msg = leaderboard_font.render(score_text, True, color)
                    window.blit(msg, (leaderboard_rect.x + 30, pos_y))

            # Show credits popup if toggled
            if show_credits:
                overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                window.blit(overlay, (0, 0))
                credits_lines = [
                    "Crazy Snake",
                    "Created by: Your Name",
                    "Version: 1.0",
                    "",
                    "Thanks for playing!"
                ]
                for i, line in enumerate(credits_lines):
                    msg = font_style.render(line, True, white)
                    window.blit(msg, (width // 2 - msg.get_width() // 2, height // 3 + i * 50))

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if show_leaderboard or show_credits:
                    if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        show_leaderboard = False
                        show_credits = False
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            selected_idx = (selected_idx - 1) % menu_count
                        elif event.key == pygame.K_DOWN:
                            selected_idx = (selected_idx + 1) % menu_count
                        elif event.key == pygame.K_RETURN:
                            if selected_idx == 0:  # Play
                                self.set_difficulty_params()
                                self.reset()
                                return
                            elif selected_idx == 1:  # Settings
                                settings_menu()
                            elif selected_idx == 2:  # Scores
                                show_leaderboard = True
                            elif selected_idx == 3:  # Credits
                                show_credits = True
                            elif selected_idx == 4:  # Exit
                                pygame.quit()
                                quit()
                        elif event.key == pygame.K_d:
                            # Cycle difficulty with D key
                            if self.difficulty == "Easy":
                                self.difficulty = "Normal"
                            elif self.difficulty == "Normal":
                                self.difficulty = "Hard"
                            else:
                                self.difficulty = "Easy"
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Difficulty button click
                        if diff_rect.collidepoint(event.pos):
                            if self.difficulty == "Easy":
                                self.difficulty = "Normal"
                            elif self.difficulty == "Normal":
                                self.difficulty = "Hard"
                            else:
                                self.difficulty = "Easy"
                        for idx, rect in enumerate(button_rects):
                            if rect.collidepoint(event.pos):
                                if idx == 0:
                                    self.set_difficulty_params()
                                    self.reset()
                                    return
                                elif idx == 1:
                                    settings_menu()
                                elif idx == 2:
                                    show_leaderboard = True
                                elif idx == 3:
                                    show_credits = True
                                elif idx == 4:
                                    pygame.quit()
                                    quit()

    def game_over_screen(self):
        window.fill(black)
        msg = font_style.render("Better Luck Next Time", True, red)
        window.blit(msg, [width // 3, height // 4])
        draw_score(self.score, self.high_score)
        draw_achievements(self.achievements)

        # --- Name Entry for Leaderboard ---
        name = ""
        input_active = True
        prompt = score_font.render("Enter your name: ", True, yellow)
        pygame.display.update()
        while input_active:
            window.fill(black)
            window.blit(msg, [width // 3, height // 4])
            window.blit(prompt, (width // 3, height // 2))
            name_surface = score_font.render(name + "|", True, white)
            window.blit(name_surface, (width // 3 + 260, height // 2))
            draw_achievements(self.achievements)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name.strip() != "":
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif len(name) < 10 and event.unicode.isprintable():
                        name += event.unicode

        # Update leaderboard with name and score
        update_leaderboard(name.strip(), self.score)

        # Show leaderboard and options
        button_width = 180
        button_height = 50
        button_gap = 20
        total_width = button_width * 3 + button_gap * 2
        start_x = (width - total_width) // 2
        y_pos = int(height // 4 + 80)

        # Create three buttons: Restart, Menu, Quit
        restart_button = pygame.Rect(start_x, y_pos, button_width, button_height)
        menu_button = pygame.Rect(start_x + button_width + button_gap, y_pos, button_width, button_height)
        quit_button = pygame.Rect(start_x + (button_width + button_gap) * 2, y_pos, button_width, button_height)

        waiting = True
        while waiting:
            window.fill(black)
            window.blit(msg, [width // 3, height // 4])
            draw_score(self.score, self.high_score)
            draw_leaderboard()
            draw_achievements(self.achievements)

            # Mouse position for hover effects
            mouse_pos = pygame.mouse.get_pos()

            # Draw Restart button with hover effect
            restart_color = (0, 255, 100) if restart_button.collidepoint(mouse_pos) else green
            pygame.draw.rect(window, restart_color, restart_button, border_radius=10)
            restart_msg = score_font.render("Restart", True, black)
            window.blit(restart_msg, (restart_button.x + 35, restart_button.y + 8))

            # Draw Menu button with hover effect
            menu_color = (255, 255, 180) if menu_button.collidepoint(mouse_pos) else yellow
            pygame.draw.rect(window, menu_color, menu_button, border_radius=10)
            menu_msg = score_font.render("Menu", True, black)
            window.blit(menu_msg, (menu_button.x + 50, menu_button.y + 8))

            # Draw Quit button with hover effect
            quit_color = (255, 100, 100) if quit_button.collidepoint(mouse_pos) else red
            pygame.draw.rect(window, quit_color, quit_button, border_radius=10)
            quit_msg = score_font.render("Quit", True, black)
            window.blit(quit_msg, (quit_button.x + 55, quit_button.y + 8))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        quit()
                    if event.key == pygame.K_c:
                        self.reset()
                        waiting = False
                    if event.key == pygame.K_m:
                        # Remove welcome screen call and go directly to menu
                        self.reset()
                        self.start_screen()  # This will skip welcome screen on subsequent calls
                        return  # Return to prevent additional resets
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.collidepoint(event.pos):
                        self.reset()
                        waiting = False
                    if menu_button.collidepoint(event.pos):
                        # Remove welcome screen call and go directly to menu
                        self.reset()
                        self.start_screen()  # This will skip welcome screen on subsequent calls
                        return  # Return to prevent additional resets
                    if quit_button.collidepoint(event.pos):
                        pygame.quit()
                        quit()

    def pause_screen(self):
        msg = font_style.render("Paused. Press P to Resume or ESC for Menu.", True, gray)
        window.blit(msg, [width // 8, height // 2])
        pygame.display.update()
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False
                    if event.key == pygame.K_ESCAPE:
                        settings_menu()
                        paused = False

    def save_game(self):
        state = {
            "snake": self.snake.body,
            "length": self.snake.length,
            "dx": self.snake.dx,
            "dy": self.snake.dy,
            "score": self.score,
            "snake_speed": self.snake_speed,
            "food": (self.food.x, self.food.y),
            "obstacles": [(o.x, o.y) for o in self.obstacles],
            "powerup": (self.powerup.x, self.powerup.y, self.powerup.type) if self.powerup else None
        }
        with open("savegame.pkl", "wb") as f:
            pickle.dump(state, f)

    def load_game(self):
        if not os.path.exists("savegame.pkl"):
            return
        with open("savegame.pkl", "rb") as f:
            state = pickle.load(f)
        self.snake.body = state["snake"]
        self.snake.length = state["length"]
        self.snake.dx = state["dx"]
        self.snake.dy = state["dy"]
        self.score = state["score"]
        self.snake_speed = state["snake_speed"]
        self.food.x, self.food.y = state["food"]
        self.obstacles = [Obstacle() for _ in state["obstacles"]]
        for i, (x, y) in enumerate(state["obstacles"]):
            self.obstacles[i].x = x
            self.obstacles[i].y = y
        if state["powerup"]:
            x, y, t = state["powerup"]
            self.powerup = PowerUp()
            self.powerup.x = x
            self.powerup.y = y
            self.powerup.type = t
        else:
            self.powerup = None

    def run(self):
        play_music()
        self.start_screen()
        running = True
        direction = None
        invincible = False
        invincible_timer = 0
        last_bonus_score = 0  # Track last score when bonus appeared
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # Pause
                    if event.key == controls["pause"]:
                        self.pause_screen()
                    # Movement (no reverse)
                    elif event.key == controls["left"] and self.snake.last_dir != "RIGHT":
                        self.snake.dx = -snake_block
                        self.snake.dy = 0
                        self.snake.last_dir = "LEFT"
                    elif event.key == controls["right"] and self.snake.last_dir != "LEFT":
                        self.snake.dx = snake_block
                        self.snake.dy = 0
                        self.snake.last_dir = "RIGHT"
                    elif event.key == controls["up"] and self.snake.last_dir != "DOWN":
                        self.snake.dy = -snake_block
                        self.snake.dx = 0
                        self.snake.last_dir = "UP"
                    elif event.key == controls["down"] and self.snake.last_dir != "UP":
                        self.snake.dy = snake_block
                        self.snake.dx = 0
                        self.snake.last_dir = "DOWN"
                    # Two player controls (WASD)
                    if self.two_player:
                        if event.key == pygame.K_a and self.snake2.last_dir != "RIGHT":
                            self.snake2.dx = -snake_block
                            self.snake2.dy = 0
                            self.snake2.last_dir = "LEFT"
                        elif event.key == pygame.K_d and self.snake2.last_dir != "LEFT":
                            self.snake2.dx = snake_block
                            self.snake2.dy = 0
                            self.snake2.last_dir = "RIGHT"
                        elif event.key == pygame.K_w and self.snake2.last_dir != "DOWN":
                            self.snake2.dy = -snake_block
                            self.snake2.dx = 0
                            self.snake2.last_dir = "UP"
                        elif event.key == pygame.K_s and self.snake2.last_dir != "UP":
                            self.snake2.dy = snake_block
                            self.snake2.dx = 0
                            self.snake2.last_dir = "DOWN"
                    # Save and Load
                    if event.key == pygame.K_F5:
                        self.save_game()
                    if event.key == pygame.K_F9:
                        self.load_game()

            self.snake.move()
            if self.two_player:
                self.snake2.move()

            # --- COLLISION CHECKS ---
            if not invincible and self.snake.check_collision():
                play_sound("lose")
                if self.score > self.high_score:
                    self.high_score = self.score
                    save_high_score(self.high_score)
                self.achievements = check_achievements(self.score)
                self.game_over_screen()
                self.start_screen()
                self.reset()
                continue

            # Obstacle collision
            for obs in self.obstacles:
                if self.snake.get_head() == [obs.x, obs.y]:
                    if not invincible:
                        play_sound("lose")
                        self.achievements = check_achievements(self.score)
                        self.game_over_screen()
                        self.start_screen()
                        self.reset()
                        continue

            # Power-up spawn logic
            # Blue bonus appears after every 5 points, blinks
            if self.score > 0 and self.score % 5 == 0 and (not self.powerup or self.powerup.type != 'bonus'):
                if last_bonus_score != self.score:
                    self.powerup = PowerUp(kind='bonus', blink=True)
                    self.powerup_timer = pygame.time.get_ticks()
                    last_bonus_score = self.score
            # Red slow appears randomly if no powerup present and not just after bonus
            elif not self.powerup and random.randint(1, 100) == 1:
                self.powerup = PowerUp(kind='slow')
                self.powerup_timer = pygame.time.get_ticks()

            # Power-up timeout (5 seconds)
            if self.powerup and pygame.time.get_ticks() - self.powerup_timer > 5000:
                self.powerup = None

            window.fill(black)
            self.food.draw()
            for obs in self.obstacles:
                obs.draw()
            if self.powerup:
                self.powerup.draw()
            self.snake.draw()
            if self.two_player:
                self.snake2.draw()
            draw_score(self.score, self.high_score)
            draw_achievements(self.achievements)

            # Eating food
            if self.snake.get_head()[0] == self.food.x and self.snake.get_head()[1] == self.food.y:
                play_sound("eat")
                self.snake.grow()
                self.score += 1
                self.food.relocate(self.snake.body)
                # Increase speed every 5 points
                if self.score % 5 == 0:
                    self.snake_speed += speed_increase
                # Add more obstacles as score increases
                if self.score % 10 == 0:
                    self.obstacles.append(Obstacle(avoid=self.snake.body + [[self.food.x, self.food.y]]))
                # Achievement popup
                new_achievements = check_achievements(self.score)
                for ach in new_achievements:
                    if ach not in self.achievements:
                        draw_achievement_popup(ach)
                        self.achievements.append(ach)

            # Power-up collision
            if self.powerup and self.snake.get_head() == [self.powerup.x, self.powerup.y]:
                if self.powerup.type == 'bonus':
                    self.score += 5
                elif self.powerup.type == 'slow':
                    self.snake_speed = max(5, self.snake_speed - 3)
                play_sound("powerup")
                self.powerup = None

            # Invincibility timer
            if invincible and pygame.time.get_ticks() - invincible_timer > 5000:
                invincible = False

            pygame.display.update()
            clock.tick(self.snake_speed)

        pygame.quit()
        quit()

if __name__ == "__main__":
    Game().run()
# --- END OF FILE ---