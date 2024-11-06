##################################################################################
# Implementation of the latency analysis of LET cause-effect chains with offset
# of Martinez et al. 
#
# J. Martinez, I. Sañudo and M. Bertogna, "Analytical Characterization of End-to-End 
# Communication Delays With Logical Execution Time," in IEEE Transactions on Computer-Aided 
# Design of Integrated Circuits and Systems, vol. 37, no. 11, pp. 2244-2254, 2018.
# 
# Author: Matthias Becker
##################################################################################
from Time import *
from Task import *
from Comparison import davareBound
from DPT_Offset import DPT
from OptimalPhasing import optimalPhasingSemiHarm
import networkx as nx
import math
import os

def calculateLatencyMartinezTCAD18(chain):

    # Compute all reading points corresponsing to the communication of 
    # \tau_n and \tau_n-1 within one hyperperiod
    # Make sure the start of the basic path is > 0
    last = chain[len(chain)-1]
    secondLast = chain[len(chain)-2]
    worstCaseLatency = davareBound(chain)
    hp = hyperperiod(chain)

    maxOffset = 0
    for task in chain:
        if task.offset > maxOffset:
            maxOffset = task.offset

    readingPoints = []
    rp_n = []
    tmpRp = 0
    n = 0
    while tmpRp < worstCaseLatency + hp + maxOffset:
        tmpRp = getReadingPoint(secondLast, last, n)
        n = n + 1
        if  worstCaseLatency + maxOffset <= tmpRp < worstCaseLatency + hp + maxOffset:
            readingPoints.append(tmpRp)
            rp_n.append(n-1)

    # Calculate the corresponding start of the basic path using Algorithm 1
    initialPublishingPoints = []
    n = 0
    for rp in readingPoints:
        #print("Reading Point to explore: x_" + str(len(chain)) + " = " + str(n) + " at time: " + printTime(rp))
        initialPublishingPoints.append(calcStartOfBP(chain, rp))
        n += 1

    # All basic paths are identified. For basic paths with the same initial publishing point, only
    # the oldest reading point at the end of the chain needs to be considered further.
    latency = []
    for i in range(len(readingPoints)-1, -1, -1):
        if i == len(readingPoints) - 1 or readingPoints[i] != readingPoints[i-1]:   # Filter out basic paths we don't need to consider
            nextRp = getReadingPoint(secondLast, last, rp_n[i] + 1) # get the next reading point at the end of the chain
            #print("Basic Path: PP = " + printTime(initialPublishingPoints[i]) + " RP = " + printTime(readingPoints[i]) + " next RP = " + printTime(nextRp))
            latency.append(getBasicPathEtoE(chain, initialPublishingPoints[i],readingPoints[i], nextRp))

    maxLatency = max(latency)

    return maxLatency

def calcStartOfBP(chain, rp):
    """ Algorithm 1 """

    # Line 1: Find n such that Q^{x_n}_{n-1, n} = rp
    last = chain[len(chain)-1]  # get n
    secondLast = chain[len(chain)-2] # get n-1

    n = 0
    while getReadingPoint(secondLast, last, n) < rp:
        n = n + 1

    # Line 2: Compute P^{x_n}_{n-1, n}
    pp = getPublishingPoint(secondLast, last, n)    # P^{x_n}_{n-1, n}
    #print("\tPublishing Point: x_" + str(len(chain)) + " = " + str(n) + " at time: " + printTime(pp))
    
    # Lines 4-6: 
    for i in range(len(chain), 2, -1):
        writer = chain[i-3] # get i-2
        reader = chain[i-2] # get i-1

        # Find the largest Q^{x_i-1}_{i-2, i-1} < Q^{x_i}_{i-1, i}
        tmp_n = 0
        while getReadingPoint(writer, reader, tmp_n) < pp:
            #print("\tReading Point: x_" + str(i-1) + " = " + str(tmp_n) + " at time: " + printTime(getReadingPoint(writer, reader, tmp_n)) + " < " + printTime(pp))
            tmp_n = tmp_n + 1
        
        tmp_n = tmp_n - 1
        #print("\tReading Point: x_" + str(i-1) + " = " + str(tmp_n) + " at time: " + printTime(getReadingPoint(writer, reader, tmp_n)))
        pp = getPublishingPoint(writer, reader, tmp_n)
        #print("\tPublishing Point: x_" + str(i-1) + " = " + str(tmp_n) + " at time: " + printTime(pp))
    return pp

