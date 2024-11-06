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

if __name__ == "__main__":
    """ Debugging """
    os.system('cls' if os.name == 'nt' else 'clear')    # Clear the terminal
