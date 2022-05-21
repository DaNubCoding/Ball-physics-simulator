from re import sub
import pygame
from pygame.locals import *
from custom_vec import VEC
from random import *
from math import *

WIDTH = 600
HEIGHT = 600
FPS = float("inf")

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF)
pygame.display.set_caption("Bouncy balls with physics")
clock = pygame.time.Clock()

gravity = 1200
border_elasticity = 0.8
sub_steps = 1
sizes = (10, 20)

absvec = lambda v: VEC(abs(v.x), abs(v.y))
inttup = lambda tup: tuple((int(tup[0]), int(tup[1])))

class Ball:
    instances = []
    regions = {}

    def __init__(self, pos):
        __class__.instances.append(self)
        self.radius = sizes[1]
        self.pos = VEC(pos)
        self.old_pos = self.pos
        self.vel = self.pos - self.old_pos
        self.acc = VEC(0, 0)
        self.color = (255, 255, 255)
        self.region = inttup(self.pos // (sizes[1] * 2) + VEC(1, 1))
        if self.region in __class__.regions:
            __class__.regions[self.region].append(self)
        else:
            __class__.regions[self.region] = [self]

    def apply_acceleration(self):
        self.acc.y += gravity * sqrt(sqrt(sqrt(sqrt(sqrt(sub_steps)))))

    def handle_collisions(self):
        for x in range(self.region[0] - 1, self.region[0] + 2):
            for y in range(self.region[1] - 1, self.region[1] + 2):
                if (x, y) not in __class__.regions: continue
                for ball in __class__.regions[(x, y)]:
                    axis = self.pos - ball.pos
                    dist = axis.length()
                    overlap = self.radius + ball.radius - dist
                    if overlap > 0 and dist > 0:
                        fac = 1 / dist * overlap * 0.5
                        self.pos += axis * fac
                        ball.pos -= axis * fac

    def update_position(self, dt):
        self.vel = self.pos - self.old_pos
        self.old_pos = self.pos.copy()
        self.pos += self.vel + self.acc * dt ** 2
        self.acc = VEC(0, 0)

        new_region = inttup(self.pos // (sizes[1] * 2) + VEC(1, 1))
        if self.region != new_region:
            if new_region in __class__.regions:
                __class__.regions[new_region].append(self)
            else:
                __class__.regions[new_region] = [self]
            __class__.regions[self.region].remove(self)
            self.region = new_region

    def handle_constraints(self):
        if self.pos.x > WIDTH - self.radius:
            self.pos.x = WIDTH - self.radius
            self.old_pos.x = self.pos.x + self.vel.x * border_elasticity
        elif self.pos.x < 0 + self.radius:
            self.pos.x = 0 + self.radius
            self.old_pos.x = self.pos.x + self.vel.x * border_elasticity
        if self.pos.y > HEIGHT - self.radius:
            self.pos.y = HEIGHT - self.radius
            self.old_pos.y = self.pos.y + self.vel.y * border_elasticity
        elif self.pos.y < 0 + self.radius:
            self.pos.y = 0 + self.radius
            self.old_pos.y = self.pos.y + self.vel.y * border_elasticity

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
            if sum([len(balls) for balls in Ball.regions.values()]) <= 1000:
                Ball(mpos)
        if event.type == KEYDOWN:
            if event.key == K_c:
                for ball in Ball.instances.copy():
                    ball.kill()

    sub_dt = dt / sub_steps
    for _ in range(sub_steps):
        for ball in Ball.instances:
            ball.apply_acceleration()
            ball.handle_collisions()
            ball.update_position(sub_dt)
            ball.handle_constraints()
    for ball in Ball.instances:
        ball.draw(screen)

    pygame.display.flip()

pygame.quit()
quit()
