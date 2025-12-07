import pygame
import random
import math

# --- Константы и конфигурация ---
# Вместо game_config.json
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
FPS = 60
BACKGROUND_COLOR = (20, 24, 36)
TEXT_COLOR = (235, 235, 235)

PADDLE_WIDTH = 120
PADDLE_HEIGHT = 16
PADDLE_SPEED = 420
PADDLE_COLOR = (80, 200, 220)

BALL_RADIUS = 10
BALL_SPEED = 520
BALL_COLOR = (255, 255, 255)

BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_HEIGHT = 22
BRICK_PADDING = 8
BRICK_TOP_OFFSET = 80
BRICK_COLORS = [(243, 86, 112), (255, 191, 71), (117, 214, 164)]
BRICK_STRENGTH = 1

INITIAL_LIVES = 3


class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PADDLE_WIDTH, PADDLE_HEIGHT])
        self.image.fill(PADDLE_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = (WINDOW_WIDTH - PADDLE_WIDTH) // 2
        self.rect.y = WINDOW_HEIGHT - PADDLE_HEIGHT - 30
        self.speed = PADDLE_SPEED

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed * dt

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH


class Ball(pygame.sprite.Sprite):
    def __init__(self, paddle):
        super().__init__()
        self.radius = BALL_RADIUS
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, BALL_COLOR, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        self.speed = BALL_SPEED
        self.paddle = paddle
        self.reset()

    def reset(self):
        self.rect.centerx = self.paddle.rect.centerx
        self.rect.bottom = self.paddle.rect.top - 4
        self.velocity = [0, 0]
        self._launched = False

    def launch(self):
        if self._launched:
            return
        self._launched = True
        angle = math.radians(random.randint(-60, 60) - 90)
        self.velocity = [self.speed * math.cos(angle), self.speed * math.sin(angle)]

    def update(self, dt):
        if not self._launched:
            self.rect.centerx = self.paddle.rect.centerx
            self.rect.bottom = self.paddle.rect.top - 4
            return

        self.rect.x += self.velocity[0] * dt
        self.rect.y += self.velocity[1] * dt

        if self.rect.left <= 0 or self.rect.right >= WINDOW_WIDTH:
            self.velocity[0] *= -1
        if self.rect.top <= 0:
            self.velocity[1] *= -1


class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, color, strength):
        super().__init__()
        brick_width = (WINDOW_WIDTH - BRICK_PADDING * (BRICK_COLS + 1)) // BRICK_COLS
        self.image = pygame.Surface([brick_width, BRICK_HEIGHT])
        self.color = color
        self.strength = strength
        self.update_color()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def update_color(self):
        # Делаем кирпич темнее с каждым ударом
        factor = 0.5 + 0.5 * (self.strength / BRICK_STRENGTH)
        color = [int(c * factor) for c in self.color]
        self.image.fill(color)

    def hit(self):
        self.strength -= 1
        if self.strength <= 0:
            self.kill()
            return True
        self.update_color()
        return False

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Arcanoid")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.lives = INITIAL_LIVES
        self.score = 0
        self.game_over = False

        self.all_sprites = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.paddle = Paddle()
        self.ball = Ball(self.paddle)
        self.all_sprites.add(self.paddle, self.ball)
        self.create_level()

    def create_level(self):
        brick_width = (WINDOW_WIDTH - BRICK_PADDING * (BRICK_COLS + 1)) // BRICK_COLS
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = BRICK_PADDING + col * (brick_width + BRICK_PADDING)
                y = BRICK_TOP_OFFSET + row * (BRICK_HEIGHT + BRICK_PADDING)
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                brick = Brick(x, y, color, BRICK_STRENGTH)
                self.all_sprites.add(brick)
                self.bricks.add(brick)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
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
                    self.__init__() # Reset game

    def update(self, dt):
        self.all_sprites.update(dt)

        # Коллизия мяча с ракеткой
        if pygame.sprite.collide_rect(self.ball, self.paddle):
            self.ball.velocity[1] *= -1
            self.ball.rect.bottom = self.paddle.rect.top

        # Коллизия мяча с кирпичами
        hit_bricks = pygame.sprite.spritecollide(self.ball, self.bricks, False)
        for brick in hit_bricks:
            # Простая логика отскока
            self.ball.velocity[1] *= -1 
            if brick.hit():
                self.score += 10
            break 
        
        # Проверка на победу
        if not self.bricks:
            self.game_over = True

        # Мяч улетел вниз
        if self.ball.rect.top > WINDOW_HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.ball.reset()

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.all_sprites.draw(self.screen)
        
        # Отображение счета и жизней
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        lives_text = self.font.render(f"Lives: {self.lives}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (WINDOW_WIDTH - lives_text.get_width() - 10, 10))

        if self.game_over:
            self.draw_game_over()
            
        pygame.display.flip()
        
    def draw_game_over(self):
        text = "GAME OVER" if self.lives <= 0 else "YOU WIN!"
        go_text = self.font.render(text, True, TEXT_COLOR)
        go_rect = go_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 20))
        
        restart_text = self.font.render("Press 'R' to Restart", True, TEXT_COLOR)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 20))
        
        self.screen.blit(go_text, go_rect)
        self.screen.blit(restart_text, restart_rect)


if __name__ == "__main__":
    game = Game()
    game.run()