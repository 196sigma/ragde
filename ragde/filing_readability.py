import argparse
import sys

from ragde import readability
from ragde import download_10k
from ragde.utils import *

readability_metrics = [readability.difficult_words, 
                   readability.flesch_kincaid_grade, 
                   readability.reading_time,
                  readability.text_standard,
                  readability.rix,
                  readability.gunning_fog]
HEADER = ['cik', 'filing_year', 'filing_type', 
                    'difficult_words', 
                    'flesch_kincaid_grade,' 
                    'reading_time',
                    'text_standard',
                    'rix',
                    'gunning_fog']


def _filing_readability(cik, filing_year, output_file = "", filing_type="10K", verbose=False):
    """
    Calculate readability metrics for a single input
    """
    if len(output_file) == 0:
        output_file = str(cik) + str(filing_year) + "-readability.txt"
    
    if not filing_type.replace("-","").lower() == "10k":
        print("Invalid filing type!")
        return -1
    
    ## Download the filing
    req = download_10k.download_10k(firm_id=cik, year=filing_year)
    if len(req) == 0:
        print("No annual statements found for given CIK(s) and year(s).")
        return -1
    
    output_data = [HEADER]
    for storage_path in req:
        text = clean_filing(open(storage_path, 'r').read())
        metrics = [f(text) for f in readability_metrics]
        output_line = [cik, filing_year, filing_type]
        output_line.extend(metrics)
        output_data.append(output_line)

    with open(output_file, 'w') as outfile:
        for ln in output_data:
            outfile.write(','.join([str(x) for x in ln]) + '\n')

    if verbose:
        print(output_data)
    return 0

def __filing_readability(input_file, output_file = "", filing_type="10K", verbose=False):
    """
    Calculates readability metrics for a batch (csv input file)
    """

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

    output_data = [HEADER]
    
    for ln in input_lines:
        ln = ln.strip().split(',')
        cik = ln[0].strip()
        filing_year = ln[1].strip()
        filing_type = ln[2].strip()
        
        ## Download the filing
        req = download_10k.download_10k(firm_id=cik, year=filing_year)
        if len(req) == 0:
            print("No annual statements found for given CIK(s) and year(s).")
            return

        for storage_path in req:
            text = clean_filing(open(storage_path, 'r').read())

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
    if len(input_file) == 0: ## Single input
        return _filing_readability(cik, filing_year, output_file=output_file, filing_type=filing_type, verbose=verbose)
    else: ## Batch input
        print("Batch processing ...")
        return  __filing_readability(input_file=input_file, output_file=output_file, filing_type=filing_type, verbose=verbose)

def parse_args(args):
    parser = argparse.ArgumentParser(description='Get readability metrics for company filings.')
    
    parser.add_argument('--cik', help='Firm CIK number', default='', type=str)
    
    parser.add_argument('--file', help='An input File with 3-tuple of CIK, filing year, filing type', 
                        dest='input_file', 
                        default='', type=str)
    
    parser.add_argument('--output-file', help='Destination on local drive for readability metrics', 
                        default="", dest='output_file', type=str)
    
    parser.add_argument('--filing-year', help='Filing year of desired filing', dest='filing_year', type=str)
    
    parser.add_argument('--filing-type', help='Filing type of desired filing', default="10K", dest='filing_type', type=str)
    
    parser.add_argument('--verbose', help='Whether or not to display output', default=False, action='store_true')

    return parser.parse_args(args)

def main(args=None):
    # parse arguments
    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)
    
    return filing_readability(cik=args.cik, 
                             filing_year=args.filing_year,
                             input_file=args.input_file,
                             output_file=args.output_file,
                             filing_type=args.filing_type,
                             verbose=args.verbose)

if __name__ == '__main__':
    main()