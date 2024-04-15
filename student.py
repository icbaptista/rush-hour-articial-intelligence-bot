import asyncio
import getpass
import json
import os
import time
import math

# Next 4 lines are not needed for AI agents, please remove them from your code!
import websockets
from my_common import Coordinates, Map, MapException
from search import Search

if os.path.exists("log_time.txt"):
    os.remove("log_time.txt") 

if os.path.exists("log_states.txt"):
    os.remove("log_states.txt") 

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        
        level = 0                       # Level counter
        path = ""                       # Path of the solution
        gridSol = []                    # Grid of the all states that lead to a solution (to deal with crazy cars)
        cursor = None                   # Cursor coordinates
        cursor_anterior = None          # Cursor coordinates
        current_grid = None             # Current grid
        coordinates_before = []         # coordenadas anteriores
        total_time = 0
        cars = None
        everyCar = None
        crazy_car = ""
        counter_key = ""
        crazy_cars_list = []
        last_move = ""
        gri_size = 0

        while True:
            try:
                #configuração de cada nivel
                # receive game update, this must be called timely or your game will get out of sync with the server
                state = state = json.loads(  # can I block this for each level of the game? 
                    await websocket.recv()
                )
               
                if level != state["level"]:
                    level = state["level"]
                    level_changed = True
                    path = ""
                    gridSol = []
                else:
                    level_changed = False

                # Getting information about the current level from the stated
                board = Map(state["grid"])
                cursor = state["cursor"]
                grid = state["grid"]
                coords = board.coordinates
                grid_size = board.grid_size

                # Para dar cope com os carros aleatórios, podemos interromper a search e voltar quando já tivemos as coisas atualizadas  
                if level_changed and len(gridSol) == 0:
                    cars = [spot[2] for spot in board.coordinates]                                           
                    everyCar = sorted([i for n, i in enumerate(cars) if i not in cars[:n] and i != 'x' and i != 'o'])      
                    search = Search(board, everyCar)
                    print("AAAAAAAAAAAAaa")
                    grid_anterior = state["grid"]
                    cursor_anterior = state["cursor"]
                    print(f"\nLEVEL {level}: Starting search...")
                    start = time.time()
                    path, gridSol = search.searchFunction()                                      
                    end = time.time()
                    now = end - start
                    total_time += now
                    print(f"Path solution: {path}")
                    print(f"Execution elapsed time: {now} seconds")
                    logTime(now, state["level"])
                    logStates(search.statesExplored, board.movements, state["level"])
                    # Counting the total time
                    if level == "57":
                        with open("log_time.txt", "a") as file:
                            print(f"Total time: {total_time} seconds")
                            file.write(f"Total time: {total_time} seconds\n")
                elif state["grid"].split(" ")[1] not in gridSol and not level_changed and crazy_car == "":    # sign that there was a crazy car
                    print("\nCRAZY CAR!")
                    coordinates_expected = cars_coordinates(gridSol[0], grid_size)
                    current_piece = board.get(Coordinates(cursor[0], cursor[1]))
                    counter_key, crazy_car, new_path = counter_crazy_car(coords, coordinates_expected, current_piece, last_move, path)
                    #if crazy_car not in crazy_cars_list:
                    path = crazy_car + counter_key + path
                    print(f"Crazy car {crazy_car} and counter key {counter_key}")
                    print(f"New path: {path}")
                     
                
                cursor_anterior = state["cursor"]   
                #grid_anterior = state["grid"] 
                coordinates_before = board.coordinates

                # Picking the next car to move
                if path != None: 
                    car = path[0]

                # Coordinates of the car that is going to be moved
                occupiedCoord = board.piece_coordinates(car)
         
                if state["selected"] != car:                                                # if we don't have the target car selected  
                    
                    if state["selected"] != '':                                             # unlocking the car so that cursor can move to another place
                        key = " "
                        await websocket.send(json.dumps({"cmd": "key", "key": key}))
                    else:
                        if state["cursor"][0]  != occupiedCoord[1].x:                          # we will need to take the cursor to the target car
                            key = moveCursorToCarXAxis(state["cursor"], occupiedCoord)          # move cursor to car along the X axis
                            await websocket.send(json.dumps({"cmd": "key", "key": key}))  
                        elif state["cursor"][1] != occupiedCoord[1].y:                         
                            key = moveCursorToCarYAxis(state["cursor"], occupiedCoord)          # move cursor to car along the Y axis
                            await websocket.send(json.dumps({"cmd": "key", "key": key}))  
                        elif state["cursor"][1] == occupiedCoord[1].y and state["cursor"][0] == occupiedCoord[1].x:
                            key = " "
                            await websocket.send(json.dumps({"cmd": "key", "key": key}))  
                else: 
                    key = path[1]
                    last_move = car + key
                    await websocket.send(json.dumps({"cmd": "key", "key": key}))  # send key command to server - you must implement this send in the AI agent
                    if crazy_car != "":
                        crazy_car = ""
                    else: 
                        gridSol.remove(gridSol[0])  # this list is to check if grid is according to expected -> if not, there was a crazy car move
                    path = path[2:]
                    await websocket.send(json.dumps({"cmd": "key", "key": key}))  # send key command to server - you must implement this send in the AI agent
                        
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

