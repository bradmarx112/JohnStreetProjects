import torch
import random
import numpy as np
from collections import deque
from snake_game import SnakeGameAI, Direction, Point
from model import Linear_QNEt, QTrainer
from helper import plot
import os

# parameters for learning
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

# class for the agent snake 
class Agent:

    def __init__(self):
        # number of games 
        self.n_games = 0

        # random parameter for explore/exploit
        self.epsilon = 0 

        # discount rate
        self.gamma = 0.9

        self.memory = deque(maxlen=MAX_MEMORY) #popleft if over limit 
        self.model = Linear_QNEt(11,256,3)
        self.trainer = QTrainer(self.model,lr=LR,gamma=self.gamma)
        
        # length of snake 
        self.length = 3

    # return the state of the game based on current location
    def get_state(self,game):
        # get head of snake 
        head = game.snake[0]

        # check spaces directly around the snakes head 
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x+20,head.y)
        point_u = Point(head.x,head.y-20)
        point_d = Point(head.x,head.y+20)

        # booleans, only one true for the current direction 
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        # create state as list of 11 tuples 
        state = [
            # danger straight
            (dir_r and game.is_collision(point_r)) or
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # danger right 
            (dir_d and game.is_collision(point_r)) or
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),

            # danger left 
            (dir_r and game.is_collision(point_r)) or
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # direction of movement
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # food location
            game.food.x < game.head.x, # food left 
            game.food.x > game.head.x, # food right
            game.food.y < game.head.y, # food up
            game.food.y > game.head.y, # food down 
        ]

        # return the state  
        return np.array(state, dtype=int)
    
    def remember(self,state,action,reward,next_state,done):
        # add previous state information to memory que -> stored as one tuple 
        self.memory.append((state,action,reward,next_state,done)) # popleft if exceeded max mem

    # train on all previous moves of all previous games 
    def train_long_memory(self):
        # want 1000 steps from memory if memory has it 
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory,BATCH_SIZE) # list of tuples 
        # if les than 1000 memories, just take the whole thing
        else:
            mini_sample = self.memory

        # break up samples by combining all states and actions and rewards...
        states, actions, rewards, next_states, dones = zip(*mini_sample)

        # train on 1000 or all memories 
        self.trainer.train_step(states,actions,rewards,next_states,dones) 

    # train on one step after each step 
    def train_short_memory(self,state,action,reward,next_state,done):
        self.trainer.train_step(state,action,reward,next_state,done)

    # function to get the next action of the agent 
    def get_action(self,state):
        # random moves at beginning: trade off between exploration and exploitation 
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]

        # if less games, take random move 
        if self.length > 7:
            if random.randint(0,200) < self.epsilon:
                # randome index of 0,1,2
                move = random.randint(0,2) 
                final_move[move] = 1
            # if not random, make a predicted action based on state 
            else:
                state0 = torch.tensor(state,dtype=torch.float)
                # list of three raw values --> output of the nn
                prediction = self.model(state0) # forward function 

                move = torch.argmax(prediction).item()
                final_move[move] = 1
        # if not random, make a predicted action based on state 
        else:
            state0 = torch.tensor(state,dtype=torch.float)
            # list of three raw values --> output of the nn
            prediction = self.model(state0) # forward function 

            move = torch.argmax(prediction).item()
            final_move[move] = 1
    
        # return the move of the agent 
        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    tot_score = 0
    record = 0

    agent = Agent()
    game = SnakeGameAI()

    # Check if a saved model exists and load it
    if os.path.exists('./model/model.pth'):
        print('hi')
        agent.model.load('./model/model.pth')
  
    while True:
        # get old state 
        state_old = agent.get_state(game)

        # get move based on current state
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory on one step 
        agent.train_short_memory(state_old,final_move,reward,state_new,done)
        
        # remember in deque 
        agent.remember(state_old,final_move,reward,state_new,done)
     
        # if game over, train over all previous moves of all previous games 
        if done:
            # reset the game 
            game.reset()
            agent.n_games += 1

            # train on all moves of all games 
            agent.train_long_memory()

            # set new high score if needed 
            if score > record:
                record = score 
                # save current best model's weights
                agent.model.save() 

            print(f'Game: {agent.n_games} Score: {score} Record: {record}')

            plot_scores.append(score)
            tot_score += score 
            mean_score = tot_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores,plot_mean_scores,record)
    


if __name__ == '__main__':
    train()

