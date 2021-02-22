#!/usr/bin/envthon
# coding: utf-8

#import requests
#from bs4 import BeautifulSoup
#from pandas import DataFrame
#import re
#import datetime
import argparse
import os, re
import sys

import pandas as pd

def get_path(args_master):
    
        """Prepare the paths for the master DB and output DB
        """
        # Get the cwd; set as base path for the outer files
        base_path = os.getcwd()
        output_data_path = os.path.join(base_path)

        master_db = args_master

        # If master, create its path
        if master_db:
            master_db = os.path.join(output_data_path, master_db)
        
        return master_db  

def rename_job(replace_dict):
    
    # define desired replacements in replace_dict
    # use these three lines to do the replacement
    replace_dict = dict((re.escape(k), v) for k, v in replace_dict.items()) 
    #Python 3 renamed dict.iteritems to dict.items so use rep.items() for latest versions
    pattern = re.compile("|".join(replace_dict.keys()))    

    def meth(job_title):    

        return pattern.sub(lambda m: replace_dict[re.escape(m.group(0))], job_title)
    
    return meth

from itertools import permutations

gtags = ['/'.join(l) for l in permutations(['m', 'd','w'], 3)]
gtags += [l.replace('w','f') for l in gtags]
gtags += [l.replace('d','x') for l in gtags]
gtags += [l.upper() for l in gtags]
gtags = ["("+l+")" for l in gtags]


def remove_gender_tags(gender_tags):
    
    def meth(source_str):
    
        for gtag in gender_tags:
            if gtag in source_str:
                return source_str.replace(gtag, '')
                
        return source_str
    
    return meth

remove_gtags=remove_gender_tags(gtags)


def df_processing(df):
    
    first_pass = {
        "Data Scientist": "DS", 
        "Data Engineer": "DE", 
        "Data Analyst": "DA", 
        "Machine Learning Engineer": "ML Eng.",
        "ML Engineer": "ML Eng.",
        "Software Engineer": "Soft. Eng.",
        "Research Engineer": "Res. Eng.",
        "Deep Learning":"DL"
        }

    next_pass = {
        "Modelling": "Model.", 
        "Senior": "Sen.", 
        "Junior": "Jr.", 
        "Machine Learning": "ML",
        "Researcher": "Res.",
        "Analyst": "Anal.",
        "Scientist": "Sci.",    
        }

    df['DE'] = df['DE'].astype(int).astype(str)
    df.loc[(df['DE']=='0'), ['DE']] = ''
    
    df['Company'] = df['Company Name']
    
    df.loc[(df['Seniority Level']=='--missing--'),['Seniority Level']] = '--'
    df['Level']  = df['Seniority Level'].apply(lambda s: s.replace(' level',''))
    
    df['Job title'] = df['Job title'] \
            .apply(rename_job(first_pass)) \
            .apply(rename_job(next_pass)) \
            .apply(remove_gtags)
    
    return df


def main(master_db, sort_by='pdatetime', nr_of_rows=10, ascending=True, verbose=False):
    """
    """
    
    
    #['Status', 'pdate', 'Job ID', 'Job title', 'Easy', 'Company Name', 'DE',
    #   'Company Location', 'Seniority Level', 'Industry', 'Employment Type',
    #   'Job Functions', 'Number of applicants', 'pdatetime', 'Posted Date',
    #    'cdatetime', 'cdate']
    
    scols = ['pdate', 'Job ID', 'Job title', \
             'Company', 'DE', 'Level']

    sort_cols = ['Job title', 'Company Name']

    if (sort_by not in sort_cols) & (sort_by == 'pdatetime'):
        sort_col = 'pdatetime'
    else:
        sort_col = [sort_by, 'pdatetime']
        ascending = [True, ascending]
    
    import pandas as pd

    df = pd.DataFrame()
    
    if os.path.exists(master_db):
        
        #df = pd.read_csv(master_db)        
        
        df = df_processing(pd.read_csv(master_db))
        
        df.sort_values(sort_col, ascending=ascending, inplace=True)
        
        df = df[df['Status']=='3 Open'][scols]
        
        df.reset_index(drop=True, inplace=True)

        #print(df.head(nr_of_rows))
        df.to_csv('temp_output.csv', index=False, sep='%')
        
    else:
        print('Error: Invalid file or path')
        
    return None

if __name__ == '__main__':
    """
    """
    
    # Create the parser
    parser = argparse.ArgumentParser(prog='lilo_read',
                                        usage='%(prog)s [options] path',
                                        description='List the content of a folder')
    #parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

    parser.add_argument('-m',
                        '--master',
                        help='Name of input db',
                        type=str)
    'args.master'
    parser.add_argument('-s',
                        '--sortby',
                        default='pdatetime',
                        help='Column to sort on: \'pdatetime\', \'Job title\', \'Company Name\'',
                        type=str)

    parser.add_argument('-r',
                        '--rows',
                        help='Number of rows to output',
                        type=int)

    parser.add_argument('-a',
                        '--ascending',
                        default=False, 
                        action='store_true',                        
                        help='Ascending order by date')
    
    parser.add_argument('-v',
                        '--verbose',
                        default=False, 
                        action='store_true',                        
                        help='Write processing info to stdio')


    # Execute parse_args()
    args = parser.parse_args()

    # Set up the in/out-put filepaths
    master_db = get_path(args.master)
    
    main(master_db, args.sortby, args.rows, args.ascending, args.verbose)
    
    
