import csv
import matplotlib.pyplot as plt
import numpy             as np 
import pandas            as pd
import seaborn           as sns
from   matplotlib import get_backend
    
###############################################################################
#Globals
###############################################################################
verbose = False

#Refer for details: https://seaborn.pydata.org/tutorial/color_palettes.html
palette_types = {'color':     lambda n_colors, palette='bright', **kwargs : sns.color_palette(palette=palette, n_colors=n_colors),
                 'light':     lambda n_colors, color, **kwargs            : sns.light_palette(n_colors=n_colors+2, color=color, **kwargs)[2:],
                 'dark' :     lambda n_colors, color, **kwargs            : sns.dark_palette( n_colors=n_colors+2, color=color, **kwargs)[2:],
                 'cubehelix': lambda n_colors, **kwargs                   : sns.cubehelix_palette(n_colors=n_colors, **kwargs),
                 'diverging': lambda n, **kwargs                          : sns.diverging_palette(n=n, **kwargs),
                 }    
#Refer for details: https://xkcd.com/color/rgb/
all_colors    = sns.colors.xkcd_rgb

###############################################################################
#Supporting Functions
###############################################################################
def loose_match(word, keywords):
    for keyword in keywords:
        try:
            if keyword in word:
                return True
        except:
            pass
        try:
            for w in word:
                if keyword in w:
                    return True
        except:
            pass
    return False

def loose_map(word, keywords_dict, no_result=True):
    try:
        return keywords_dict[word]
    except:
        pass
    
    for keyword in keywords_dict:
        if keyword in word:
            return keywords_dict[keyword]
        try:
            for w in word:
                if keyword in w:
                    return keywords_dict[keyword]
        except:
            pass
                    
    else:
        return keywords_dict.get('__noresult__', '__noresult__') if no_result else '__noresult__'

###############################################################################
#Shortcuts
###############################################################################
def unpack(timeseries_dict, keys=[], dtype='df', start=0, stop=None, interval=1, skip=(), subtract_blank=True, subtract_initial=False):
    keys1 = keys if keys else list(timeseries_dict.keys())
    keys2 = list(timeseries_dict.keys())
    
    result = {keys1[i]: timeseries_dict[keys2[i]].export(dtype=dtype, start=start, stop=stop, interval=interval, skip=skip, subtract_blank=subtract_blank, subtract_initial=subtract_initial) for i in range(len(keys2))}
    
    return result

###############################################################################
#TimeSeries
###############################################################################
class TimeSeries(pd.DataFrame):

    _metadata = ['variable']

    def __init__(self, data=None, variable='',  *args, **kwargs):

        pd.DataFrame.__init__(self, data=data, *args, **kwargs)
        self.variable = variable
    
