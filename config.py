from dataclasses import dataclass
import json


@dataclass
class Settings:
    WINDOW_WIDTH: int
    WINDOW_HEIGHT: int
    FPS: int
    BACKGROUND_COLOR: tuple
    TEXT_COLOR: tuple

    PADDLE_WIDTH: int
    PADDLE_HEIGHT: int
    PADDLE_SPEED: int
    PADDLE_COLOR: tuple

    BALL_RADIUS: int
    BALL_SPEED: int
    BALL_COLOR: tuple

    BRICK_ROWS: int
    BRICK_COLS: int
    BRICK_HEIGHT: int
    BRICK_PADDING: int
    BRICK_TOP_OFFSET: int
    BRICK_STRENGTH_MIN: int
    BRICK_STRENGTH_MAX: int
    BRICK_COLORS: dict

    INITIAL_LIVES: int


def load_settings(file_name="config.json") -> Settings:
    with open(file_name, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    brick_colors = {int(k): tuple(v) for k, v in cfg["BRICK_COLORS"].items()}

    return Settings(
        WINDOW_WIDTH=cfg["WINDOW_WIDTH"],
        WINDOW_HEIGHT=cfg["WINDOW_HEIGHT"],
        FPS=cfg["FPS"],
        BACKGROUND_COLOR=tuple(cfg["BACKGROUND_COLOR"]),
        TEXT_COLOR=tuple(cfg["TEXT_COLOR"]),

        PADDLE_WIDTH=cfg["PADDLE_WIDTH"],
        PADDLE_HEIGHT=cfg["PADDLE_HEIGHT"],
        PADDLE_SPEED=cfg["PADDLE_SPEED"],
        PADDLE_COLOR=tuple(cfg["PADDLE_COLOR"]),

        BALL_RADIUS=cfg["BALL_RADIUS"],
        BALL_SPEED=cfg["BALL_SPEED"],
        BALL_COLOR=tuple(cfg["BALL_COLOR"]),

        BRICK_ROWS=cfg["BRICK_ROWS"],
        BRICK_COLS=cfg["BRICK_COLS"],
        BRICK_HEIGHT=cfg["BRICK_HEIGHT"],
        BRICK_PADDING=cfg["BRICK_PADDING"],
        BRICK_TOP_OFFSET=cfg["BRICK_TOP_OFFSET"],
        BRICK_STRENGTH_MIN=cfg["BRICK_STRENGTH_MIN"],
        BRICK_STRENGTH_MAX=cfg["BRICK_STRENGTH_MAX"],
        BRICK_COLORS=brick_colors,

        INITIAL_LIVES=cfg["INITIAL_LIVES"],
    )


SETTINGS = load_settings()
