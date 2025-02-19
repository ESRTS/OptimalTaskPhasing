#!/bin/bash

# Specify the number of samples per configuration
if [ $# -eq 0 ]
then
  echo "Specify the number of samples per configuration (e.g. './experiment3.sh 1000' )."
  exit 1
else
  SAMPLES=$1

  if [ $(($SAMPLES % 5)) -eq 0 ]
  then 
    echo "Collecting $SAMPLES samples for each configuration."
  else
    echo "Number of samples must divide by 5."
    exit 1
  fi
fi

# Set the number of threads/cores that are used for the experiment.
CORES=4

# The samples with heuristic are collected in 5 batches with different seeds. Here the number of samples per batch is calculated.
SAMPLES_HEURISTIC_INDIVIDUAL=$(($SAMPLES/5))

###
# Run the experiment with the heuristic for a chain length of 2 to 4. The 
###
python3 main.py experiment3/heuristic1 --synthetic --cores $CORES --automotivePeriods --minlength 2 --maxlength 4 --incrementlength 1 --heuristic --experimentCount $SAMPLES_HEURISTIC_INDIVIDUAL --seed 345
python3 main.py experiment3/heuristic2 --synthetic --cores $CORES --automotivePeriods --minlength 2 --maxlength 4 --incrementlength 1 --heuristic --experimentCount $SAMPLES_HEURISTIC_INDIVIDUAL --seed 456
python3 main.py experiment3/heuristic3 --synthetic --cores $CORES --automotivePeriods --minlength 2 --maxlength 4 --incrementlength 1 --heuristic --experimentCount $SAMPLES_HEURISTIC_INDIVIDUAL --seed 567
python3 main.py experiment3/heuristic4 --synthetic --cores $CORES --automotivePeriods --minlength 2 --maxlength 4 --incrementlength 1 --heuristic --experimentCount $SAMPLES_HEURISTIC_INDIVIDUAL --seed 678
python3 main.py experiment3/heuristic5 --synthetic --cores $CORES --automotivePeriods --minlength 2 --maxlength 4 --incrementlength 1 --heuristic --experimentCount $SAMPLES_HEURISTIC_INDIVIDUAL --seed 789

###
# Run the experiment to collect results without the heuristic for chain length 5 to 10
###
python3 main.py experiment3/heuristicBase --synthetic --cores $CORES --automotivePeriods --minlength 5 --maxlength 10 --incrementlength 1 --experimentCount $SAMPLES --seed 123

###
# Run the experiment to collect results without the heuristic for chain length of 50
###
python3 main.py experiment3/heuristicBase50 --synthetic --cores $CORES --automotivePeriods --minlength 50 --maxlength 50 --incrementlength 1 --experimentCount $SAMPLES --seed 123

###
# To plot the results all individual measurements are combined in a common data folder
###
python3 plotting.py experiment3 --type COMBINE --input "heuristic1,heuristic2,heuristic3,heuristic4,heuristic5,heuristicBase,heuristicBase50"

###
# Generate plots for the combined data
###
python3 plotting.py experiment3 --type NORMAL --minlength 2 --maxlength 50 --incrementlength 1

###
# Open the plot that is used for Figure 8.
###
open output/experiment3/plots/AnalysisTimeComp.pdf &