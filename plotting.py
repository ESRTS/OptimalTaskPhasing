##################################################################################
# Plotting functionality
# 
# Author: Matthias Becker
##################################################################################
#import pandas as pd
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

def readData(dataFolder, length):

    # Syncronous release DPT analysis
    syncLatency = []
    syncDur = []
    # Optimal phasing and analysis
    optLatency = []
    optDur = []
    # Offsets and DPT analysis
    offsetLatency = []
    offsetDur = []

    filename = dataFolder + "/length_" + str(length) + ".csv"
    with open(filename,'r') as csvfile: 
        data = csv.reader(csvfile, delimiter = ',') 
        for row in data: 
            syncLatency.append(float((row[1])))
            syncDur.append(float((row[2])))
            optLatency.append(float(row[3]))
            optDur.append(float(row[4]))
            offsetLatency.append(float(row[5]))
            offsetDur.append(float(row[6]))
    
    return [syncLatency, syncDur, optLatency, optDur, offsetLatency, offsetDur]

def plot(dataFolder, dstFolder, start, stop, step):
    """ Create plotw for the files in the dataFolder. """
    expName = dataFolder.split('/')[-1]
    
    print("Generating Plots for data " + expName)

    # Syncronous release DPT analysis
    syncLatency = []
    syncDur = []
    # Optimal phasing and analysis
    optLatency = []
    optDur = []
    # Offsets and DPT analysis
    offsetLatency = []
    offsetDur = []

    for length in range(start, stop+1, step):   # Read data from CSV files. 
        data = readData(dataFolder, length)

        syncLatency.append(data[0])
        syncDur.append(data[1])
        optLatency.append(data[2])
        optDur.append(data[3])
        offsetLatency.append(data[4])
        offsetDur.append(data[5])

    plt.close()
    configure_mpl_for_tex()

    plt.xlabel('Chain Length')
    plt.ylabel('Norm. Latency')