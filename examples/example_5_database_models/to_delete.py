import setup_bmss                   as lab
import BMSS.models.model_handler    as mh
import BMSS.models.setup_cf         as sc

import pandas as pd
import matplotlib.pyplot as plt

def subtract_blank(file):
    df = pd.read_csv(file+'_raw.csv', header=[0,1])
    
    to_drop = []
    time    = ''
    for column in df.columns:
        scenario, trial_num = column
        
        if 'Time' in scenario:
            time=scenario
            continue
        
        if 'Blank' in scenario:
            to_drop.append(column)
            continue
        
        df[scenario, trial_num] -= df['Blank', trial_num]
    
 
    df.drop(columns=to_drop, inplace=True)
    
    return df, time

def mu_sd(df, file, time):
    mu = df.mean(axis=1, level=0)
    sd = df.std(axis=1, level=0)
    sd.drop(columns=[time], inplace=True)
    
    cols2 = [column+'std' for column in sd.columns]
    sd.columns = cols2
    
    df2 = pd.concat([mu, sd], axis=1)
    
    df2.to_csv(file+'.csv',index=False)
    
    return df2

file1 = 'data/pTet_promoter_od'
od, time = subtract_blank(file1)
od2 = mu_sd(od, file1, time)

file2 = 'data/pTet_promoter_rfp'
rfp, time = subtract_blank(file2)
rfp_od = rfp/od
rfp_od[time] = rfp[time]
rfp_od2 = mu_sd(rfp_od, file2, time)

rfp_od_mu = rfp_od.mean(axis=1, level=0)
rfp_od_mu = rfp_od.mean(axis=1, level=0)

# df1 = pd.read_csv(file1+'.csv')
# df2 = pd.read_csv(file2+'.csv')
# df3 = df1/df2
# df3['Time(min)'] = df1['Time(min)']

# df3.to_csv('data/pTet_promoter_rfp.csv', index=False)



# if __name__ == '__main__':
#     '''
#     In this example, we want to perform curvefitting for the pTet promoter using 
#     a model in the BMSS database and a model not in the database.
    
#     Create settings template for 
#     '''
#     template_settings_filename = 'settings_template.ini'
    
#     system_types_settings_names = [('BMSS, Logistic, Inducible', '__default__'),
#                                    ('Inducible_Double_DegradingInducer', )]
    
#     sc.make_settings_template(system_types_settings_names, filename=template_settings_filename)
    