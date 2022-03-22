import pygame
from pygame.locals import *
from custom_vec import VEC
from random import *
from math import *

WIDTH = 600
HEIGHT = 600
FPS = 144

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
        self.vel = VEC(uniform(-750, 750), uniform(-500, 250))
        self.radius = randint(*sizes)
        self.mass = self.radius ** 2 * pi
        self.color = (choice(colors), choice(colors), choice(colors))
        self.moving = True

    def update(self):
        self.vel.y += gravity * dt
        self.vel -= self.vel.normalize()
        if -6 < self.vel.x < 6:
            self.vel.x = 0
        if -6 < self.vel.y < 6:
            self.vel.y = 0
        self.pos += self.vel * dt
        new_region = inttup(self.pos // (sizes[1] * 2) + VEC(1, 1))
        if self.region != new_region:
            if new_region in __class__.regions:
                __class__.regions[new_region].append(self)
            else:
                __class__.regions[new_region] = [self]
            __class__.regions[self.region].remove(self)
            self.region = new_region

        for x in range(self.region[0] - 1, self.region[0] + 2):
            for y in range(self.region[1] - 1, self.region[1] + 2):
                if (x, y) in __class__.regions:
                    for ball in __class__.regions[(x, y)]:
                        dist = self.pos.distance_to(ball.pos)
                        if dist <= self.radius + ball.radius and ball != self:
                            overlap = -(dist - self.radius - ball.radius)
                            self.pos += overlap * (self.pos - ball.pos) / dist
                            ball.pos -= overlap * (self.pos - ball.pos) / dist
                            self.vel *= 0.85
                            n = (ball.pos - self.pos).normalize()
                            k = self.vel - ball.vel
                            p = 2.0 * (n * k) / (self.mass + ball.mass)
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
    screen.fill((0, 0, 0))
    pygame.display.set_caption(f"Bouncy balls with physics | FPS: {str(int(clock.get_fps()))}")

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            mpos = VEC(pygame.mouse.get_pos())
            if sum([len(balls) for balls in Ball.regions.values()]) <= 150:
                Ball(mpos)
        if event.type == KEYDOWN:
            if event.key == K_c:
                for ball in Ball.instances.copy():
                    ball.kill()

    for region in Ball.regions.copy():
        for ball in Ball.regions[region]:
            ball.update()
    for ball in Ball.instances:
        ball.draw(screen)

    pygame.display.flip()

pygame.quit()
quit()
