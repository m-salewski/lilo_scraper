#!/usr/bin/env python
# coding: utf-8

from helpers import get_cleaned_tags
from helpers import job_detail_keys, get_job_details_dc

def get_job_id(soup):

    job_id = None

    for step in soup.find_all("meta", {"name":"apple-itunes-app"}):
        attr_list = step.attrs['content'].split()

        for e in attr_list:
            if 'voyager' in e:
                voyager = e
        job_id = e.split('/jobs/view/')[1].split('/')[0]

    return job_id


def get_job_description(soup):

    job_descr = None
    
    for step in soup.find_all("div", {"class":"jobs-box__html-content jobs-description-content__text t-14 t-black--light t-normal"}):
        job_descr = step.text
    
    return job_descr


def get_job_title(soup):
    for tag in soup.find_all('h1',  {'class':"jobs-top-card__job-title t-24"}):
        job_title = tag.text.strip()
    
    return job_title

    
def get_job_details(soup):
    
    job_details = None
    for tag in soup.find_all('div',  {'class':"jobs-description-details ember-view"}):
        job_details = tag.text.strip()
    
    job_details_list = get_cleaned_tags(job_details)
    
    return job_details_list


def get_name_and_loc(soup):
    
    # Get the name of the company and the location
    name_and_loc = []
    for tag in soup.find_all('h3',  {'class':"jobs-top-card__company-info t-14 mt1"}):
        name_and_loc.append(tag.text.split('\n'))
    
    name_and_loc = [e.strip() for e in [e.strip() for e in name_and_loc[0]] if e != '']
    
    return name_and_loc
    
    
def get_posted_and_applicants(soup):
    
    date_posted = []
    
    for tag in soup.find_all('p', {'class':"mt1 full-width flex-grow-1 t-14 t-black--light"}):
        date_posted.append(tag.text)

    date_posted = date_posted[0]
    
    date_posted = get_cleaned_tags(date_posted)
    posted_applicants = [e for e in date_posted if e != 'New']    

    return posted_applicants


def get_applicants(soup): 
    """
    obsolete
    """
    # Get the number of applicants
    applicants = []
    for tag in soup.find_all('span', {'class':"jobs-top-card__bullet"}):
        applicants.append(tag.text)
        
    if len(applicants) > 1:       
        inds = [i for i, x in enumerate(applicants) if "applicants" in x]

        new_appls = ""
        for i in inds:            
            new_appls += applicants[i]
        
        applicants = new_appls
    else:
        applicants = applicants[0]
        
    applicants = get_cleaned_tags(applicants)
    
    return applicants
