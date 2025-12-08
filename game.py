import pygame
from config import SETTINGS as C
from sprites import Paddle, Ball, Brick
import random


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.sound_block_break = pygame.mixer.Sound("sounds/гриша.ogg")
        self.sound_block_hit = pygame.mixer.Sound("sounds/block_hit.wav")
        self.sound_victory = pygame.mixer.Sound("sounds/victory.wav")
        self.sound_game_over = pygame.mixer.Sound("sounds/game_over.wav")

        self.screen = pygame.display.set_mode((C.WINDOW_WIDTH, C.WINDOW_HEIGHT))
        pygame.display.set_caption("Arcanoid")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.lives = C.INITIAL_LIVES
        self.score = 0
        self.game_over = False

        self.all_sprites = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()

        self.paddle = Paddle()
        self.ball = Ball(self.paddle)

        self.all_sprites.add(self.paddle, self.ball)
        self.create_level()

    def create_level(self):
        brick_width = (C.WINDOW_WIDTH - C.BRICK_PADDING * (C.BRICK_COLS + 1)) // C.BRICK_COLS
        for row in range(C.BRICK_ROWS):
            for col in range(C.BRICK_COLS):
                x = C.BRICK_PADDING + col * (brick_width + C.BRICK_PADDING)
                y = C.BRICK_TOP_OFFSET + row * (C.BRICK_HEIGHT + C.BRICK_PADDING)
                strength = random.randint(C.BRICK_STRENGTH_MIN, C.BRICK_STRENGTH_MAX)
                brick = Brick(x, y, strength)
                self.all_sprites.add(brick)
                self.bricks.add(brick)

    def run(self):
        while self.running:
            dt = self.clock.tick(C.FPS) / 1000.0
            self.handle_events()
            if not self.game_over:
                self.update(dt)
            self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.ball.launch()
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()

    def update(self, dt: float):
        self.all_sprites.update(dt)

        if pygame.sprite.collide_rect(self.ball, self.paddle) and self.ball.velocity[1] > 0:
            self.ball.bounce_off_paddle(self.paddle)

        hit_bricks = pygame.sprite.spritecollide(self.ball, self.bricks, False)
        for brick in hit_bricks:
            self.ball.velocity[1] *= -1
            destroyed = brick.hit()
            if destroyed:
                self.sound_block_break.play()
                self.score += 10
            else:
                self.sound_block_hit.play()
            break

        if not self.bricks:
            if not self.game_over:
                self.sound_victory.play()
            self.game_over = True

        if self.ball.rect.top > C.WINDOW_HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                if not self.game_over:
                    self.sound_game_over.play()
                self.game_over = True
            else:
                self.ball.reset()

    def draw(self):
        self.screen.fill(C.BACKGROUND_COLOR)
        self.all_sprites.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, C.TEXT_COLOR)
        lives_text = self.font.render(f"Lives: {self.lives}", True, C.TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (C.WINDOW_WIDTH - lives_text.get_width() - 10, 10))

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_game_over(self):
        text = "GAME OVER" if self.lives <= 0 else "YOU WIN!"
        go_text = self.font.render(text, True, C.TEXT_COLOR)
        go_rect = go_text.get_rect(center=(C.WINDOW_WIDTH / 2, C.WINDOW_HEIGHT / 2 - 20))

        restart_text = self.font.render("Press 'R' to Restart", True, C.TEXT_COLOR)
        restart_rect = restart_text.get_rect(center=(C.WINDOW_WIDTH / 2, C.WINDOW_HEIGHT / 2 + 20))

        self.screen.blit(go_text, go_rect)
        self.screen.blit(restart_text, restart_rect)
