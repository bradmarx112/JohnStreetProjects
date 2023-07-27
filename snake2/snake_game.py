import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
#font = pygame.font.SysFont('arial', 25)

# reset function --> after each game agent should be able to reset and restart
# reward function for agent
# play(action) --> direction 
# game_iteration 
# is_collision 

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')
Bomb_Point = namedtuple('Point', 'x,y,direction')

# rgb colors
WHITE = (255, 255, 255)
GREEN = (0,200,0)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 200

class SnakeGameAI:
    
    # initialize the snake and the game 
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        # init game state
        self.direction = Direction.RIGHT
        
        # initalize snake head and body --> three blocks long
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        self.length = len(self.snake)
        
        # initalize zero score and place down food
        self.score = 0
        self.food = None

        # bomb stuff
        self.bomb_list = []
        self.moving_bombs = []
        self.counter = 0

        self._place_food()
        self._place_bomb()
        
        # initalize frame iterations to zero 
        self.frame_iteration = 0
        
    # function to reset the game and let agent replay
    def reset(self):
        # init game state
        self.direction = Direction.RIGHT
        
        # initalize snake head and body --> three blocks long
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        self.length = len(self.snake)
        
        # initalize zero score and place down food
        self.score = 0
        self.food = None
        self.bomb_list = []
        self._place_food()
        self._place_bomb()
        
        # initalize frame iterations to zero 
        self.frame_iteration = 0

        self.counter = 0

    # function to place down food randomly    
    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)

        # call again if the food was placed in the snake
        if (self.food in self.snake) or (self.food in self.bomb_list): 
            self._place_food()
    
    # function to place a bomb 
    def _place_bomb(self):
        # place coordinates of bomb 
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE

        # give bomb default direction 
        if len(self.bomb_list) % 2 == 0:
            dir = 'RIGHT'
        else:
            dir = 'DOWN'

        # craete bomb 
        bomb = Bomb_Point(x, y, dir)
    
        # check if the bomb is in bad spot and recall bomb 
        if bomb in self.bomb_list or bomb in self.snake or (bomb.x == self.food.x and bomb.y == self.food.y):
            self._place_bomb()

        # increment move counter if bomb list is full 
        # elif len(self.bomb_list) == 10:
        #     if self.counter < 9: 
        #         self.counter += 1
        else:
            self.bomb_list.append(bomb)
    
    # function to move bombs 
    def move_bomb(self):
        # move all bombs that are below the counter 
        for i in range(self.counter):
                # grab bomb 
                bomb = self.bomb_list[i]

                # change bombs direction based on logic 
                if bomb.direction == 'RIGHT':
                    if bomb.x + BLOCK_SIZE < self.w:
                        bomb = Bomb_Point(bomb.x + BLOCK_SIZE, bomb.y,bomb.direction)
                    else:
                        bomb = Bomb_Point(bomb.x - BLOCK_SIZE, bomb.y,'LEFT')
                elif bomb.direction == 'LEFT':
                    if bomb.x - BLOCK_SIZE > 0:
                        bomb = Bomb_Point(bomb.x - BLOCK_SIZE, bomb.y,bomb.direction)
                    else:
                        bomb = Bomb_Point(bomb.x + BLOCK_SIZE, bomb.y,'RIGHT')
                elif bomb.direction == 'UP':
                    if bomb.y - BLOCK_SIZE > 0:
                        bomb = Bomb_Point(bomb.x, bomb.y-BLOCK_SIZE,bomb.direction)
                    else:
                        bomb = Bomb_Point(bomb.x, bomb.y+BLOCK_SIZE,'DOWN')
                else:
                    if bomb.y + BLOCK_SIZE < self.h:
                        bomb = Bomb_Point(bomb.x, bomb.y+BLOCK_SIZE,bomb.direction)
                    else:
                        bomb = Bomb_Point(bomb.x, bomb.y-BLOCK_SIZE,'UP')
                self.bomb_list[i] = bomb

    
    # function to play a step of the game based on the action choosen by the agent 
    def play_step(self,action):
        # increment the frame iteration 
        self.frame_iteration += 1 

        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move based on the agents action 
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        game_over = False
        reward = -1*(self.frame_iteration/(len(self.snake)*10))

        # if snake collided or frame iterations is too long, end game 
        if self.is_collision():
            # end game 
            game_over = True
            
            # moving pos
            # give negative reward 
            reward = -10
            return reward, game_over, self.score
        if self.frame_iteration > 100*len(self.snake):
            # end game 
            game_over = True

            # give negative reward 
            reward = -10
            return reward, game_over, self.score
            
        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10 
            self._place_food()
            self._place_bomb()
            self.length += 1
        # move the snake by removing the last element in list 
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score
    
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x >  self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True
        # hits bomb
        for bomb in self.bomb_list:
            if pt.x == bomb.x and pt.y == bomb.y:
                return True
        
        return False
        
    def _update_ui(self):
        self.display.fill(BLACK)
        
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
            
        pygame.draw.rect(self.display, GREEN, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        # move bombs
        self.move_bomb()

        # draw bombs 
        for bomb in self.bomb_list:
            pygame.draw.rect(self.display, RED, pygame.Rect(bomb.x, bomb.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
    
    # function to move snake 
    def _move(self, action):
        #[straight,left,right]
        
        # possible directions 
        clock_wise = [Direction.RIGHT, Direction.DOWN,Direction.LEFT,Direction.UP]
        idx = clock_wise.index(self.direction)

        # straight --> keep going in same direction 
        if np.array_equal(action, [1,0,0]):
            new_direction = clock_wise[idx]
        # left --> clockwise rotation of current direction 
        elif np.array_equal(action,[0,1,0]):
            next_idx = (idx + 1) % 4 
            new_direction = clock_wise[next_idx]
        # right --> counter clockwise rotation of current direction 
        else:
            next_idx = (idx - 1) % 4 
            new_direction = clock_wise[next_idx]
        
        # set direction as new direction based on action 
        self.direction = new_direction

        x = self.head.x
        y = self.head.y

        # change head coordinates based on move 
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        # set new head location     
        self.head = Point(x, y)
        