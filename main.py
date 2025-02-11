from Time import *
from Task import hyperperiod
from DPT_Offset import *
from OptimalPhasing import *
from Comparison import *
from MartinezTCAD18 import *
from plotting import *
import random
from timeit import default_timer as timer
from datetime import datetime
import os
import shutil
import psutil
import argparse
from multiprocessing import Pool, Manager
import threading

def runConfiguration(seed, length, basePath, expCount, onlyMaxHarmonic, runHeuristic, timeout, expPerDot, q, automotivePeriods, k, numPeriods):
    """ This is executed as thread and handles all experiments for one chain length. 
        Output is written to a dedicated CSV-file, and update information is sent to the logger thread.
    """
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
                q.put([length, "."])

            # Generate a random chain of the given length with max harmonic periods. This is always needed for reproducable results!
            if onlyMaxHarmonic == True:
                maxHarmonic = False
                while maxHarmonic is False:
                    if automotivePeriods == True:
                        chain = generateRandomTasks(length, 0.5)        # Utilization does not matter since we focus on LET
                    else:
                        chain = generateRandomTasks2kMax(length, 0.5, k, numPeriods, 200)  # Utilization does not matter since we focus on LET

                    maxHarmonic = isMaxHarmonic(chain)          # Only keep max harmoic chains
            else:
                if automotivePeriods == True:
                    chain = generateRandomTasks(length, 0.5)        # Utilization does not matter since we focus on LET
                else:
                    chain = generateRandomTasks2kMax(length, 0.5, k, numPeriods, 200)  # Utilization does not matter since we focus on LET
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
                # Martinez TCAD'18 
                #############################
                startMartinez = timer()
                martinezLatency = calculateLatencyMartinezTCAD18(chain) / hp
                durMartinez = timer() - startMartinez

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
                # Combinations Offset Heuristic
                #############################
                numAssignments = combinationsHeuristic(chain, getMaxDeltaHeuristic(chain))
                    
                #############################
                # Offset Heuristic Martinez et al.
                #############################
                if runHeuristic:
                    startOffsetHeuristic = timer()
                    if timeout > 0:
                        heuristicLatency = heuristicOptimalPhasingTimeout(chain, mseconds(1), timeout)
                        if heuristicLatency > 0:    # -1 is returned in case of a timeout
                            heuristicLatency = heuristicLatency / hp
                    else:
                        heuristicLatency = heuristicOptimalPhasing(chain, mseconds(1)) / hp
                    durOffsetHeuristic = timer() - startOffsetHeuristic
                else:
                    heuristicLatency = -1
                    durOffsetHeuristic = -1

                # Make sure the optimal phasing is always smaller or equal than the synchronous release
                assert optPhasingLatency <= synchronousLatency, chainString(chain) + " Optimal Phasing Latency: " + printTime(optPhasingLatency) + " Synchronous Latency: " + printTime(synchronousLatency)

                # Make sure the optimal phasing is always smaller or equal than the random phasing
                assert optPhasingLatency <= rndPhasingLatency, chainString(chain) + " Optimal Phasing Latency: " + printTime(optPhasingLatency) + " Random Phasing Latency: " + printTime(rndPhasingLatency)

                # Make sure the latency by Martinez TCAD'18 is the same as Becker JSA'17
                assert martinezLatency == offsetLatency, "Latency Martinez TCAD'18: " + printTime(martinezLatency) + " Latency Becker JSA'17: " + printTime(offsetLatency) + " Chain: " + chainString(chain)

                # Make sure that the latency we compute with the proposed phasing is always equal to the exact analysis
                assert optPhasingLatency == offsetLatency, chainString(chain) + " Optimal Phasing Latency: " + printTime(optPhasingLatency) + " Offset Latency: " + printTime(offsetLatency)

                # Make sure that the offset heuristic latency is the same as our optimal latency
                #assert optPhasingLatency == heuristicLatency, chainString(chain) + " Optimal Phasing Latency: " + printTime(optPhasingLatency) + " Offset Heuristic Latency: " + printTime(heuristicLatency)

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
                           + "{:.6f}".format(martinezLatency) + ',' + "{:.6f}".format(durMartinez) + ','
                           + "{:.6f}".format(heuristicLatency) + ',' + "{:.6f}".format(durOffsetHeuristic) + ','
                           + str(numAssignments) + ',' + str(maxHarmonic) + '\n')
                    
        file.close()
        q.put([length, " -> Best: " + "{:.4f}".format(bestRatio) + " Worst: " + "{:.4f}".format(worstRatio)])

