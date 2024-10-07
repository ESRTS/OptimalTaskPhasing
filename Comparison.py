from Time import *
from Task import *
import random
import os

def davareBound(chain):
    """ This function computes the worst-case bound for the task chain.

        Davare, Zhu, Di Natale, Pinello, Kanajan, and Sangiovanni-Vincentelli. 2007. 
        Period optimization for hard real-time distributed automotive systems. 
        In Proceedings of the 44th annual Design Automation Conference (DAC '07). 
    """
    
    bound = 0

    for task in chain:
        bound = bound + (2 * task.period)

    return bound

def randomPhasing(chain, seed):
    """ This function applies a random offset between each consecutive task of the chain.
    """

    rnd = random.Random() # Get a independent instance of Random, to not affect the sequence of generated tasks in the main experiment
    rnd.seed(seed)
    
    predecessor = None

    for task in chain:
        if predecessor != None:
            
            minPeriod = min(task.period, predecessor.period)
              
            task.offset = rnd.randint(0, minPeriod - 1)      

        predecessor = task

def offsetAssignmentHeuristic(chain, offsetGranularity):
    """ This function computes thenumber of latency computations required to find the optimal 
        offset according to the offset assignment heuristic of:
        J. Martinez, I. Sañudo and M. Bertogna, "Analytical Characterization of End-to-End 
        Communication Delays With Logical Execution Time," in IEEE Transactions on Computer-Aided 
        Design of Integrated Circuits and Systems, vol. 37, no. 11, pp. 2244-2254, 2018.
    """

    combinations = 1    # how often the latency analysis needs to be performed

    periods = []

    for task in chain:
        if len(periods) == 0:
            periods.append(task.period)
        else:
            periodsLcm = math.lcm(*periods)
            offsetMax = math.gcd(task.period, periodsLcm) 

            assert offsetMax % offsetGranularity == 0

            combinations = int(combinations * (offsetMax / offsetGranularity))
    
    #assert countLatencyTest % offsetGranularity = 0

    return combinations

if __name__ == "__main__":
    """ Debugging """
    os.system('cls' if os.name == 'nt' else 'clear')    # Clear the terminal

    task1 = Task('Task1', useconds(1), mseconds(10), mseconds(10), 0)
    task2 = Task('Task2', useconds(1), mseconds(1), mseconds(1), 0)
    task3 = Task('Task3', useconds(1), mseconds(10), mseconds(10), mseconds(1))

    chain = [task1, task2, task3]

    assignments = offsetAssignmentHeuristic(chain, mseconds(1))

    print(str(assignments) + " offset assignments to check")