"""
@author: jingwui

Module to access Brenda to retrieve the Km and Kcat informations for enzymes

References:
    https://www.brenda-enzymes.org/soap.php
    https://www.brenda-enzymes.org/enzyme.php?ecno=6.2.1.12#KM%20VALUE%20[mM]
    
Requirements:
    pip install zeep
    
"""


import os
import numpy as np
import hashlib
import sqlite3
import urllib.request
from zeep import Client, helpers 
from sqlite3 import Error
from pandas import DataFrame


class access_brenda:
    
    wsdl = "https://www.brenda-enzymes.org/soap/brenda_zeep.wsdl"
    password = hashlib.sha256("Brenda1234".encode("utf-8")).hexdigest()
    client = Client(wsdl)
    email = "yeohjingwui@gmail.com"
    
    
    def get_allECNumber(self):
        '''Return all the ECNumbers in the form of list from Brenda, and the
        total ECNumber available.'''
        parameters = (self.email, self.password)
        EcNumberlist = self.client.service.getEcNumbersFromEnzymeNames(*parameters)
        return EcNumberlist, len(EcNumberlist)
        
    
    def get_allEnzymeSynonyms(self, export_csv = True, filepath = ''):
        '''Return a dict containing all EcNumbers as the keys and the corresponding
        Enzyme Synonyms in the form of list as the values, and also return
        in the form of dataframe. The export_csv argument allows users to export
        the dataframe in CSV file.
        '''
        EcNumberlist, _ = self.get_allECNumber()
        EcEnzymedict = {}

        for e in EcNumberlist[:]:
            print(e)
            Enzymelist = self.getEnzymeName_fromEc(e)

            EcEnzymedict[e] = Enzymelist
            
        headers = ['EcNumber', 'Enzyme_Synonyms']
        Eclist = list(EcEnzymedict.keys())
        Synlist = [str(v) for v in list(EcEnzymedict.values())] # must be in the form of str
        
        df = DataFrame(list(zip(Eclist, Synlist)),
                       columns = headers)
            
        if export_csv:
            df.to_csv(os.path.join(filepath, 'EcTable.csv'))
            
        return EcEnzymedict, df
    
    
    def getEnzymeName_fromEc(self, EcNumber):
        '''Return list of enzyme synonyms.'''
        parameters = (self.email, self.password, "ecNumber*"+EcNumber,\
                      "organism*", "synonyms*")
        resultString = []
        try:
            resultString = self.client.service.getEnzymeNames(*parameters)
        except Exception:
            pass
        
        Enzymelist = [i['synonyms'] for i in resultString]
        
        return Enzymelist
    
    
    def create_database(self, DBfile, DBtable, df):
        '''This function is to create a database table from a dataframe that
        contains the EcNumber and Enzyme Synonyms to ease the search process
        of obtaining the EcNumber. Only need to run once if there is no .db file
        or when we are to update the database with the latest info from Brenda.
        ''' 
        # create a database connection
        conn = self.create_connection(DBfile)
        
        with conn:
            c = conn.cursor()
        
            # create table
            c.execute('''CREATE TABLE IF NOT EXISTS '''+DBtable+
                      str(tuple(list(df.columns))))
            
            conn.commit()
            
            df.to_sql(DBtable, conn, if_exists = 'replace', index = False)
        
        conn.commit()
        conn.close()
        
        return print("The EcNumber-Enzymes database has been updated successfully! ")
    
        
    def delete_DBtable(self, DBfile, DBtable):
        '''To delete the Table from the database before creating a new table
        with updated data from online database.
        '''
        conn = self.create_connection(DBfile)
        
        cur = conn.cursor()
        
        cur.execute("DROP TABLE IF EXISTS "+DBtable)
        
        conn.commit()
        
        return print(DBtable, "has been dropped from", DBfile)
        
        
    def select_all_tasks(self, DBfile, DBtable, exportcsv = True, filepath = ''):
        '''To fetch all data from the table inside the Database file and
        return in the format of dataframe. To enable more manipulations
        such as getting the ECNumber based on the enzyme synonyms. This function
        also enables the export of dataframe in the form of CSV file using the
        exportcsv argument.
        '''
        conn = self.create_connection(DBfile)
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM "+DBtable)
        
        col_name=[i[0] for i in cur.description]
        df = DataFrame(cur.fetchall(), columns = col_name)
        
        if exportcsv:
            df.to_csv(os.path.join(filepath, 'retrieved_EcTable.csv'))
    
        return df

    
    def getEcNumber_from_DBfile(self, DBfile, DBtable, Enzymeslist,\
                                exportcsv = True, filepath = ''):
        '''Search the EcNumber based on the enzyme synonym. More synonyms can
        be specified in the form of Synonym1|Synonym2. This function allows
        multiple search of Enzymes listed in the Enzymeslist.
        Return:
            edict: a nested dictionary containing the searched enzymes
            as first keys, and 'indexlist' and 'EcNumber' as second keys containing
            lists of found EcNumbers with their indexes.
            
            dbdict: a dictionary containing the searched enzymes as keys, and
            the found rows in the form of dataframe.
        '''
        df = self.select_all_tasks(DBfile, DBtable, exportcsv = exportcsv,\
                                   filepath = filepath)
        
        edict = {}
        dbdict = {}
        
        for e in Enzymeslist:
            df_found = df[df['Enzyme_Synonyms'].str.contains(e)]
            indexlist = df_found.index.tolist()
            edict[e] = {}
            edict[e]['indexlist'] = indexlist
            edict[e]['EcNumber'] = df.iloc[indexlist]['EcNumber'].values.tolist()
            dbdict[e] = df_found
        
        return edict, dbdict

        
    def create_connection(self, DBfile):
        '''Create connection to the sql database file.'''
        conn = None
        try:
            conn = sqlite3.connect(DBfile)
        except Error as e:
            print(e)
            
        return conn
    
    
    def get_KmValue(self, ecnumberlist, substrate = [''], organism = [''],\
                    exportcsv = True, filepath = ''):
        '''Get the Km value [mM] based on the given ecnumber in the form of list.
        Single or multiple ecnumbers can be provided. The corresponding substrate
        or/and organism can also be provided to filter the result. However,
        the substrate or organism must have an exact match. So it is better to
        use the df_search function which is able to identify substrings. Just
        use the default [''] to get all Km values for this function. This function
        also enables the export of dataframe in the form of CSV file using the
        exportcsv argument.
        Return:
            resultlist: list of dictionaries containing all the information.
            
            dfkm: a dataframe containing the result.
        '''
        num = len(ecnumberlist)
        
        substratelist = substrate*num if substrate  == [''] else substrate
        organismlist = organism*num if organism  == [''] else organism
        
        resultlist = []
        
        for i, ecnumber in enumerate(ecnumberlist):
            parameters = (self.email, self.password,"ecNumber*"+ecnumber,\
                          "kmValue*", "kmValueMaximum*",\
                          "substrate*"+substratelist[i],\
                          "commentary*", "organism*"+organismlist[i],\
                          "ligandStructureId*", "literature*")
            
            resultobject = self.client.service.getKmValue(*parameters)
            
            # Convert zeep object to python dict
            resultdict = self.convert_zeepobjecttodict(resultobject)
            
            resultlist += resultdict
        
        # Generate DataFrame from the list of dictionaries
        dfkm = DataFrame(resultlist)
        
        if exportcsv:
            dfkm.to_csv(os.path.join(filepath, 'KmValue.csv'))
        
        return resultlist, dfkm
    
    
    def convert_zeepobjecttodict(self, zeepobject):
        '''Convert zeep object to python dict.'''
        resultdict = helpers.serialize_object(zeepobject, dict)
        
        return resultdict
    
    
    def get_KcatKmValue(self, ecnumberlist, substrate = [''], organism = [''], \
                        exportcsv = True, filepath = ''):
        '''Get the Kcat/Km value [1/mMs-1] based on the given ecnumber in the form of list.
        Single or multiple ecnumbers can be provided. The corresponding substrate
        or/and organism can also be provided to filter the result. However,
        the substrate or organism must have an exact match. So it is better to
        use the df_search function which is able to identify substrings. Just
        use the default [''] to get all Km values for this function. This function
        also enables the export of dataframe in the form of CSV file using the
        exportcsv argument.
        Return:
            resultlist: list of dictionaries containing all the information.
            
            dfkcatkm: a dataframe containing the result.
        '''        
        num = len(ecnumberlist)
        
        substratelist = substrate*num if substrate  == [''] else substrate
        organismlist = organism*num if organism  == [''] else organism
        
        resultlist = []
        
        for i, ecnumber in enumerate(ecnumberlist):
        
            parameters = (self.email, self.password,"ecNumber*"+ecnumber,\
                          "kcatKmValue*", "kcatKmValueMaximum*",\
                          "substrate*"+substratelist[i], "commentary*",\
                          "organism*"+organismlist[i], "ligandStructureId*",\
                          "literature*")
            
            resultobject = self.client.service.getKcatKmValue(*parameters)
            
            # Convert zeep object to python dict
            resultdict = self.convert_zeepobjecttodict(resultobject)
            
            resultlist += resultdict
            
        # Generate DataFrame from the list of dictionaries
        dfkcatkm = DataFrame(resultlist)
        
        if exportcsv:
            dfkcatkm.to_csv(os.path.join(filepath, 'KcatKmValue.csv'))
        
        return resultlist, dfkcatkm

    
    def df_search(self, df, searchdict, exportcsv = True, filepath = ''):
        '''Return the filtered dataframe based on the search keys and values
        provided in the search dictionary. This search function allows seaching
        for case-insensitive substring match. Users can choose not to export the
        filtered dataframe in CSV file by setting exportcsv to False.
        '''
        searchlist = []
        for k, v in searchdict.items():
            if k in df.columns:
                searchlist.append(df[k].str.contains(v, case = False))
        
        # use bitwise operator & instead of logical operator AND
        result = np.bitwise_and.reduce(np.array(searchlist))
        
        df_filter = df[result]
        
        if exportcsv:
            df_filter.to_csv(os.path.join(filepath, 'df_filter.csv'))
        
        return df_filter
    
    
    def test_request(self):
        '''Try to use request module to access using url but it is forbidden'''
        string1 = "https://www.brenda-enzymes.org/enzyme.php?ecno="
        html = urllib.request.urlopen(string1+'4.2.1.17'+'#NATURAL%20SUBSTRATE')
        
        return html    

                
