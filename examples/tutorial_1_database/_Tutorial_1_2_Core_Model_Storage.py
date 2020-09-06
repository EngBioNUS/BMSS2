import setup_bmss                as lab
import BMSS.models.model_handler as mh

'''
Tutorial 1 Part 2: Using the Database.
- Add, edit and retrieve models.
- Delete and restore models.

'''
    
if __name__ == '__main__':
    
    #Fill in the filenames here
    filename = 'testmodel.ini'
        
    #Add new core model/Replace existing core model
    #Note that this assigns a unique id to the core model that is then printed to the console.
    system_type = mh.config_to_database(filename)
    
    #View the database
    #Get all system_types as a list
    lst = mh.list_models()
    
    #Export a copy of the entire database as a DataFrame
    #Note that changes to the DataFrame do not affect the database.
    #Refer to the Pandas documentation for DataFrame operations.
    df = mh.to_df()
    r  = df[df['system_type'] == system_type]
    
    #Search the database
    #This returns a list of core_models with system_types containing the keyword
    #Try searching using the core model's id
    search_result_1 = mh.search_database('TestModel', search_type='system_type')
    core_model_1    = search_result_1[0]
    model_id        = core_model_1['id']
    search_result_2 = mh.search_database(model_id, search_type='id')
    
    #If you already know the exact system_type or id, use quick_search to directly return the core model.
    #This function is a wrapper for search_database tha returns the first result.
    search_result_3 = mh.quick_search(system_type)
    search_result_4 = mh.quick_search(model_id)
    
    #Deactivate a core model and remove it from searches.
    #Change name to reactivate
    mh.deactivate(system_type)
    
    #Check if it is still visible in the list view and search results
    new_lst         = mh.list_models()
    search_result_5 = mh.search_database(system_type)
    
    #Note that you can still see it when exporting the database as a DataFrame
    new_df = mh.to_df()
    
    # #Restore it and see if it is searchable
    mh.restore(system_type)
    search_result_6 = mh.search_database(system_type)
    
    # #Create a file for the function and store it in the database
    # #Navigate to BMSS/models/model_functions and see if you can find it.
    mh.model_to_code(core_model_1, local=False)
    
    