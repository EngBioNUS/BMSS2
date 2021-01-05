__This tutorial includes three different functions__

1. To generate SBML files from the model database
	- Running only the function will bring up 2 prompts.
	- First prompt indicates which model you would like to be converted
	- Second prompt indicates which settings you would like to be converted
	- Note: Model and Settings data should match in terms of the number of variables and parameters to avoid error 


2. To generate SBML files from a list of configuration files.
	- Running only this function will generate SBML files from the .ini files listed in the variable "files"
	- Use this if you want to only convert selected files from the whole folder.


3. To autogenerate SBML files for all .ini files stored inside ConfigSBML folder
	- Running this function will convert all .ini files stored in ConfigSBML folder in SBML files.
	- Note: Ensure that all .ini files are in correct format or the function will terminate with error.
