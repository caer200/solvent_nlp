# Extracting crystallization solvent for literature
The repository contains files for extracting crystallization solvent from supplementary information PDFs using Natural Lanugage Processing (NLP).

# Running the example code.
The example code can be run on google colaboratory using this link [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/caer200/solvent_nlp/blob/main/example.ipynb)

No installation is required.

# Rules for extarcting crystallization solvent
The crystallization solvent is extracted using rule-based method. Shown below are the rules from the [solvent_parser.py](solvent_parser.py) file

```
solvent = (solvent_name + Optional(R('/|and|:|-|&|') + solvent_name))(u'solvent').add_action(join)
prefix = (R('^(re)?(-)?crystalli[sz](ation|ed)$', re.I) +Optional(T('RB')) + Optional(T('IN')) + Optional(I('a') + Optional(T('CD') + W(":") + T('CD')) + (I('mixture') | I('solution')) + I('of')) + Optional(T('JJ'))+ Optional(R('\[|\(|\{')))
crys_sol = (prefix + solvent)(u'crys_sol')
```



## Disclaimer
Web scraping articles from publishers website may need prior approval. The web scraping code provide here by the authors is for demonstration purpose only.
