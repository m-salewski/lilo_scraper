# Errors

## `rename_files_and_dirs(files, directory, verbose)`
### `get_job_id`

Specifically, in `job_id = e.split('/jobs/view/')[1].split('/')[0]`
the error looks like this:
```
Traceback (most recent call last):
  File "loli_scraping.py", line 244, in <module>
    main(args.directory, args.master, args.verbose)
  File "loli_scraping.py", line 193, in main
    rename_files_and_dirs(files, directory, verbose)
  File "/home/sandm/Notebooks/LinkedIn_html_scraper/file_processing.py", line 93, in rename_files_and_dirs
    job_id = get_job_id_wrapper(filename)
  File "/home/sandm/Notebooks/LinkedIn_html_scraper/file_processing.py", line 37, in get_job_id_wrapper
    return get_job_id(soup)    
  File "/home/sandm/Notebooks/LinkedIn_html_scraper/internal_processing.py", line 17, in get_job_id
    job_id = e.split('/jobs/view/')[1].split('/')[0]
IndexError: list index out of range
```
**Problem** the string `'/jobs/view/'` was not found, nor was the job ID; the webpage wasn't downloaded correctly
**Solution**: click again on the link, be sure to "Show more", then save the webpage.

### `[Errno 39] Directory not empty:`

**Problem** `os.rename(source_dpath,dest_dpath)` could not write to `dest_path` since it was not empty
```
Traceback (most recent call last):
  File "loli_scraping.py", line 244, in <module>
    main(args.directory, args.master, args.verbose)
  File "loli_scraping.py", line 193, in main
    rename_files_and_dirs(files, directory, verbose)
  File "/home/sandm/Notebooks/LinkedIn_html_scraper/file_processing.py", line 112, in rename_files_and_dirs
    os.rename(source_dpath,dest_dpath)
OSError: [Errno 39] Directory not empty: 'saved_webpages/Senior Data Scientist (m_f_d) for established medtech company | Berlin Brandenburg Airport | LinkedIn_files' -> 'saved_webpages/dirs/Senior_Data_Scientist_m_f_d_for_established_medtech_company__Berlin_Brandenburg_Airport__LinkedIn_1822338647_files'
```
**Solution** Include an additional check, `os.path.isdir(dest_dpath)==False` to ensure the directory does not already exist.

### `TypeError: argument of type 'NoneType' is not iterable` in Applied
```
Traceback (most recent call last):
  File "loli_scraping.py", line 244, in <module>
    main(args.directory, args.master, args.verbose)
  File "loli_scraping.py", line 202, in main
    pdf_new = get_jobs_wrapper(applied_dir,'1 Applied', pdf_new, verbose)
  File "loli_scraping.py", line 28, in get_jobs_wrapper
    pdf_new = get_jobs_df(files,verbose)
  File "loli_scraping.py", line 60, in get_jobs_df
    job_details_list = get_job_details(soup)
  File "/home/sandm/Notebooks/LinkedIn_html_scraper/internal_processing.py", line 45, in get_job_details
    job_details_list = get_cleaned_tags(job_details)
  File "/home/sandm/Notebooks/LinkedIn_html_scraper/helpers.py", line 29, in get_cleaned_tags
    while '  ' in tagtext:
TypeError: argument of type 'NoneType' is not iterable
```
**Solution** Re-seave the html; or exclude since it is in the 'Applied' dir