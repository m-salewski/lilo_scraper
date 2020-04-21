#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup
import re
import sys
import os

#from internal_processing import get_job_details, get_name_and_loc, get_posted_and_applicants
from internal_processing import get_job_title, get_job_id, get_job_description

# Get the location and local files

def get_files(directory = './saved_webpages/'):
    # bookmark backup directory
    if not os.path.isdir(directory):
        print('Error?', directory)
        
    for path, dirs, files in os.walk(directory):
    # If there are any other directory in the backup directory, 
    # we need to stop the process and get the backup files only
        if path == directory:
            break
        
    files = sorted(files) # sort all the backup files
    
    return files

def get_job_id_wrapper(filename):
        
        # Open the file and soup it
        f = open(filename,'r')
        soup = BeautifulSoup(f.read(), "lxml")
        f.close()

        return get_job_id(soup)    


def get_source_dir(filename, directory, verbose=False):

    change_dirname = True
    
    dirp = filename.replace('.html', "_files")

    #print(dirp)
    source_fpath = directory
    if os.path.isdir(directory+'dirs/'+dirp):
        if verbose: print('\tin dirs/')
        source_fpath += 'dirs/'
    
    elif os.path.isdir(directory+dirp):
        if verbose: print('\tin base')
    else:
        if verbose: print('Nope:',filename)
        change_dirname = False
        
        
    return source_fpath, change_dirname
        

def rename_files_and_dirs(files, directory = './saved_webpages/', verbose=False):

    #main_dir = os.path.abspath(directory)

    if 'Closed/' in directory:
        directory = directory.replace('Closed/','')
    elif 'Closed' in directory:
        directory = directory.replace('Closed','')
    elif 'Applied/' in directory:
        directory = directory.replace('Applied/','')
    elif 'Applied' in directory:
        directory = directory.replace('Applied','')
    else:
        pass
    dirs = directory + 'dirs/'
    
    for file_ in files:

        # Check if the file is already processed
        #if file_.split('_LinkedIn')[1] != '.html':
        if len(file_.split('_LinkedIn')) > 1:            
            if verbose: print('\t\tAlready processed:',file_)
            continue
        else:
            if verbose: print(file_)

        # Get job ID
        filename = directory+file_
        job_id = get_job_id_wrapper(filename)
    
        newname = file_.replace(' ', '_').replace('LinkedIn.html', f'LinkedIn_{job_id}')
            
        source_dpath, change_dirname = get_source_dir(file_, directory, verbose)
        
        source_fpath = os.path.join(directory,file_)
        dest_fpath = os.path.join(directory,newname+'.html')
        os.rename(source_fpath,dest_fpath)
        
        if (change_dirname):
            source_dpath = os.path.join(source_dpath,filename.replace('.html', "_files"))
            dest_dpath = os.path.join(dirs,newname+'_files')
            
            os.rename(source_dpath,dest_dpath)

    return None
