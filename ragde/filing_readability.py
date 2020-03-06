import readability
import download_10k
import re
from bs4 import BeautifulSoup

def clean_filing(text):
    text = re.sub(r'[0-9]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\"', '', text)
    
    
    text = BeautifulSoup(text, "lxml").text.encode('ascii', 'ignore')
    return text

def get_filing_readability(cik, filing_year, output_file = "", filing_type="10K", verbose=False):
    readability_metrics = ['difficult_words', 'flesch_kincaid_grade']
    
    if len(output_file) == 0:
        output_file = str(cik) + str(filing_year) + "-readability.txt"
    
    if not filing_type.replace("-","").lower() == "10k":
        print("Invalid filing type!")
        return
    
    ## Download the filing
    for quarter in [1,2,3,4]:
        req = download_10k.download_10k(firm_id=cik, year=filing_year, quarter=quarter)
        if req is not None:
            break
    if req is None:
        print("No annual statements found for given CIK(s) and year(s).")
        return

    text = clean_filing(open(req['storage_path'], 'r').read())
    
    output_data = [['cik', 'filing_year', 'filing_type', *readability_metrics]]
    metrics = [eval('readability.'+m+'(text)') for m in readability_metrics]
    output_line = [cik, filing_year, filing_type]
    output_line.extend(metrics)
    output_data.append(output_line)

    with open(output_file, 'w') as outfile:
        for ln in output_data:
            outfile.write(','.join([str(x) for x in ln]) + '\n')

    if verbose:
        print(output_data)
    return

