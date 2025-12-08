import pygame
from config import SETTINGS as C


class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([C.PADDLE_WIDTH, C.PADDLE_HEIGHT])
        self.image.fill(C.PADDLE_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = (C.WINDOW_WIDTH - C.PADDLE_WIDTH) // 2
        self.rect.y = C.WINDOW_HEIGHT - C.PADDLE_HEIGHT - 30
        self.speed = C.PADDLE_SPEED

    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed * dt

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > C.WINDOW_WIDTH:
            self.rect.right = C.WINDOW_WIDTH
