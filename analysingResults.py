import matplotlib.pyplot as plt
import click as ck

def timeVScomplexity(algorithm, file): 
    file_time = open("log_time.txt",'r')
    file0 = open("log_states.txt",'r')

    time = []
    # open a file 
    with open('log_time.txt', 'r') as f:
        line = f.readline()
        while line:
            time.append(float(line.split(" ")[1]))
            line = f.readline()
        
    complexity = []
    with open('log_states.txt','r') as f: 
        line = f.readline()
        while line:
            complexity.append(float(line.split(" ")[9]))
            line = f.readline()

    plt.plot(time, complexity,  label = algorithm)
    # naming the x axis
    plt.xlabel('time (s)')
    # naming the y axis
    plt.ylabel('level complexity (number of movements)')
    # giving a title to my graph
    plt.title('Complexity of level vs Elasped Solution Time')
    plt.grid()
    # show a legend on the plot
    plt.legend()
    # function to show the plot
    plt.show()


def statesVScomplexity(algorithm, file): 

    states = []
    movements = []
    with open('log_states.txt','r') as f: 
        line = f.readline()
        while line:
            states.append(float(line.split(" ")[5]))
            movements.append(float(line.split(" ")[9]))
            line = f.readline()

    plt.plot(movements, states, 'o', label = algorithm)
    # naming the x axis
    plt.xlabel('Level of complexity')
    # naming the y axis
    plt.ylabel('Number of explored nodes')
    # giving a title to my graph
    plt.title('Comparing Number of visited Nodes!')
    plt.grid()
    # show a legend on the plot
    plt.legend()
    # function to show the plot
    plt.show()


def timeVSlevel(algorithm, file): 
    time = []
    level = []
    with open('log_states.txt','r') as f: 
        line = f.readline()
        while line:
            level.append(float(line.split(" ")[1]))
            time.append(float(line.split(" ")[4]))
            line = f.readline()

    plt.plot(level, time, label = algorithm)
    # naming the x axis
    plt.xlabel('Level')
    # naming the y axis
    plt.ylabel('Time (s)')
    # giving a title to my graph
    plt.title('Elasped time for finding a solution each level')    
    plt.grid()
    # show a legend on the plot
    plt.legend()
    # function to show the plot
    plt.show()

@ck.command()
@ck.option("--algorithm", "-a", default = "greedy", required = False, help="The algorithm to use")
@ck.option("--independent", "-i", default = "level", required = False, help="The independent variable")
@ck.option("--dependent", "-d", default = "time", required = False, help="The dependent variable")
@ck.option("--file", "-f", default = "log_time.txt", required = False, help="File to read from")

def main(algorithm, independent, dependent, file):
    if independent == "level" and dependent == "time":
        timeVSlevel(algorithm, file)
    elif independent == "complexity" and dependent == "states":
        statesVScomplexity(algorithm, file)
    elif independent == "complexity" and dependent == "time":
        timeVScomplexity(algorithm, file)

if __name__ == "__main__":
    main()