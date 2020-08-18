'''
Make a new project and set up files.
'''

from shutil import copytree
from os     import chdir, getcwd, mkdir

def make_new_project(mode='cmd', new_name=''):
    '''
    Use cmd when not accessing this function via a GUI
    '''
    if mode == 'cmd':
        if new_name == '':
            new_name = input('Type project name here: ')
        
        copytree('template', new_name)
        cwd = getcwd()
        chdir(new_name)
        mkdir('data')
        chdir(cwd)
        
if __name__ == '__main__':
    make_new_project()
