# Optimal Task Phasing for End-To-End Latency in Harmonic and Semi-Harmonic Automotive Systems

This document describes the steps to reproduce the evaluation of the paper:

<i>Optimal Task Phasing for End-To-End Latency in Harmonic and Semi-Harmonic Automotive Systems</i>\
<i>Mario Günzel, Matthias Becker</i>

The paper is under submission at RTAS 2025.

This document is structured as follows:
* [Platform Requirements](#platform-requirements)
* [Setup and Installation](#setup-and-installation)
* [Reproducing Experiments ](#reproducing-experiments)
* [Executing Configurations Manually](#executing-configurations-manually)

## Platform Requirements

The evaluations shown in the paper are performed on a platform containing an Intel Xeon Silver 4114 processor with 10 cores (20 threads) at 2.2 GHz and 32 GB RAM, running Linux. 
Experiments that include the heuristic to explore all unique offset combinations can exceed the available memory in rare cases.

The results can be replecated with smaller platforms as well, at the cost of longer runtime. 
The virtual machine, a configuration of 5 CPUs and 4 GB RAM offers a good tradeoff.


## Setup and Installation

The artifact can be used in two ways: (1) Using the pre-installed virtual machine image. Using the
virtual machine image is the recommended approach. (2) Manual installation on Linux or OSX
(Windows not tested). The setup for both cases is described below.

### Using the Virtual Machine Image

A virtual machine image based on Ubuntu 24.10 is provided at the link: [VM download link]()

The VM is based on an image obtained from [osboxes.org](www.osboxes.org).

* **User:** osboxes.org
* **Password:** osboxes.org

The source code is deployed on the desktop and all required software is installed. 
To move to the folder and activate the prepared virtual environment, the following commands are executed:

```
cd Desktop/OptimalTaskPhasing
source .venv/bin/activate
```

Afterwards, the steps described below to [reproduce the experiment](#reproducing-experiments) can be followed. 

### Installing Manually
As a prerequisite, the following should be installed on the platform:
* Python 3.10.12 or 3.12.7 (other versions might work as well)
* Git
* Latex (for plots using matplotlib)

Clone the git repository:
```
git clone https://github.com/ESRTS/OptimalTaskPhasing 
```
Change the directory to the repository:
```
cd OptimalTaskPhasing 
```
To avoid version conflicts with required packets, it is recommended to use a virtual environment
to reproduce the experiments. A new virtual environment is created in a folder .venv in the current
directory by the following command:
```
python3 -m venv .venv
```
The virtual environment in activated by the following command:
```
source .venv/bin/activate
```
Finally, the requirements can be installed to the virtual environment:
```
pip install -r requirements.txt
```

### File Structure

    .
    ├── output                                  # The folder includes all generated output 
    |   ├──example_run                          # Structure of generated output for one execution (not in repository)
    |      ├──data                              # Results of the experiment run (here assuming a varying chain length from 2 to 10)
    |      |  ├──length_2.csv                   # All results for a chain length of 2
    |      |  ├──...
    |      |  └──length_10.csv                  # All results for a chain length of 2
    |      ├──plots                             # The folder includes all generated plots for this configuration
    |      |  ├──AnalysisTimeComp.pdf
    |      |  ├──AvrgLatencyComp.pdf
    |      |  ├──HeuristicCombinations.pdf
    |      |  ├──LatencyComp.pdf
    |      |  ├──NormalizedLatency.pdf
    |      |  └──length_10.csv
    |      └──experiment_settings.csv
    ├──Comparison.py                            # Methods for general comparison (Davare bound and random phasing)
    ├──DPT_Offset.py                            # Exact analyis for LET chains with offset Becker JSA 2017
    ├──main.py                                  # Methods to parse arguments and parallelize execution of different chain lengths
    ├──MartinezTCAD18.py                        # Exact analysis for LET chains and heuristic offset assignment from Martinez et al. TCAD 2018
    ├──OptimalPhasing.py                        # Proposed approach for optimal task phasing 
    ├──plotting.py                              # Methods to plot the different results
    ├──README.md                                # Instructions for the artifact
    ├──requirements.txt                         # Required packages and versions
    ├──Task.py                                  # Task and task chains, as well as methods to generate random tasks for different settings
    └──Time.py                                  # Helper methods to handle timestamps

## Reproducing Experiments 

The paper includes four experiments.
Note that experiment four is a new experiment added during
shepherding. 
The shepherding process is ongoing.
The mapping of experiment to paper element, as well as the expected runtimes with the virtual machine, is shown in the table below.
For pots in the paper, 1000 random chains are evaluated for each data point.
This can be very timeconsuming and a reduced number of samples can be used instead (e.g. 50).
If a smaller number of samples per data point are used, the curves look more uneven but the general trends and observations are visible.

| Name          | Paper       | Runtime 50  | Runtime 1000    |
|---------------|-------------|-------------|-----------------|
| [Experiment 1](#experiment-1)  | Table 1     | < 5 s (no sample count needed)|
| [Experiment 2](#experiment-2)  | Figure 7    | ~30 min      | 10h            |
| [Experiment 3](#experiment-3)  | Figure 8    |  min         | h              |
| [Experiment 4](#experiment-4)  | Shepherding |  min         | h              |


To reproduce the experiments of the paper, dedicated scripts are provided. Where applicable, the number of evaluated task chains per configuration can be configured as argument, allowing to generate results with less data points in reduced runtime. 

For each experiment, we assume the current folder is `OptimalTaskPhasing` and the virtual environment is active:

```
cd OptimalTaskPhasing
source .venv/bin/activate
```

### Experiment 1

This experiment evaluates an automotive use-case in two configurations. First, with harmonic
periods and then with semi-harmonic periods. For each configuration, the end-to-end latency with
synchronous release is compared to the end-to-end latency with optimal phasing. The runtime to
obtain the optimal phasing is reported for the proposed approach and the State-of-the-Art heuristic.
Results are reported in `Table 1`.

Change the permission of the script to be executable, and execute experimet1.sh:
```
chmod 777 experiment1.sh
./experiment1.sh
```

The results will be printed to the terminal. 
Detailed in formation on each case-study setting (harmonic and semi-harmonic periods) is printed to the terminal.
This includes additional information not part of Table 1, such as the number of configurations checked by the heuristic etc. 
At the end of the printout, `Table 1` is shown.

### Experiment 2

This experiment shows the end-to-end latency with optimal phasing normalized to the end-to-end
latency with synchronous release. The chain length is varied from 2 to 50 in steps of 2, and for
each configuration, 1000 chains are evaluated. The results are presented as box-plot in `Figure 7`.

Change the permission of the script to be executable, and execute experimet2.sh:
```
chmod 777 experiment2.sh
./experiment2.sh 1000
```

As argument, the number of task chains evaluated for each chain length is configured. 
This way, the runtime of the experiment can be reduced. 
The results will be saved to the folder `output/experiment2`. 
CSV-files for each evaluated chain length are stored in the subfolder `/data`. 
The generated plots are stored in the subfolder `/plots`.
The plot named `output/experiment2/plots/NormalizedLatency.pdf` is shown as `Fig. 7` in the paper and opened at the end of  the script.

### Experiment 3

This experiment compares the runtime of the proposed approach to the State-of-the-Art heuristic.
The chain length is varied from 2 to 10, plus an additional chain length of 50 is shown. For each
configuration 1000 measurements are performed. As the heuristic has a long runtime, those results
are only included for a chain length of 1, 2, and 3. The results are presented as box-plot in `Figure 8`.

Change the permission of the script to be executable, and execute experimet3.sh:
```
chmod 777 experiment3.sh
./experiment3.sh 1000
```

As argument, the number of task chains evaluated for each chain length is configured. 
This way, the runtime of the experiment can be reduced. 
Note that several subfolders are created for this experiment under `output/experiment3`. 
Due to the long runtime of the heuristic approach only the first three data points are executed with the
heuristic. 
Later data points up to a chain length of 10 as well as a chain length of 50 are executed separately. 
Those results are automatically collected and combined for the final plot. 
The combined results will be saved to the folder `output/experiment3/`. 
CSV-files for each evaluated chain length are stored in the subfolder `/data`. The generated plots are stored in the
subfolder `/plots`. The plot named `output/experiment3/combined/plots/AnalysisTimeComp.pdf` is shown as `Fig. 8` in the paper and opened at the end of  the script.

### Experiment 4

This experiment compares the end-to-end latency with optimal phasing normalized to the end-to-
end latency with synchronous release for chains for random (2,k)-max harmonic periods. A curve
representing the geometric mean for a given value of k is plotted. 

`Note that this experiment is
part of the shepherding process and not part of the original submission.`

Change the permission of the script to be executable, and execute experimet4.sh:
```
chmod 777 experiment4.sh
./experiment4.sh 1000
```

As argument, the number of task chains evaluated for each chain length is configured. 
This way, the runtime of the experiment can be reduced. 
The results will be saved to the folder `output/experiment4`. 
For each evaluated value of `k`, a subfolder is created named `/kx`, where `x` stands for the value of `k` that is used in the experiment. 
The same structure as in the other experiments is found within those folders, i.e. a `/data` folder for the
CSV-files and a `/plots` folder for individual plots. 
The final plot combines all sub-experiments and is stored in `output/experiment4/plots`, where the plot named `MeanLatencyComp.pdf`. 
The plot is opened at the end of the script.

## Executing Configurations Manually

The python code provides the means to collect data for one configuration with varying number of tasks in a chain. 
Those results are saved in the folder `output` in the structure shown above. 
To configure the experiment, different arguments are provided. 

### Using the Case Study

For this configuration, only the `targetFolder` and the argument `--casestudy` are provided. Results are written to the folder `output/targetFolder`. No additional configuration is possible/needed. 
```
python main.py targetFolder --casestudy
```

### Using Automotive Periods

To run experiments with tasks periods in a chain drawn from the automotive period set (i.e. v, as reported by Kramer et al. in WATERS 2015), the following configuration is used:

```
python main.py targetFolder --synthetic --automotivePeriods --minlength 2 --maxlength 50 --incrementlength 2 --experimentCount 1000 --seed 123 --cores 10
```

`--synthetic`: Flag to indicate that task chains are randomly generated.

`--automotivePeriods`: Flag to indicate that task periods are drawn from the set [1,2,5,10,20,50,100,200,1000].

`--minlength`: Smallest chain lengh evaluated.

`--maxlength`: Largest chain length evaluated.

`--incrementlength`: Chain length increment between smallest and largest length that is evalauted. 

`--experimentCount`: Number of task chains evaluated for each chain length. 

`--seed`: Seed for the random number generator. 

`--cores`: Number of threads used in the experiment. If a number larger than than the number of available cores is specified, only as many threads as available cores are used. 

### Using (2,k)-max Harmonic Periods

To run experiments with task periods in a chain drawn from (2,k)-max harmonic period sets, the following configuration is used. 
In the current implementation, the largest possible hyperperiod that is considered is `1000ms`, as in the automotive task set. 
For each task chain, a random (2,k)-max harmonic period set is generated. To prevent period sets with only very few periods, the number of required periods in the period set used for task chain generation is specified as well.

```
python main.py targetFolder --synthetic --minlength 2 --maxlength 50 --incrementlength 2 --experimentCount 1000 --kValue 5  --numPeriods 10 --seed 123 --cores 10
```

`--synthetic`: Flag to indicate that task chains are randomly generated.

`--minlength`: Smallest chain lengh evaluated.

`--maxlength`: Largest chain length evaluated.

`--incrementlength`: Chain length increment between smallest and largest length that is evalauted. 

`--experimentCount`: Number of task chains evaluated for each chain length. 

`--kValue`: Specifies the value of `k` for the generation of (2,k)-max harmonic period sets used in the task chain generation. 

`--numPeriods`: Number of periods in the generated (2,k)-max harmonic period sets used in the task chain generation.

`--seed`: Seed for the random number generator. 

`--cores`: Number of threads used in the experiment. If a number larger than than the number of available cores is specified, only as many threads as available cores are used. 

