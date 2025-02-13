##################################################################################
# Optimal task phasing for single chains.
#
# - Optimal task phasing to minimize end-to-end latency for max-harmonic 
#   and semi-harmonic automotive periods
# - Computation of end-to-end latency bound under phasing
# 
# Author: Matthias Becker
##################################################################################
from Time import *
from Task import *
import os
from DPT_Offset import *

def optimalPhasingMaxHarm(chain):
    """ Function assigns optimal task phases to minimize end-to-end latency 
        and returns the end-to-end latency bound. Theorem 10. 
    """
    
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

def optimalPhasingSemiHarm(chain):
    """ Function assigns optimal task phasing for semi harmonic automotive periods 
        to minimize the end-to-end latency and returns the latency bound. 
    """

    max1Period = getMaxPeriod(chain)    # Get the largest task period
    max2Period = getMax2Period(chain)   # Get the secod largest period

    if is2kMaxHarmonic(chain) == False:
    #if not((max1Period == mseconds(5) and max2Period == mseconds(2)) or (max1Period == mseconds(50) and max2Period == mseconds(20))):
        print("max1Period: " + printTime(max1Period))
        print("max2Period: " + printTime(max2Period))

    assert is2kMaxHarmonic(chain)
  #  assert (max1Period == mseconds(5) and max2Period == mseconds(2)) or (max1Period == mseconds(50) and max2Period == mseconds(20)) # Make sure the chain has semi harmonic automotive periods!
    
    # Compute tasks where periods switch between max1 and max2
    nu = getPeriodSwitches(chain) 

    gamma = max1Period % max2Period

    tau_p = getFirstOccurance(chain, max1Period)

    # Set task phases to be optimal 
    if math.ceil(len(nu) / 2) * gamma >= max1Period:
        """ Phasing according to Eq. 46, 47 """
        offset = 0

        for task in chain:
            task.offset = offset

            offset = offset + task.period
    else:
        """ Phasing according to Eq. 48, 49 """
        offset = 0

        for task in chain:
            task.offset = offset
            
            if (task.period == max1Period) and (task != tau_p) and (task in nu):
                task.offset = task.offset + gamma
                offset = offset + gamma
                
            offset = offset + task.period
    
    # Compute the latency bound (Eq. 34)

    # Compute the sum of all periods
    periodSum = 0
    for task in chain:
        periodSum = periodSum + task.period

    latencyBound = periodSum + max1Period + min(max1Period, math.ceil(len(nu) / 2) * gamma)

    return latencyBound

def getFirstOccurance(chain, period):
    """ Return the task with T == period that has the lowest index in the chain (i.e. the first occurance). """

    for task in chain:
        if task.period == period:
            return task

def getPeriodSwitches(chain):
    """ Function returns the tasks that appear after a switch between T^E_{max,1} and T^E_{max,2}."""
    nu = []

    max1Period = getMaxPeriod(chain)    # Get the largest task period
    max2Period = getMax2Period(chain)   # Get the secod largest period

    # Compute how often periods switch between max1 and max2

    lastFound = 0
    for task in chain:
        if task.period == max1Period:
            if lastFound == max2Period:
                nu.append(task)
            lastFound = max1Period

        if task.period == max2Period:
            if lastFound == max1Period:
                nu.append(task)
            lastFound = max2Period

    return nu

