import argparse
import sys

import readability
import download_10k
import re
from bs4 import BeautifulSoup

readability_metrics = [readability.difficult_words, 
                   readability.flesch_kincaid_grade, 
                   readability.reading_time,
                  readability.text_standard,
                  readability.rix,
                  readability.gunning_fog]

def clean_filing(text):
    text = re.sub(r'[0-9]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\"', '', text)
    
    
    text = BeautifulSoup(text, "lxml").text.encode('ascii', 'ignore').decode("utf-8")
    return text

def _filing_readability(cik, filing_year, output_file = "", filing_type="10K", verbose=False):
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
    
    output_data = [['cik', 'filing_year', 'filing_type', 
                    'difficult_words', 
                    'flesch_kincaid_grade,' 
                    'reading_time',
                    'text_standard',
                    'rix',
                    'gunning_fog']]
    
    metrics = [f(text) for f in readability_metrics]
    output_line = [cik, filing_year, filing_type]
    output_line.extend(metrics)
    output_data.append(output_line)

    with open(output_file, 'w') as outfile:
        for ln in output_data:
            outfile.write(','.join([str(x) for x in ln]) + '\n')

    if verbose:
        print(output_data)
    return

def __filing_readability(input_file, output_file = "", filing_type="10K", verbose=False):

    if not filing_type.replace("-","").lower() == "10k":
        print("Invalid filing type!")
        return
    
    if len(output_file) == 0:
        output_file = "readability.txt"    

    try:
        input_lines = open(input_file, 'r').readlines()
    except:
        print("Invalid input file.")
        return

    output_data = [['cik', 'filing_year', 'filing_type', 
                    'difficult_words', 
                    'flesch_kincaid_grade,' 
                    'reading_time',
                    'text_standard',
                    'rix',
                    'gunning_fog']]
    
    for ln in input_lines:
        ln = ln.strip().split(',')
        cik = ln[0].strip()
        filing_year = ln[1].strip()
        filing_type = ln[2].strip()
        
        ## Download the filing
        for quarter in [1,2,3,4]:
            req = download_10k.download_10k(firm_id=cik, year=filing_year, quarter=quarter)
            if req is not None:
                break
        if req is None:
            print("No annual statements found for given CIK(s) and year(s).")
            return

        text = clean_filing(open(req['storage_path'], 'r').read())
        
        metrics = [f(text) for f in readability_metrics]
        output_line = [cik, filing_year, filing_type]
        output_line.extend(metrics)
        output_data.append(output_line)

        if verbose:
            print(output_data)
            
    with open(output_file, 'w') as outfile:
        for ln in output_data:
            outfile.write(','.join([str(x) for x in ln]) + '\n')
    return

def filing_readability(cik="", filing_year="", input_file="", output_file = "", filing_type="10K", verbose=False):
    if len(input_file) == 0:
        return _filing_readability(cik, filing_year, output_file=output_file, filing_type=filing_type, verbose=verbose)
    else:
        return  __filing_readability(input_file=input_file, output_file=output_file, filing_type=filing_type, verbose=verbose)

def parse_args(args):
    parser     = argparse.ArgumentParser(description='Get readability metrics for company filings.')
    parser.add_argument('--cik', help='Firm CIK number', default='', type=str)
    parser.add_argument('--file', help='An input File with 3-tuple of CIK, filing year, filing type', dest=input_file, default='', type=str)
    parser.add_argument('--output-file', help='Destination on local drive for readability metrics', default="", dest='output_file', type=str)
    parser.add_argument('--filing-year', help='Filing year of desired filing', dest='filing_year', type=str)
    parser.add_argument('--filing-type', help='Filing type of desired filing', default="10K", dest='filing_type', type=str)
    parser.add_argument('--verbose', help='Whether or not to display output', default=False, action='store_false')

    return parser.parse_args(args)

def main(args=None):
    # parse arguments
    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)
    
    return filing_readability(cik=args.cik, 
                             filing_year=args.filing_year,
                             input_file=args.file,
                             output_file=args.output_file,
                             filing_type=args.filing_type,
                             verbose=args.verbose)

if __name__ == '__main__':
    main()