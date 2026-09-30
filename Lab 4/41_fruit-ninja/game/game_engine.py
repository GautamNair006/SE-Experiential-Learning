import pygame
import random
import numpy as np
from .fruit import Fruit

WHITE = (255, 255, 255)
RED = (230, 60, 60)
GRAY = (180, 180, 180)
YELLOW = (240, 210, 60)
GREEN = (90, 200, 90)
ORANGE = (230, 140, 40)
BOMB_BLACK = (30, 30, 30)
FRUIT_COLORS = [(220, 60, 60), (230, 140, 40), (230, 200, 40), (90, 180, 90)]

DIFFICULTIES = {
    "EASY": {"bomb_chance": 0.05, "color": GREEN},
    "MEDIUM": {"bomb_chance": 0.15, "color": ORANGE},
    "HARD": {"bomb_chance": 0.30, "color": RED},
}

class SoundManager:
    """Generates procedural sound effects using numpy audio arrays."""
    def __init__(self):
        self.sample_rate = 44100
        self.enabled = pygame.mixer.get_init() is not None

        if self.enabled:
            self.slice_sound = self._create_slice_sound()
            self.bomb_sound = self._create_bomb_sound()
            self.game_over_sound = self._create_game_over_sound()

    def _samples_to_sound(self, samples):
        # Scale to 16-bit integer PCM array
        scaled = np.int16(samples * 32767)
        # Convert 1D mono array to 2D stereo array for Pygame mixer
        stereo = np.column_stack((scaled, scaled))
        return pygame.sndarray.make_sound(stereo)

    def _create_slice_sound(self):
        duration = 0.12  # seconds
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Frequency sweep from 800 Hz down to 200 Hz
        freq = np.linspace(800, 200, len(t))
        envelope = np.exp(-t * 30)
        samples = np.sin(2 * np.pi * freq * t) * envelope
        return self._samples_to_sound(samples)

    def _create_bomb_sound(self):
        duration = 0.45
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Low noise explosion effect
        noise = np.random.uniform(-1.0, 1.0, len(t))
        envelope = np.exp(-t * 8)
        samples = noise * envelope
        return self._samples_to_sound(samples)

    def _create_game_over_sound(self):
        duration = 0.6
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Descending dual-tone jingle
        freq1 = np.where(t < 0.3, 300, 200)
        freq2 = np.where(t < 0.3, 240, 160)
        envelope = np.exp(-t * 3)
        samples = (0.5 * np.sin(2 * np.pi * freq1 * t) + 0.5 * np.sin(2 * np.pi * freq2 * t)) * envelope
        return self._samples_to_sound(samples)

    def play_slice(self):
        if self.enabled:
            self.slice_sound.play()

    def play_bomb(self):
        if self.enabled:
            self.bomb_sound.play()

    def play_game_over(self):
        if self.enabled:
            self.game_over_sound.play()


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.fruits = []
        self.trail = []

        self.spawn_interval = 55
        self._spawn_timer = 0
        self.difficulty = "MEDIUM"
        self.bomb_chance = DIFFICULTIES[self.difficulty]["bomb_chance"]
        self.speed_scale = 1.0

        self.lives = 3
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 28)
        self.title_font = pygame.font.SysFont("Arial", 50, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 20, bold=True)

        self.game_over = False
        self.should_quit = False
        self.button_rects = {}

        self.sounds = SoundManager()

    def set_difficulty(self, mode):
        if mode in DIFFICULTIES:
            self.difficulty = mode
            self.bomb_chance = DIFFICULTIES[mode]["bomb_chance"]

    def restart(self, difficulty=None):
        if difficulty:
            self.set_difficulty(difficulty)
        self.fruits.clear()
        self.trail.clear()
        self.lives = 3
        self.score = 0
        self._spawn_timer = 0
        self.game_over = False

    def spawn_fruit(self):
        x = random.randint(60, self.width - 60)
        vy = -random.uniform(13, 16) * self.speed_scale
        vx = random.uniform(-2, 2)
        gravity = 0.35
        kind = "bomb" if random.random() < self.bomb_chance else "fruit"

        fruit = Fruit(x, self.height + 30, vx, vy, gravity, kind=kind)
        fruit.color = BOMB_BLACK if kind == "bomb" else random.choice(FRUIT_COLORS)
        self.fruits.append(fruit)

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                for key, rect in self.button_rects.items():
                    if rect.collidepoint(pos):
                        if key in DIFFICULTIES:
                            self.restart(difficulty=key)
                        elif key == "EXIT":
                            self.should_quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.restart("EASY")
                elif event.key == pygame.K_2:
                    self.restart("MEDIUM")
                elif event.key == pygame.K_3:
                    self.restart("HARD")
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.should_quit = True
            return

        if event.type == pygame.MOUSEMOTION:
            self._handle_motion(event.pos)

    def _handle_motion(self, pos):
        if self.trail:
            last_pos = self.trail[-1]
            for fruit in self.fruits:
                if not fruit.sliced and fruit.intersects_segment(last_pos, pos):
                    self._slice(fruit)
        else:
            for fruit in self.fruits:
                if not fruit.sliced and fruit.contains_point(pos[0], pos[1]):
                    self._slice(fruit)

        self.trail.append(pos)
        if len(self.trail) > 15:
            self.trail.pop(0)

    def _slice(self, fruit):
        fruit.sliced = True
        if fruit.kind == "bomb":
            self.sounds.play_bomb()
            self._trigger_game_over()
        else:
            self.sounds.play_slice()
            self.score += 1

    def _trigger_game_over(self):
        if not self.game_over:
            self.game_over = True
            self.sounds.play_game_over()

    def handle_input(self):
        pass

    def update(self):
        if self.game_over:
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.spawn_fruit()

        still_alive = []
        for fruit in self.fruits:
            fruit.update()
            if fruit.sliced:
                continue
            if fruit.off_screen(self.height):
                if fruit.kind == "fruit":
                    self.lives -= 1
                continue
            still_alive.append(fruit)
        self.fruits = still_alive

        if self.lives <= 0:
            self._trigger_game_over()

    def render(self, screen):
        for fruit in self.fruits:
            color = getattr(fruit, "color", WHITE)
            pygame.draw.circle(screen, color, (int(fruit.x), int(fruit.y)), fruit.radius)

        if len(self.trail) >= 2:
            pygame.draw.lines(screen, WHITE, False, self.trail, 3)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(lives_text, (self.width - 130, 10))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            go_surf = self.title_font.render("GAME OVER", True, RED)
            go_rect = go_surf.get_rect(center=(self.width // 2, 110))
            screen.blit(go_surf, go_rect)

            score_surf = self.font.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = score_surf.get_rect(center=(self.width // 2, 175))
            screen.blit(score_surf, score_rect)

            prompt_surf = self.font.render("Play Again - Select Difficulty:", True, YELLOW)
            prompt_rect = prompt_surf.get_rect(center=(self.width // 2, 235))
            screen.blit(prompt_surf, prompt_rect)

            self.button_rects = {}
            btn_width, btn_height = 260, 48
            btn_x = self.width // 2 - btn_width // 2

            options = [
                ("EASY", "1. Easy (5% Bombs)", 285),
                ("MEDIUM", "2. Medium (15% Bombs)", 345),
                ("HARD", "3. Hard (30% Bombs)", 405),
            ]

            mouse_pos = pygame.mouse.get_pos()

            for key, label, y_pos in options:
                rect = pygame.Rect(btn_x, y_pos, btn_width, btn_height)
                self.button_rects[key] = rect

                is_selected = (self.difficulty == key)
                is_hovered = rect.collidepoint(mouse_pos)
                bg_color = (60, 70, 90) if not (is_selected or is_hovered) else (90, 110, 140)
                border_color = DIFFICULTIES[key]["color"] if is_selected else WHITE

                pygame.draw.rect(screen, bg_color, rect, border_radius=8)
                pygame.draw.rect(screen, border_color, rect, width=2 if not is_selected else 4, border_radius=8)

                txt_surf = self.button_font.render(label, True, WHITE)
                txt_rect = txt_surf.get_rect(center=rect.center)
                screen.blit(txt_surf, txt_rect)

            exit_rect = pygame.Rect(btn_x, 475, btn_width, btn_height)
            self.button_rects["EXIT"] = exit_rect
            exit_hover = exit_rect.collidepoint(mouse_pos)
            exit_bg = (120, 40, 40) if exit_hover else (70, 30, 30)

            pygame.draw.rect(screen, exit_bg, exit_rect, border_radius=8)
            pygame.draw.rect(screen, RED, exit_rect, width=2, border_radius=8)

            exit_surf = self.button_font.render("Exit Game (Esc)", True, WHITE)
            exit_rect_txt = exit_surf.get_rect(center=exit_rect.center)
            screen.blit(exit_surf, exit_rect_txt)