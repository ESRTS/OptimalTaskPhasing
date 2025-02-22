##################################################################################
# Plotting functionality
# 
# Author: Matthias Becker
##################################################################################
import seaborn as sns
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import csv
import os
import argparse
from pathlib import Path
import warnings 

warnings.filterwarnings("ignore")  # Tick labels for some boxplots are arranges manually which creates warnings. Those are turned off here. 

def configure_mpl_for_tex():
    "Configures matplotlib for LaTeX embedding"
    # Inspired by https://jwalton.info/Embed-Publication-Matplotlib-Latex/
    # Adjusted from the version of Tobias Blass

    # Width of the IEEE template column, determined by \the\columnwidth
    width_pts = 252
    golden_ratio = (5**.5 - 1) / 2
    # Width of the figure relative to the page
    rel_width = 1.5

    inches_per_pt = 1 / 72.27

    # Figure width in inches
    width_in = width_pts * inches_per_pt * rel_width
    # Figure height in inches
    height_in = width_in * 0.5
    width_in = width_in * 1
    
    settings = {
        "figure.figsize": (width_in, height_in),
        "text.usetex": True,
        "font.family": "serif",
        "font.size": 10,
        "font.serif": ["computer modern roman"],
        "axes.labelsize": 10,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "lines.markersize": 7
    }
    mpl.rcParams.update(settings)

def getMinRuntimeOurs(dataFolder, length):
    minRuntime = 100
    filename = dataFolder + "/length_" + str(length) + ".csv"
    with open(filename,'r') as csvfile: 
        data = csv.reader(csvfile, delimiter = ',') 
        for row in data: 
            runtime = float((row[4]))
            if minRuntime > runtime:
                minRuntime = runtime
    return minRuntime

def getMaxRuntimeOurs(dataFolder, length):
    maxRuntime = 0
    filename = dataFolder + "/length_" + str(length) + ".csv"
    with open(filename,'r') as csvfile: 
        data = csv.reader(csvfile, delimiter = ',') 
        for row in data: 
            runtime = float((row[4]))
            if maxRuntime < runtime:
                maxRuntime = runtime
    return maxRuntime

def getAvrgRuntimeOurs(dataFolder, length):
    runtime = []
    filename = dataFolder + "/length_" + str(length) + ".csv"
    with open(filename,'r') as csvfile: 
        data = csv.reader(csvfile, delimiter = ',') 
        for row in data: 
            runtime.append(float((row[4])))

    return np.average(runtime)

def readDataFrameIndividual(dataFolder, length):
    """ Reads the data for individual appraoches. """
    outputData = []

    filename = dataFolder + "/length_" + str(length) + ".csv"

    pFilename = Path(filename)
    if pFilename.is_file() is False:
        return None

    with open(filename,'r') as csvfile: 
        data = csv.reader(csvfile, delimiter = ',') 
        for row in data: 
            outputData.append(['Worst-Case Phasing', length, float((row[7])), float((row[8]))])
            outputData.append(['Syncronous Release', length, float((row[1])), float((row[2]))])
            outputData.append(['Optimal Phasing', length, float((row[3])), float((row[4]))])
            #outputData.append(['OFFSET_EXP', length, float((row[5])), float((row[6]))])
            outputData.append(['Random Phasing', length, float((row[9])), float((row[10]))])
            outputData.append(['Martinez_Latency', length, float((row[11])), float((row[12]))])
            if float((row[13])) > 0:    # If the heuristic is not executed in the experiment config a value of -1 is written
                outputData.append(['SOTA Heuristic [27]', length, float((row[13])), float((row[14]))])
            
            martinezAnalysisDur = float((row[11]))
            combinations = int(row[15]) # Number of combinations to check
            outputData.append(['Heuristic Est. [27]', length, 0.0, combinations * martinezAnalysisDur])

            assert row[3] == row[5]
    
    return outputData

def readDataFrameRatio(dataFolder, length):

    outputData = []

    filename = dataFolder + "/length_" + str(length) + ".csv"

    pFilename = Path(filename)
    if pFilename.is_file() is False:
        return None
    
    with open(filename,'r') as csvfile: 
        data = csv.reader(csvfile, delimiter = ',') 
        for row in data: 
            outputData.append(['Improvement', length, float((row[3])) / float((row[1]))])
    
    return outputData