def logger_thread(q, start, stop, step):
    """ This is the logger thread that collects the update information from each experiment thread to 
        print a rudimentary bargraph of the experiment status.
    """
    data = []
    index = []
    i = 0

    for length in range(start, stop + 1, step):
        index.append(length)
        data.append("Chain Length: %02d" % (length,))


    while True:
        record = q.get()
        if record is None:
            break

        length = record[0]
        appendString = record[1]

        # Find the entry
        i = 0
        for entry in index:
            if entry == length:
                data[i] = data[i] + appendString
            i = i + 1
        os.system('cls' if os.name == 'nt' else 'clear')    # Clear the terminal
        for row in data:
            print(row)

    stepChainLength = 2                         # Step between two examined chain length
    
def experiments(destinationFolder, seed, onlyMaxHarmonic, runHeuristic, timeout, expCount, minChainLength, maxChainLength, stepChainLength, numCpu, automotivePeriods, k, numPeriods):
    """
    This function executes the experiments with cause-effect chains that have automotive periods. 
    The chain length is varied from minChainLength to maxChainLength, and for each setting expCount random chains are examined.
    A threadpool is used the size of the physical CPUs - 1. Each chain length is dispatched to a thread.
    """
    expStart = datetime.now()
    print("Start at:", expStart.strftime("%d/%m/%Y %H:%M:%S"))

    # if onlyMaxHarmonic:
    #     print("Experiment: Max. Harmonic Chains")
        
    #     # Paths to write files to
    #     basePath = "output/expMaxHarmonic"      # Experiment data is stored here
    #     dstPath = "plots/maxHarmonic"           # Final plots are stored here
    # else:
    #     print("Experiment: Semi Harmonic Chains")

    #     # Paths to write files to
    #     basePath = "output/expSemiHarmonic"     # Experiment data is stored here
    #     dstPath = "plots/semiHarmonic"          # Final plots are stored here

    outputPath = os.path.join("output", destinationFolder) 
    basePath = os.path.join(outputPath, "data") 
    dstPath = os.path.join(outputPath, "plots") 

    # Configuration for the crude progress bar (no need to change, only visual effect. No effect on experiment itself)
    progressDotsMax = 50                    # Config for the length of the crude progress bar
    expPerDot = math.floor(expCount / progressDotsMax)
    if expPerDot == 0:
        expPerDot = 1   # must be at least 1

    os.makedirs(basePath, exist_ok=True)    # Create output folder if it does not exist

    print("Using thread pool with " + str(numCpu) + " CPUs.")
    pool = Pool(processes=numCpu)    # Create a thread pool

    threadData = []
    m = Manager()
    q = m.Queue()

    for length in range(minChainLength, maxChainLength+1, stepChainLength): # Each chain length
        tmp = (seed, length, basePath, expCount, onlyMaxHarmonic, runHeuristic, timeout, expPerDot, q, automotivePeriods, k, numPeriods)
        threadData.append(tmp)
        #runConfiguration(seed, length, basePath, expCount, onlyMaxHarmonic, runHeuristic)

    
    lp = threading.Thread(target=logger_thread, args=(q,minChainLength, maxChainLength, stepChainLength))
    lp.start()
    result = pool.starmap(runConfiguration, threadData) # Run a thread for each configuration, i.e. chain length. This is blocking!
    q.put(None) # Tell the logging thread to finish

    os.makedirs(dstPath, exist_ok=True)    # Create plots folder if it does not exist   
    plot(basePath, dstPath, minChainLength, maxChainLength, stepChainLength)

    expFinish = datetime.now()
    print("\nFinished at:", expFinish.strftime("%d/%m/%Y %H:%M:%S"))

    expDuration = expFinish - expStart
    print("Duration:", expDuration)

