from Time import *
from Task import Task
from DPT_Offset import *
from OptimalPhasing import *
import random
from timeit import default_timer as timer
import os

def experimentMaxHarmonic(seed):
    print("Experiment: Max. Harmonic Chains")

    basePath = "output/expMaxHarmonic"
    os.makedirs(basePath, exist_ok=True)    # Create output folder if it does not exist

    

    expCount = 10  # Number of experiments for each configuration and data point

    minChainLength = 2      # Minimum length of generated chains
    maxChainLength = 10     # Maximum length of generated chains
    stepChainLength = 1     # Step between two examined chain length

    for length in range(minChainLength, maxChainLength+1, stepChainLength): # Each chain length
        print("Chain Length: ", length)

        random.seed(seed)   # For reproducability we use the seed here for each chain length

        existingResults = 0

        filePath = basePath + '/length_' + str(length) + '.csv'
        if os.path.isfile(filePath) is True:
            existingResults = sum(1 for _ in open(filePath))    # Get the number of results that alredy exist

        with open(filePath, "a") as file:
            for i in range(1, expCount+1):                                        # Each experiment for the chain length

                # Generate a random chain of the given length with max harmonic periods. This is always needed for reproducable results!
                maxHarmonic = False
                while maxHarmonic is False:
                    chain = generateRandomTasks(length, 0.5)    # Utilization does not matter since we focus on LET
                    maxHarmonic = isMaxHarmonic(chain)          # Only keep max harmoic chains

                if i > existingResults: # Only run the analysis if results don't exist yet
                    # DPT analysis 
                    startDpt = timer()
                    dpt = DPT(chain)
                    dpt.getDpt()
                    synchronousLatency = dpt.maxAge
                    durDpt = timer() - startDpt

                    # Optimal Phasing
                    startOpt = timer()
                    optPhasingLatency = optimalPhasing(chain)
                    durOpt = timer() - startOpt

                    # DPT analysis with phasing 
                    startDptOffset = timer()
                    dptOffset = DPT(chain)
                    dptOffset.getDpt()
                    offsetLatency = dptOffset.maxAge
                    durDptOffset = timer() - startDptOffset

                    assert optPhasingLatency <= synchronousLatency

                    file.write(str(i) + ',' + str(synchronousLatency) + ',' + "{:.6f}".format(durDpt) 
                            + ',' + str(optPhasingLatency) + ',' + "{:.6f}".format(durOpt)
                            + ',' + str(offsetLatency) + ',' + "{:.6f}".format(durDptOffset) + '\n')
            file.close()
                


def main():

    experimentMaxHarmonic(123)

if __name__ == "__main__":
    main()