def readMaxHarmRatio(dataFolder, length):
    total = 0
    maxHarm = 0

    filename = dataFolder + "/length_" + str(length) + ".csv"
    with open(filename,'r') as csvfile: 
        data = csv.reader(csvfile, delimiter = ',') 
        for row in data: 
            if row[16] == 'False':
                maxHarm = maxHarm + 1
            total = total + 1

    return maxHarm

def readMaxHarmRatioData(dataFolder, start, stop, step):
    outputData = []
    for length in range(start, stop+1, step):   # Read data from CSV files.
        outputData.append(readMaxHarmRatio(dataFolder, length))

    return outputData

def readOffsetHeuristicData(dataFolder, start, stop, step):

    outputData = []

    for length in range(start, stop+1, step):   # Read data from CSV files.
        filename = dataFolder + "/length_" + str(length) + ".csv"
        with open(filename,'r') as csvfile: 
            data = csv.reader(csvfile, delimiter = ',') 
            for row in data: 
                outputData.append(['Heuristic', length, int(row[15])])
    
    return outputData

def readAverageValues(dataFolder, start, stop, step):

    outputData = []

    for length in range(start, stop+1, step):   # Read data from CSV files. 

        filename = dataFolder + "/length_" + str(length) + ".csv"

        avrgSync = 0
        avrgOpt = 0
        avrgWorst = 0
        avrgRnd = 0
        count = 0

        with open(filename,'r') as csvfile: 
            data = csv.reader(csvfile, delimiter = ',') 
            for row in data: 
                avrgSync = avrgSync + float((row[1]))
                avrgOpt = avrgOpt + float((row[3]))
                avrgWorst = avrgWorst + float((row[7]))
                avrgRnd = avrgRnd + float((row[9]))
                count = count + 1
        
        avrgSync = avrgSync / count
        avrgOpt = avrgOpt / count
        avrgWorst = avrgWorst / count
        avrgRnd = avrgRnd / count

        outputData.append(['Worst-Case Phasing', avrgWorst, length])
        outputData.append(['Syncronous Release', avrgSync, length])
        outputData.append(['Optimal Phasing', avrgOpt, length])
        outputData.append(['Random Phasing', avrgRnd, length])
    return outputData

def geo_mean(iterable):
    """ Compute the geometric mean. Using mapping to log domain to avoid overflow as described here:
        https://stackoverflow.com/questions/43099542/python-easy-way-to-do-geometric-mean-in-python#:~:text=You%20can%20also%20calculate%20the,result%3A%201.8171205928321397
    """
    a = np.array(iterable)
    return np.exp(np.log(a).mean())

def readAverageValuesGeometric(dataFolder, start, stop, step):

    outputData = []

    for length in range(start, stop+1, step):   # Read data from CSV files. 

        filename = dataFolder + "/length_" + str(length) + ".csv"

        sync = []
        opt = []
        worst = []
        rnd = []

        with open(filename,'r') as csvfile: 
            data = csv.reader(csvfile, delimiter = ',') 
            for row in data: 
                sync.append(float((row[1])))
                opt.append(float((row[3])))
                worst.append(float((row[7])))
                rnd.append(float((row[9])))
        
        avrgSync = geo_mean(sync)
        avrgOpt = geo_mean(opt)
        avrgWorst = geo_mean(worst)
        avrgRnd = geo_mean(rnd)

        outputData.append(['Worst-Case Phasing', avrgWorst, length])
        outputData.append(['Syncronous Release', avrgSync, length])
        outputData.append(['Optimal Phasing', avrgOpt, length])
        outputData.append(['Random Phasing', avrgRnd, length])
    return outputData

def getImprovementForChainLength(dataFolder, length) :

    imp = []
    filename = dataFolder + "/length_" + str(length) + ".csv"

    with open(filename,'r') as csvfile: 
            data = csv.reader(csvfile, delimiter = ',') 
            for row in data: 
                sync = float((row[1]))
                opt = float((row[3]))
                imp.append(opt/sync)
    
    return np.average(imp)

def getMaxImprovementForChainLength(dataFolder, length) :
    filename = dataFolder + "/length_" + str(length) + ".csv"
    maxImp = 100000
    with open(filename,'r') as csvfile: 
            data = csv.reader(csvfile, delimiter = ',') 
            for row in data: 
                sync = float((row[1]))
                opt = float((row[3]))
                imp = opt/sync
                if imp < maxImp:
                    maxImp = imp
    return maxImp

