##################################################################################
# Plotting functionality
# 
# Author: Matthias Becker
##################################################################################
import seaborn as sns
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

def configure_mpl_for_tex():
    "Configures matplotlib for LaTeX embedding"
    # Inspired by https://jwalton.info/Embed-Publication-Matplotlib-Latex/
    # Adjusted from the version of T. Blass

    # Width of the IEEE template column, determined by \the\columnwidth
    width_pts = 252
    golden_ratio = (5**.5 - 1) / 2
    # Width of the figure relative to the page
    rel_width = 1.5

    inches_per_pt = 1 / 72.27

    # Figure width in inches
    width_in = width_pts * inches_per_pt * rel_width
    # Figure height in inches
    height_in = width_in * 0.5#golden_ratio
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

def readDataFrameIndividual(dataFolder, length):
    """ Reads the data for individual appraoches. """
    outputData = []

    filename = dataFolder + "/length_" + str(length) + ".csv"
    with open(filename,'r') as csvfile: 
        data = csv.reader(csvfile, delimiter = ',') 
        for row in data: 
            outputData.append(['Worst-Case Phasing', length, float((row[7])), float((row[8]))])
            outputData.append(['Syncronous Release', length, float((row[1])), float((row[2]))])
            outputData.append(['Optimal Phasing', length, float((row[3])), float((row[4]))])
            #outputData.append(['OFFSET_EXP', length, float((row[5])), float((row[6]))])
            outputData.append(['Random Phasing', length, float((row[9])), float((row[10]))])
            assert row[3] == row[5]
    
    return outputData

def readDataFrameRatio(dataFolder, length):

    outputData = []

    filename = dataFolder + "/length_" + str(length) + ".csv"
    with open(filename,'r') as csvfile: 
        data = csv.reader(csvfile, delimiter = ',') 
        for row in data: 
            outputData.append(['Improvement', length, float((row[3])) / float((row[1]))])
    
    return outputData

def readOffsetHeuristicData(dataFolder, start, stop, step):

    outputData = []

    for length in range(start, stop+1, step):   # Read data from CSV files.
        filename = dataFolder + "/length_" + str(length) + ".csv"
        with open(filename,'r') as csvfile: 
            data = csv.reader(csvfile, delimiter = ',') 
            for row in data: 
                outputData.append(['Heuristic', length, int(row[11])])
    
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

def plot(dataFolder, dstFolder, start, stop, step):
    """ Create plotw for the files in the dataFolder. """
    expName = dataFolder.split('/')[-1]
    
    print("Generating Plots for data " + expName)

    data = []

    for length in range(start, stop+1, step):   # Read data from CSV files. 
        data.extend(readDataFrameIndividual(dataFolder, length))

    df = pd.DataFrame(data, columns=['Approach', 'Chain Length', 'Latency [$H$]', 'Computation Time [s]'])

    ######################################################################################################
    # BOXPLOT comparing latency of sync approach to optimal phasing
    ######################################################################################################
    configure_mpl_for_tex()

    plt = sns.boxplot(x = df['Chain Length'],
            y = df['Latency [$H$]'],
            hue = df['Approach'], fliersize=2, linewidth=1, palette='Set2')
    #plt.set_yscale("log")
   
    plt.legend(loc="upper left")
    #plt.set(ylim=(0, 2))
    
    plt.figure.savefig(dstFolder + "/LatencyComp.pdf", bbox_inches='tight')
    
    plt.cla()

    ######################################################################################################
    # BOXPLOT comparing analysis time of different approaches
    ######################################################################################################
    configure_mpl_for_tex()

    indexAge = df[ (df['Approach'] == 'Random Phasing') ].index
    df.drop(indexAge , inplace=True)

    plt = sns.boxplot(x = df['Chain Length'],
            y = df['Computation Time [s]'],
            hue = df['Approach'], fliersize=2, linewidth=1, palette='Set2')
    plt.set_yscale("log")
   
    plt.legend(ncol=2, loc="upper left")
    plt.set_ylim(top=100)

    plt.figure.savefig(dstFolder + "/AnalysisTimeComp.pdf", bbox_inches='tight')
    
    plt.cla()

    ######################################################################################################
    # BOXPLOT comparing ratio between latency of sync approach and optimal phasing (opt / sync)
    ######################################################################################################

    data = []

    for length in range(start, stop+1, step):   # Read data from CSV files. 
        data.extend(readDataFrameRatio(dataFolder, length))

    df = pd.DataFrame(data, columns=['Approach', 'Chain Length', 'Optimal / Syncronous'])

    configure_mpl_for_tex()

    plt = sns.boxplot(x = df['Chain Length'],
            y = df['Optimal / Syncronous'],
            hue = df['Approach'], fliersize=2, linewidth=1, palette='Set2')
    #plt.set_yscale("log")
   
    plt.get_legend().remove()
    #plt.legend(ncol=2, loc="upper left")
    #plt.set(ylim=(0, 2))
    
    plt.figure.savefig(dstFolder + "/LatencyReduction.pdf", bbox_inches='tight')
    
    plt.cla()

    ######################################################################################################
    # Lineplot comparing different latency values
    ######################################################################################################
    
    #data = readAverageValues(dataFolder, start, stop, step)
    data = readAverageValuesGeometric(dataFolder, start, stop, step)
   
    df = pd.DataFrame(data, columns=['Approach', 'Average Latency [$H$]', 'Chain Length'])

    configure_mpl_for_tex()
    g = sns.lineplot(data = df, x = 'Chain Length', y = 'Average Latency [$H$]', hue='Approach', palette='Set2')

    g.legend_.set_title(None)

    plt.figure.savefig(dstFolder + "/AvrgLatencyComp.pdf", bbox_inches='tight')
    
    plt.cla()

    ######################################################################################################
    # Boxplot for the phasing combinations to check by the heuristic of Martinez et al.
    ######################################################################################################

    data = readOffsetHeuristicData(dataFolder, start, stop, step)

    df = pd.DataFrame(data, columns=['Approach', 'Chain Length', 'Phase Combinations'])

    configure_mpl_for_tex()

    plt = sns.boxplot(x = df['Chain Length'],
            y = df['Phase Combinations'],
            hue = df['Approach'], fliersize=2, linewidth=1, palette='Set2')
    plt.set_yscale("log")
   
    plt.get_legend().remove()
    #plt.legend(ncol=2, loc="upper left")
    #plt.set(ylim=(0, 2))
    
    plt.figure.savefig(dstFolder + "/HeuristicCombinations.pdf", bbox_inches='tight')
    
    plt.cla()