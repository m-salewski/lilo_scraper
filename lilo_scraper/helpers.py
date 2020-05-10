#!/usr/bin/envthon
# coding: utf-8

import datetime

def get_deutsch(trial_text):
    if ('ü' in trial_text) | \
	('Ü' in trial_text) | \
	('ö' in trial_text) | \
	('Ö' in trial_text) | \
	('ä' in trial_text) | \
	('Ä' in trial_text):
        return True         
    elif (' der ' in trial_text) | \
	(' dem ' in trial_text) | \
	(' den ' in trial_text) | \
	(' das ' in trial_text) | \
	('Die ' in trial_text) | \
	('Der ' in trial_text) | \
	('Das ' in trial_text):
        return True    
    else: 
        return False


def get_cleaned_tags(tagtext):
    
    # Clean the double spaces
    while '  ' in tagtext:
        tagtext = tagtext.replace('  ',' ')
    
    # Clean the double returns
    while '\n\n' in tagtext:
        tagtext = tagtext.replace('\n\n', '')  
    
    # Split into a list of words based on the intrisic returns
    tagtext = tagtext.split('\n')
    
    # used str.split to clean the rest
    tagtext = [e.strip() for e in tagtext if e.strip() != '']
    
    return tagtext

# TODO put _all_ keys here!!!
job_detail_keys = [
    'Company Name', 
    'Company Location',
    'Seniority Level',
    'Industry',
    'Employment Type',
    'Job Functions',
    'Posted Date',
    'Number of applicants'
]

def get_job_details_dc(job_detail_keys):
    
    # Check for missing keys
    def check_in_list(in_list):
        for k in job_detail_keys:
        
            if k not in in_list:
                in_list += [k,'--missing--']
        return in_list
    
    def inner(job_details_list):

        job_details_dc = {}
        
        job_details_list = check_in_list(job_details_list)
        
        inds = sorted([job_details_list.index(k) for k in job_detail_keys])
        
        inds += [len(job_details_list)+1]
        
        for a,b in zip(inds[:-1],inds[1:]):
            k = job_details_list[a]
            v = job_details_list[a+1:b]
            job_details_dc[k] = v
            #print(a,b,k,v)

        return job_details_dc
    
    return inner


def clean_dict(dc):

    new_dc = {}
    for k,v in dc.items():

        if type(v) == list:
            #print(k,v)
            if len(v) > 1:
                newv = ''
                
                for e in v[:-1]:
                    newv += e + " | "
                newv += v[-1]
                
            elif len(v) == 0:
                newv = '--missing--'
            else:
                newv = v[0]
        else: 
            newv = v
        new_dc[k] = newv
    
    return new_dc


from datetime import timedelta

def get_adj_date(time,today):
    
    if 'month' in time:
        week_multiplier = 28
    elif 'week' in time:
        week_multiplier = 7
    elif 'day' in time:
        week_multiplier = 1
    else:
        week_multiplier = 0
    
    if time != '--missing--':
        units = int(time.split('Posted ')[1].split()[0])
    else:
        units = 0
        
    days_to_subtract = units*week_multiplier

    adjusted_date = today - timedelta(days=days_to_subtract)

    #adjusted_date = str(d.date())#.split(' ')[0].replace('-','.')
    
    return str(adjusted_date.date()),adjusted_date
