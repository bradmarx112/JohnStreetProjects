import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('snake_game/arial.ttf', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 30

class Ball:

    def __init__(self, loc: Point, w, h):
        self.position = loc
        self.init_pos = loc
        self.w = w - BLOCK_SIZE
        self.h = h - BLOCK_SIZE
        
        self.reset()

    def reset(self) -> None:
        self.position = self.init_pos
        self.angle = random.randint(179, 359) + 0.01  # Added to avoid divide by zero errors later
        self.at_wall = False

    def move_ball(self) -> None:
        if self.at_wall:
            self._compute_angle()
            self.at_wall = False

        potential_point = Point(self.position.x + np.cos(np.deg2rad(self.angle))*BLOCK_SIZE, \
                                self.position.y + np.sin(np.deg2rad(360 - self.angle))*BLOCK_SIZE)  # Flip because y axis is inverted

        if self.position.y > self.h:
            self.reset()

        if potential_point.x > self.w or potential_point.x < 0 or potential_point.y < 0:

            if np.cos(np.deg2rad(self.angle)) >= 0:
                tol_x = self.w - self.position.x
            else:
                tol_x = self.position.x
            
            if np.sin(np.deg2rad(360 - self.angle)) >= 0:
                tol_y = self.h - self.position.y 
            else:
                tol_y = self.position.y

            pct_bad_x = np.abs(tol_x / (np.cos(np.deg2rad(self.angle))*BLOCK_SIZE))
            pct_bad_y = np.abs(tol_y / (np.sin(np.deg2rad(360 - self.angle))*BLOCK_SIZE))

            req_shrinkage = min(pct_bad_x, pct_bad_y)
            self.at_wall = True
        else:
            req_shrinkage = 1
        self.position = Point(self.position.x + np.cos(np.deg2rad(self.angle))*BLOCK_SIZE*req_shrinkage, \
                                self.position.y + np.sin(np.deg2rad(360 - self.angle))*BLOCK_SIZE*req_shrinkage)

    def _compute_angle(self) -> None:
        if (int(self.position.x) == 0 or int(self.position.x) == self.w) and \
            (int(self.position.y) == 0 or int(self.position.y) == self.h):
            self.angle = (self.angle + 180) % 360
        elif int(self.position.x) == 0 or int(self.position.x) == self.w:
            if self.angle >= 180:
                self.angle += 2*(270 - self.angle)
            else:
                self.angle += 2*(90 - self.angle)

        elif int(self.position.y) == 0 or int(self.position.y) == self.h:
            if np.cos(np.deg2rad(self.angle)) <= 0:
                self.angle += 2*(180 - self.angle)
            else:
                self.angle = 360 - self.angle


class BrickBreakGame:

    def __init__(self, w=640, h=480, paddle_length=4, n_bricks=20, brick_depth_ratio=0.3):
        self.w = w
        self.h = h
        self.n_bricks = n_bricks
        self.brick_depth = int(self.h * brick_depth_ratio)
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Brick Break')
        self.clock = pygame.time.Clock()
        self.paddle_len = paddle_length
        self.reset()

    def reset(self):
        self.paddle = []
        mid = (self.w / BLOCK_SIZE) // 2
        start_pos = mid - (self.paddle_len // 2)
        for block_id in range(self.paddle_len):
                self.paddle.append(Point(x=(start_pos + block_id)*BLOCK_SIZE, y=self.h-BLOCK_SIZE))
        
        brickset = set()
        for brick_id in range(self.n_bricks):
            brickset.add(Point(x=random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE,
                               y=random.randint(0, (self.brick_depth)//BLOCK_SIZE )*BLOCK_SIZE))
        self.bricks = list(brickset)
        self.paddle_dir = Direction.RIGHT
        self.ball = Ball(Point(self.w/2, self.h/2), self.w, self.h)

    def play_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        self._move()
        self._update_ui()
        self.clock.tick(SPEED)
        return self.paddle

    def _move(self):
        if self.paddle_dir == Direction.RIGHT:
            if self.paddle[-1].x > self.w - BLOCK_SIZE*2:
                self.paddle.insert(0, Point(x=self.paddle[0].x - BLOCK_SIZE, y=self.h-BLOCK_SIZE))
                self.paddle.pop()
                self.paddle_dir = Direction.LEFT
            else:
                self.paddle.append(Point(x=self.paddle[-1].x + BLOCK_SIZE, y=self.h-BLOCK_SIZE))
                self.paddle.pop(0)

        elif self.paddle_dir == Direction.LEFT:
            if self.paddle[0].x <= 0:
                self.paddle.append(Point(x=self.paddle[-1].x + BLOCK_SIZE, y=self.h-BLOCK_SIZE))
                self.paddle.pop(0)
                self.paddle_dir = Direction.RIGHT
            else:
                self.paddle.insert(0, Point(x=self.paddle[0].x - BLOCK_SIZE, y=self.h-BLOCK_SIZE))
                self.paddle.pop()
        
        self.ball.move_ball()

    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.paddle:
            # print(pt)
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        for bricks in self.bricks:
            # print(pt)
            pygame.draw.rect(self.display, RED, pygame.Rect(bricks.x, bricks.y, BLOCK_SIZE, BLOCK_SIZE))
            
        pygame.draw.rect(self.display, RED, pygame.Rect(self.ball.position.x, self.ball.position.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score:" + "Test", True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

if __name__ == '__main__':
    block_test = BrickBreakGame()
    while True:
        block_test.play_step()
