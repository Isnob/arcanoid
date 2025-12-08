import pygame
from config import SETTINGS as C


class Brick(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, strength: int):
        super().__init__()
        brick_width = (C.WINDOW_WIDTH - C.BRICK_PADDING * (C.BRICK_COLS + 1)) // C.BRICK_COLS
        self.image = pygame.Surface([brick_width, C.BRICK_HEIGHT])

        self.strength = strength
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.update_color()

    def update_color(self):
        level = max(1, min(3, self.strength))
        color = C.BRICK_COLORS[level]
        self.image.fill(color)

    def hit(self) -> bool:
        self.strength -= 1
        if self.strength <= 0:
            self.kill()
            return True
        self.update_color()
        return False