#    @classmethod
#    def _internal_ctor(cls, *args, **kwargs):
#        kwargs['data'] = args[0]
#        kwargs['variable'] = 'haha'
#        return cls(**kwargs)
#    
#    @property
#    def _constructor(self):
#        return TimeSeries._internal_ctor

    
    def __str__(self):
        global verbose
        if verbose:
            return super().__str__()
        else:
            temp = ', '.join([s for s in self.scenarios() if s != 'Time'])
            return self.__class__.__name__ + ' ' + self.variable + '{\n' + temp + '\n}'
    
    def __repr__(self):
        return self.__str__()
    
    def copy(self, *args, **kwargs):
        df     = super().copy(*args, **kwargs)
        return TimeSeries(data=df, variable=self.variable)
    
    ###############################################################################
    #Truncation
    ###############################################################################
    def cut(self, start=0, stop=None, inplace=True):
        stop1  = stop if stop else self.time().iloc[-1]
        cond   = (self.time() < start) | (self.time() > stop1)
        result = self.drop(self[cond].index, inplace=inplace)

        if inplace:
            self.reset_index(drop=True, inplace=True)
            return self
        else:
            result.reset_index(drop=True, inplace=True)
            return TimeSeries(data=result, variable=self.variable)
    
    def nth_row(self, start=0, stop=None, interval=1, inplace=True):
        stop1  = stop if stop else self.shape[0] 
        
        if inplace:
            index = [x for x in range(start, stop1) if (x-start)%interval]
            self.drop(index=index, inplace=True)
            self.reset_index(drop=True, inplace=True)
            return self
        
        else:
            result = self.iloc[start:stop1:interval,:]
            result.reset_index(drop=True, inplace=True)
            return TimeSeries(data=result, variable=self.variable)
    
    ###############################################################################
    #Access
    ###############################################################################        
    def scenarios(self):
        return list(self.columns.levels[0])
    
    def trials(self):
        return self.columns.tolist()
    
    def time(self):
        try:
            return self['Time', 'Time']
        except:
            pass
        try:
            return self['Time']
        except:
            raise Exception('No column named Time.')
    
    def not_time(self):
        return self.trials()[1:]
      
    def export(self, dtype='df', start=0, stop=None, interval=1, skip=(), subtract_blank=True, subtract_initial=False):
        stop1 = stop if stop else self.shape[0]
        df    = self
        if subtract_blank:
            df = df.subtract_blank(inplace=False, remove_blank=True)
        if subtract_initial:
            df = df.subtract_initial(inplace=False)
        
        to_drop = [column for column in df if loose_match(column, skip)]

        df.drop(columns=to_drop, inplace=True)
        
        if dtype == 'np':
            return df.values[start:stop1:interval,:]
        
        elif dtype == 'df':
            df  = df.iloc[start:stop1:interval,:]
            return df
        
        elif dtype == 'curvefit':
            df        = df.nth_row(start=start, stop=stop, interval=interval)
            scenarios = [scenario for scenario in df.scenarios() if not loose_match(scenario, skip)]
            mu        = df.scenario_mean().values
            sd        = df.scenario_sd().values
            df        = df.flatten()
            scenarios = [scenario for scenario in df.columns if not loose_match(scenario, skip)]
            df        = df.values
            
            result = {}
            for pair in [('data',df), ('mu', mu), ('sd', sd)]:
                key         = pair[0]
                array       = pair[1]
                width       = array.shape[1]
                result[key] = {i: array[:,i] for i in range(width)}

                result[key][-1] = scenarios
                result[key][-2] = self.variable
            
            return result
        
    ###############################################################################
    #Supporting Methods
    ###############################################################################
    #IMPORTANT: Return values are DataFrames, not TimeSeries 
    def flatten(self):
        '''
        Stacks trials for the same scenario into same column.
        Only works on data with equal num of trials per scenario.
        '''
        result   = {}
        time     = []
        width    = -1
        for scenario, sub_df in self.groupby(axis=1, level=0):
            if scenario == 'Time':
                time = list(sub_df.to_numpy())
            else:
                width  = sub_df.shape[1]
                result[scenario] = sub_df.unstack().to_numpy()
            
        result = pd.DataFrame(result)
        result.insert(0, 'Time', np.array(time*width))   
        
        return result
        
    ###############################################################################
    #Statistical Shortcuts
    ############################################################################### 
    #IMPORTANT: Return values are DataFrames, not TimeSeries       
    def scenario_sd(self):
        
        df         = self.std(axis=1, level=0)
        df['Time'] = self['Time'].values

        return df
    
    def scenario_mean(self):
        df         = self.mean(axis=1, level=0)
        df['Time'] = self['Time'].values

        return df
    
    def trial_sd(self):
        df         = self.std(axis=1, level=1)
        df['Time'] = self['Time'].values

        return df
    
    def trial_mean(self):
        df         = self.mean(axis=1, level=1)
        df['Time'] = self['Time'].values

        return df    
        
    ###############################################################################
    #Analysis Shortcuts
    ###############################################################################
    def diff(self):

        result = super().diff()
        result.drop(0)
        result['Time'] = self.time().values
        
        return result 
            
    def subtract_blank(self, inplace=True, remove_blank=True):
        '''
        Subtracts blank and gets rid of columns with Blank in their names.
        '''

        df = self if inplace else self.copy()

        for column in self:
            if column[0] == 'Time' or 'Blank' in column[0]:
                continue
            try:
                key = 'Blank ' + column[0], column[1]
                df[column] -= df[key]
            except:
                pass
            
            try:

                key = 'Blank', column[1]
                df[column] -= df[key]
                
            except:
                pass
                    
        if remove_blank:
            to_drop = [c for c in self if 'Blank' in c[0]]
            df.drop(columns=to_drop, inplace=True)
            df.columns = pd.MultiIndex.from_tuples(df.columns.to_list())

        return df
    
    def subtract_initial(self, inplace=True):
        result           = self if inplace else self.copy()
        columns          = self.not_time()
        first_row_values = self.iloc[0,1:]
        
        result[columns] -= first_row_values
        return result
    
    ##############################################################################
    #Arithmetic Shortcuts
    ##############################################################################    
    def __add__(self, x, new_name=''):
        
        columns    = self.not_time()
        
        if type(x) == TimeSeries:
            new_name1 = new_name  if new_name else '('+self.variable+'+'+x.variable+')'
            result    = self[columns].add(x[x.not_time()].values, axis=0)
       
        elif type(x) == pd.Series:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].add(x.values, axis=0)
            
        else:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].add(x, axis=0)
        
        return self._arithmetic_helper(result, new_name1)
    
    def __sub__(self, x, new_name=''):
        
        columns    = self.not_time()
        
        if type(x) == TimeSeries:
            new_name1 = new_name  if new_name else '('+self.variable+'-'+x.variable+')'
            result    = self[columns].sub(x[x.not_time()].values, axis=0)
       
        elif type(x) == pd.Series:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].sub(x.values, axis=0)
            
        else:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].sub(x, axis=0)
        
        return self._arithmetic_helper(result, new_name1)
    
    def __mul__(self, x, new_name=''):
        
        columns    = self.not_time()
        
        if type(x) == TimeSeries:
            new_name1 = new_name  if new_name else '('+self.variable+'*'+x.variable+')'
            result    = self[columns].mul(x[x.not_time()].values, axis=0)
       
        elif type(x) == pd.Series:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].mul(x.values, axis=0)
            
        else:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].mul(x, axis=0)
        
        return self._arithmetic_helper(result, new_name1)
    
    def __div__(self, x, new_name=''):
        
        columns    = self.not_time()
        
        if type(x) == TimeSeries:
            new_name1 = new_name  if new_name else '('+self.variable+'/'+x.variable+')'
            result    = self[columns].div(x[x.not_time()].values, axis=0)
       
        elif type(x) == pd.Series:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].div(x.values, axis=0)
            
        else:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].div(x, axis=0)
        
        return self._arithmetic_helper(result, new_name1)

    def __truediv__(self, x, new_name=''):
        
        columns    = self.not_time()
        
        if type(x) == TimeSeries:
            new_name1 = new_name  if new_name else '('+self.variable+'/'+x.variable+')'
            result    = self[columns].truediv(x[x.not_time()].values, axis=0)
       
        elif type(x) == pd.Series:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].truediv(x.values, axis=0)
            
        else:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].truediv(x, axis=0)
        
        return self._arithmetic_helper(result, new_name1)
    
    def __pow__(self, x, new_name=''):
        
        columns    = self.not_time()
        
        if type(x) == TimeSeries:
            new_name1 = new_name  if new_name else '('+self.variable+'^'+x.variable+')'
            result    = self[columns].pow(x[x.not_time()].values, axis=0)
       
        elif type(x) == pd.Series:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].pow(x.values, axis=0)
            
        else:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].pow(x, axis=0)
        
        return self._arithmetic_helper(result, new_name1)
    
    def __mod__(self, x, new_name=''):
        
        columns    = self.not_time()
        
        if type(x) == TimeSeries:
            new_name1 = new_name  if new_name else '('+self.variable+'%'+x.variable+')'
            result    = self[columns].mod(x[x.not_time()].values, axis=0)
       
        elif type(x) == pd.Series:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].mod(x.values, axis=0)
            
        else:
            new_name1 = new_name if new_name else self.variable
            result    = self[columns].mod(x, axis=0)
        
        return self._arithmetic_helper(result, new_name1)
    
    def log(self, x=None, new_name=''):
        
        columns    = self.not_time()
        
        if type(x) == TimeSeries:
            new_name1 = new_name if new_name else  'log(' + self.variable + ')' 
            result    = np.log(self[columns])
        
        return self._arithmetic_helper(result, new_name1)
    
    def _arithmetic_helper(self, result, variable):
        time   = self.time() 
        result.insert(0, time.name, time.values)
        result = TimeSeries(data=result, variable=self.variable)
        return result
    
