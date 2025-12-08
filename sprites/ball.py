import pygame
import math
import random
from config import SETTINGS as C


class Ball(pygame.sprite.Sprite):
    def __init__(self, paddle):
        super().__init__()
        self.radius = C.BALL_RADIUS
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, C.BALL_COLOR, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        self.speed = C.BALL_SPEED
        self.paddle = paddle
        self.reset()

    def reset(self):
        self.rect.centerx = self.paddle.rect.centerx
        self.rect.bottom = self.paddle.rect.top - 4
        self.velocity = [0.0, 0.0]
        self._launched = False

    def launch(self):
        if self._launched:
            return
        self._launched = True
        angle_deg = random.randint(30, 150)
        angle = math.radians(angle_deg)
        self.velocity = [
            self.speed * math.cos(angle),
            -self.speed * math.sin(angle),
        ]

    def update(self, dt: float):
        if not self._launched:
            self.rect.centerx = self.paddle.rect.centerx
            self.rect.bottom = self.paddle.rect.top - 4
            return

        self.rect.x += self.velocity[0] * dt
        self.rect.y += self.velocity[1] * dt

        if self.rect.left <= 0:
            self.rect.left = 0
            self.velocity[0] *= -1
        elif self.rect.right >= C.WINDOW_WIDTH:
            self.rect.right = C.WINDOW_WIDTH
            self.velocity[0] *= -1

        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity[1] *= -1

    def bounce_off_paddle(self, paddle):
        relative_intersect_x = self.rect.centerx - paddle.rect.centerx
        normalized_offset = relative_intersect_x / (paddle.rect.width / 2)
        normalized_offset = max(-1, min(1, normalized_offset))

        max_bounce_angle = math.radians(70)
        angle = normalized_offset * max_bounce_angle

        speed = math.hypot(*self.velocity) or self.speed
        self.velocity[0] = speed * math.sin(angle)
        self.velocity[1] = -speed * math.cos(angle)
        self.rect.bottom = paddle.rect.top - 1