def getMinImprovementForChainLength(dataFolder, length) :
    filename = dataFolder + "/length_" + str(length) + ".csv"
    min = 0
    with open(filename,'r') as csvfile: 
            data = csv.reader(csvfile, delimiter = ',') 
            for row in data: 
                sync = float((row[1]))
                opt = float((row[3]))
                imp = opt/sync
                if imp > min:
                    min = imp
    return min

def plot(dataFolder, dstFolder, start, stop, step):
    """ Create plotw for the files in the dataFolder. """
    
    print("Generating Plots for folder: " + dataFolder)

    data = []
    gap = False
    xOrder = []
    xTicksLabels = []
    gaps = []

    #['Worst-Case Phasing', length, float((row[7])), float((row[8]))])  
    for length in range(start, stop+1, step):   # Read data from CSV files. 
        tmp = readDataFrameIndividual(dataFolder, length)
        if tmp is not None:
            if gap is True:
                xOrder.append(length-1) # Since there was a gap before at least this one does not exist
                xTicksLabels.append('...')
                gaps.append(len(xTicksLabels))
            xOrder.append(length)
            xTicksLabels.append(str(length))
            gap = False
            data.extend(tmp)
        else:
            gap = True

    df = pd.DataFrame(data, columns=['Approach', 'Cause-Effect Chain Length', 'Latency [$H$]', 'Runtime [s]'])

    ######################################################################################################
    # BOXPLOT comparing end-to-end latency of different appraoches
    ######################################################################################################
    configure_mpl_for_tex()

    plt = sns.boxplot(x = df['Cause-Effect Chain Length'],
            y = df['Latency [$H$]'],
            hue = df['Approach'], fliersize=2, linewidth=1, palette='Set2', order=xOrder)
    #plt.set_yscale("log")
   
    plt.legend(loc="upper left")
    #plt.set(ylim=(0, 2))
    
    plt.set_xticklabels(xTicksLabels)

    plt.figure.savefig(dstFolder + "/LatencyComp.pdf", bbox_inches='tight')
    
    plt.cla()

    ######################################################################################################
    # BOXPLOT comparing analysis time of different approaches
    ######################################################################################################
    configure_mpl_for_tex()

    indexAge = df[ (df['Approach'] == 'Random Phasing') ].index
    df.drop(indexAge , inplace=True)

    indexAge = df[ (df['Approach'] == 'Syncronous Release') ].index
    df.drop(indexAge , inplace=True)

    indexAge = df[ (df['Approach'] == 'Worst-Case Phasing') ].index
    df.drop(indexAge , inplace=True)

    indexAge = df[ (df['Approach'] == 'Martinez_Latency') ].index
    df.drop(indexAge , inplace=True)

    #indexAge = df[ (df['Approach'] == 'Heuristic [27]') ].index
    #df.drop(indexAge , inplace=True)

    indexAge = df[ (df['Approach'] == 'Heuristic Est. [27]') ].index
    df.drop(indexAge , inplace=True)
    
    plt = sns.boxplot(x = df['Cause-Effect Chain Length'],
            y = df['Runtime [s]'],
            hue = df['Approach'], fliersize=2, linewidth=1, palette='Set2', order=xOrder)
    plt.set_yscale("log")
   
    plt.set_xticklabels(xTicksLabels)

    plt.legend(ncol=1, loc="upper right")

    d = .015
    p = 0.01
    
    kwargs = dict(transform=plt.transAxes, clip_on=False)
    
    for i in gaps:
        xpos = (1 / (len(xTicksLabels) + 0.5)) * i
        plt.plot((xpos-0.001, xpos-0.001), (0, -0.05), **kwargs, linewidth=2, color = 'w')    # This overwrites the tick mark
    
    #plt.set_ylim(top=100)

    plt.figure.savefig(dstFolder + "/AnalysisTimeComp.pdf", bbox_inches='tight')
    
    plt.cla()

    ######################################################################################################
    # BOXPLOT comparing ratio between latency of sync approach and optimal phasing (opt / sync)
    ######################################################################################################

    data = []

    for length in range(start, stop+1, step):   # Read data from CSV files. 
        tmp = readDataFrameRatio(dataFolder, length)

        if tmp is not None:
            data.extend(tmp)

    df = pd.DataFrame(data, columns=['Approach', 'Cause-Effect Chain Length', 'Optimal / Synchronous'])

    configure_mpl_for_tex()

    plt = sns.boxplot(x = df['Cause-Effect Chain Length'],
            y = df['Optimal / Synchronous'],
            hue = df['Approach'], fliersize=2, linewidth=1, palette='Set2', order=xOrder)
    #plt.set_yscale("log")
   
    plt.get_legend().remove()

    plt.set_xticklabels(xTicksLabels)

    #plt.legend(ncol=2, loc="upper left")
    #plt.set(ylim=(0, 2))
    
    d = .015
    p = 0.01
    
    kwargs = dict(transform=plt.transAxes, clip_on=False)
    
    for i in gaps:
        xpos = (1 / (len(xTicksLabels) + 1)) * i
        plt.plot((xpos-0.001, xpos-0.001), (0, -0.05), **kwargs, linewidth=4, color = 'w')    # This overwrites the tick mark

    plt.figure.savefig(dstFolder + "/NormalizedLatency.pdf", bbox_inches='tight')
    
    plt.cla()

