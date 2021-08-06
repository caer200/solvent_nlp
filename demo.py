# Crystallization solvent extraction with NLP

"""We first import the required code"""
import sys, os
sys.path.append(os.path.abspath(__file__))
from webscraping import *        # this code is for webscraping the PDF SI
from solvent_parser import *     # this code parses the solvent from text


""" The function below returns a the compound names and solvent used for crystallization 
 from the parsed records"""
def get_compounds_with_solvent(records):
    data = []
    for compound in records:
        if compound.get("crystallization"):
            data.append(compound)
    return data

""" Let us fetch a SI using the webscraping code """
saveloc = "."  # location to save the PDF
doi = "10.1039/C4OB01574F"

sc = SIScraper(doi=doi, saveloc=saveloc)
sc.retrieveSI()

""" We use chemdataextractor (https://chemdataextractor.org) to do the processsing followed
by tokenization. The rule-based parsing of crystallization solvent is described in the solvent_parser.py.
We use the CompundParser that is built-in chemdataextractor and the SolventParser that we develop to extract
the crystallization solvent """

doc = Document.from_file(sc.filename)  # loading the PDF
records = doc.records.serialize()  # fetching the results from NLP as a python dict
print(get_compounds_with_solvent(records))