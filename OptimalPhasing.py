##################################################################################
# Optimal task phasing for single chains.
#
# - Optimal task phasing to minimize end-to-end latency
# - Computation of end-to-end latency bound under phasing
# 
# Author: Matthias Becker
##################################################################################
from Time import *
from Task import *
import os

def optimalPhasing(chain):
    """ Function assigns optimal task phases to minimize end-to-end latency 
        and returns the end-to-end latency bound. Theorem 10. """
    
    # Set task phases to be optimal (Definition 9)
    offset = 0

    for task in chain:
        task.offset = offset
        offset = offset + task.period

    # Compute the latency bound (Theorem 10)
    maxPeriod = getMaxPeriod(chain) # Get the largest task period

    periodSum = 0
    for task in chain:
        periodSum = periodSum + task.period

    latencyBound = periodSum + maxPeriod

    return latencyBound

if __name__ == '__main__':
    """ Debugging """
    os.system('cls' if os.name == 'nt' else 'clear')    # Clear the terminal

    # Example Fig. 2b
    task1 = Task('Task1', useconds(1), mseconds(10), mseconds(10), 0)
    task2 = Task('Task2', useconds(1), mseconds(1), mseconds(1), 0)
    task3 = Task('Task3', useconds(1), mseconds(10), mseconds(10), mseconds(1))

    chain = [task1, task2, task3]

    latencyBound = optimalPhasing(chain)

    print("Max Data Age = %s" % (printTime(latencyBound)))