def gen2kmaxPlot(dstPath, sourcePaths, minChainLength, maxChainLength, stepChainLength, kValueItems):
    '''
    Method generates the plot to compare the mean latency of cause-effect chains with different (2,k)-max periods (i.e. one curve for each provided value of 'k'). 
    '''
    graphData = []
    for i in range(0,len(sourcePaths)):
        print("K=" + str(kValueItems[i]) + " Path: " + str(sourcePaths[i]))

        
        
        for length in range(minChainLength, maxChainLength+1, stepChainLength):   # Read data from CSV files. 

            filename = sourcePaths[i] + "/length_" + str(length) + ".csv"
            opt = []
            with open(filename,'r') as csvfile: 
                data = csv.reader(csvfile, delimiter = ',') 
                for row in data: 
                    #opt.append(float((row[3])))
                    opt.append(float((row[3])) / float((row[1])))
            avrgOpt = geo_mean(opt)

            graphData.append(['(2,'+str(kValueItems[i])+')-max harmonic', avrgOpt, length])


    #print(graphData)
    df = pd.DataFrame(graphData, columns=['Approach', 'Optimal / Synchronous', 'Cause-Effect Chain Length'])

    configure_mpl_for_tex()
    g = sns.lineplot(data = df, x = 'Cause-Effect Chain Length', y = 'Optimal / Synchronous', hue='Approach', palette='Set2')

    g.legend_.set_title(None)

    if not os.path.isdir(dstPath):
        os.makedirs(dstPath)

    g.figure.savefig(dstPath + "/MeanLatencyComp.pdf", bbox_inches='tight')
    
    g.cla()

def combineResults(destinationFolder, input) :

    paths = input.split(',')
    
    # If the data folder exists, it and its content is deleted here. This is important as file merging appends to the new csv-files!
    dataPath = os.path.join("output", destinationFolder, "data") 
    if os.path.isdir(dataPath):
        allfiles = [f for f in os.listdir(dataPath) if os.path.isfile(os.path.join(dataPath, f))]
        for fileName in allfiles:
            filePath = os.path.join(dataPath, fileName)
            os.remove(filePath)
        os.rmdir(dataPath)
    os.makedirs(dataPath)   

    # If the plots folder exists, it and its content is deleted here.
    plotsPath = os.path.join("output", destinationFolder, "plots") 
    if os.path.isdir(plotsPath):
        allfiles = [f for f in os.listdir(plotsPath) if os.path.isfile(os.path.join(plotsPath, f))]
        for fileName in allfiles:
            filePath = os.path.join(plotsPath, fileName)
            os.remove(filePath)
        os.rmdir(plotsPath)
    os.makedirs(plotsPath)
    
    for path in paths:
        sourceDataPath = os.path.join("output", destinationFolder, path, "data")  # The experiment results are stored here.
        
        allfiles = [f for f in os.listdir(sourceDataPath) if os.path.isfile(os.path.join(sourceDataPath, f))]
        
        for fileName in allfiles:
            srcFilePath = os.path.join(sourceDataPath, fileName)
            dstFilePath = os.path.join(dataPath, fileName)
            #print(srcFilePath + " -> " + dstFilePath) 

            srcFile = open(srcFilePath, "r")
            dstFile = open(dstFilePath, "a")

            dstFile.write(srcFile.read())

            srcFile.close()
            dstFile.close()


