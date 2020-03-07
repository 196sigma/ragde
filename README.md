## ragdE

ragdE (pronounced ragg-ed) is a Python library for textual analysis of company financial disclosures. In the US, publicly traded corporations are required to file many documents about their business activities with the Securities and Exchange Commission (SEC). Based on considerable academic research, ragdE allows you to discover various readability metrics for these filings.

## Installation

The easiest way to install ragdE is to clone this repository and pip install in the terminal/command line:

```
$ git clone git@github.com:196sigma/ragde.git
$ cd ragde
$ pip install .
```

Alternatively, to install ragdE by source code, download this repository and sequentially run following commands in your terminal/command line.

```
$ python setup.py build
$ python setup.py install
```

### Dependencies
* Python3.6+
* pyphen
* numpy

### Testing

```
$ pytest ragdE/tests/tests.py
```

## Usage
You will need to know the Central Index Key (CIK) of the company you are analyzing. These can be searched for on the SEC website: https://www.sec.gov/edgar/searchedgar/cik.htm

```
$ filing_readability --cik 1001039 --output-file 'disney-10k-readability-2011.txt' --filing-year 2011 filing-type 10-K --verbose True
```

For batch processing point the script to a comma-separated file of CIK, filing year, filing type tuples:

```
$ filing_readability --input_file my-companies.txt
```

### Readability Metrics
Current readability metrics supported are:

* difficult words
* Flesch-Kincaid
* Gunning-Fog
* reading time
* rix index
* text standard

### Filing Types
Current filing types (US firms only) supported are:

* 10-K