if __name__ == '__main__':
    """ Debugging """
    os.system('cls' if os.name == 'nt' else 'clear')    # Clear the terminal

    # # Example Fig. 2b
    # print("=====================================================================================")
    # print("Example: Max-Harmonic (Fig. 2b)")
    # task1 = Task('Task1', useconds(1), mseconds(10), mseconds(10), 0)
    # task2 = Task('Task2', useconds(1), mseconds(1), mseconds(1), 0)
    # task3 = Task('Task3', useconds(1), mseconds(10), mseconds(10), 0)

    # chain = [task1, task2, task3]

    # latencyBound = optimalPhasingMaxHarm(chain)

    # print("Max Data Age = %s" % (printTime(latencyBound)))

    # assert latencyBound == mseconds(31) # Check that the result is correct
    
    # # Example Fig. 4b
    # print("\n=====================================================================================")
    # print("Example: Semi Harminic Automotive (Fig. 4b)")
    # task1 = Task('Task1', useconds(1), mseconds(5), mseconds(5), 0)
    # task2 = Task('Task2', useconds(1), mseconds(1), mseconds(1), 0)
    # task3 = Task('Task3', useconds(1), mseconds(2), mseconds(2), 0)
    # task4 = Task('Task4', useconds(1), mseconds(1), mseconds(1), 0)

    # chain = [task1, task2, task3, task4]

    # latencyBound = optimalPhasingSemiHarm(chain)

    # print("Max Data Age = %s" % (printTime(latencyBound)))

    # assert latencyBound == mseconds(15) # Check that the result is correct

    # print("\n=====================================================================================")
    # task1 = Task('Task1', useconds(1), mseconds(20), mseconds(20), 0)
    # task2 = Task('Task2', useconds(1), mseconds(50), mseconds(50), 0)
    # task3 = Task('Task3', useconds(1), mseconds(5), mseconds(5), 0)
    # task4 = Task('Task4', useconds(1), mseconds(20), mseconds(20), 0)

    # chain = [task1, task2, task3, task4]

    # print(chainString(chain))

    # latencyBound = optimalPhasingSemiHarm(chain)

    # assert latencyBound == mseconds(155) # Check that the result is correct

    # print("Max Data Age = %s" % (printTime(latencyBound)))

    # # Test Chain
    # print("\n=====================================================================================")
    # #To Check 50000 -> 20000 -> 1000 -> 50000 -> 50000 -> 1000 Optimal Phasing Latency: 2.32 Offset Latency: 2.72
    # task1 = Task('Task1', useconds(1), mseconds(50), mseconds(50), 0)
    # task2 = Task('Task2', useconds(1), mseconds(20), mseconds(20), 0)
    # task3 = Task('Task3', useconds(1), mseconds(1), mseconds(1), 0)
    # task4 = Task('Task4', useconds(1), mseconds(50), mseconds(50), 0)
    # task5 = Task('Task4', useconds(1), mseconds(50), mseconds(50), 0)
    # task6 = Task('Task4', useconds(1), mseconds(1), mseconds(1), 0)

    # chain = [task1, task2, task3, task4, task5, task6]

    # print(chainString(chain))
    
    # latencyBound = optimalPhasingSemiHarm(chain)

    # print("Offset:")
    # prev = 0
    # for task in chain:
    #     print(printTime(task.offset) + " delta: " + printTime(task.offset - prev))
    #     prev = task.offset

    # print("\nLatency Bound: " + printTime(latencyBound))

    # dptOffset = DPT(chain)
    # dptOffset.getDpt()
    # offsetLatency = dptOffset.maxAge

    # print("Exact Analysis: " + printTime(offsetLatency))

    print("\n=====================================================================================")
    task1 = Task('Task1', useconds(1), mseconds(18), mseconds(18), 0)
    task2 = Task('Task2', useconds(1), mseconds(4), mseconds(4), 0)
    task3 = Task('Task3', useconds(1), mseconds(4), mseconds(4), 0)
    task4 = Task('Task4', useconds(1), mseconds(3), mseconds(3), 0)


    chain = [task1, task2, task3, task4 ]

    if is2kMaxHarmonic(chain) is not True:
        print(":NOT MAX-HARMONIC!")

    latencyBound = optimalPhasingSemiHarm(chain)
    print("\nLatency Bound: " + printTime(latencyBound))

    dpt = DPT(chain)
    dpt.getDpt()
    print("\nLatency Bound: " + printTime(dpt.maxAge))

    prev = 0
    for task in chain:
        print(printTime(task.offset) + " delta: " + printTime(task.offset - prev))
        prev = task.offset

    assert latencyBound == dpt.maxAge