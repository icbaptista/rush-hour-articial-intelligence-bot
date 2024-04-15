import os
from common import Map
from search import Search
import time

def readLevelsFromFile():
    levels = []
    with open("levels.txt", "r") as f:
        for line in f:
            levels.append(line.strip())
    return levels

def logTime(time, level):
    with open("log_search.txt", "a") as file:
        file.write(f"Level {level} - Time: {time} seconds\n")

if os.path.exists("log_search.txt"):
    os.remove("log_search.txt") 

total_time = 0
levels = readLevelsFromFile()
print(levels)

for line in levels:
    board = Map(line)
    print(board.grid)
    cars = [spot[2] for spot in board.coordinates]  
    everyCar = sorted([i for n, i in enumerate(cars) if i not in cars[:n] and i != 'x' and i != 'o']) 
    search = Search(board, everyCar)
    level = line.split(" ")[0]

    print(f"\nLEVEL {level}: Starting search...")
    start = time.time()
    path, gridSol = search.searchFunction()                                          
    end = time.time()
    now = end - start
    total_time += now

    # Output examples
    # Path AdAdAdAd
    # GridSol [["ooooooAAAAAoooo"], ["oooooAAAoooooo"]]

    print(f"Path solution: {path}")
    print(f"Execution elapsed time: {now} seconds")
    logTime(now, level)

with open("log_search.txt", "a") as file:
    print(f"Total time: {total_time} seconds")
    file.write(f"Total time: {total_time} seconds\n")