###############################################################################
#Import
###############################################################################                
def import_timeseries(filename):
    result = import_csv(filename)
    result = {key: TimeSeries(data=result[key], variable=key) for key in result}
    return result

def import_csv(filename):
    '''
    File should be in csv time series markup format. 
    Returns a dictionary with format 
    {'y1':{'scenarios':[...], 'trials': [...], 'data': [...]}}
    '''
    
    filename1 = filename + '.csv' if filename[-3:] != 'csv' else filename
    
    with open(filename1) as file:
        result    = {}
        reader    = csv.reader(file)
        variable  = None
        in_header = False
        in_data   = False
        columns   = []
        table     = []
        curr_line = 0
        first_row = True
        
        for row in reader:
            curr_line += 1
            if first_row:
                first_row = False
                continue
            elif isempty(row):
                continue
            elif row[0] == 'Data':
                if table:
                    #Convert table to pd.DataFrame
                    result[variable] = table_to_DataFrame(table, columns)    
                variable  = row[1]
                in_header = True
                in_data   = False  
            elif in_header:
                columns   = read_header(row, curr_line)
                in_header = False
                in_data   = True
            elif in_data:
                try:
                    row_ = [float(x) for x in row]
                    table.append(row_)
                except:
                    raise Exception('Invalid Data in line ' + curr_line)
                    
        if table:
            #Convert table to pd.DataFrame
            result[variable] = table_to_DataFrame(table, columns)
            
        return result

