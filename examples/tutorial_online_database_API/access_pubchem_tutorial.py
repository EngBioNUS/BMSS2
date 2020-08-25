"""
@author: jingwui

Module to access PubChem to retrieve information for chemicals
Properties: ['INCHI', 'INCHIKEY', 'MolecularFormula','CanonicalSMILES', 'MolecularWeight']

Keys to be used as second input argument to specify the requested properties
'0' = 'INCHI'
'1' = 'INCHIKEY'
'2' = 'MolecularFormula'
'3' = 'CanonicalSMILES'
'4' = 'MolecularWeight'

Reference:
    https://pubchemdocs.ncbi.nlm.nih.gov/pug-rest-tutorial
    https://pubchem.ncbi.nlm.nih.gov/#query=ferulic%20acid
    https://pubchempy.readthedocs.io/en/latest/api.html
"""


import __init__
import BMSS.databaseAPI.access_pubchem as pubchem_api

from time import process_time

    
if __name__ == "__main__":
    
    '''Create an object from the class.'''
    ap = pubchem_api.access_pubchem()
    
    
    '''Use the function with multiple access, get the MolecularWeight
    and MolecularFormula for each compound.'''
    t0 = process_time() # to get the time for comparison
    output = ap.search_pubchem(['ferulic acid', 'vanillin'], ['4', '2'])
    print("Time elapsed: ", process_time()-t0, 's') 
    print("\nOutput in a list of dictionaries:\n", output)
    
    
    '''Use the function with single access per chemical, faster.'''
    t1 = process_time()
    output = ap.search_pubchem2(['ferulic acid', 'vanillin'], ['4', '2'])
    print("\nTime elapsed: ", process_time()-t1, 's') 
    print("\nOutput in a list of dictionaries:\n", output) # CID refers to compound ID
    print("\nFerulic acid's molecular weight:\n", output[0]['MolecularWeight'])
    

    