def caseStudy(dstPath):
    """ Run the two configurations of the Autonomous Emergency Braking System (AEBS)
    """
    basePath = os.path.join('output', dstPath)  # Experiment data is stored here
    dstPath = os.path.join('plots', dstPath)    # Final plots are stored here

    # If there exists a folder for the case-study data it is removed here to have consistent results stored
    if os.path.exists(basePath) and os.path.isdir(basePath):
        shutil.rmtree(basePath)

    os.makedirs(basePath)    # Create output folder 

    print("\n=====================================================================================")
    print("= Case-Study with harmonic automotive periods")
    print("=====================================================================================")
    task1 = Task('Task1', useconds(1), mseconds(10), mseconds(10), 0)
    task2 = Task('Task2', useconds(1), mseconds(50), mseconds(50), 0)
    task3 = Task('Task3', useconds(1), mseconds(10), mseconds(10), 0)
    task4 = Task('Task1', useconds(1), mseconds(50), mseconds(50), 0)
    chain = [task1, task2, task3, task4]

    dpt = DPT(chain)
    dpt.getDpt()
    print("Syncronous Release Exact Analysis : " + chainString(chain) + " => Latency = " + printTime(dpt.maxAge))

    combinations = combinationsHeuristic(chain, mseconds(1))

    print("Case Study: " + str(combinations) + " combinations are checked with the heuristic.")

    start = timer()
    heur = heuristicOptimalPhasing(chain, mseconds(1))
    durationHeuristic = timer() - start

    print("Heuristic: " + chainString(chain) + " => Latency = " + printTime(heur) + " in " + str(durationHeuristic * 1000) + " ms")

    dpt = DPT(chain)
    dpt.getDpt()
    print("Exact Analysis : " + chainString(chain) + " => Latency = " + printTime(dpt.maxAge))

    task1 = Task('Task1', useconds(1), mseconds(10), mseconds(10), 0)
    task2 = Task('Task2', useconds(1), mseconds(50), mseconds(50), 0)
    task3 = Task('Task3', useconds(1), mseconds(10), mseconds(10), 0)
    task4 = Task('Task1', useconds(1), mseconds(50), mseconds(50), 0)

    start = timer()
    opt = optimalPhasingMaxHarm(chain)
    durationOptimal = timer() - start

    print("Optimal Latency = " + printTime(opt) + " in " + str(durationOptimal * 1000) + " ms")

    print("\nMartinez Latency = " + printTime(calculateLatencyMartinezTCAD18(chain)))

    print("Ours Optimal: " + chainString(chain) + " => Latency = " + printTime(opt))
    assert heur == opt

    filePath = os.path.join(basePath, 'case_study_harmonic.csv') 
    with open(filePath, "a") as file:
        file.write(str(heur) + "," + "{:.6f}".format(durationHeuristic * 1000) + "," + str(opt) + "," + "{:.6f}".format(durationOptimal * 1000) )
        file.close()

    # Case Study - Semi-Harmonic Automotive
    print("\n=====================================================================================")
    print("= Case-Study with semi-harmonic automotive periods")
    print("=====================================================================================")
    task1 = Task('Task1', useconds(1), mseconds(20), mseconds(20), 0)
    task2 = Task('Task2', useconds(1), mseconds(50), mseconds(50), 0)
    task3 = Task('Task3', useconds(1), mseconds(20), mseconds(20), 0)
    task4 = Task('Task1', useconds(1), mseconds(50), mseconds(50), 0)
    chain = [task1, task2, task3, task4]

    dpt = DPT(chain)
    dpt.getDpt()
    print("Syncronous Release Exact Analysis : " + chainString(chain) + " => Latency = " + printTime(dpt.maxAge))

    combinations = combinationsHeuristic(chain, mseconds(1))


    print("Case Study: " + str(combinations) + " combinations are checked with the heuristic.")

    start = timer()
    heur = heuristicOptimalPhasing(chain, mseconds(1))
    durationHeuristic = timer() - start

    print("Heuristic: " + chainString(chain) + " => Latency = " + printTime(heur) + " in " + str(durationHeuristic * 1000) + " ms")

    dpt = DPT(chain)
    dpt.getDpt()
    print("Exact Analysis : " + chainString(chain) + " => Latency = " + printTime(dpt.maxAge))

    task1 = Task('Task1', useconds(1), mseconds(20), mseconds(20), 0)
    task2 = Task('Task2', useconds(1), mseconds(50), mseconds(50), 0)
    task3 = Task('Task3', useconds(1), mseconds(20), mseconds(20), 0)
    task4 = Task('Task1', useconds(1), mseconds(50), mseconds(50), 0)

    start = timer()
    opt = optimalPhasingSemiHarm(chain)
    durationOptimal = timer() - start

    print("Optimal Latency = " + printTime(opt) + " in " + str(durationOptimal * 1000) + " ms")

    print("\nMartinez Latency = " + printTime(calculateLatencyMartinezTCAD18(chain)))

    print("Ours Optimal: " + chainString(chain) + " => Latency = " + printTime(opt))
    assert heur == opt

    filePath = os.path.join(basePath, 'case_study_semiharmonic.csv') 
    with open(filePath, "a") as file:
        file.write(str(heur) + "," + "{:.6f}".format(durationHeuristic * 1000) + "," + str(opt) + "," + "{:.6f}".format(durationOptimal * 1000) )
        file.close()

def storeExperimentConfig(args):
    """ This function creates a text file with all configuration options set.  
        The file will be stored in the main folder of the experiment configuration.
        This is to keep track of the used configurations. """ 
    
    destinationFolder = args.destination
    outputPath = os.path.join("output", destinationFolder) 

    os.makedirs(outputPath, exist_ok=True)    # Create output folder if it does not exist

    filePath = os.path.join(outputPath, 'experiment_settings.csv') 
    with open(filePath, "a") as file:
        file.write("Synthetic Experiments = " + str(args.synthetic) + "\n")
        file.write("Case-Study = " + str(args.casestudy) + "\n")
        file.write("Minimum Chain Length = " + str(args.minlength) + "\n")
        file.write("Maximyum Chain Length = " + str(args.maxlength) + "\n")
        file.write("Step Chain Length = " + str(args.incrementlength) + "\n")
        file.write("Heuristic = " + str(args.heuristic) + "\n")
        file.write("Experiment Count = " + str(args.experimentCount) + "\n")
        if args.seed is not None:
            file.write("Seed = " + str(args.seed) + "\n")
        else:
            file.write("Seed = 123\n")
        file.close()

