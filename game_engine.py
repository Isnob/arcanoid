from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum, auto
import math
from pathlib import Path
from typing import Dict, List, Tuple

import pygame


Color = Tuple[int, int, int]


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()


@dataclass
class DifficultyConfig:
    name: str
    ball_speed_multiplier: float
    paddle_speed_multiplier: float
    brick_strength: int


@dataclass
class GameConfig:
    title: str
    version: str
    max_players: int
    initial_lives: int
    difficulty_levels: List[str]
    window_width: int
    window_height: int
    fps: int
    background_color: Color
    text_color: Color
    paddle_width: int
    paddle_height: int
    paddle_speed: float
    paddle_color: Color
    ball_radius: int
    ball_speed: float
    ball_color: Color
    brick_rows: int
    brick_cols: int
    brick_height: int
    brick_padding: int
    brick_top_offset: int
    brick_colors: List[Color]
    difficulty_map: Dict[str, DifficultyConfig]

    @classmethod
    def load(cls, path: Path, difficulty: str) -> "GameConfig":
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)

        difficulty_key = difficulty.lower()
        game_data = data["game"]
        window = data["window"]
        paddle = data["paddle"]
        ball = data["ball"]
        bricks = data["bricks"]
        difficulty_data_raw = data["difficulty"]
        difficulty_data = {key.lower(): value for key, value in difficulty_data_raw.items()}

        if difficulty_key not in difficulty_data:
            available = ", ".join(difficulty_data.keys())
            raise ValueError(f"Unknown difficulty '{difficulty}'. Available: {available}")

        diff_map = {
            name: DifficultyConfig(
                name=name,
                ball_speed_multiplier=info.get("ball_speed", 1.0),
                paddle_speed_multiplier=info.get("paddle_speed", 1.0),
                brick_strength=info.get("brick_strength", 1),
            )
            for name, info in difficulty_data.items()
        }

        return cls(
            title=game_data["title"],
            version=game_data["version"],
            max_players=game_data["max_players"],
            initial_lives=game_data["initial_lives"],
            difficulty_levels=[value.lower() for value in game_data["difficulty_levels"]],
            window_width=window["width"],
            window_height=window["height"],
            fps=window["fps"],
            background_color=tuple(window["background_color"]),
            text_color=tuple(window["text_color"]),
            paddle_width=paddle["width"],
            paddle_height=paddle["height"],
            paddle_speed=paddle["speed"],
            paddle_color=tuple(paddle["color"]),
            ball_radius=ball["radius"],
            ball_speed=ball["speed"],
            ball_color=tuple(ball["color"]),
            brick_rows=bricks["rows"],
            brick_cols=bricks["cols"],
            brick_height=bricks["height"],
            brick_padding=bricks["padding"],
            brick_top_offset=bricks["top_offset"],
            brick_colors=[tuple(color) for color in bricks["colors"]],
            difficulty_map=diff_map,
        )


class GameObject:
    def __init__(self, rect: pygame.Rect, color: Color):
        self.rect = rect
        self.color = color

    def update(self, dt: float) -> None:
        raise NotImplementedError

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)


