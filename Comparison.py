from Time import *
from Task import *
import random
import os

def davareBound(chain):
    """ This function computes the worst-case bound for the task chain.
        Davare, Zhu, Di Natale, Pinello, Kanajan, and Sangiovanni-Vincentelli. 
        Period optimization for hard real-time distributed automotive systems. 
        In Proceedings of the 44th annual Design Automation Conference (DAC), 2007. 
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

    ### Compute combinations based on offset range to check as described in paper ###

    combinationsIndividual = 1    # how often the latency analysis needs to be performed

    periods = []

    for task in chain:

        assert task.period % offsetGranularity == 0

        tmpPeriod = int(task.period / offsetGranularity)

        if len(periods) != 0:
            periodsLcm = math.lcm(*periods)
            offsetMax = math.gcd(tmpPeriod, periodsLcm) 
            combinationsIndividual = int(combinationsIndividual * offsetMax)
        periods.append(tmpPeriod)

    ### Compute combinations from complexity as described in paper ###

    prod = 1

    for task in chain:

        assert task.period % offsetGranularity == 0

        prod = prod * int(task.period / offsetGranularity)

    hp = hyperperiod(chain) / offsetGranularity

    combinations = int(int(prod) / int(hp))

    ### Make sure both versions result in the same number of combinations to check ###
    assert combinations == combinationsIndividual, chainString(chain) + "\nCombinations: " + str(combinations) + " Combinations Individual: " + str(combinationsIndividual)

    return combinations 

if __name__ == "__main__":
    """ Debugging """
    os.system('cls' if os.name == 'nt' else 'clear')    # Clear the terminal

    task1 = Task('Task1', useconds(1), mseconds(1000), mseconds(1000), 0)
    task2 = Task('Task2', useconds(1), mseconds(200), mseconds(200), 0)
    task3 = Task('Task3', useconds(1), mseconds(10), mseconds(10), 0)
    task4 = Task('Task1', useconds(1), mseconds(1000), mseconds(1000), 0)
    task5 = Task('Task1', useconds(1), mseconds(50), mseconds(50), 0)
    task6 = Task('Task1', useconds(1), mseconds(1), mseconds(1), 0)
    task7 = Task('Task1', useconds(1), mseconds(100), mseconds(100), 0)
    task8 = Task('Task1', useconds(1), mseconds(1000), mseconds(1000), 0)
    task9 = Task('Task1', useconds(1), mseconds(100), mseconds(100), 0)
    task10 = Task('Task1', useconds(1), mseconds(1000), mseconds(1000), 0)
    task11 = Task('Task1', useconds(1), mseconds(200), mseconds(200), 0)

    chain = [task1, task2, task3, task4, task5, task6, task7, task8, task9, task10, task11]

    assignments = offsetAssignmentHeuristic(chain, mseconds(1))

    print(str(assignments) + " offset assignments to check")