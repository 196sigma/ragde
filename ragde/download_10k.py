import urllib
import os
import gzip
import pandas as pd

MASTER_INDEX_DIR = "master"
MASTER_INDEX_DIR_ZIPPED = os.path.join(MASTER_INDEX_DIR, "zipped")
MASTER_INDEX_DIR_UNZIPPED = os.path.join(MASTER_INDEX_DIR, "unzipped")
MASTER_INDEX_DIR_10K_CSV = os.path.join(MASTER_INDEX_DIR, "csv")
_10K_DIR = '10K'

if not os.path.isdir(_10K_DIR):
    os.makedirs(_10K_DIR)
if not os.path.isdir(MASTER_INDEX_DIR):
    os.makedirs(MASTER_INDEX_DIR)
if not os.path.isdir(MASTER_INDEX_DIR_ZIPPED):
    os.makedirs(MASTER_INDEX_DIR_ZIPPED)
if not os.path.isdir(MASTER_INDEX_DIR_UNZIPPED):
    os.makedirs(MASTER_INDEX_DIR_UNZIPPED)
if not os.path.isdir(MASTER_INDEX_DIR_10K_CSV):
    os.makedirs(MASTER_INDEX_DIR_10K_CSV)
    
    
## Download the master index file from the SEC
## Unzip the master index file
## Convert the master index file from pipe-separated to csv, keeping only 10-K like filings
def download_master(year, quarter, storage_path):
    download_url = "https://www.sec.gov/Archives/edgar/full-index/%s/QTR%s/master.gz" % (year, quarter)
    req = urllib.request.urlretrieve(download_url, storage_path)
    if req:
        return 0
    else:
        return -1

def unzip_master(storage_path, unzipped_storage_path):
    i = 0
    with gzip.open(storage_path, 'rb') as infile:
        with open(unzipped_storage_path, 'wb') as outfile:
            for line in infile:
                i += 1
                if i > 11: ## skip header information (metadata)
                    outfile.write(line)
    return i

## TODO: rename 'get_10ks_from_master'
def master_to_csv(unzipped_storage_path, csv_filepath):
    x = pd.read_csv(unzipped_storage_path, sep="|", encoding="latin1", header=None)
    x.columns = ["cik", "company_name", "form_type", "date_filed","edgar_url"]
    form_10k = x[x["form_type"].apply(lambda x: str(x).find("10-K") > -1)]

    form_10k.to_csv(csv_filepath, index=False)
    return None

def run(year, quarter):

    ## Location where raw gzip file of submissions (master) from SEC server will be stored
    storage_path = os.path.join(MASTER_INDEX_DIR_ZIPPED, "master-%s-QTR%s.gz" % (year, quarter))

    ## Location where unzipped "master" file will be stored
    unzipped_storage_path = os.path.join(MASTER_INDEX_DIR_UNZIPPED, "master-%s-QTR%s" % (year, quarter))

    ## Location where CSV file of records of 10-K submissions will be stored
    csv_storage_path =  os.path.join(MASTER_INDEX_DIR_10K_CSV, "master-{}-QTR{}-10K.csv".format(year, quarter))
    
    if not os.path.isfile(storage_path):
        ## Download raw gzip file from SEC server
        download_master(year, quarter, storage_path)
    else:
        print(storage_path, " already exists")
        
    if not os.path.isfile(unzipped_storage_path):
        ## Unzip "master" file
        unzip_master(storage_path, unzipped_storage_path)
    else:
        print(unzipped_storage_path, " already exists")
        
    if not os.path.isfile(csv_storage_path):
        ## Convert "master" (fixed-with file) to csv
        master_to_csv(unzipped_storage_path, csv_storage_path)
    else:
        print(csv_storage_path, " already exists")
        
    return None

def search_cik_by_firm(firm_search_string):
    """
    Return the best matched CIK to a string of firm name
    """
    return cik

def get_10k_by_firm(year, firm):
    """
    Retrieve the appropriate 10-K filing for a given firm by firm name in a given year-quarter.
    """
    cik = search_cik_by_firm(firm)
    
    text_10k = get_10k_by_cik(year, cik)
    
    return text_10k

def get_10k_by_cik(year, cik, verbose=False):
    """
    Retrieve the appropriate 10-K filing for a given firm by CIK in a given year-quarter.
    Returns a list of storage paths for the downloaded 10Ks.
    """
    
    try:
        cik = int(cik)
    except:
        print("CIK must be integer")

    print(cik)

    filing_urls = []
    for quarter in [1,2,3,4]:
        run(year, quarter)

        edgar_url_base = "https://www.sec.gov/Archives/"

        csv_storage_path =  os.path.join(MASTER_INDEX_DIR_10K_CSV, "master-{}-QTR{}-10K.csv".format(year, quarter))

        master_index_csv = pd.read_csv(csv_storage_path)

        filing_urls.extend(list(master_index_csv[master_index_csv['cik'] == cik]['edgar_url']))

    if len(filing_urls) == 0:
        if verbose:
            print("Filing not found for {} in {}, quarter {}".format(cik, year, quarter))
        return

    edgar_urls = [edgar_url_base + filing_url for filing_url in filing_urls]
    storage_paths_10ks = [os.path.join(_10K_DIR, x.split("/")[-1]) for x in edgar_urls]

    output = []
    for edgar_url, storage_path_10k in zip(edgar_urls, storage_paths_10ks):
        try:
            req = urllib.request.urlretrieve(edgar_url, storage_path_10k)
            output.append(storage_path_10k)
        except:
            continue
    return output

def download_10k(firm_id, year):
    if firm_id.isdigit():
        req = get_10k_by_cik(year, firm_id)
    else:
        req = get_10k_by_firm(year, firm_id)
    return req