class MovingObject(GameObject):
    def __init__(self, rect: pygame.Rect, color: Color, speed: float):
        super().__init__(rect, color)
        self.speed = speed
        self.velocity = pygame.Vector2()
        self.position = pygame.Vector2(rect.topleft)

    def move(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.rect.topleft = (int(self.position.x), int(self.position.y))

    def sync_position(self) -> None:
        self.position.update(self.rect.topleft)


class Paddle(MovingObject):
    def __init__(self, config: GameConfig, speed_multiplier: float = 1.0):
        rect = pygame.Rect(
            (config.window_width - config.paddle_width) // 2,
            config.window_height - config.paddle_height - 30,
            config.paddle_width,
            config.paddle_height,
        )
        super().__init__(rect, config.paddle_color, speed=config.paddle_speed * speed_multiplier)
        self.bounds = pygame.Rect(0, rect.y, config.window_width, rect.height)

    def update(self, dt: float, direction: int = 0) -> None:  # type: ignore[override]
        self.velocity.x = self.speed * direction
        self.move(dt)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.bounds.width:
            self.rect.right = self.bounds.width
        self.sync_position()


class Ball(MovingObject):
    def __init__(self, config: GameConfig, difficulty: DifficultyConfig):
        self.radius = config.ball_radius
        rect = pygame.Rect(
            config.window_width // 2 - self.radius,
            config.window_height // 2,
            self.radius * 2,
            self.radius * 2,
        )
        super().__init__(rect, config.ball_color, speed=config.ball_speed * difficulty.ball_speed_multiplier)
        self._launched = False

    def reset(self, paddle_rect: pygame.Rect) -> None:
        self.stick_to_paddle(paddle_rect)
        self._launched = False
        self.velocity.update(0, 0)

    def stick_to_paddle(self, paddle_rect: pygame.Rect) -> None:
        self.rect.centerx = paddle_rect.centerx
        self.rect.bottom = paddle_rect.top - 4
        self.sync_position()

    def launch(self) -> None:
        if self._launched:
            return
        self._launched = True
        self.velocity = pygame.Vector2(0.6, -1).normalize() * self.speed

    def update(self, dt: float) -> None:  # type: ignore[override]
        if not self._launched:
            return
        self.move(dt)

    def bounce_horizontal(self) -> None:
        self.velocity.x *= -1
        self._clamp_speed()

    def bounce_vertical(self) -> None:
        self.velocity.y *= -1
        self._clamp_speed()

    def _clamp_speed(self) -> None:
        if self.velocity.length() == 0:
            self.velocity = pygame.Vector2(0.6, -1).normalize() * self.speed
        else:
            self.velocity = self.velocity.normalize() * self.speed

    def draw(self, surface: pygame.Surface) -> None:  # type: ignore[override]
        pygame.draw.circle(surface, self.color, self.rect.center, self.radius)


class Brick(GameObject):
    def __init__(self, rect: pygame.Rect, color: Color, strength: int = 1, points: int = 50):
        super().__init__(rect, color)
        self.strength = strength
        self.points = points

    def update(self, dt: float) -> None:  # type: ignore[override]
        return

    def hit(self) -> bool:
        self.strength -= 1
        return self.strength <= 0

    def draw(self, surface: pygame.Surface, font: pygame.font.Font | None = None, text_color: Color | None = None) -> None:  # type: ignore[override]
        super().draw(surface)
        if font and text_color:
            text = font.render(str(self.strength), True, text_color)
            rect = text.get_rect(center=self.rect.center)
            surface.blit(text, rect)


class Level:
    def __init__(self, config: GameConfig, difficulty: DifficultyConfig, layout: List[dict] | None = None):
        self.config = config
        self.difficulty = difficulty
        self.bricks: List[Brick] = []
        self.brick_font = pygame.font.Font(None, 18)
        self.brick_text_color: Color = config.text_color
        if layout:
            self._build_from_layout(layout)
        else:
            self._build_bricks()

    def _build_bricks(self) -> None:
        available_width = self.config.window_width - self.config.brick_padding * 2
        brick_width = (available_width - (self.config.brick_cols - 1) * self.config.brick_padding) // self.config.brick_cols

        for row in range(self.config.brick_rows):
            for col in range(self.config.brick_cols):
                x = self.config.brick_padding + col * (brick_width + self.config.brick_padding)
                y = self.config.brick_top_offset + row * (self.config.brick_height + self.config.brick_padding)
                color = self.config.brick_colors[row % len(self.config.brick_colors)]
                vertical_bonus = self.config.brick_rows - row - 1
                strength = max(1, self.difficulty.brick_strength + vertical_bonus)
                brick = Brick(
                    pygame.Rect(x, y, brick_width, self.config.brick_height),
                    color,
                    strength=strength,
                    points=50 * strength,
                )
                self.bricks.append(brick)

    def _build_from_layout(self, layout: List[dict]) -> None:
        for item in layout:
            rect = pygame.Rect(
                int(item["x"]),
                int(item["y"]),
                int(item["width"]),
                int(item["height"]),
            )
            color = tuple(item.get("color", self.config.brick_colors[0]))
            strength = max(1, int(item.get("strength", 1)))
            brick = Brick(rect, color, strength=strength, points=50 * strength)
            self.bricks.append(brick)

    def draw(self, surface: pygame.Surface) -> None:
        for brick in self.bricks:
            brick.draw(surface, self.brick_font, self.brick_text_color)


class HUD:
    def __init__(self, config: GameConfig, difficulty: DifficultyConfig):
        pygame.font.init()
        self.font = pygame.font.Font(None, 28)
        self.big_font = pygame.font.Font(None, 48)
        self.config = config
        self.difficulty = difficulty

    def draw_header(self, surface: pygame.Surface, score: int, lives: int) -> None:
        text = f"Score: {score}    Lives: {lives}    Difficulty: {self.difficulty.name}"
        rendered = self.font.render(text, True, self.config.text_color)
        surface.blit(rendered, (12, 12))

    def draw_center(self, surface: pygame.Surface, message: str, subline: str | None = None) -> None:
        center_x = self.config.window_width // 2
        center_y = self.config.window_height // 2
        text = self.big_font.render(message, True, self.config.text_color)
        rect = text.get_rect(center=(center_x, center_y))
        surface.blit(text, rect)

        if subline:
            sub = self.font.render(subline, True, self.config.text_color)
            sub_rect = sub.get_rect(center=(center_x, center_y + 48))
            surface.blit(sub, sub_rect)


class GameEngine:
    def __init__(self, config: GameConfig, difficulty: str, level_layout: List[dict] | None = None):
        self.config = config
        difficulty_key = difficulty.lower()
        self.difficulty = config.difficulty_map[difficulty_key]
        self.custom_layout = level_layout
        self.state = GameState.MENU
        self.screen = pygame.display.set_mode((config.window_width, config.window_height))
        pygame.display.set_caption(f"{config.title} {config.version}")
        self.clock = pygame.time.Clock()

        self.paddle = Paddle(config, speed_multiplier=self.difficulty.paddle_speed_multiplier)
        self.ball = Ball(config, self.difficulty)
        self.level = Level(config, self.difficulty, layout=level_layout)
        self.hud = HUD(config, self.difficulty)

        self.score = 0
        self.lives = config.initial_lives
        self.running = True
        self.victory = False

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(self.config.fps)
            self._handle_events()
            if self.state == GameState.MENU:
                self._update_menu()
            elif self.state == GameState.PLAYING:
                self._update_gameplay(dt)
            elif self.state == GameState.GAME_OVER:
                self._update_game_over()
            self._draw()
            pygame.display.flip()
        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.state == GameState.MENU and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.state = GameState.PLAYING
                if self.state == GameState.PLAYING and event.key == pygame.K_SPACE:
                    self.ball.launch()
                if self.state == GameState.GAME_OVER and event.key == pygame.K_r:
                    self._reset_game()

    def _update_menu(self) -> None:
        self.ball.reset(self.paddle.rect)

    def _update_gameplay(self, dt_ms: float) -> None:
        dt = dt_ms / 1000.0
        keys = pygame.key.get_pressed()
        direction = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction += 1

        self.paddle.update(dt, direction)
        if not self.ball._launched:
            self.ball.stick_to_paddle(self.paddle.rect)
        self.ball.update(dt)

        if self.ball.rect.left <= 0 or self.ball.rect.right >= self.config.window_width:
            if self.ball.rect.left <= 0:
                self.ball.rect.left = 0
            else:
                self.ball.rect.right = self.config.window_width
            self.ball.sync_position()
            self.ball.bounce_horizontal()
        if self.ball.rect.top <= 0:
            self.ball.rect.top = 0
            self.ball.sync_position()
            self.ball.bounce_vertical()
        if self.ball.rect.bottom >= self.config.window_height:
            self._lose_life()
            return

        if self.ball.rect.colliderect(self.paddle.rect) and self.ball.velocity.y > 0:
            self._bounce_from_paddle()

        self._handle_brick_collisions()

        if not self.level.bricks:
            self.victory = True
            self.state = GameState.GAME_OVER

    def _update_game_over(self) -> None:
        self.ball.reset(self.paddle.rect)

    def _lose_life(self) -> None:
        self.lives -= 1
        if self.lives <= 0:
            self.state = GameState.GAME_OVER
            return
        self.ball.reset(self.paddle.rect)

    def _bounce_from_paddle(self) -> None:
        offset = (self.ball.rect.centerx - self.paddle.rect.centerx) / (self.paddle.rect.width / 2)
        offset = max(-1.0, min(1.0, offset))
        angle = offset * 45
        speed = self.ball.speed
        rad = math.radians(angle)
        self.ball.velocity = pygame.Vector2(speed * math.sin(rad), -abs(speed * math.cos(rad)))
        self.ball._clamp_speed()
        self.ball.rect.bottom = self.paddle.rect.top - 1
        self.ball.sync_position()

    def _handle_brick_collisions(self) -> None:
        for brick in list(self.level.bricks):
            if self.ball.rect.colliderect(brick.rect):
                overlap_left = self.ball.rect.right - brick.rect.left
                overlap_right = brick.rect.right - self.ball.rect.left
                overlap_top = self.ball.rect.bottom - brick.rect.top
                overlap_bottom = brick.rect.bottom - self.ball.rect.top

                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                if min_overlap in (overlap_left, overlap_right):
                    if min_overlap == overlap_left:
                        self.ball.rect.right = brick.rect.left - 1
                    else:
                        self.ball.rect.left = brick.rect.right + 1
                    self.ball.bounce_horizontal()
                else:
                    if min_overlap == overlap_top:
                        self.ball.rect.bottom = brick.rect.top - 1
                    else:
                        self.ball.rect.top = brick.rect.bottom + 1
                    self.ball.bounce_vertical()
                self.ball.sync_position()

                if brick.hit():
                    self.level.bricks.remove(brick)
                    self.score += brick.points
                break

    def _draw(self) -> None:
        self.screen.fill(self.config.background_color)
        if self.state == GameState.MENU:
            self.hud.draw_center(
                self.screen,
                self.config.title,
                "Press SPACE to serve the ball",
            )
        if self.state == GameState.GAME_OVER:
            title = "You win!" if self.victory else "Game over"
            self.hud.draw_center(self.screen, title, "Press R to restart or ESC to exit")

        self.level.draw(self.screen)
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        self.hud.draw_header(self.screen, self.score, self.lives)

    def _reset_game(self) -> None:
        self.paddle = Paddle(self.config, speed_multiplier=self.difficulty.paddle_speed_multiplier)
        self.ball = Ball(self.config, self.difficulty)
        self.level = Level(self.config, self.difficulty, layout=self.custom_layout)
        self.score = 0
        self.lives = self.config.initial_lives
        self.victory = False
        self.state = GameState.MENU
        self.ball.reset(self.paddle.rect)
