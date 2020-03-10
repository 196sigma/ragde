import download_10k
import spacy
from ragde import utils
from collections import Counter
import os

max_limit = 1000000

def shard_text(text, max_limit=1000000):
    output = []
    while len(text) > max_limit:
        output.append(text[:max_limit])
        text = text[max_limit:]
    output.append(text)
    return output

def _filing_named_entities(input_file):
    """
    Helper function. Extracts named entities from a filing.
    Returns [((ent_1, label_1), count_1), ..., ((ent_n, label_n), count_n)]
    """
    
    nlp = spacy.load("en_core_web_sm")

    text = open("10K/0001193125-11-321340.txt", "r").read()
    text = utils.clean_filing(text)  

    named_entities = []
    if len(text) > max_limit:
        text_list = shard_text(text)

        doc_list = [nlp(t) for t in text_list]

        for doc in doc_list:
            for ent in doc.ents:
                named_entities.append((ent.text, ent.label_))
    else:
        doc = nlp(text)
        for ent in doc.ents:
            named_entities.append((ent.text, ent.label_))
    named_entities = Counter(named_entities)
    
    return list(named_entities.most_common())

def filing_named_entities(cik, filing_type, filing_year, output_file="", verbose=False):
    """
    Extracts named entities for a single input. Stores output in output/<output_file>
    """
    
    if not filing_type.replace("-","").lower() == '10k':
        print("Incorrect filing type. Currently supported filing types are:\n* 10K")
        return -1
    HEADER = ['entity', 'label', 'count']
    ## Download the filing
    req = download_10k.download_10k(firm_id=cik, year=filing_year)
    if len(req) == 0:
        print("No annual statements found for given CIK(s) and year(s).")
        return -1

    ## get NEs
    n_files_output = 0 ## in case we need to increment the output filename for multiple filings that are returned
    for storage_path in req:
        output_data = [HEADER]
        print("Extracting named entities from {} in {}".format(filing_type, storage_path))
        ners = filing_named_entities(storage_path)

        if len(output_file)==0:
            output_file = '-'.join([cik, filing_year, filing_type])
        if n_files_output > 0:
            output_file = n_files_output + '-' + output_file
        for row in ners:
            entity = row[0][0]
            label = row[0][1]
            count = row[1]
            output_line = [entity, label, count]
            output_data.append(output_line)

        with open(os.path.join('output',output_file), 'w') as outfile:
            for ln in output_data:
                outfile.write(','.join([str(x) for x in ln]) + '\n')
        n_files_output += 1
        
    return 0

def parse_args(args):
    parser = argparse.ArgumentParser(description='Get readability metrics for company filings.')
    
    parser.add_argument('--cik', help='Firm CIK number', default='', type=str)
    
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
    
    return filing_named_entities(cik=args.cik, 
                             filing_year=args.filing_year,
                             output_file=args.output_file,
                             filing_type=args.filing_type,
                             verbose=args.verbose)

if __name__ == '__main__':
    main()