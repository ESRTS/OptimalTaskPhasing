#!/bin/bash

# Specify the number of samples per configuration
if [ $# -eq 0 ]
then
  echo "Please specify the number of samples per configuration (e.g. './experiment2.sh 1000')."
  exit 1
else
  SAMPLES=$1
  echo "Collecting $SAMPLES samples for each configuration."
fi

# Record the time this experiment is started
STARTTIME=$(date +%s)

# Set the number of threads/cores that are used for the experiment.
CORES=4

###
# Run the experiment to evaluate the end-to-end latency with the automotive period set.
###
python3 main.py experiment2 --synthetic --cores "$CORES" --automotivePeriods --minlength 2 --maxlength 50 --incrementlength 2 --experimentCount "$SAMPLES" --seed 123

###
# Open the plot that is used for Figure 7.
###
open output/experiment2/plots/NormalizedLatency.pdf &

# Record the time this experiment is finished and print the runtime
ENDTIME=$(date +%s)
echo "\r\nIt takes $(($ENDTIME - $STARTTIME)) seconds to complete experiment 2 with $SAMPLES samples for each configuration."
echo "output/experiment2/plots/NormalizedLatency.pdf corresponds to Fig. 7 in the paper."