def isnum(x):
    try:
        float(x)
        return True
    except:
        return False

def isempty(row):
    for i in row:
        if i.rstrip() != '' :
            return False
    return True

def read_header(line, num=0):
    
    trials   = [('Time', 'Time')]
    scenario = ''
    n        = 1
    
    if line[0] != 'Time':
        raise Exception('Line ' + str(num) + 'First column was not Time.')
    
    for i in range(1, len(line)):
        if line[i] == '#':
            break
        elif line[i] == 'Time':
            raise Exception('Line ' + str(num) + ': Additional columns labeled Time.')
        else:   
            if line[i]:
                scenario = line[i]
                n = 1
            
            value  = scenario, n
            trials.append(value)
            n     += 1
    
    return trials        

def table_to_DataFrame(table, columns):
    #Convert to np.array to ensure all lines have same length
    array = np.array(table)
    #Ensure columns does not exceed width of table
    width = array.shape[1]
    diff  = len(columns) - width
    if diff: 
        columns = columns[:-diff]
    #Create DataFrame
    columns = pd.MultiIndex.from_tuples(columns, names=('scenarios', 'trials'))
    result  = pd.DataFrame(data=array, columns=columns)
    table.clear()
    
    return result
        
###############################################################################
#Visualization
###############################################################################   
def plot_time_series_scatter(ts, ts_x=None, skip=[], color_dict={}, figs=[], AX=None, plot_no_match=False, marker='+', legend_args={}, line_args={}):
    
    figs1, AX1, color_dict1, skip1 = setup_plot(ts, skip=skip, figs=figs, AX=AX, color_dict=color_dict)
    for trial in ts:
        if loose_match(trial, skip1):
            continue
        else:
            ax = loose_map(trial, AX1, no_result=plot_no_match)
            if not ax or type(ax) == str:
                continue
            
            color = loose_map(trial, color_dict1, no_result=plot_no_match)
            if type(color) == str:
                if color == '__noresult__':
                    continue
            
            label = make_label(trial)
            ax.ticklabel_format(style='sci', scilimits=(-2,3))
            x = get_x(ts, ts_x,trial)
            ax.plot(x, ts[trial], marker, label=label, color=color, **line_args) 
            try:
                ax.legend(**legend_args)
            except:
                pass

    try:
        list(map(fs, figs1))
    except:
        pass
                                    
    return figs1, AX1

