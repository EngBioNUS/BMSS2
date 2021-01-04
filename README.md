# BMSS2
![alt text](https://github.com/EngBioNUS/BMSS2/blob/master/BMSSDiagram.png?raw=true)

## Features
* Database-driven model storage 
* Simulation and sensitivity analysis and result plotting
* Model fitting and selection
* Trace analysis for _a_ _posteriori_ identifiability analysis
* Strike-GOLDD algorithm in Python for _a_ _priori_ identifiability analysis
* Export of models in SBML format
For more information, refer to the BMSS2 documentation. If you wish to know more about our work, visit the [NUS Engineering Biology Lab website (https://engbio.syncti.org/)][NUS Engineering Biology Lab website]


## Recommended IDE
Spyder IDE from Anaconda Distribution [Anaconda Installation]

Recommended: Python 3.7, Other Python versions will be tested soon. 

## Dependencies: 
Install the dependent packages using pip as shown below.
```
pip install numpy matplotlib seaborn pandas numba scipy SALib dnaplotlib pyyaml
```

## Optional
If you wish to put your code in notebook format, install Jupyter using pip as shown below.
```
pip install jupyter
```
or if you are using Anaconda:
```
conda install jupyter
```

[Anaconda Installation]: <https://www.anaconda.com/products/individual>

## Examples
The examples folder contains case studies for the characterization of common genetic constructs. Detailed explanations of BMSS2's functionalities can be found in the files labeled "tutorial".
