import re
from bs4 import BeautifulSoup
import string

def clean_filing(text, remove_xbrl=True, to_lower=True, remove_punctuation=True):
    if remove_xbrl:
        xml_start = max(text.find('<XBRL>'), text.find('<xbrl>'))
        text = text[:xml_start]
    
    text = BeautifulSoup(text, "lxml").text.encode('ascii', 'ignore').decode("utf-8")

    text = re.sub(r'[0-9]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\"', '', text)
        
    if to_lower:
        text = text.lower()
        
    if remove_punctuation:
        text = text.translate(str.maketrans('', '', string.punctuation))
        
    return text
