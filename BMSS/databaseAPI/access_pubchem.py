"""
@author: jingwui

Module to access PubChem to retrieve information for chemicals
Properties: ['INCHI', 'INCHIKEY', 'MolecularFormula','CanonicalSMILES', 'MolecularWeight']

Reference:
    https://pubchemdocs.ncbi.nlm.nih.gov/pug-rest-tutorial
    https://pubchem.ncbi.nlm.nih.gov/#query=ferulic%20acid
    https://pubchempy.readthedocs.io/en/latest/api.html

"""

import urllib.request
from urllib.error import HTTPError
from time import process_time

class access_pubchem:
    '''Class to access PubChem to retrieve properties of chemicals.
    Example usage:
        >> import access_pubchem
        >>
        >> ap = access_pubchem()
        >> ap.search_pubchem(['ferulic acid', 'vanillin'], ['2', '4'])
        
    return:
        a list of dictionary containing the chemical name and the requested
        properties
    '''
    
    # information mapping
    prop = {}
    prop['0'] = 'INCHI'
    prop['1'] = 'INCHIKEY'
    prop['2'] = 'MolecularFormula'
    prop['3'] = 'CanonicalSMILES'
    prop['4'] = 'MolecularWeight'
    
    string1 = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
    string3 = "/property/" 
    
    def namecheck(self, chemical_name):
        '''To change the chemical input to the required format'''
        return chemical_name.replace(" ", "%20")
    
    def search_pubchem(self, chemical_namelist, prop_numlist):
        '''Get the chemical name and request properties
        and return the output from pubchem
        '''
        string4 = "/TXT"
        
        outputlist = []
        
        for n in chemical_namelist:
            string2 = self.namecheck(n)
            
            outputdict = {}
            
            for p in prop_numlist:
                if p in self.prop.keys():
                    stringprop = self.prop[p]
                    
                try:
                    outputstr = self.get_outputstr(string2, stringprop, string4)
                except HTTPError:
                    print(n, "'s", stringprop, 'is not found')
                    outputstr = 'Not found'
                    pass
                
                outputdict['Chemical Name'] = n
                outputdict[stringprop] = outputstr.replace('\n','')
                
            outputlist.append(outputdict)
                
        return outputlist
    
    def get_outputstr(self, string2, stringprop, string4):
        '''To access the url and return the output in string'''
        html = urllib.request.urlopen(self.string1 + string2 +\
                                      self.string3 + stringprop +\
                                      string4).read()
        html2 = html.decode('UTF-8')
        
        return html2
    
    def search_pubchem2(self, chemical_namelist, prop_numlist):
        '''This is to test if we have multiple properties with single request,
        This function is faster although it needs more output processing
        '''
        string4 = "/CSV" # must be in the form of CSV
        
        propname = []
        for p in prop_numlist:
            if p in self.prop.keys():
                propname.append(self.prop[p])
        
        stringprop = ','.join(propname)
        
        outputlist = []
                
        for n in chemical_namelist:
            string2 = self.namecheck(n)
            
            outputstr = self.get_outputstr(string2, stringprop, string4)
            
            outputstrlist = outputstr.split('\n')     
            outputstrlist.pop() # remove the last item
            
            proplist = outputstrlist[0].split(',')
            valuelist = outputstrlist[1].split(',')
            
            outputdict = {}
            
            outputdict['Chemical Name'] = n
            
            for i, c in enumerate(proplist):
                c = c.replace('"', '')
                outputdict[c] = valuelist[i].replace('"','')
            
            outputlist.append(outputdict)
            
        return outputlist 

    
def main():
    
    # create an object from the class
    ap = access_pubchem()
    t0 = process_time() # to get the time for comparison
    
    # to test the function with multiple access
    output = ap.search_pubchem(['ferulic acid', 'vanillin'], ['4', '2'])
    print("Time elapsed: ", process_time()-t0, 's') 
    print(output)
    
    t1 = process_time()
    
    # to test the function with single access per chemical
    output = ap.search_pubchem2(['ferulic acid', 'vanillin'], ['4', '2'])
    print("Time elapsed: ", process_time()-t1, 's') 
    print(output)
    print(output[0]['MolecularWeight'])
    
#enable the script to be run from command line
if __name__ == "__main__":
    main()
    