if __name__ == "__main__":        
    # create object from the class
    ab = access_brenda()

#    EcNumberlist, totalEcNumber = ab.get_allECNumber()   
#    print(EcNumberlist.index('1.14.14.19'), totalEcNumber)
    
    resultstring = ab.getEnzymeName_fromEc('1.14.14.19')
    print(resultstring)
    
    
    #####################################################
    # Create new database table with updated info from Brenda
    #####################################################
    
#    '''Get all the Enzymes Synonyms for all EcNumbers and return the dataframe.'''
#    EcEnzymedict, fulldf = ab.get_allEnzymeSynonyms()
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
    
    
    
    ## debugging purpose
#    col = ['EcNumber', 'Enzyme_Synonyms']
#    list1 = ['1.1.1.1', '1.1.2']
#    list2 = ["['nar+']","['Yel 5'-hello']"]
#    dftest = DataFrame(list(zip(list1, list2)), columns = col)
#    print(dftest)
    
    
    
#    df = ab.select_all_tasks('EcTable.db', 'EcNumberdb', exportcsv = True)
#    print(df) #df.dtypes
#    
#    searchlist = ['3-hydroxyacyl', '1-acylglycerol']
#    pattern = '|'.join(searchlist)
#    print(df[df['Enzyme_Synonyms'].str.contains(pattern)].index.tolist())
    
    
#    # search Ec Numbers for a list of Enzymes 
#    edict, dbdict = ab.getEcNumber_from_DBfile('EcTable.db', 'EcNumberdb', ['1-acylglycerol', 'DCX|xylulose'])
#    print(edict)
#    print(dbdict)
#    print(dbdict['DCX|xylulose']['Enzyme_Synonyms'])
    
