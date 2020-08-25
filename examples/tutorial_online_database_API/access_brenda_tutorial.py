"""
@author: jingwui

Module to access Brenda to retrieve the Km and Kcat informations for enzymes

References:
    https://www.brenda-enzymes.org/soap.php
    https://www.brenda-enzymes.org/enzyme.php?ecno=6.2.1.12#KM%20VALUE%20[mM]
    
Requirements:
    pip install zeep
"""


import __init__
import os
import BMSS.databaseAPI.access_brenda as brenda_api

'''Save all the output files to the 'Outputs' folder.'''
path0 = os.path.abspath(os.path.dirname(__file__))
print(path0)
outputpath = os.path.join(path0, 'Outputs')
print(outputpath)

#'''Save to the existing folder.'''
#outputpath = ''

                
if __name__ == "__main__":        
    
    '''Create an object from the class.'''
    ab = brenda_api.access_brenda()
    
    
    #########################################################
    # Create new database table with updated info from Brenda, only run once
    #########################################################
    
#    '''Get all the Enzymes Synonyms for all EcNumbers and return the dataframe.'''
#    EcEnzymedict, fulldf = ab.get_allEnzymeSynonyms(export_csv = True,\
#                                                    filepath = outputpath)
#    print(EcEnzymedict) # 7984
#    print(fulldf)
#    
#    '''Delete the table from database file for the purpose of generating
#    new table for storing updated databases.'''
#    ab.delete_DBtable('EcTable.db', 'EcNumberdb')
#    
#    '''Create the new table with EcNumber and enzyme synonyms from 
#    the dataframe (to update the database with new information from Brenda.'''
#    ab.create_database('EcTable.db', 'EcNumberdb', fulldf)



    '''Get all EcNumbers.'''
    EcNumberlist, totalEcNumber = ab.get_allECNumber()   
    print('List of all EcNumbers:\n', EcNumberlist)
    print('\nTotal EcNumbers:\n', totalEcNumber)
    
    
    '''Get the enzyme synonyms based on EcNumber if we know that beforehand.'''
    Enzymelist = ab.getEnzymeName_fromEc('4.3.1.25')
    print('\nlist of Enzyme Synonyms:\n', Enzymelist)
    
    
    '''Get all the database information from the database Table.'''
    df = ab.select_all_tasks('EcTable.db', 'EcNumberdb', exportcsv = True,\
                             filepath = outputpath)
    print(df) 

    
    '''Search EcNumbers based on a list of Enzymes Synonyms.''' 
    edict, dbdict = ab.getEcNumber_from_DBfile('EcTable.db',\
                                               'EcNumberdb',\
                                               ['PAL|tyrosine ammonia-lyase', '4CL'],\
                                               exportcsv = True,
                                               filepath = outputpath)
    print('\nDict with the searched enzymes and the EcNumbers:\n', edict) 
    print('\nDict with the searched enzymes and the dataframes:\n', dbdict)
    # PAL: 4.3.1.25
    # 4CL: 6.2.1.12
    
    
    '''Get the Kcat/Km value [1/mMs-1] based on the given ecnumbers.'''
    outputkcatkm, dfkcatkm = ab.get_KcatKmValue(['4.3.1.25', '6.2.1.12'],\
                                                substrate = [''],\
                                                organism = ['rhodotorula Toruloides', ''],\
                                                exportcsv = True,\
                                                filepath = outputpath)
    print('\nList of dictionaries with Kcat/Km info:\n', outputkcatkm)
    print('\nThe resulting Kcat/Km dataframe:\n', dfkcatkm)
    
    
    '''Get the Km value [mM] based on the given ecnumbers.'''
    outputkm, dfkm = ab.get_KmValue(['4.3.1.25', '6.2.1.12'],\
                                    substrate = [''],\
                                    organism = ['rhodotorula Toruloides', ''],\
                                    exportcsv = True,\
                                    filepath = outputpath)
    print('\nList of dictionaries with Km info:\n', outputkm)    
    print('\nThe resulting Km dataframe:\n', dfkm)
    
    
    '''Get the filtered dataframe based on the search keys and values
    provided in dictionary; allow seaching for case-insensitive substring match.'''
    dfkm_filter = ab.df_search(dfkm,\
                               {'ecNumber':'4.3.1.25',\
                                'substrate':'tyr|tyrosine',\
                                'organism': 'rhodotorula Toruloi'},\
                                exportcsv = True, filepath = outputpath)
    print(dfkm_filter)
