# This module is to run Combinatorial Simulations and Analyses 

The module supports the following functionalities:
* to enable users to generate model using human-readable configuration .ini format, and store, retrieve, and modify model from database.
* to auto-set the combinations based on the different options given to the different parts of gene circuit provided by users.
* to auto-run the combinatorial simulations based on the auto-generated combinations
* to auto-rank the behaviors of the combinatorial gene circuit configurations
* to quickly demonstrate the graphical outputs using visualization tools with easy-to-use helper functions
* to run global sensitivity analysis to identify how the different parts of gene circuit affect the output expressions. 

## Recommended IDE
Anaconda (Python 3.7) - more other python versions will be tested.

Using Spyder IDE from Anaconda (Python distribution) 

## Dependencies:
pip install SALib

pip install dnaplotlib


## For Anaconda (Jupyter Notebook should be available by default), else:
conda install jupyter
