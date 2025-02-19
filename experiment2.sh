#!/bin/bash

# Specify the number of samples per configuration
if [ $# -eq 0 ]
then
  echo "Specify the number of samples per configuration (e.g. './experiment2.sh 1000' )."
  exit 1
else
  SAMPLES=$1
  echo "Collecting $SAMPLES samples for each configuration."
fi

# Set the number of threads/cores that are used for the experiment.
CORES=4

###
# Run the experiment to evaluate the end-to-end latency with the automotive period set.
###
python3 main.py experiment2 --synthetic --cores "$CORES" --automotivePeriods --minlength 2 --maxlength 50 --incrementlength 2 --experimentCount "$SAMPLES" --seed 123


