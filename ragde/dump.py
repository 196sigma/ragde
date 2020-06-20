import os
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
import time
import re
import pickle
import urllib
import gzip

N_PROC = cpu_count()
SLEEP_TIME = 1
## Download filings
output_dir = "D:/10k"

MIN_YEAR = 1994
MAX_YEAR = 2016
HOME_DIR = "."
MASTER_INDEX_DIR = "%s/sec-downloads" % HOME_DIR

def download_index_files(min_year=MIN_YEAR, max_year=MAX_YEAR, quarters=[1, 2, 3, 4], download_dir = MASTER_INDEX_DIR):
    index_base = "https://www.sec.gov/Archives/edgar/full-index/%s/QTR%s/master.gz"
    for year in range(min_year, min_year + 1):
        for quarter in quarters:
            print("Downloading index file for %s, Q%s" % (year, quarter))
            try:
                download_fpath = "%s/master-%s-QTR%s.gz" % (download_dir, year, quarter)
                if not os.path.isdir(download_dir):
                    print("Creating directory for index files at " + download_dir)
                    os.makedirs(download_dir)
                else:
                    print("Directory for index files already exists...")
                print("Downloading index files into "+download_fpath)
                urllib.request.urlretrieve(index_base % (year, quarter), download_fpath)
            except:
                print("WARNING: Download failed!")

            unzip_index_files(download_fpath, download_fpath.replace('.gz',''))
    return 0

## Unzip
def unzip_index_files(path_to_file, path_to_destination):
    print("unzipping file %s" % path_to_file)

    try:
        with gzip.open(path_to_file, 'rb') as infile:
            with open(path_to_destination, 'wb') as outfile:
                for line in infile:
                    outfile.write(line)
    except:
        print("WARNING: Unzip failed!")

    print("All files unzipped!")
    return 0

def download_filing_from_url(filing_url):
    status = -1
    filename = filing_url.split("/")[-1]
    filename = os.path.join(output_dir, filename)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        print("Directory ", output_dir, " Created ")

    if not os.path.isfile(filename):
        time.sleep(SLEEP_TIME)
        status = urllib.request.urlretrieve(filing_url, filename)
    return status


"""
        try:
            time.sleep(.1)
            status = urllib.request.urlretrieve(filing_url, filename)
            #print("Downloaded successfully {} to {}".format(filing_url, filename))
        except:
            print("could not download{}".format(filing_url))
"""

def get_filings_from_index_yearly(master_index_file, filing_type='10K'):
    """
    master_index_file: file with all year-quarter master index files (master.idx) compiled
    """
    filings = []
    if filing_type == '10K':
        with open(master_index_file, "r", encoding='latin-1', errors='surrogateescape') as infile:
            for line in infile:
                line = line.strip().split("|")
                form_type = line[2]
                if re.search(r'^10-K', form_type):
                    filings.append(line)
    elif filing_type == '8K':
        with open(master_index_file, "r") as infile:
            for line in infile:
                line = line.strip().split("|")
                form_type = line[2]
                if re.search(r'^8-K', form_type):
                    filings.append(line)
    elif filing_type == '13F':
        with open(master_index_file, "r") as infile:
            for line in infile:
                line = line.strip().split("|")
                form_type = line[2]
                if re.search(r'^13F', form_type):
                    filings.append(line)

    return filings

def get_filings_from_index_all(master_index_dir, filing_type='10K'):
    filings = []
    master_index_files = os.listdir(master_index_dir)
    for f in master_index_files:
        filings.extend(get_filings_from_index_yearly(f, filing_type=filing_type))
    return filings

def dump(filing_types="10K", filing_years="all", company_id="all"):
    """dump downloads en masse all of the given filing types. For example, all 10-K's
    filing_types: type of filings
    filing_years: years to download filings
    company_id: company CIK or ticker to download filings fow

    returns: None"""
    if filing_types == '10K' and filing_years == 'all':
        download_index_files()
        filings = get_filings_from_index_all(MASTER_INDEX_DIR)

        # TODO: download filings
        # -- append url base to each link from index file
        # -- store filing in appropriate directory (by Year?)
    return None