def counter_crazy_car(coordinates, coordinates_expected, current_piece, last_move, path):
    diffInExpected = [x for x in coordinates_expected if x not in coordinates]
    diffInCurrent = [x for x in coordinates if x not in coordinates_expected]

    if len(diffInExpected) > 1:
        diffInCurrent = [x for x in diffInCurrent if x[2] != current_piece]
        diffInExpected = [x for x in diffInExpected if x[2] != current_piece]
        path = last_move + path
    

    if len(diffInExpected) == 0 and len(diffInCurrent) == 0:
       return "", ""

    # Movimentos horizontais
    # If the car is moving to the left 
    if diffInExpected[0][0] > diffInCurrent[0][0]:
        key = "d"
    elif diffInExpected[0][0] < diffInCurrent[0][0]:
        key = "a"
    # Movimentos verticais
    elif diffInExpected[0][1] > diffInCurrent[0][1]:
        key = "s"
    elif diffInExpected[0][1] < diffInCurrent[0][1]:
        key = "w"

    #if key + diffInExpected[0][2] in path:
    #    return "", ""

    return key, diffInExpected[0][2], path

# Function to find the coordinates of the car (from common.py)
def cars_coordinates(grid, grid_size):
    """Representation of ocupied map positions through tuples x,y,value."""
    new_grid = []
    l = []
    for i, pos in enumerate(grid):
        l.append(pos)
        if (i + 1) % grid_size == 0:
            new_grid.append(l)
            l = []
    
    coordinates = []
    for y, line in enumerate(new_grid):
        for x, column in enumerate(line):
            if column != "o":
                coordinates.append((x, y, column))

    return coordinates  
    

# Function to find the coordinates of the car
def findCoordinates(lst, car):
    lala = []
    for a in range(len(lst)):
        for i in range(len(lst[a])):
            if lst[a][i] == car:
                lala.append((i,a))
    return lala

# Function to find the shortest path to the cursor
# Coordenadas do cursor -> [coluna, linha]
def moveCursorToCarXAxis(cordCursor,cordCar):
    if cordCursor[0] - cordCar[1].x > 0:
        #print("a")
        return "a"
    elif cordCursor[0] - cordCar[1].x < 0:
        #print("d")
        return "d"

def moveCursorToCarYAxis(cordCursor,cordCar):
    if cordCursor[1] - cordCar[1].y < 0:
        #print("s")
        return "s"
    elif cordCursor[1] - cordCar[1].y > 0:
        #print("w")
        return "w"

def pretty_grid(grid): 
    nl = '\n'
    a = int(len(grid)//math.sqrt(len(grid)))
    temp = grid
    for i in range(a):
        print("".join(temp[0:a]))
        temp = temp[a:]
    print(nl)

def turnStringIntoGrid(grid):
    line = []
    grid = ""
    size = 6
    for i, pos in enumerate(grid):
        line.append(pos)
        if (i + 1) % size == 0:
            grid.append(line)
            line = []
    print(grid)

def logTime(time, level):
    with open("log_time.txt", "a") as file:
        file.write(f"Level {level} - Time: {time} seconds\n")

def logStates(states, movements, level):
    with open("log_states.txt", "a") as file:
        file.write(f"Level {level} - States expored: {states} - Level complexity: {movements}\n")
    
# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
