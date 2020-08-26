import setup_bmss                   as lab
import BMSS.models.settings_handler as sh

'''
Tutorial 1 Part 3: Creating and saving templates for settings.
- Create settings template that can be used for analysis in later tutorials.
- Add, edit and retrieve settings.
- Delete and restore settings.
'''
    
if __name__ == '__main__':
    '''
    BMSS includes modules analyzing models. Repeatedly coding common settings such 
    as the initial values you want to use is tedious. The BMSS database helps you
    avoid this problem by allowing you to save common settings associated with a 
    particular core model with a many-to-one (settings vs core model) relationship.
    
    Each settings is a dictionary that can be created using the constructor
    make_settings or read-in from a .ini file.
    '''
    
    #IMPORTANT! 
    #YOU MUST RUN PART1 WITHOUT DELETING THE CORE MODEL BEFORE RUNNING THIS!
    
    #Fill in the filenames here
    filename = 'testmodel.ini'
    
    system_types_settings_names = sh.config_to_database(filename)
    
    system_type, settings_name = system_types_settings_names[0]
    
    #View the database
    #Get all system_types as a list
    lst = sh.list_settings()
    
    #Export a copy of the entire database as a DataFrame
    #Note that changes to the DataFrame do not affect the database.
    #Refer to the Pandas documentation for DataFrame operations.
    df = sh.to_df()
    r  = df[df['system_type'] == system_type]
    
    #Retrieve param ensemble
    search_result1 = sh.quick_search(system_type=system_type, settings_name=settings_name)
    
    #Print search result
    for key in search_result1:
        print(key)
        print(search_result1[key])
        print()
    
    #Create a template
    sh.make_settings_template(system_types_settings_names, filename='settings_template.ini')
        
    #Deactivate a settings and remove it from searches.
    sh.delete(system_type=system_type, settings_name=settings_name)
    
    #Check if it is still visible in the list view and search results
    new_lst         = sh.list_settings()
    search_result_5 = sh.search_database(system_type, settings_name)
    
    #Note that you can still see it when exporting the database as a DataFrame
    new_df = sh.to_df()
    
    #Restore it and see if it is searchable
    sh.restore(system_type, settings_name)
    search_result_6 = sh.search_database(system_type)