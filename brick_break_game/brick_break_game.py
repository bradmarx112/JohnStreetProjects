import pygame
import random
import numpy as np
from math import radians, cos, sin

from utils import Direction, Point, WHITE, RED, GREEN, BLUE1, BLUE2, BLACK, BLOCK_SIZE, SPEED
from brick_patterns import spiral

pygame.init()
font = pygame.font.Font('snake_game/arial.ttf', 25)

class Ball:

    def __init__(self, loc: Point, w, h):
        self.position = loc
        self.init_pos = loc
        self.w = w
        self.h = h
        self.ball_dim = BLOCK_SIZE//2
        
        self.angle = random.randint(0, 359) + 0.01  # Added to avoid divide by zero errors later
        self.cos_angle = cos(radians(self.angle))
        self.sin_angle = sin(radians(360 - self.angle))
        self.at_wall = False

    def update_angle(self, blocker: Point = None) -> None:
        if not blocker:
            strtx, strty =  self.ball_dim, self.ball_dim
            endx, endy = self.w - self.ball_dim, self.h - self.ball_dim
        else:
            strtx, strty = blocker.x, blocker.y
            endx, endy = blocker.x + BLOCK_SIZE, blocker.y + BLOCK_SIZE
        if (int(self.position.x) + self.ball_dim == strtx or int(self.position.x) == endx) and \
            (int(self.position.y) + self.ball_dim == strty or int(self.position.y) == endy):
            self.angle = (self.angle + 180) % 360
        elif int(self.position.x) + self.ball_dim == strtx or int(self.position.x) == endx:
            if self.angle >= 180:
                self.angle += 2*(270 - self.angle)
            else:
                self.angle += 2*(90 - self.angle)

        elif int(self.position.y) + self.ball_dim == strty or int(self.position.y) == endy:
            if self.cos_angle <= 0:
                self.angle += 2*(180 - self.angle)
            else:
                self.angle = 360 - self.angle
        
        # Update Trig values (amount ball will move in x and y directions at current angle)
        self.cos_angle = cos(radians(self.angle))
        self.sin_angle = sin(radians(360 - self.angle))


