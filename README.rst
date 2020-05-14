============
lilo_scraper
============


Retrieve info from locally-saved webpages from LinkedIn.


Description
===========

A web-scraper built on BeautifulSoup to extract information from downloaded LinkedIn job adverts, with URLs like `https://www.linkedin.com/jobs/view/1234567890/`, and compile it all into a CSV file for management in Xcel or Pandas for quick inspection.

The collected information is:

- Intrinsic Data (from LinkedIn)
    - Job ID
    - Job title
    - Company Location
    - Company Name
    - Seniority Level
    - Industry
    - Employment Type
    - Job Functions
    - Number of applicants
 
 - Derived data
    - DE (identifies whether the job ad is in German)
    - Status (based on how webpages are locally stored, determines which jobs are closed, applied for, etc.)
    - Posted Date (a duration fro when the job was first posted)
    - Data of webpage download (used to adjust the Posted Date)

Usage
=====

Basic usage is::

    python lilo_scraping.py -d <./path/saved_webpages_dir> -m <./path/master.csv> -v

Known Issues
============

The master file is assumed to be there from the start, but it is not included. 
    
    
Note
====

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
