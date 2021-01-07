import setup_bmss                as lab
import BMSS.models.model_handler as mh

'''
Tutorial 1 Part 1: Introduction to the core model data structure.
- Learn how to describe a system of ODEs using a dictionary.
'''
    
if __name__ == '__main__':
    
    '''
    A core model is a dict with the following information and is used when interfacing the BMSS database.
    Each core model contains the following key-value pairs.
    system_type : A str of keywords joined by ", ". Keywords cannot contain spaces.
    id          : A unique str identifier. This is modified upon inserting the model into the database.
    states      : A list of str. The state variables of the system.
    parameters  : A list of str. The parameters of the system.
    inputs      : A list of str. The inputs to the system.
    equations   : A list of str. The last block of lines correspond to the differentials of the states.
    ia          : A str containing the name of a file with an identifiability analysis report if any.
    
    A core model can be documented using a .ini file which BMSS can read.
    '''
    
    #Fill in the filenames here
    filename = 'TestModel_Dummy.ini'
    
    #Read a .ini file and return a core_model
    core_model_1 = mh.from_config(filename)
    
    for key in core_model_1:
        print(key)
        print(core_model_1[key])
        print()
    
    '''
    BMSS also provides a constructor that allows you construct core models on the fly.
    
    IMPORTANT: When in doubt, always use the constructor to ensure that your data 
    is formatted correctly.
    '''

    core_model_2 = mh.make_core_model(system_type = core_model_1['system_type'],
                                      states      = core_model_1['states'],
                                      parameters  = core_model_1['parameters'],
                                      inputs      = core_model_1['inputs'],
                                      equations   = core_model_1['equations'],
                                      ia          = core_model_1['ia']
                                      )
    
    '''
    Once the core model has been created. We can create callable functions that can be used for integration.
    '''
    #Convert the model into code
    #Open the file named TestModel_Dummy.py
    code = mh.model_to_code(core_model_1, local=True) #Don't touch the local argument for now.
    
    #Note that all functions by this code are standardized to accept inputs in the form y, t, params
    
    