#    edict, dbdict = ab.getEcNumber_from_DBfile('EcTable.db', 'EcNumberdb', ['1.1.1.10', 'DCX|xylulose'])
#    print(edict)
#    print(dbdict)
#    print(dbdict['1.1.1.10'])
    
#    edict, dbdict = ab.getEcNumber_from_DBfile('EcTable.db', 'EcNumberdb', ['PAL', '4CL'])
#    print(edict) 
#    print(dbdict)
    # PAL: 4.3.1.25
    # 4CL: 6.2.1.12
    
#    outputkcatkm, dfkcatkm = ab.get_KcatKmValue(['4.3.1.25', '6.2.1.12'],\
#                                                substrate = [''],\
#                                                organism = ['rhodotorula Toruloides', ''],\
#                                                exportcsv = True)
#    print(outputkcatkm)
#    print(dfkcatkm)
    
    
    outputkm, dfkm = ab.get_KmValue(['4.3.1.25', '6.2.1.12'],\
                                    substrate = [''],\
                                    organism = ['rhodotorula Toruloides', ''],\
                                    exportcsv = True)
    print(outputkm)    
    print(dfkm)
    
    dfkm_filter = ab.df_search(dfkm, {'ecNumber':'4.3.1.25', \
                                      'substrate':'tyr|tyrosine',\
                                      'organism': 'rhodotorula Toruloi'})
    print(dfkm_filter)

  
#    print(type(dfkm['substrate'].str.contains('tyr|tyrosine', case = False)))
#    
#    print(dfkm[dfkm['substrate'].str.contains('tyr|tyrosine', case = False) &
#               dfkm['organism'].str.contains('rhodotorula Toruloi', case = False)])
#    
#    dfkm_filter = ab.df_search(dfkm, {'ecNumber':'4.3.1.25', 'substrate': 'tyr|tyrosine','organism': 'rhodotorula Toruloi'})
#    print(dfkm_filter)
    
    
#    # This query function can only find exact match
#    dfkm_filter = dfkm.query("substrate == 'L-tyrosine'")
#    print(dfkm_filter)
    

    
#    '''To test the get substrates products function'''
##    outputsp = ab.get_substratesproducts('4.2.1.17')
#    outputsp = ab.get_naturalsubstratesproducts('4.2.1.17')
#    print(outputsp)