def plot_time_series_errorbar(ts, ts_x=None, skip=[], color_dict={}, figs=[], AX=None, plot_no_match=False, marker='+', legend_args={}, line_args={}, show_err=True):
    ts_mu, ts_sd     = ts   if type(ts) == tuple else (ts.scenario_mean(),   ts.scenario_sd())
    ts_x_mu, ts_x_sd = ts_x if type(ts) == tuple else (ts_x.scenario_mean(), ts_x.scenario_sd()) if type(ts_x) == TimeSeries else (None, None)
    
    figs1, AX1, color_dict1, skip1 = setup_plot(ts_mu, skip=skip, figs=figs, AX=AX, color_dict=color_dict)
    
    for trial in ts_mu:
        if loose_match(trial, skip1):
            continue
        else:
            ax = loose_map(trial, AX1, no_result=plot_no_match)
            if not ax or type(ax) == str:
                continue
            
            color = loose_map(trial, color_dict1, no_result=plot_no_match)
            if type(color) == str:
                if color == '__noresult__':
                    continue
            
            ax.ticklabel_format(style='sci', scilimits=(-2,3))
            x    = get_x(ts_mu, ts_x_mu, trial)
            yerr = ts_sd[trial] if show_err else None
            ax.errorbar(x, ts_mu[trial], yerr=yerr, marker=marker, label=trial, color=color, **line_args) 
            try:
                ax.legend(**legend_args)
            except:
                pass

    try:
        list(map(fs, figs1))
    except:
        pass
                                    
    return figs1, AX1

def get_x(ts, ts_x, key):
    try:
        return ts_x[key].values
    except:
        return ts_x if type(ts_x) in [pd.DataFrame, np.ndarray,list, tuple] else ts['Time'].values

def setup_plot(ts, skip=[], figs=[], AX={}, color_dict={}, palette='bright'):
    skip1       = skip + ['Time', 'Blank']
    if color_dict:
        color_dict1 = color_dict 
    elif type(ts.columns) == pd.Index:
        color_dict1 = make_color_dict(ts.columns, palette=palette)
    else:
        color_dict1 = make_color_dict(ts.columns.levels[0], palette=palette)
    
    if AX:
        AX1   = AX 
        figs1 = figs
    else:
        figs1 = figs if figs else [plt.figure()]
        ax    = figs1[-1].add_subplot(1, 1, 1)
        
        if type(ts.columns) == pd.Index:
            AX1   = {scenario:ax for scenario in ts.columns if not loose_match(scenario, ['Time', 'Blank'])}
        else:
            AX1   = {scenario:ax for scenario in ts.columns.levels[0] if not loose_match(scenario, ['Time', 'Blank'])}
    
    return figs1, AX1, color_dict1, skip1

def make_label(trial):
    try:
        return '_'.join([str(t) for t in trial])
    except:
        return trial
    
