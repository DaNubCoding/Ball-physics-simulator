import pygame
from pygame.locals import *
from random import *
from math import *

WIDTH = 1200
HEIGHT = 600
FPS = float("inf")
VEC = pygame.math.Vector2

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF)
pygame.display.set_caption("Bouncy balls with physics")
clock = pygame.time.Clock()

gravity = 3200
air_friction = 0.99
colors = range(50, 255, 10)
sizes = (15, 25)

absvec = lambda v: VEC(abs(v.x), abs(v.y))
inttup = lambda tup: tuple((int(tup[0]), int(tup[1])))

class Ball:
    instances = []
    regions = {}

    def __init__(self, pos):
        __class__.instances.append(self)
        self.pos = VEC(pos)
        self.region = inttup(self.pos // (sizes[1] * 2) + VEC(1, 1))
        if self.region in __class__.regions:
            __class__.regions[self.region].append(self)
        else:
            __class__.regions[self.region] = [self]
        self.vel = VEC(0, 0)
        self.radius = randint(*sizes)
        self.mass = self.radius ** 2 * pi
        self.color = (choice(colors), choice(colors), choice(colors))
        self.moving = True
        self.collisions = []

    def update_position(self):
        self.vel.y += gravity * dt
        if self.vel != VEC(0, 0):
            self.vel -= self.vel.normalize() * 160 * dt
        self.pos += self.vel * dt

        new_region = inttup(self.pos // (sizes[1] * 2) + VEC(1, 1))
        if self.region != new_region:
            if new_region in __class__.regions:
                __class__.regions[new_region].append(self)
            else:
                __class__.regions[new_region] = [self]
            __class__.regions[self.region].remove(self)
            self.region = new_region

    def update_pushout(self):
        self.collisions = []
        for x in range(self.region[0] - 1, self.region[0] + 2):
            for y in range(self.region[1] - 1, self.region[1] + 2):
                if (x, y) in __class__.regions:
                    for ball in __class__.regions[(x, y)]:
                        dist = self.pos.distance_to(ball.pos)
                        if dist < self.radius + ball.radius and ball != self:
                            self.collisions.append(ball)
                            overlap = -(dist - self.radius - ball.radius) * 0.5
                            pushout = overlap * (self.pos - ball.pos).normalize() if self.pos - ball.pos != VEC(0, 0) else VEC(0, 0)
                            self.pos += pushout
                            ball.pos -= pushout
    
    def update_collision(self):
        for ball in self.collisions:
            self.vel *= 0.85
            n = (ball.pos - self.pos).normalize() if ball.pos - self.pos != VEC(0, 0) else VEC(0, 0)
            k = self.vel - ball.vel
            p = 2 * (n * k) / (self.mass + ball.mass)
            self.vel -= p * ball.mass * n
            ball.vel += p * self.mass * n

        if self.pos.x < self.radius:
            self.vel.x *= -0.8
            self.pos.x = self.radius
        elif self.pos.x > WIDTH - self.radius:
            self.vel.x *= -0.8
            self.pos.x = WIDTH - self.radius
        if self.pos.y < self.radius:
            self.vel.y *= -0.8
            self.pos.y = self.radius
        elif self.pos.y > HEIGHT - self.radius:
            if self.vel.y <= gravity * dt:
                self.vel.y = 0
            else:
                self.vel.y *= -0.8
            self.pos.y = HEIGHT - self.radius

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)

    def kill(self):
        __class__.instances.remove(self)
        __class__.regions[self.region].remove(self)
        del self

running = True
while running:
    dt = clock.tick_busy_loop(FPS) / 1000
    screen.fill((30, 30, 30))
    pygame.display.set_caption(f"Bouncy balls with physics | FPS: {str(int(clock.get_fps()))} | Ball count: {len(Ball.instances)}")

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            mpos = VEC(pygame.mouse.get_pos())
            if sum([len(balls) for balls in Ball.regions.values()]) <= 1000:
                Ball(mpos)
        if event.type == KEYDOWN:
            if event.key == K_c:
                for ball in Ball.instances.copy():
                    ball.kill()

    # shuffle(Ball.instances)
    for ball in Ball.instances:
        ball.update_position()
        ball.update_pushout()
        ball.update_collision()
        ball.draw(screen)

    pygame.display.flip()

pygame.quit()
quit()
