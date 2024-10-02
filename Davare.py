from Time import *
from Task import *

def davareBound(chain):

    bound = 0

    for task in chain:
        bound = bound + (2 * task.period)

    return bound