def make_color_dict(words, palette='muted'):
    '''
    Generates a color to each word using the palette.
    The palette can be:
        1. The name of a matplotlib palette e.g. 'muted'
        2. A list of tuples containing color values e.g. ['#029386']
        3. A dict with the palette_type: color/light/dark etc. and other keyword arguments e.g. color=all_colors['teal']
        4. A dict mapping each word to a color
    '''
    if type(palette) == dict:
        if palette.get('palette_type'):
            palette_type = palette['palette_type']
            func = palette_types[palette_type]
            colors    = func(len(words)+1, **{key: palette[key] for key in palette if key != 'palette_type'})
            colors    = [tuple(c) for c in colors]
        else:
            return palette
    elif type(palette) == list or type(palette) == tuple:
        colors = palette
        colors = [x if type(x) == tuple or type(x) == list else all_colors[x] for x in colors]
            
    else:
        colors    = sns.color_palette(palette, len(words)+1)
    
    color_dict = {words[i]: colors[i] for i in range(len(words))}
    color_dict['__noresult__'] = colors[-1]
    return color_dict
 
def fs(figure):
    try:
        plt.figure(figure.number)
        backend   = get_backend()
        manager   = plt.get_current_fig_manager()
        
        if backend == 'TkAgg':
            manager.resize(*manager.window.maxsize())
        
        elif backend == 'Qt5Agg' or backend == 'Qt4Agg': 
            manager.window.showMaximized()
        
        else:
            manager.frame.Maximize(True)
        plt.pause(0.03)
    except:
        pass
    return figure
    
    
if __name__ == '__main__':
    plt.close('all')
    try:
        plt.style.use('stylelib/dark_style.mplstyle')
    except:
        pass
    
    #Open the file to see the format
    #It requires minimal preprocessing
    #No need to calculate mean and sd since it can be done here!
    verbose   = False
    filenames = ['examples/Strain A7 M9 Data.csv']
    
    filename = filenames[0]

    TS = import_timeseries(filename)
    
    OD600 = TS['OD600']
    
    #TimeSeries groups the samples into scenarios e.g. inducer conc
    #and trials i.e. replicates for that scenario
    print('scenarios', OD600.scenarios())
    print()
    print('trials', OD600.trials())
    print()
    print(OD600)
    
    OD600.subtract_blank(inplace=True)
    OD600.subtract_initial(inplace=True)
    OD600.cut(stop=400, inplace=True) #Truncate data
    OD600.nth_row(interval=4) #Thin data
    
    #Plot data
    #Colors can be controlled simply by specifying a list of words
    #make_color_dict creates a dict mapping those words to colors determined by the palette argument
    #Scenarios/trials matching that word will be plotted using that color
    #There are multiple ways to specify the palette argument!
    figs  = []
    AX    = []
    words = ['A7.1', 'A7.2', 'A7.3']
    palette = {'palette_type':'light','color': all_colors['cobalt']}
    palette = {'palette_type':'cubehelix', 'start': 0, 'rot': 0.4,}
    color_dict = make_color_dict(words, palette=palette)
    
    #Alternatively, you can specify the whole color_dict yourself
    #In this case, make_color_dict will just ignore the words argument and return the palette
    palette = {'A7.1': all_colors['teal'], 
               'A7.2': all_colors['pale red'], 
               'A7.3': all_colors['soft blue']
               }
    color_dict = make_color_dict(words, palette=palette)
    
    #Plot individual data points or means with errorbars
    figs, AX   = plot_time_series_scatter(OD600, color_dict=color_dict)
    figs, AX   = plot_time_series_errorbar(OD600, color_dict=color_dict)
    
    
    #Create your own layout by passing in a dictionary of axes
    #Each axis is indexed under a word
    #Scenarios/trials matching containing that word will be plotted under that axis
    figs  = [plt.figure()]
    AX_   = [figs[0].add_subplot(3, 1, i+1) for i in range(3)]
    words = ['0.15', '0.2', '0.3']
    AX    = {word[i]: AX_[i] for i in range(len(words))}
    print(AX)

    palette = ['cobalt', 'dull yellow', 'coral' ]
     
    color_dict = make_color_dict(words, palette=palette)
    figs, AX   = plot_time_series_errorbar(OD600, color_dict=color_dict)
    
