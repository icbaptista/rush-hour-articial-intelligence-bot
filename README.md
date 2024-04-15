# ia-rush
Projecto de Inteligência Artificial 2022 - Rush Hour

In our AI project, we are using the best frist search algorithm for our search strategy as we found that it is the most efficient.

Heuristic: number of blocking cars + distance of red car to exit

Cost: distance to parent node is given by the steps that the cursor needs to make to get to the new node/configuration (Manhattan distance)


## Information about project files 

The code implemented for this project is inside *student.py* and the *search.py* files.

We also havre the script *testing_search.py* that tests the search function only. 

Only the contents in the main branch are to be considered for evaluation. In the other branches, we are testing new strategies for dealing with crazy cars and they are not considered for evalutation.

In the log_time.txt file, the execution time for every level can be found and in the log_search.txt file, the execution time for every level using the *test_search.py* script will be found.

## How to install

Make sure you are running Python 3.7 or higher

`$ pip install -r requirements.txt`

*Tip: you might want to create a virtualenv first*

## How to play

open 3 terminals:

`$ python3 server.py`

`$ python3 viewer.py`

`$ python3 client.py`

to play using the sample client make sure the client pygame window has focus

## Score and level 

We are able to solve all levels and the maximum score achieved was 1549487.

### Keys

Directions: arrows

## Debug Installation

Make sure pygame is properly installed:

python -m pygame.examples.aliens

# Tested on:
- OSX Monterey 12.5.1ch
