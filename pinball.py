import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pinball Game")

# Colors
BLACK = (0, 0, 0)
GREY = (50, 50, 50)
WHITE = (255, 255, 255)
RED = (220, 30, 30)
BLUE = (60, 80, 230)
YELLOW = (240, 240, 40)
GREEN = (40, 220, 70)

# Physics
FPS = 60
GRAVITY = 0.45
BOUNCE = 0.8

# Flipper settings
FLIPPER_LENGTH = 100
FLIPPER_WIDTH = 20
FLIPPER_ANGLE = 30  # Degrees max swing
FLIPPER_SPEED = 18  # Degrees per frame

# Ball settings
BALL_RADIUS = 15
BALL_INIT_POS = (WIDTH // 2, HEIGHT // 2)
BALL_INIT_VEL = (3, -10)

# Bumper settings
BUMPER_RADIUS = 30
BUMPER_POSITIONS = [(170, 250), (430, 250), (300, 400)]
BUMPER_SCORE = 100

FONT = pygame.font.SysFont(None, 36)

class Flipper:
    def __init__(self, x, y, is_left):
        self.x = x
        self.y = y
        self.is_left = is_left
        self.angle = 0
        self.active = False

    def update(self):
        target = -FLIPPER_ANGLE if self.active else 0
        if self.is_left:
            if self.angle > target:
                self.angle -= FLIPPER_SPEED
                if self.angle < target:
                    self.angle = target
            elif self.angle < target:
                self.angle += FLIPPER_SPEED
                if self.angle > target:
                    self.angle = target
        else:
            target = FLIPPER_ANGLE if self.active else 0
            if self.angle < target:
                self.angle += FLIPPER_SPEED
                if self.angle > target:
                    self.angle = target
            elif self.angle > target:
                self.angle -= FLIPPER_SPEED
                if self.angle < target:
                    self.angle = target

    def get_points(self):
        angle_rad = math.radians(self.angle)
        if self.is_left:
            base_angle = math.radians(210)
        else:
            base_angle = math.radians(-30)
        total_angle = base_angle + angle_rad
        dx = math.cos(total_angle) * FLIPPER_LENGTH
        dy = math.sin(total_angle) * FLIPPER_LENGTH
        p1 = (self.x, self.y)
        p2 = (self.x + dx, self.y + dy)
        return p1, p2

    def draw(self, surface):
        p1, p2 = self.get_points()
        pygame.draw.line(surface, YELLOW, p1, p2, FLIPPER_WIDTH)

class Ball:
    def __init__(self):
        self.x, self.y = BALL_INIT_POS
        self.vx, self.vy = BALL_INIT_VEL
        self.radius = BALL_RADIUS

    def update(self):
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        # Collide with table boundaries
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = -self.vx * BOUNCE
        if self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx = -self.vx * BOUNCE
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = -self.vy * BOUNCE
        # Bottom (ball falls out - reset)
        if self.y - self.radius > HEIGHT:
            self.__init__()

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)

    def collide_with_flipper(self, flipper: Flipper):
        p1, p2 = flipper.get_points()
        # Find closest point on flipper to ball
        px, py = closest_point_on_segment((self.x, self.y), p1, p2)
        dist = math.hypot(self.x - px, self.y - py)
        if dist < self.radius + FLIPPER_WIDTH // 2:
            # Reflect ball velocity
            dx = self.x - px
            dy = self.y - py
            length = math.hypot(dx, dy)
            if length == 0:
                length = 1
            nx, ny = dx / length, dy / length
            dot = self.vx * nx + self.vy * ny
            self.vx = self.vx - 2 * dot * nx
            self.vy = self.vy - 2 * dot * ny
            self.vx += nx * 8 * (1 if flipper.active else 0.4)
            self.vy += ny * 8 * (1 if flipper.active else 0.4)
            # Move ball out of collision
            self.x = px + nx * (self.radius + FLIPPER_WIDTH // 2 + 1)
            self.y = py + ny * (self.radius + FLIPPER_WIDTH // 2 + 1)

    def collide_with_bumper(self, bumper):
        dx = self.x - bumper.x
        dy = self.y - bumper.y
        dist = math.hypot(dx, dy)
        if dist < self.radius + bumper.radius:
            nx, ny = dx / dist, dy / dist
            self.vx = self.vx - 2 * (self.vx * nx + self.vy * ny) * nx
            self.vy = self.vy - 2 * (self.vx * nx + self.vy * ny) * ny
            self.vx += nx * 8
            self.vy += ny * 8
            self.x = bumper.x + nx * (self.radius + bumper.radius + 1)
            self.y = bumper.y + ny * (self.radius + bumper.radius + 1)
            return True
        return False

class Bumper:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BUMPER_RADIUS

    def draw(self, surface):
        pygame.draw.circle(surface, GREEN, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, BLACK, (self.x, self.y), self.radius, 3)

def closest_point_on_segment(p, a, b):
    # Returns closest point to p on segment ab
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return a
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    return (ax + t * dx, ay + t * dy)

def main():
    clock = pygame.time.Clock()
    ball = Ball()
    left_flipper = Flipper(180, 700, True)
    right_flipper = Flipper(420, 700, False)
    bumpers = [Bumper(x, y) for (x, y) in BUMPER_POSITIONS]
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Input
        keys = pygame.key.get_pressed()
        left_flipper.active = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right_flipper.active = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        # Update
        left_flipper.update()
        right_flipper.update()
        ball.update()
        ball.collide_with_flipper(left_flipper)
        ball.collide_with_flipper(right_flipper)
        for bumper in bumpers:
            if ball.collide_with_bumper(bumper):
                score += BUMPER_SCORE

        # Draw
        screen.fill(GREY)
        pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, HEIGHT), 8)
        for bumper in bumpers:
            bumper.draw(screen)
        left_flipper.draw(screen)
        right_flipper.draw(screen)
        ball.draw(screen)

        # Draw score
        score_surf = FONT.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surf, (20, 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()