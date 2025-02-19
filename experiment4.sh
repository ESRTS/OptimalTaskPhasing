#!/bin/bash

# Specify the number of samples per configuration
if [ $# -eq 0 ]
then
  echo "Specify the number of samples per configuration (e.g. './experiment4.sh 1000' )."
  exit 1
else
  SAMPLES=$1
  echo "Collecting $SAMPLES samples for each configuration."
fi

# Set the number of threads/cores that are used for the experiment.
CORES = 4

# Number of periods in one tasset for the chain generation.
NUM_PERIODS = 10

###
# Run the experiment to evaluate the end-to-end latency with the automotive period set.
###
python3 main.py experiment4/k3 --synthetic --cores $CORES -minlength 2 --maxlength 50 --incrementlength 2 --experimentCount $SAMPLES --kValue 3 --numPeriods $NUM_PERIODS --seed 123
python3 main.py experiment4/k5 --synthetic --cores $CORES -minlength 2 --maxlength 50 --incrementlength 2 --experimentCount $SAMPLES --kValue 5 --numPeriods $NUM_PERIODS --seed 123
python3 main.py experiment4/k7 --synthetic --cores $CORES -minlength 2 --maxlength 50 --incrementlength 2 --experimentCount $SAMPLES --kValue 7 --numPeriods $NUM_PERIODS --seed 123
python3 main.py experiment4/k9 --synthetic --cores $CORES -minlength 2 --maxlength 50 --incrementlength 2 --experimentCount $SAMPLES --kValue 9 --numPeriods $NUM_PERIODS --seed 123

###
# Call the plotting explicitly with the configuration to collect all data recorded above. 
###
python3 plotting.py experiment4 -minlength 2 --maxlength 50 --incrementlength 2 --kValue "3,5,7,9,max" --source "experiment4/k3,experiment4/k5experiment4/k7experiment4/k9"