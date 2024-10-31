from Time import *
from Task import hyperperiod
from DPT_Offset import *
from OptimalPhasing import *
from Comparison import *
from plotting import *
import random
from timeit import default_timer as timer
import os

def experiments(seed, onlyMaxHarmonic):
    """
    This function executes the experiments with cause-effect chains that have automotive periods. 
    The chain length is varied from minChainLength to maxChainLength, and for each setting expCount random chains are examined.
    """

    if onlyMaxHarmonic:
        print("Experiment: Max. Harmonic Chains")
        
        # Paths to write files to
        basePath = "output/expMaxHarmonic"      # Experiment data is stored here
        dstPath = "plots/maxHarmonic"           # Final plots are stored here
    else:
        print("Experiment: Semi Harmonic Chains")

        # Paths to write files to
        basePath = "output/expSemiHarmonic"     # Experiment data is stored here
        dstPath = "plots/semiHarmonic"          # Final plots are stored here
    
    # Experiment Configuration
    expCount = 50                               # Number of experiments for each configuration and data point
    minChainLength = 2                          # Minimum length of generated chains
    maxChainLength = 10                         # Maximum length of generated chains
    stepChainLength = 1                         # Step between two examined chain length

    # Configuration for the crude progress bar (no need to change, only visual effect. No effect on experiment itself)
    progressDotsMax = 50                    # Config for the length of the crude progress bar
    expPerDot = math.floor(expCount / progressDotsMax)

    os.makedirs(basePath, exist_ok=True)    # Create output folder if it does not exist

    for length in range(minChainLength, maxChainLength+1, stepChainLength): # Each chain length
        print("Chain Length: ", "%02d" % (length,), end =" ", flush=True)

        random.seed(seed)   # For reproducability we use the seed here for each chain length

        existingResults = 0

        # In case the previous experiment was stopped, check how many systems have been processed and contiue from there
        filePath = basePath + '/length_' + str(length) + '.csv'
        if os.path.isfile(filePath) is True:
            existingResults = sum(1 for _ in open(filePath))    # Get the number of results that alredy exist

        with open(filePath, "a") as file:

            bestRatio = 1000000
            worstRatio = 0

            for i in range(1, expCount+1):                      # Each experiment for the chain length

                if i % expPerDot == 0:                          # This is only to plot some crude progress bar
                    print(".", end =" ", flush=True)

                # Generate a random chain of the given length with max harmonic periods. This is always needed for reproducable results!
                if onlyMaxHarmonic == True:
                    maxHarmonic = False
                    while maxHarmonic is False:
                        chain = generateRandomTasks(length, 0.5)    # Utilization does not matter since we focus on LET
                        maxHarmonic = isMaxHarmonic(chain)          # Only keep max harmoic chains
                else:
                    chain = generateRandomTasks(length, 0.5)    # Utilization does not matter since we focus on LET
                    maxHarmonic = isMaxHarmonic(chain)

                hp = hyperperiod(chain)

                if i > existingResults:                         # Only run the analysis if results don't exist yet
                    #############################
                    # DPT analysis 
                    #############################
                    startDpt = timer()
                    dpt = DPT(chain)
                    dpt.getDpt()
                    synchronousLatency = dpt.maxAge / hp
                    durDpt = timer() - startDpt

                    #############################
                    # Optimal Phasing
                    #############################
                    if maxHarmonic:
                        startOpt = timer()
                        optPhasingLatency = optimalPhasingMaxHarm(chain) / hp
                        durOpt = timer() - startOpt
                    else:
                        startOpt = timer()
                        optPhasingLatency = optimalPhasingSemiHarm(chain) / hp
                        durOpt = timer() - startOpt

                    #############################
                    # DPT analysis with phasing 
                    #############################
                    startDptOffset = timer()
                    dptOffset = DPT(chain)
                    dptOffset.getDpt()
                    offsetLatency = dptOffset.maxAge / hp
                    durDptOffset = timer() - startDptOffset

                    #############################
                    # Davare bound, i.e. worst-case phasing
                    #############################
                    startDavare = timer()
                    davareLatency = davareBound(chain) / hp
                    durDavare = timer() - startDavare

                    #############################
                    # Random phasing between tasks
                    #############################
                    startRandomPhasing = timer()
                    randomPhasing(chain, seed)
                    rndPhasingDpt = DPT(chain)
                    rndPhasingDpt.getDpt()
                    rndPhasingLatency = rndPhasingDpt.maxAge / hp
                    durRandomPhasing = timer() - startRandomPhasing

                    #############################
                    # Offset Heuristic
                    numAssignments = offsetAssignmentHeuristic(chain, mseconds(1))
                    #############################

                    # Make sure the optimal phasing is always smaller or equal than the synchronous release
                    assert optPhasingLatency <= synchronousLatency, chainString(chain) + " Optimal Phasing Latency: " + str(optPhasingLatency) + " Synchronous Latency: " + str(synchronousLatency)

                    # Make sure the optimal phasing is always smaller or equal than the random phasing
                    assert optPhasingLatency <= rndPhasingLatency, chainString(chain) + " Optimal Phasing Latency: " + str(optPhasingLatency) + " Random Phasing Latency: " + str(rndPhasingLatency)

                    # Make sure that the latency we compute with the proposed phasing is always equal to the exact analysis
                    assert optPhasingLatency == offsetLatency, chainString(chain) + " Optimal Phasing Latency: " + str(optPhasingLatency) + " Offset Latency: " + str(offsetLatency)

                    ratio = optPhasingLatency / synchronousLatency 
                    if ratio < bestRatio:
                        bestRatio = ratio

                    if ratio > worstRatio:
                        worstRatio = ratio

                    file.write(str(i) + ',' + "{:.6f}".format(synchronousLatency) + ',' + "{:.6f}".format(durDpt) + ',' 
                               + "{:.6f}".format(optPhasingLatency) + ',' + "{:.6f}".format(durOpt) + ',' 
                               + "{:.6f}".format(offsetLatency) + ',' + "{:.6f}".format(durDptOffset) + ',' 
                               + "{:.6f}".format(davareLatency) + ',' + "{:.6f}".format(durDavare) + ',' 
                               + "{:.6f}".format(rndPhasingLatency) + ',' + "{:.6f}".format(durRandomPhasing) + ','
                               + str(numAssignments) + ',' + str(maxHarmonic) + '\n')
                    
            file.close()
            print(" -> Best: " + "{:.4f}".format(bestRatio) + " Worst: " + "{:.4f}".format(worstRatio))

    os.makedirs(dstPath, exist_ok=True)    # Create plots folder if it does not exist   
    plot(basePath, dstPath, minChainLength, maxChainLength, stepChainLength)

def main():

    onlyMaxHarmonic = False  # Set this flag to false to keep also chains that are not max-harmonic
    experiments(123, onlyMaxHarmonic)

if __name__ == "__main__":
    main()