def getBasicPathEtoE(chain, publishingPoint, readingPoint, nextReadingPoint):
    """ Equation 5"""
    
    # Length of the basic path
    theta = readingPoint - publishingPoint 

    # Equation 5
    latency = chain[0].period + theta + nextReadingPoint - readingPoint
    
    # In addition to Equation 5 we add the period of the last task in the chain to mark when the data is overwritten by the next basic path
    latency = latency  + chain[len(chain)-1].period 

    return latency

def getReadingPoint(wTask, rTask, n):
    """ Equation 4 """

    rp = rTask.offset + math.ceil((n * max(rTask.period, wTask.period) + max(rTask.offset, wTask.offset) - rTask.offset) / rTask.period) * rTask.period

    return rp

def getPublishingPoint(wTask, rTask, n):
    """ Equation 3 """

    pp = wTask.offset + math.floor((n * max(rTask.period, wTask.period) + max(rTask.offset, wTask.offset) - wTask.offset) / wTask.period) * wTask.period

    return pp

def combinationsHeuristic(chain, offsetGranularity):
    """ This function computes the number of latency computations required to find the optimal 
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
    # Commented out since very large chains get rounidng errors?! 
    #assert combinations == combinationsIndividual, chainString(chain) + "\nCombinations: " + str(combinations) + " Combinations Individual: " + str(combinationsIndividual)

    return combinationsIndividual 

class OffsetNode:
    """ This is a helper class we use as vertex in the tree to represent all offset combinations. """
    def __init__(self, task_id, offset):
        self.task_id = task_id
        self.offset = offset

def heuristicOptimalPhasing(chain, offsetGranularity):
    """ Implements Algorithm 2 to identify the optimal phasing, considering the complete depth of the chain. 
        This is implemented by building a tree where each level represents a task in the chain (starting from task 0) and a distinct offset assignment.
        We then have to check the latency for each path from the root node to leafe nodes. 
        Once an end node is reached, the latency of the chain is analyzed. The smallest latency and related leafe node is returned. That way we can then
        reconstruct the offset assignment without the need to search the tree again. """

    for task in chain:
        assert task.period % offsetGranularity == 0

    graph = nx.DiGraph()
    
    rootCase = OffsetNode(0,0)
    graph.add_node(rootCase)            # task 0 has always offset 0
    prevLcm = int(chain[0].period / offsetGranularity)

    ret = createCombinationsRec(chain, 1, prevLcm, graph, rootCase, offsetGranularity)    # recursively create all possible combinations 

    # Now we have to assign the offsets to the task according to the smallest latency value that was found.
    node = ret[1]    # Get the leafe node associated with the smallest latency

    while True:
        chain[node.task_id].offset = node.offset * offsetGranularity
        assert graph.in_degree(node) <= 1

        if graph.in_degree(node) == 1:
            inputEdges = graph.in_edges(node)
            for u, v in inputEdges: #
                node = u
        else:
            break
    return ret[0]

def createCombinationsRec(chain, pos, prevLcm, graph, node, offsetGranularity):
    """ Recursively explore all non-equivalent period combinations. """

    if pos >= len(chain):
        # Analyze offsets if we reached the end of the chain.
        maxLatency = calculateLatencyMartinezTCAD18(chain)
        #print("Analysing: " + chainString(chain) + " => Latency = " + printTime(maxLatency))
        
        return [maxLatency, node]    # return the latency but also the final node, so we can reconstruct the offsets at the end
    
    period = int(chain[pos].period / offsetGranularity)

    rangeBound = math.gcd(period, prevLcm)

    prevLcm = math.lcm(period, prevLcm) # compute the LCM of all previous periods for the next depth

    bestOffset = None
    for offset in range(0, rangeBound):
        #print("Pos: " + str(pos) + " Range Bound: " + str(rangeBound))
        newNode = OffsetNode(pos, offset)
        chain[pos].offset = offset * offsetGranularity  # Set the offset also for the task in the chain
        graph.add_node(newNode)
        graph.add_edge(node, newNode)

        ret = createCombinationsRec(chain, pos+1, prevLcm, graph, newNode, offsetGranularity)
        
        if bestOffset is None:
            bestOffset = ret
        else:
            if bestOffset[0] > ret[0]:
                bestOffset = ret

    return bestOffset
            
if __name__ == '__main__':
    """ Debugging """
    os.system('cls' if os.name == 'nt' else 'clear')    # Clear the terminal

    # Example Fig. 12 in the paper
    task1 = Task('Task1', useconds(1), mseconds(3), mseconds(3), 0)
    task2 = Task('Task2', useconds(1), mseconds(7), mseconds(7), 0)
    task3 = Task('Task3', useconds(1), mseconds(3), mseconds(3), 0)

    chain = [task1, task2, task3]

    latency = calculateLatencyMartinezTCAD18(chain)

    print("Latency: " + str(latency))

    dpt = DPT(chain)
    dpt.getDpt()

    assert latency == dpt.maxAge, printTime(latency) + " vs. " + printTime(dpt.maxAge)

    # Case Study - Harmonic
    print("\n=====================================================================================")
    task1 = Task('Task1', useconds(1), mseconds(10), mseconds(10), 0)
    task2 = Task('Task2', useconds(1), mseconds(50), mseconds(50), 0)
    task3 = Task('Task3', useconds(1), mseconds(10), mseconds(10), 0)
    task4 = Task('Task1', useconds(1), mseconds(50), mseconds(50), 0)
    chain = [task1, task2, task3, task4]

    combinations = combinationsHeuristic(chain, mseconds(1))

    print("Case Study: " + str(combinations) + " are checked with the heuristic.")

    # Case Study - Semi-Harmonic Automotive
    print("\n=====================================================================================")
    task1 = Task('Task1', useconds(1), mseconds(20), mseconds(20), 0)
    task2 = Task('Task2', useconds(1), mseconds(50), mseconds(50), 0)
    task3 = Task('Task3', useconds(1), mseconds(20), mseconds(20), 0)
    task4 = Task('Task1', useconds(1), mseconds(50), mseconds(50), 0)
    chain = [task1, task2, task3, task4]

    combinations = combinationsHeuristic(chain, mseconds(1))


    print("Case Study: " + str(combinations) + " are checked with the heuristic.")

    heur = heuristicOptimalPhasing(chain, mseconds(1))
    
    print("Heuristic: " + chainString(chain) + " => Latency = " + printTime(heur))

    dpt = DPT(chain)
    dpt.getDpt()
    print("Exact Analysis : " + chainString(chain) + " => Latency = " + printTime(dpt.maxAge))

    task1 = Task('Task1', useconds(1), mseconds(20), mseconds(20), 0)
    task2 = Task('Task2', useconds(1), mseconds(50), mseconds(50), 0)
    task3 = Task('Task3', useconds(1), mseconds(20), mseconds(20), 0)
    task4 = Task('Task1', useconds(1), mseconds(50), mseconds(50), 0)
    opt = optimalPhasingSemiHarm(chain)

    print("Optimal Latency = " + printTime(opt))

    print("Martinez Latency = " + printTime(calculateLatencyMartinezTCAD18(chain)))

    print("Ours Optimal: " + chainString(chain) + " => Latency = " + printTime(opt))
    assert heur == opt
    # Example
    print("\n=====================================================================================")

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

    assignments = combinationsHeuristic(chain, mseconds(1))

    print(str(assignments) + " offset assignments to check")

    print("\n=====================================================================================")

    # Example Fig. 12 in the paper
    task1 = Task('Task1', useconds(1), mseconds(10), mseconds(10), 0)
    task2 = Task('Task2', useconds(1), mseconds(5), mseconds(5), 0)

    chain = [task1, task2]

    latency = calculateLatencyMartinezTCAD18(chain)

    print("Latency before offset heuristic: " + str(latency))

    heuristicOptimalPhasing(chain, mseconds(1))

    task1 = Task('Task1', useconds(1), mseconds(10), mseconds(10), 0)
    task2 = Task('Task2', useconds(1), mseconds(5), mseconds(5), mseconds(10))

    chain = [task1, task2]

    dpt = DPT(chain)
    dpt.getDpt()

    assert latency == dpt.maxAge, printTime(latency) + " vs. " + printTime(dpt.maxAge)