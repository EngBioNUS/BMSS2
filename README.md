# BMSS2
This package supports routine building and analysis of kinetic models for biological systems. This includes simulation, sensitivity analysis, model selection and identifiability analysis. The whole package is database-driven which allows one to interactively retrieve, store and update model information and implementation from/into SQL databases to ensure reproducibility and reusability, particularly for ease of model selection. 

__*Note:*__ An extensible web app database listing some of the pre-established models can be found at https://engbio.syncti.org/BMSS2/index.html

![alt text](https://github.com/EngBioNUS/BMSS2/blob/master/BMSSDiagram.png?raw=true)

## Documentation
The documentation can be found at https://bmss2.readthedocs.io/en/latest/BMSS.html

## Features
* Database-driven model manipulation and storage 
* Model simulation
* Sensitivity analysis
* Parameter estimation using Bayesian Inference
* Model selection
* Trace analysis for _a_ _posteriori_ identifiability analysis
* Strike-GOLDD algorithm in Python for _a_ _priori_ identifiability analysis
* Support read/export of models in SBML format and model export in COMBINE archive

For more information, refer to the BMSS2 documentation. If you wish to know more about our work, visit the [NUS Engineering Biology Lab website](https://engbio.syncti.org).

## Recommended IDE
Spyder IDE from Anaconda Distribution [Anaconda Installation]

Recommended: Python 3.7, Other Python versions will be tested soon. 

## Dependencies: 
Install the dependent packages using pip as shown below.
```
pip install numpy matplotlib seaborn pandas numba scipy SALib dnaplotlib pyyaml synbiopython
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

## Getting started
The examples folder contains 
* Step-by-step explanations of BMSS2's functionalities labeled as tutorials
* Case studies for the characterization of common genetic constructs labeled as examples. 

## License

Copyright __*2020 EngBioNUS*__

Licensed under the __Apache License, Version 2.0__ (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
```
    http://www.apache.org/licenses/LICENSE-2.0
```
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## Contact Us
Please feel free to contact us at EngBioBMSS.help@gmail.com if you have any questions or to report any bugs.

[guidelines for contributing]: <https://github.com/EngBioNUS/BMSS2/blob/master/contributing.md>

## Contributing to the Project
Anyone and everyone is welcome to contribute. Please review the [guidelines for contributing]
