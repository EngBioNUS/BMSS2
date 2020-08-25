"""
@author: jingwui

https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py
https://pythonspot.com/matplotlib-bar-chart/
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import seaborn as sns
import pandas as pd


def S2heatmap(figNum, S2data, S2CIdata, xylabels, xyticklabel, **kwargs):
    '''Plot the heatmap for second-order sensitivity analysis results.''' 
    fig, (ax,ax2) = plt.subplots(ncols=2, figsize=(18, 6))
    fig.subplots_adjust(wspace=0.01)
    with sns.axes_style("white"):
        sns.heatmap(S2data, cmap="Reds", ax=ax, annot=True,\
                    xticklabels = xyticklabel,\
                    yticklabels = xyticklabel, cbar=False,\
                    linecolor='white', linewidths=.1)
        fig.colorbar(ax.collections[0], ax=ax,location="left",\
                     use_gridspec=False, pad=0.2)
        ax.yaxis.tick_left()
        ax.xaxis.tick_bottom()
        ax.tick_params(rotation=0)
        ax.set_title('Sensitivity Analysis (second-order)')
        sns.heatmap(S2CIdata, cmap="Blues", ax=ax2, annot=True,\
                    xticklabels = xyticklabel,\
                    yticklabels = xyticklabel, cbar=False,\
                    linecolor='white', linewidths=.1)
        fig.colorbar(ax2.collections[0], ax=ax2,location="right",\
                     use_gridspec=False, pad=0.2)
        ax2.yaxis.tick_right()
        ax2.xaxis.tick_bottom()
        ax2.tick_params(rotation=0)
        ax2.set_title('95% Confidence Intervals')
    plt.show()
    
    
def Biheatmap(figNum, df1, df2, xylabels, ax=None, **kwargs):
    '''Plot the combined heatmap for two different datasets.'''
    figsize = (10,6)
    if figsize in kwargs:
        figsize = kwargs.get('figsize')
        
    dfcombine = pd.concat([df1, df2], axis=1)
    
    if len(df2.shape)>1:
        df2len = df2.shape[1]
        data1 = dfcombine.iloc[:,:-df2len]
        data2 = dfcombine.iloc[:,-df2len:]
    else:
        df2len = 1
        data1 = dfcombine.iloc[:,:-1]
        data2 = dfcombine.iloc[:,-1:]
        
    df1len = df1.shape[1]
    widthratio = df1len/df2len
    
    annot = True
    fmt = '.2g'
    
    if 'annot' in kwargs:
        annot = kwargs.get('annot')
        fmt = ''
        
    font_scale= 1.0
    if 'font_scale' in kwargs:
        font_scale = kwargs.get('font_scale')
        sns.set(font_scale=font_scale) 
        
    if not ax is None:
        ax = ax
        axs = ax.subgridspec(nrows = 1, ncols=2, wspace=0.01,\
                             width_ratios = [widthratio, 1+2*(1/df2len)]) 
        ax1 = [plt.subplot(axs[i]) for i, _ in enumerate(axs)]

    else:
        if figNum == []:
            fig, ax1 = plt.subplots(nrows = 1, ncols=2, figsize= figsize,\
             gridspec_kw={'width_ratios': [widthratio, 1+2*(1/df2len)]})  
        else:
            fig, ax1 = plt.subplots(nrows = 1, ncols=2, figsize= figsize,\
             num = figNum, gridspec_kw={'width_ratios': [widthratio, 1+2*(1/df2len)]})
        fig.subplots_adjust(wspace=0.01)
    
    # increase fontsize for all labels   
    with sns.axes_style("white"):
        cmap = plt.get_cmap('Blues')
        sns.heatmap(data1, cmap=truncate_colormap(cmap, 0.2, 1), ax=ax1[0], annot=annot,\
                    fmt = fmt, cbar=False, linecolor='white', linewidths=.1)
        plt.colorbar(ax1[0].collections[0], ax=ax1[0],location="left",\
                     use_gridspec=False, pad=0.13)
        ax1[0].yaxis.tick_left()
        ax1[0].xaxis.tick_bottom()
        ax1[0].tick_params(rotation=0)
        ax1[0].set_title('Configurations')
        ax1[0].set(xlabel = xylabels[0], ylabel = xylabels[1])
        cmap = plt.get_cmap('Reds')
        sns.heatmap(data2, cmap=truncate_colormap(cmap, 0.2, 1), ax=ax1[1], annot=True,\
                    cbar=False, linecolor='white', linewidths=.1)
        cb2 = plt.colorbar(ax1[1].collections[0], ax=ax1[1], location="right",\
                     use_gridspec=False, pad=0.2)
        cb2.ax.yaxis.set_offset_position('left')
        ax1[1].yaxis.tick_right()
        ax1[1].xaxis.tick_bottom()
        ax1[1].tick_params(rotation=0)
        ax1[1].set_title('Output')

    plt.show()
    
    # reset to default
    font_scale= 1.0
    sns.set(font_scale=font_scale) 
    
    return ax1
    

def heatmap(figNum, dataarray, xylabels, xyticklabels, ax=None, **kwargs):
    '''Plot the heatmap.'''
    plt.rcParams["savefig.format"] = 'png'
    plt.rcParams["savefig.dpi"] = 300
    
    figsize = (8,6)
    
    if 'figsize' in kwargs:
        figsize = kwargs.get('figsize')
        
    if not ax is None:
        ax = ax
    else:
        if figNum == []:
            fig = plt.figure(figsize = figsize)   
        else:
            fig = plt.figure(figNum, figsize = figsize)
        ax = fig.add_axes([0.16,0.1,0.78,0.78])     
    
    mask = False
    cmap = plt.get_cmap('Blues')
    annot = True
    fmt = '.2g'
    
    if 'cmap' in kwargs:
        cmap = plt.get_cmap(kwargs.get('cmap'))
    if 'mask' in kwargs:
        mask = kwargs.get('mask')
    if 'annot' in kwargs:
        annot = kwargs.get('annot')
        fmt = ''
        
    new_cmap = truncate_colormap(cmap, 0.2, 1)
    
    font_scale=1.2
    if 'font_scale' in kwargs:
        font_scale = kwargs.get('font_scale')
    # increase fontsize for all labels
    sns.set(font_scale=font_scale)
    with sns.axes_style("white"):
        hm = sns.heatmap(dataarray, annot=annot, fmt = fmt, xticklabels=xyticklabels[0],\
                         yticklabels=xyticklabels[1], cmap=new_cmap, linecolor='white',\
                         linewidths=.1, mask = mask, ax = ax)

    hm.set(xlabel = xylabels[0], ylabel = xylabels[1])
    hm.set_yticklabels(hm.get_yticklabels(), rotation=0)
    hm.set_xticklabels(hm.get_xticklabels(), rotation=0)
    
    if 'savefig' in kwargs:
        plt.savefig(kwargs.get('savefig'), transparent=False)
        
    return ax
    
    
def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    '''Truncate the colormap so that we remove the extreme colors
    such as black and white.
    '''
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap


def plotbar(figNum, data, xylabels, legend = [], alpha = 0.5, ax=None, **kwargs):
    '''Plot the bar chart.'''
    plt.rcdefaults()
    plt.rcParams['font.family'] = 'Calibri' #'Arial'
    plt.rcParams['font.weight'] = 'normal' #'bold'
    plt.rcParams['font.size'] = 18
    plt.rcParams['axes.labelsize'] = 18
    plt.rcParams['axes.labelweight'] = 'normal' #'bold'
    plt.rcParams['axes.linewidth'] = 2
    plt.rcParams['legend.frameon'] = False
    plt.rcParams["legend.handletextpad"] = 0.3
    plt.rcParams["legend.columnspacing"] = 0.5
    plt.rcParams["legend.borderaxespad"] = 0
    plt.rcParams.update({'axes.spines.top': False, 'axes.spines.right': False}) 
    
    figsize = (7,4)
    if 'figsize' in kwargs:
        figsize = kwargs.get('figsize')
        
    if not ax is None:
        ax = ax
    else:
        if figNum == []:
            fig = plt.figure(figsize = figsize)   
        else:
            fig = plt.figure(figNum, figsize = figsize)
        ax = fig.add_axes([0.12,0.16,0.85,0.78]) 
    
    width = 0.5
    #width = 0.25
    
    if 'width' in kwargs:
        width = kwargs.get('width')
    x_pos1 = np.arange(len(data))
    
#    x_pos2 = [x + width for x in x_pos1]
#    x_pos3 = [x + width for x in x_pos2]
    if len(data.shape) > 1:
        
        for i in range(data.shape[1]):
            b1 = ax.bar(x_pos1, data[:,i], width, align='center', label = legend[i], alpha = alpha) #, **kwargs)
    else:
        b1 = ax.bar(x_pos1, data, width, align='center', label = legend, alpha = alpha)#, **kwargs)
    ax.set_xlabel(xylabels[0])
    ax.set_ylabel(xylabels[1])
    
    for key, value in kwargs.items():
        if 'SetYlim' in key:
            ax.set_ylim(value)
        if 'Autolabel' in key:
            if kwargs.get('Autolabel'):
                autolabel(b1, ax, 'bottom')

    ax.legend(loc='upper left',fontsize = 14)
    if legend == []:
        ax.get_legend().set_visible(False)
    # Set Y Axis Ticker to Scientific Style
    ax.ticklabel_format(style='sci', axis='x', scilimits=(-2, 3))
    ax.ticklabel_format(style='sci', axis='y', scilimits=(-2, 1))  # scilimits=(0, 0) for all
    
    if 'set_xticklabels' in kwargs:
        ax.set_xticks(x_pos1)
        ax.set_xticklabels(kwargs.get('set_xticklabels')) #, fontsize = 13, rotation=0)
    
    if 'set_xticklabelsoffset' in kwargs:
        [tick.set_pad(kwargs.get('set_xticklabelsoffset')) for tick in ax.xaxis.get_major_ticks()]
    

def plotfig(figNum, x, y, xylabels = [], legend = [], Errorbarstd = [],
            Correlation = False, ax = None, **kwargs):
    '''Plotting figures with errorbar or lines.'''
    
    # Default settings for figure
    plt.rcdefaults()
    plt.rcParams['font.family'] = 'Calibri' #'Arial'
    plt.rcParams['font.weight'] = 'normal' #'bold'
    plt.rcParams['font.size'] = 18
    plt.rcParams['axes.labelsize'] = 18
    plt.rcParams['axes.labelweight'] = 'normal' #'bold'
    plt.rcParams['axes.linewidth'] = 2
    plt.rcParams['legend.frameon'] = False
    plt.rcParams["legend.handletextpad"] = 0.3
    plt.rcParams["legend.columnspacing"] = 0.5
    plt.rcParams["legend.borderaxespad"] = 0
    plt.rcParams.update({'axes.spines.top': False, 'axes.spines.right': False}) 
    
    figsize = (6,4)
    
    if 'figsize' in kwargs:
        figsize = kwargs.get('figsize')
        
    if not ax is None:
        ax = ax
    else:
        if figNum == []:
            fig = plt.figure(figsize = figsize)   
        else:
            fig = plt.figure(figNum, figsize = figsize)
        ax = fig.add_axes([0.16,0.16,0.8,0.78]) 
        
    if len(y.shape) > 1:
        linestyle = ['solid']*y.shape[1]
    else:
        linestyle = 'solid'
    
    cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    
    for key, value in kwargs.items():
        if 'ResetColor' in key:
            if value == True:
                plt.gca().set_prop_cycle(None)
            else: 
                next
                
        if 'Linestyle' in key:
            linestyle = value
                
        if 'Colors' in key:
            cycle = value
            
#    linestyle = [(0, (5,1)), 'solid', 'dotted', 'solid', (0, (3, 5, 1, 5)), \
#                 'solid', (0,(1,10)), 'solid']
            
    if legend == []:
        if len(y.shape) >1:
            legend = ['']*y.shape[1]
        else:
            legend = ['']
    else:
        legend = legend
        
    #cmap = plt.get_cmap("tab10")
    if Errorbarstd != []:
        if Correlation == True:
            if len(y.shape) > 1:
                for i in range(y.shape[1]):
                #plt.errorbar(x, y[:,i], yerr = Errorbarstd[:,i], capsize = 2, linestyle='None', marker = '.', markersize = 4, label = legend[i])
                    ax.errorbar(x[:,i], y[:,i], yerr = Errorbarstd[:,i], capsize = 2, linestyle='None', 
                                 marker = '.', ms = 10, ecolor = 'k', elinewidth = 1.5, color = cycle[i], #color = cmap(i),
                                 label = legend[i])
            else: 
                ax.errorbar(x, y, yerr = Errorbarstd, capsize = 2, linestyle='None', 
                                 marker = '.', ms = 10, ecolor = 'k', elinewidth = 1.5,
                                 label = legend[0]) 
                        
        else:
            if len(y.shape) > 1:
                for i in range(y.shape[1]):
                    ax.errorbar(x, y[:,i], yerr = Errorbarstd[:,i], capsize = 2, linestyle='None', 
                                 marker = '.', ms = 10, ecolor = 'k', elinewidth = 1.5, color = cycle[i], #cmap(i),
                                 label = legend[i])
            else: 
                ax.errorbar(x, y, yerr = Errorbarstd, capsize = 2, linestyle='None', 
                                 marker = '.', ms = 10, ecolor = 'k', elinewidth = 1.5, 
                                 label = legend[0])
        ax.legend(loc='upper left', prop={'size': 14},frameon=False)
    else:
        if Correlation == True:
            if len(y.shape)>1:
                for j in range(y.shape[1]):
                    ax.plot(x[:,j], y[:,j], label = legend[j], linestyle = linestyle[j],\
                             color = cycle[j], linewidth=2)  # Pep
            else:
                ax.plot(x, y, label = legend[0], linewidth=2)
        else:
            if len(y.shape)>1:
                for j in range(y.shape[1]):
                    ax.plot(x, y[:,j], label = legend[j], linestyle = linestyle[j], \
                             color = cycle[j], linewidth=2)  # Pep
            else:
                ax.plot(x, y, label = legend[0], linewidth=2)
        ax.legend(loc='upper left', prop={'size': 12.5},frameon=False)
    
    handles, labels = ax.get_legend_handles_labels()
    
    if len(handles) > 3: 
        ncol = 2
        loc = 'upper left'
        prop = {'size': 14}
        ax.legend(loc=loc, ncol = ncol, prop=prop,frameon=False)
    
    count = 0
    LinewErrorBar = False
    for key in handles: 
        if 'ErrorbarContainer' in str(key):
            count += 1
        if 'Line2D' in str(key):
            LinewErrorBar = True   
            
    if (count > 0) and (LinewErrorBar == True):
        errorlist = []
        linelist = []
        errorlabel = []
        linelabel = []
        for i in range(count):
            errorlist.append(handles[count+i])
            linelist.append(handles[i])
            errorlabel.append(labels[count+i])
            linelabel.append(labels[i])
            
        handlelist = errorlist + linelist
        labellist = errorlabel + linelabel
        
        if len(handlelist) > 3: 
            ncol = 2
            loc = 'upper left'
            #prop = {'size': 12.5}
            prop = {'size': 12.5}
        else:
            ncol = 1
            loc = 'upper left'
            prop = {'size': 14}
            
        ax.legend(handlelist, labellist, ncol=ncol, loc=loc, prop=prop,frameon=False)
        
    else: 
        pass
    
    if xylabels:
        ax.set_xlabel(xylabels[0])
        ax.set_ylabel(xylabels[1])
    # Set Y Axis Ticker to Scientific Style
    ax.ticklabel_format(style='sci', axis='x', scilimits=(-2, 3))
    ax.ticklabel_format(style='sci', axis='y', scilimits=(-2, 1))  # scilimits=(0, 0) for all
    # Figure border
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # set the y-spine
    #ax.spines['bottom'].set_position('zero')
        
    for key, value in kwargs.items():
        if 'SetZeroXaxis' in key:
            if value == True:
                ax.spines['bottom'].set_position('zero')
            else:
                continue
        if 'SetXlim' in key:
            ax.set_xlim(value)
        if 'SetYtick' in key:
            ax.yaxis.set_ticks(np.arange(value[0], value[1], value[2]))
        if 'SetYlim' in key:
            ax.set_ylim(value)
    
    #plt.tight_layout()
    plt.show()


def autolabel(rects, ax, va):
    '''Attach a text label above each bar displaying its height.'''
    for rect in rects:
        #ax = plt.gca()
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.02*height,
                '%.2E' % height,
                ha='center', va=va, fontsize = 10)
        