def main():
    os.system('cls' if os.name == 'nt' else 'clear')    # Clear the terminal

    # Setup the arguments for the experiment program.
    parser = argparse.ArgumentParser()

    parser.add_argument("destination", help="Name of the folder to store the results.", type=str)
    parser.add_argument("-synth", "--synthetic", help="Set flag to run the experiment on synthetic chains.", action="store_true")
    parser.add_argument("-cs","--casestudy", help="Set to true to execute the case study.", action="store_true")
    parser.add_argument("-c","--cores", help="Set the number of cores to use for the experiment.", type = int)
    parser.add_argument("-ap", "--automotivePeriods", help="Set flag to run the experiment with automotive periods.", action="store_true")

    parser.add_argument("-heur","--heuristic", help="Set to true to enable the offset heuristic of Martinez et al. TCAD'18 (long runtime).", action="store_true")
    parser.add_argument("-to","--timeout", help="Timeout for the heuristic.", type=int)
    parser.add_argument("-min","--minlength", help="Minimum length of generated chains.", type=int)
    parser.add_argument("-max","--maxlength", help="Maximum length of generated chains.", type=int)
    parser.add_argument("-inc","--incrementlength", help="Step between two examined chain length.", type=int)
    parser.add_argument("-exp","--experimentCount", help="Number of experiments for each configuration and data point.", type=int)
    parser.add_argument("-sed","--seed", help="Seed for the random number generator.", type=int)
    parser.add_argument("-k","--kValue", help="(2,k)-max harmonic periods.", type=int)
    parser.add_argument("-np","--numPeriods", help="Minimum number of periods with random (2,k)-max harmonic periods in period sets during generation.", type=int)

    args = parser.parse_args()

    # Experiment Configuration

    destinationFolder = args.destination                 # Subfolder name to store the experiments results at
    runSyntheticExperiments = args.synthetic             # Set flag to run the experiment on synthetic chains
    runCaseStudy = args.casestudy                        # Set to true to execute the case study

    numCpu = psutil.cpu_count(logical=False) - 1         # Get the number of physical CPUs. We use all but one for the experiment by default
    if args.cores is not None:
        numCpu = min(numCpu, args.cores)

    if runSyntheticExperiments:

        automotivePeriods = args.automotivePeriods

        # Configuration for the synthetic experiments
        onlyMaxHarmonic = False                         # Set this flag to false to keep also chains that are not max-harmonic
        runHeuristic = args.heuristic                   # Set this flag to enable the offset heuristic by Martinez et al.  

        if args.timeout is not None:
            timeout = args.timeout
        else:
            timeout = 0

        if args.experimentCount is not None:
            expCount = args.experimentCount             # Number of experiments for each configuration and data point
        else:
            print("--experimentCount is mandatory for syntehtic experiments.")
            return

        if args.minlength is not None:
            minChainLength = args.minlength             # Minimum length of generated chains
        else:
            print("--minlength is mandatory for syntehtic experiments.")
            return

        if args.maxlength is not None:
            maxChainLength = args.maxlength             # Maximum length of generated chains
        else:
            print("--maxlength is mandatory for syntehtic experiments.")
            return

        if args.incrementlength is not None: 
            stepChainLength = args.incrementlength      # Step between two examined chain length
        else:
            print("--incrementlength is mandatory for syntehtic experiments.")
            return

        if args.seed is not None:
            seed = args.seed
        else:
            seed = 123  # Default Seed

        if automotivePeriods is False:
            if args.kValue is not None: 
                k = args.kValue      # k-value of (2,k)-max harmonic periods
            else:
                print("--For random (2,k)-max harmonic periods, a k value needs to be specified.")
                return
            
            if args.numPeriods is not None: 
                numPeriods = args.numPeriods      # numPeriods of (2,k)-max harmonic periods
            else:
                print("--For random (2,k)-max harmonic periods, a numPeriods value needs to be specified.")
                return
        else:
            k = 0
            numPeriods = 0

        experiments(destinationFolder, seed, onlyMaxHarmonic, runHeuristic, timeout, expCount, minChainLength, maxChainLength, stepChainLength, numCpu, automotivePeriods, k, numPeriods)

    if runCaseStudy:
        caseStudy(destinationFolder)

    storeExperimentConfig(args) # Store the experiment configuration for traceability

if __name__ == "__main__":
    main()