#!/bin/bash

# Record the time this experiment is started
STARTTIME=$(date +%s)

###
# Run the case study.
###
python3 main.py experiment1 --casestudy 

# Record the time this experiment is finished and print the runtime
ENDTIME=$(date +%s)
echo "\r\nIt takes $(($ENDTIME - $STARTTIME)) seconds to complete experiment 1."