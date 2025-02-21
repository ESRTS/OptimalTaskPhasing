#!/bin/bash

# Specify the number of samples per configuration
if [ $# -eq 0 ]
then
  echo "Please specify the number of samples per configuration (e.g. './experiment4.sh 1000')."
  exit 1
else
  SAMPLES=$1
  echo "Collecting $SAMPLES samples for each configuration."
fi

# Record the time this experiment is started
STARTTIME=$(date +%s)

# Set the number of threads/cores that are used for the experiment.
CORES=4

# Number of periods in one tasset for the chain generation.
NUM_PERIODS=5

###
# Run the experiment to evaluate the end-to-end latency with the automotive period set.
###
python3 main.py experiment4/k3 --synthetic --cores $CORES --minlength 2 --maxlength 50 --incrementlength 2 --experimentCount $SAMPLES --kValue 3 --numPeriods $NUM_PERIODS --seed 123
python3 main.py experiment4/k9 --synthetic --cores $CORES --minlength 2 --maxlength 50 --incrementlength 2 --experimentCount $SAMPLES --kValue 9 --numPeriods $NUM_PERIODS --seed 123
python3 main.py experiment4/k15 --synthetic --cores $CORES --minlength 2 --maxlength 50 --incrementlength 2 --experimentCount $SAMPLES --kValue 15 --numPeriods $NUM_PERIODS --seed 123
python3 main.py experiment4/k21 --synthetic --cores $CORES --minlength 2 --maxlength 50 --incrementlength 2 --experimentCount $SAMPLES --kValue 21 --numPeriods $NUM_PERIODS --seed 123

###
# Call the plotting explicitly with the configuration to collect all data recorded above. 
###
python3 plotting.py experiment4 --type 2KMAX --minlength 2 --maxlength 50 --incrementlength 2 --kValue "3,9,15,21" --source "experiment4/k3,experiment4/k9,experiment4/k15,experiment4/k21"

###
# Open the plot that is used for the new experiment (currently being added during shepherding).
###
open output/experiment4/plots/MeanLatencyComp.pdf &

# Record the time this experiment is finished and print the runtime
ENDTIME=$(date +%s)
echo "\r\nIt takes $(($ENDTIME - $STARTTIME)) seconds to complete experiment 3 with $SAMPLES samples for each configuration."