class BrickBreakGame:

    def __init__(self, w=640, h=480, paddle_length=4, n_bricks=20, brick_depth_ratio=0.3):
        self.w = w - BLOCK_SIZE
        self.h = h - BLOCK_SIZE
        self.n_bricks = n_bricks
        self.brick_depth = int(self.h * brick_depth_ratio) - (int(self.h * brick_depth_ratio) % BLOCK_SIZE)
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Brick Break')
        self.clock = pygame.time.Clock()
        self.paddle_len = paddle_length
        self.reset()

    def reset(self) -> None:
        self.paddle = []
        mid = (self.w / BLOCK_SIZE) // 2
        start_pos = mid - (self.paddle_len // 2)
        for block_id in range(self.paddle_len):
                self.paddle.append(Point(x=(start_pos + block_id)*BLOCK_SIZE, y=self.h - BLOCK_SIZE))
        
        # brickset = set()
        # for brick_id in range(self.n_bricks):
        #     brickset.add(Point(x=random.randint(0, (self.w)//BLOCK_SIZE )*BLOCK_SIZE,
        #                        y=random.randint(0, (self.brick_depth)//BLOCK_SIZE )*BLOCK_SIZE))
        self.bricks = spiral(self.w, self.brick_depth)
        self.blocker = None
        self.score = 0
        self.paddle_dir = Direction.RIGHT
        self.ball = Ball(Point(self.w//2, self.h//2), self.w, self.h)

    def play_step(self, action: list = None) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        self._move(action=action)
        if self.blocker in self.bricks:
            self.score += 1
        self.bricks = [brick for brick in self.bricks if brick != self.blocker]

        self._update_ui()
        self.clock.tick(SPEED)

    def _move(self, action: list = None):
        self._move_paddle(action=action)
        
        self._move_ball()

    def _move_paddle(self, action: list = None) -> None:
        '''
        Moves paddle one space based on parameters in 'action' list. 
        [1, 0, 0] means move left, [0, 0, 1] means move right, [0, 1, 0] means do not move
        '''
        if not action:
            self._auto_move()
        else:
            # Check if moving left
            if np.array_equal(action, [1, 0, 0]):
                # Only move if not touching left side of screen
                if self.paddle[0].x >= BLOCK_SIZE:
                    self.paddle.insert(0, Point(x=self.paddle[0].x - BLOCK_SIZE, y=self.h - BLOCK_SIZE))
                    self.paddle.pop()
            
            # Check if moving right
            elif np.array_equal(action, [0, 0, 1]):
                # Only move if not touching right side of screen
                if self.paddle[-1].x + BLOCK_SIZE > self.w:
                    self.paddle.append(Point(x=self.paddle[-1].x + BLOCK_SIZE, y=self.h - BLOCK_SIZE))
                    self.paddle.pop(0)
            
            # If action is [0, 1, 0] then do nothing (stay in same place)

    def _auto_move(self) -> None:
        if self.paddle_dir == Direction.RIGHT:
            if self.paddle[-1].x > self.w - BLOCK_SIZE:
                self.paddle.insert(0, Point(x=self.paddle[0].x - BLOCK_SIZE, y=self.h - BLOCK_SIZE))
                self.paddle.pop()
                self.paddle_dir = Direction.LEFT
            else:
                self.paddle.append(Point(x=self.paddle[-1].x + BLOCK_SIZE, y=self.h - BLOCK_SIZE))
                self.paddle.pop(0)

        elif self.paddle_dir == Direction.LEFT:
            if self.paddle[0].x <= 0:
                self.paddle.append(Point(x=self.paddle[-1].x + BLOCK_SIZE, y=self.h - BLOCK_SIZE))
                self.paddle.pop(0)
                self.paddle_dir = Direction.RIGHT
            else:
                self.paddle.insert(0, Point(x=self.paddle[0].x - BLOCK_SIZE, y=self.h - BLOCK_SIZE))
                self.paddle.pop()

    def _move_ball(self) -> None:
        
        if self.ball.at_wall:
            self.ball.update_angle(self.blocker)
            self.ball.at_wall = False

        potential_point = Point(self.ball.position.x + self.ball.cos_angle*BLOCK_SIZE, \
                                self.ball.position.y + self.ball.sin_angle*BLOCK_SIZE)  # Flip because y axis is inverted

        if self.ball.position.y + self.ball.ball_dim > self.h:
            self.reset()
        else:
            blocker_shrinkage, self.blocker = self._get_blocker_shrinkage()

            if potential_point.x + self.ball.ball_dim > self.w or potential_point.x < 0 or potential_point.y < 0 or blocker_shrinkage != 1.0:

                if self.ball.cos_angle >= 0:
                    tol_x = self.w - (self.ball.position.x + self.ball.ball_dim)
                else:
                    tol_x = self.ball.position.x
                
                if self.ball.sin_angle >= 0:
                    tol_y = self.h - (self.ball.position.y + self.ball.ball_dim) 
                else:
                    tol_y = self.ball.position.y

                pct_bad_x = np.abs(tol_x / (self.ball.cos_angle*BLOCK_SIZE))
                pct_bad_y = np.abs(tol_y / (self.ball.sin_angle*BLOCK_SIZE))

                req_shrinkage = min(pct_bad_x, pct_bad_y, blocker_shrinkage)
                self.ball.at_wall = True
            else:
                req_shrinkage = 1.0
            self.ball.position = Point(self.ball.position.x + self.ball.cos_angle*BLOCK_SIZE*req_shrinkage, \
                                    self.ball.position.y + self.ball.sin_angle*BLOCK_SIZE*req_shrinkage)

    def _get_blocker_shrinkage(self) -> float:

        relevant_shrinkage = 1.0
        closest_block = None
        for block in self.paddle + self.bricks:
            # if block == self.blocker:
            #     continue
            if self.ball.cos_angle >= 0:
                x_tol_frm_origin = block.x - (self.ball.position.x + self.ball.ball_dim)
                
            else:
                x_tol_frm_origin = self.ball.position.x - (block.x + BLOCK_SIZE)

            if abs(x_tol_frm_origin) > BLOCK_SIZE + self.ball.ball_dim:
                continue

            if x_tol_frm_origin < 0:
                x_tol_frm_origin = BLOCK_SIZE

            if self.ball.sin_angle >= 0:
                y_tol_frm_origin = block.y - (self.ball.position.y + self.ball.ball_dim)
                
            else:
                y_tol_frm_origin = self.ball.position.y - (block.y + BLOCK_SIZE)

            if abs(y_tol_frm_origin) > BLOCK_SIZE + self.ball.ball_dim:
                continue

            if y_tol_frm_origin < 0:
                y_tol_frm_origin = BLOCK_SIZE

            pct_bad_x = np.abs(x_tol_frm_origin / (self.ball.cos_angle*BLOCK_SIZE))
            pct_bad_y = np.abs(y_tol_frm_origin / (self.ball.sin_angle*BLOCK_SIZE))

            feasible_shrinkages = [1.0]

            if (block.x < self.ball.position.x + self.ball.cos_angle*BLOCK_SIZE*pct_bad_y < block.x + BLOCK_SIZE) or \
                block.x < (self.ball.position.x + self.ball.ball_dim) + self.ball.cos_angle*BLOCK_SIZE*pct_bad_y < block.x + BLOCK_SIZE:
                feasible_shrinkages.append(pct_bad_y)
                
            if (block.y < self.ball.position.y + self.ball.sin_angle*BLOCK_SIZE*pct_bad_x < block.y + BLOCK_SIZE) or \
                block.y < (self.ball.position.y + self.ball.ball_dim) + self.ball.sin_angle*BLOCK_SIZE*pct_bad_x < block.y + BLOCK_SIZE:
                feasible_shrinkages.append(pct_bad_x)

            shrinkage = min(feasible_shrinkages)
            if shrinkage < relevant_shrinkage:
                closest_block = block
                relevant_shrinkage = shrinkage

        return relevant_shrinkage, closest_block

    def _update_ui(self) -> None:
        self.display.fill(BLACK)

        for pt in self.paddle:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        for bricks in self.bricks:
            pygame.draw.rect(self.display, RED, pygame.Rect(bricks.x, bricks.y, BLOCK_SIZE, BLOCK_SIZE))
            
        pygame.draw.rect(self.display, GREEN, pygame.Rect(self.ball.position.x, self.ball.position.y, self.ball.ball_dim, self.ball.ball_dim))
        
        text = font.render(f"Score: {str(self.score)}", True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

if __name__ == '__main__':
    block_test = BrickBreakGame()
    while True:
        block_test.play_step()
