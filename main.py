import argparse
import json
import random
import sys
from pathlib import Path

import pygame

from game_engine import GameConfig, GameEngine


def load_level_layout(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    if "bricks" not in data or not isinstance(data["bricks"], list):
        raise ValueError("Level file must contain a 'bricks' list.")
    bricks: list[dict] = []
    for item in data["bricks"]:
        try:
            x = int(item["x"])
            y = int(item["y"])
            width = int(item["width"])
            height = int(item["height"])
            strength = int(item["strength"])
            color = tuple(item.get("color", (255, 255, 255)))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid brick entry: {item}") from exc
        bricks.append(
            {
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "strength": strength,
                "color": color,
            }
        )
    return bricks


def generate_level_layout(config: GameConfig, density: float, difficulty: str) -> list[dict]:
    density = max(0.0, min(1.0, density))
    diff = config.difficulty_map[difficulty.lower()]
    available_width = config.window_width - config.brick_padding * 2
    brick_width = (available_width - (config.brick_cols - 1) * config.brick_padding) // config.brick_cols
    bricks: list[dict] = []

    for row in range(config.brick_rows):
        for col in range(config.brick_cols):
            if random.random() > density:
                continue
            x = config.brick_padding + col * (brick_width + config.brick_padding)
            y = config.brick_top_offset + row * (config.brick_height + config.brick_padding)
            color = config.brick_colors[row % len(config.brick_colors)]
            vertical_bonus = config.brick_rows - row - 1
            strength = max(1, diff.brick_strength + vertical_bonus)
            bricks.append(
                {
                    "x": x,
                    "y": y,
                    "width": brick_width,
                    "height": config.brick_height,
                    "strength": strength,
                    "color": color,
                }
            )
    return bricks


def save_level_layout(path: Path, bricks: list[dict]) -> None:
    payload = {"bricks": bricks}
    with path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Arcanoid launcher")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).with_name("game_config.json"),
        help="Path to game_config.json",
    )
    parser.add_argument(
        "--difficulty",
        default="medium",
        help="Difficulty level to use (defined in the config file).",
    )
    parser.add_argument(
        "--level-file",
        type=Path,
        help="Path to pre-generated level layout JSON (positions and strength of bricks).",
    )
    parser.add_argument(
        "--generate-level",
        type=Path,
        metavar="OUTPUT",
        help="Generate a random level JSON using current config/difficulty and exit.",
    )
    parser.add_argument(
        "--density",
        type=float,
        default=0.85,
        help="Fill ratio for generated levels (0-1). Used with --generate-level.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Seed for random level generation (optional).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    try:
        config = GameConfig.load(config_path, args.difficulty)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    if args.seed is not None:
        random.seed(args.seed)

    if args.generate_level:
        layout = generate_level_layout(config, args.density, args.difficulty)
        save_level_layout(args.generate_level, layout)
        print(f"Level generated to: {args.generate_level}")
        return 0

    level_layout = None
    if args.level_file:
        try:
            level_layout = load_level_layout(args.level_file)
        except FileNotFoundError:
            print(f"Level file not found: {args.level_file}", file=sys.stderr)
            return 1
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"Failed to load level: {exc}", file=sys.stderr)
            return 1

    pygame.init()
    engine = GameEngine(config, args.difficulty, level_layout=level_layout)
    engine.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
