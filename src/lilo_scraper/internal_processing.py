#!/usr/bin/envthon
# coding: utf-8

from helpers import get_cleaned_tags
from helpers import job_detail_keys, get_job_details_dc
import re

def get_job_id(soup, verbose=False):
    """
    """
    job_id = None

    for step in soup.find_all("meta", {"name":"apple-itunes-app"}):
        #print(step)
        attr_list = step.attrs['content'].split()

        for e in attr_list:
            try:
                if 'voyager' in e:
                    
                    splits = ['/jobs/view/','/']
                    job_id = e.split(splits[0])[1].split(splits[1])[0]
                    if '?' in job_id:
                        job_id = job_id.split('?')[0]
                    break
            except:
                if verbose: print("\tno voyager")
                pass
            
            try:
                if 'currentJobId=' in e:
                    splits = ['currentJobId=','&']
                    job_id = e.split(splits[0])[1].split(splits[1])[0]
                    if verbose: print('currentJobId=', job_id)
                    break
            except:
                if verbose: print("\tno currentJobId")
                pass
            
        if job_id != None:
            if verbose: print(job_id)
            break
    
    return job_id


def get_job_description(soup):
    """
    """
    job_descr = None
    tag = "jobs-box__html-content jobs-description-content__text t-14 t-black--light t-normal"
    for step in soup.find_all("div", {"class": tag}):    
        job_descr = step.text
    
    if job_descr == None:
        tag = "jobs-box__html-content jobs-description-content__text t-14 t-normal"
        for step in soup.find_all("div", {"class": tag}): 
            job_descr = step.text
    
    return job_descr


def get_job_title(soup):
    """
    """
    job_title = ''
    for tag in soup.find_all('h1',  {'class':"jobs-top-card__job-title t-24"}):
        job_title = tag.text.strip()
    if job_title == '' or job_title == None:
        # Update 01.12.2020
        job_title = soup.find('h1',  {'class':"t-24"}).text.strip()
        #job_title = ['Job title', job_title]
        
    return job_title


def get_job_details(soup):
    """
    """
    job_details = None
    for tag in soup.find_all('div',  {'class':"jobs-description-details ember-view"}):
        job_details = tag.text.strip()
        
    if job_details == None:
        job_details = ''
        for tag in soup.find_all('div',  {'class':"jobs-box__group"}):
            job_details+=tag.text.strip()+'\n'

    job_details_list = get_cleaned_tags(job_details)
    
    return job_details_list


def get_name_and_loc(soup):
    """
    Get the Compnay name and location
    
    Note: these were usually together in a tag 
    """
    #TODO: check to see if this can be superceded by json-scraping
    # Get the name of the company and the location
    name_and_loc = []
    # Legacy version; until 01.12.2020
    for tag in soup.find_all('h3',  {'class':"jobs-top-card__company-info t-14 mt1"}):
        name_and_loc.append(tag.text.split('\n'))
    
    if name_and_loc != []:
        name_and_loc = [e.strip() for e in [e.strip() for e in name_and_loc[0]] if e != '']
    else:
        # Update from 01.12.2020
        tags = soup.find('div',{'class':"mt2"})

        #name = tags.find('a', {'class':"ember-view t-black t-normal"}).text.strip()
        for tt in tags.find_all('span'):
            if tt.attrs != {}:
                for k in tt.attrs['class']:
                    # Note: 'subtitle-primary-grouping' is not unique to getting the company's name
                    if 'subtitle-primary-grouping' in k:
                        # NOTE: this may not work;
                        name = tt.text.strip().split('\n\n')[0].strip()
                        break

        loc = tags.find('span', {'class':"jobs-unified-top-card__bullet"}).text.strip()

        name_and_loc = ['Company Name', name, 'Company Location', loc]
        
    return name_and_loc
    
    
def get_posted_and_applicants(soup):
    """
    """
    
    #TODO: clean and remove the `if`-part of this conditional; maybe `else` is enough
    date_posted = []
    
    for tag in soup.find_all('p', {'class':"mt1 full-width flex-grow-1 t-14 t-black--light"}):
        date_posted.append(tag.text)

    if date_posted != []:
        date_posted = date_posted[0]
        
        date_posted = get_cleaned_tags(date_posted)
        output = [e for e in date_posted if e != 'New']  
    
    else:
        # Update from 01.12.2020
        date_posted = get_date_posted(soup)

        posted_applicants = get_applicants(soup)

        output = ['Posted Date', date_posted, 'Number of applicants', posted_applicants]

    return output


def get_date_posted(soup):
    """
    """
    date_posted = soup.find('span', string=re.compile(" ago"))
    #NOTE: this could also contain "Posted (.*) ago"
    
    if (date_posted == None) | (date_posted == ''):
        
        # If empty, check if closed
        date_posted = soup.find(string=re.compile("No longer accepting"))
        
        if (date_posted == None) | (date_posted == ''):
            return 'MISSING'
        else: 
            return date_posted.strip()
    else:
        return date_posted.text.strip()
    
    
def get_applicants(soup):
    """
    """
    # Works as planned!
    try:
        for t in soup.find_all(string=re.compile(" applicant")):        
            tt = t.replace("Over","").strip().split(' ')
            if (len(tt) == 2) & (tt[0] != 'Top'):
                #print(t)
                return t
    except:
        pass
    
    # Tag 1
    final_result = ''
    try:
        results = soup.find_all('span',class_=re.compile(" applicant"))
        count=0
        for result in results:
            if 'applicant' in result.text.strip():
                final_result = result.text.strip()
                return final_result 
    except:
        pass
    # Alternative Tag 1 (also applies to older versions?)
    try:
        result = soup.find('div',string=re.compile("Be an early applicant"))     
        #print(result.text.strip())
        final_result = "< 25 applicants"#result.text.strip() 
        return final_result
    except:
        pass

    # Tag 2, oldest version
    try:
        result = soup.find('span',class_="ml1")      
        final_result = result.text.strip() 
        return final_result
    except:
        pass

    # Reporting the results
    return final_result


def get_applicants_(soup): 
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


def get_easy_apply(soup, verbose=False):
    """
    Check if the ad offers "Easy Apply" (only with LinkedIn)
    """
    # Usually looks like this:
    # <span class="artdeco-button__text">
    tag = soup.find("span", class_="artdeco-button__text", string=re.compile("Easy Apply"))
    
    if verbose: print(tag)
    
    if tag != None:
        return True
    else:
        return False
