

# Next 4 lines are not needed for AI agents, please remove them from your code!
import queue
import pygame
import websockets
from my_common import Coordinates, Map, MapException
import gc
import asyncio
import heapq
import hashlib

class Search: 
    def __init__(self, map, cars):
        init_grid = turnGridIntoString(map.grid)

        self.redCarPos = [(pos[0], pos[1]) for pos in map.coordinates if pos[2] == 'A']                   # red car position
       
        # tuple (mapa, parent, depth, cost, heuristic, selectedCar, path, allStates)
        self.init = (map, None, 0, 0, 100, "A", "", [init_grid])                                          # initial configuration
        
        self.open_nodes = []                                                        # list of unexplored states, placed in a queue                                                     
        heapq.heapify(self.open_nodes)
        heapq.heappush(self.open_nodes, (10, self.init))                            # adding the initial configuration to the queue

        self.visited = set()                                                          # list of explored states to not explore again                                                          
        self.visited.add(map.__hash__())                                            # adding the initial configuration to the list

        self.everyCar = cars

        self.cost_so_far = {}
        self.cost_so_far[init_grid] = 0
         
        self.strategy = "greedy"
    
        self.solution = ""
        self.solutionPath = ""
        self.statesExplored = 0

    def heuristic(self, map): 
        distance_to_exit = map.grid_size - (self.redCarPos[0][0] + 1)
        number_blocking_cars = len([pos for pos in map.coordinates if pos[1] == self.redCarPos[0][1]])
        #len([pos for pos in next_map.coordinates if pos[1] == self.redCarPos[0][1]]) / 2
        return distance_to_exit + number_blocking_cars


    def searchFunction(self):
        while self.open_nodes != []:
            current = heapq.heappop(self.open_nodes)[1]                      # poping the first element of the list
            self.statesExplored += 1

            if self.goalReached(current[0]):
                print("\nFound solution!")
                print(self.solution)
                pretty_grid(current[0].grid)
                print("\n")
                print("Total steps: ", current[2])
                print("Total states explored: ", len(self.visited))
                self.solution = current[0].grid
                self.solutionPath = current[6]
                return self.solutionPath, current[7]
            else: 
                next_states = self.generate_next_moves(current)                     # generating new configurations with new moves
                #print("\nChildren\n")
                lnewnodes = [] 
                parentCord = current[0].piece_coordinates(current[5])
                for next in next_states:  
                    next_map = next[0]
                    next_direction = next[1]
                    next_car = next_direction[0]
                    next_grid = turnGridIntoString(next_map.grid)
                    # This is slower -> if next_grid not in self.visited and not current.in_parent(next_map) and next_grid not in current.allStates:
                    new_hash = next_map.__hash__()
                    if new_hash not in self.visited and next_grid not in current[7]:
                        new_cost = current[3] + self.distance_to_parent(parentCord, next_car, next_map)
                        new_heuristic = self.heuristic(next_map)
                        if  next_grid not in self.cost_so_far or self.cost_so_far[next_grid] < new_cost:
                            self.cost_so_far[next_grid] = new_cost
                            # tuple (mapa, parent, depth, cost, heuristic, selectedCar, path, allStates)
                            new_node = (next_map, current, current[2] + 1, new_cost, new_heuristic, next_car, current[6] + next_direction, current[7] + [next_grid])                      
                            heapq.heappush(self.open_nodes, (new_heuristic, new_node))
                            self.visited.add(new_hash)
        return None

    # Manhattan distance
    def distance_to_parent(self, parentCord, child, current_map):
        currentCord = current_map.piece_coordinates(child)
        return abs(parentCord[0].x - currentCord[0].x) + abs(parentCord[0].y - currentCord[0].y)

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes = self.open_nodes + [(100, lnewnodes[n]) for n in range(len(lnewnodes))] 
        elif self.strategy == 'depth':
            # heapq.heapify(self.open_nodes)
            self.open_nodes[:0] = [(100, lnewnodes[n]) for n in range(len(lnewnodes))]
        elif self.strategy == 'uniform':
            self.open_nodes = self.open_nodes + [(lnewnodes[n].cost, lnewnodes[n]) for n in range(len(lnewnodes))]
        elif self.strategy == 'greedy':
            self.open_nodes = self.open_nodes + [(lnewnodes[n].heuristic, lnewnodes[n]) for n in range(len(lnewnodes))]
        elif self.strategy == 'A*':
            self.open_nodes = self.open_nodes + [(lnewnodes[n].cost + lnewnodes[n].heuristic, lnewnodes[n]) for n in range(len(lnewnodes))]
        heapq.heapify(self.open_nodes)

    # generating new configurations with new moves (each node/vertex in the search)          
    def generate_next_moves(self, current):
        #print("\nGenerating New Moves")
        next_moves = []
        for car in self.everyCar:                                                                       # we need to generate new moves for every car 
            positions = current[0].piece_coordinates(car)                                            # we need to move in both directions if possible 
            if (self.is_horizontal(positions)):                                                         # checking if a car moves horizontally 
                new_coord = Coordinates(positions[0].x - 1, positions[0].y) 
                if (self.can_move_left(new_coord, current[0])):                                      # checking if a car can move to the left                                                                                  
                    new_map = Map(current[0].__repr__())                                             # creating a new map for the new node 
                    direction_vector = Coordinates(-1,0)                                                
                    new_map.move(car, direction_vector)                                                 # moving car along a direction vector    
                    direction = car + "a"                  
                    next_moves.append((new_map, direction))                                                        
                new_coord = Coordinates(positions[-1].x + 1, positions[-1].y)   
                if (self.can_move_right(new_coord, current[0])):                                     # checking if a car can move to the left 
                    new_map = Map(current[0].__repr__())                                             # creating a new map for the new node 
                    direction_vector = Coordinates(1,0)                                                
                    new_map.move(car, direction_vector)                                                 # moving car along a direction vector    
                    direction = car + "d"                  
                    next_moves.append((new_map, direction))                                                                            
            elif (self.is_vertical(positions)):                                                         # checking if a car moves vertically 
                new_coord = Coordinates(positions[0].x , positions[0].y - 1) 
                if (self.can_move_up(new_coord, current[0])):                                        # checking if a car can move to the top of the grid 
                    new_map = Map(current[0].__repr__())                                             # creating a new map for the new node 
                    direction_vector = Coordinates(0,-1)                                                
                    new_map.move(car, direction_vector)                                                 # moving car along a direction vector    
                    direction = car + "w"                  
                    next_moves.append((new_map, direction))                                                                           
                new_coord = Coordinates(positions[-1].x, positions[-1].y + 1) 
                if (self.can_move_down(new_coord, current[0])):                                      # checking if a car can move to the bottom of the grid  
                    new_map = Map(current[0].__repr__())                                             # creating a new map for the new node 
                    direction_vector = Coordinates(0, 1)                                                
                    new_map.move(car, direction_vector)                                                 # moving car along a direction vector    
                    direction = car + "s"                  
                    next_moves.append((new_map, direction))                                                                            
        return next_moves

    # Checking if a car moves horizontally 
    def is_horizontal(self, positions): 
        if positions[0].y == positions[1].y:
            return True
        else :
            return False 

    # Checking if a car moves vertically
    def is_vertical(self, positions): 
        if positions[0].x == positions[1].x:
            return True
        else :
            return False    

    # Checking if a car can move to the left
    def can_move_left(self, new_coord, current):
        if (new_coord.x != -1):                                                                 # checking if car is next to the wall 
            if (not self.is_there_an_obstacle(new_coord, current)):
                return True
        else: 
            return False 

    # Checking if a car can move to the right
    def can_move_right(self, new_coord, current):
        if (new_coord.x != current.grid_size):                                            # checking if car is next to the wall 
            if (not self.is_there_an_obstacle(new_coord, current)):
                return True
        else: 
            return False       

    # Checking if a car can move to the top of the grid
    def can_move_up(self, new_coord, current):
        if (new_coord.y != -1):                                                                 # checking if car is next to the wall 
            if (not self.is_there_an_obstacle(new_coord, current)):
                return True
        else: 
            return False  

    # Checking if a car can move to the bottom of the grid 
    def can_move_down(self, new_coord, current):
        if (new_coord.y != current.grid_size):                                            # checking if car is next to the wall 
            if (not self.is_there_an_obstacle(new_coord, current)):
                return True
        else: 
            return False 

    # Checking if there is already a piece in a certain coordinate in the map -> returns True if car is in the defined coordinate
    def is_there_an_obstacle(self, cord, map):
        if (map.grid[cord.y][cord.x] != 'o'): 
            return True
        else: 
            return False 

    # Checking if we found the exit 
    def goalReached(self, current): 
        if current.test_win():
            return True
        else:  
            return False      

def pretty_grid(grid): 
    nl = '\n'
    for a in grid: 
        print("".join(a))

def turnGridIntoString(grid):
    string = ""
    for a in grid:
        string += "".join(a)
    return string

def custom_hashing(grid):
    # Initialize empty string
    s = ""
    # Iterate over grid
    for y, line in enumerate(grid):
        for x, column in enumerate(line):
            # If the current position contains a car, append its coordinates and identity to the string
            if column != "o" and column != "x":
                s += f"{x},{y},{column}"
    # Compute hash value of the string and return it
    return hashlib.sha256(s.encode()).hexdigest()