if __name__ == '__main__':

    # Setup the arguments for the experiment program.
    parser = argparse.ArgumentParser()

    parser.add_argument("destination", help="Name of the folder to store the results.", type=str)

    parser.add_argument("-t","--type", help="Defines the plot type 'NORMAL', '2KMAX', 'COMBINE'.", type=str)

    parser.add_argument("-i","--input", help="List of source paths to data that should be combined.", type=str)

    parser.add_argument("-min","--minlength", help="Minimum length of generated chains.", type=int)
    parser.add_argument("-max","--maxlength", help="Maximum length of generated chains.", type=int)
    parser.add_argument("-inc","--incrementlength", help="Step between two examined chain length.", type=int)
    parser.add_argument("-exp","--experimentCount", help="Number of experiments for each configuration and data point.", type=int)
    parser.add_argument("-k","--kValues", help="List of k-values in the plot.", type=str)
    parser.add_argument("-s","--source", help="List of source folders for each k-value.", type=str)

    parser.add_argument("-heur","--heuristic", help="Set to true to enable the offset heuristic of Martinez et al. TCAD'18 (long runtime).", action="store_true")



    args = parser.parse_args()

    destinationFolder = args.destination                 # Subfolder name to store the experiments results at    

    type = args.type                                     # Select which type of function to call 

    if type == 'NORMAL':    # Used to plot results from one main.py execution

        if args.minlength is not None:
            minChainLength = args.minlength             # Minimum length of generated chains
        else:
            print("--minlength is mandatory for syntehtic experiments.")
            exit(1)

        if args.maxlength is not None:
                maxChainLength = args.maxlength             # Maximum length of generated chains
        else:
            print("--maxlength is mandatory for syntehtic experiments.")
            exit(1)

        if args.incrementlength is not None: 
            stepChainLength = args.incrementlength      # Step between two examined chain length
        else:
            print("--incrementlength is mandatory for syntehtic experiments.")
            exit(1)

        outputPath = os.path.join("output", destinationFolder) 
        basePath = os.path.join(outputPath, "data") 
        dstPath = os.path.join(outputPath, "plots") 

        plot(basePath, dstPath, minChainLength, maxChainLength, stepChainLength)
    elif type == '2KMAX':   # Used to plot a grapg with multiple (2,k)-max harmonic curves, one for each provided 'k'. 

        if args.minlength is not None:
            minChainLength = args.minlength             # Minimum length of generated chains
        else:
            print("--minlength is mandatory for syntehtic experiments.")
            exit(1)

        if args.maxlength is not None:
                maxChainLength = args.maxlength             # Maximum length of generated chains
        else:
            print("--maxlength is mandatory for syntehtic experiments.")
            exit(1)

        if args.incrementlength is not None: 
            stepChainLength = args.incrementlength      # Step between two examined chain length
        else:
            print("--incrementlength is mandatory for syntehtic experiments.")
            exit(1)
        
        if args.kValues is not None: 
            kValueItems = args.kValues.split(',')
        else:
            print("--kValues is mandatory for syntehtic experiments.")
            exit(1)
        
        if args.source is not None: 
            sourceItems = args.source.split(',')
            sourcePaths = []

            for source in sourceItems:
                sourcePaths.append(os.path.join(os.path.join('output',source), "data") )
        else:
            print("--source is mandatory for syntehtic experiments.")
            exit(1)
        
        outputPath = os.path.join("output", destinationFolder) 
        dstPath = os.path.join(outputPath, "plots") 

        gen2kmaxPlot(dstPath, sourcePaths, minChainLength, maxChainLength, stepChainLength, kValueItems)


    elif type == 'COMBINE': # Used to combine results from multiple calls to main.py in a single data set.

        if args.input is not None:
            input = args.input             # Minimum length of generated chains
        else:
            print("--source a mandatory parameter.")
            exit(1)

        combineResults(destinationFolder, input)
    else:
        print("Unknown plotting type: " + str(type))
    