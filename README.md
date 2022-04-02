# Extracting crystallization solvent from materials science literature
The repository contains files for extracting crystallization solvent from supplementary information PDFs using Natural Lanugage Processing (NLP).

# Running the example code.
The example code can be run on google colaboratory using this link [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/caer200/solvent_nlp/blob/main/example.ipynb)

No installation is required.

# Rules for extarcting crystallization solvent
The crystallization solvent is extracted using rule-based method. The general rule is to search for solvent that follows the word crystallize or recrystallize. Shown below are the rules from [solvent_parser.py](solvent_parser.py) file.

```
solvent = (solvent_name + Optional(R('/|and|:|-|&|') + solvent_name))(u'solvent').add_action(join)
prefix = (R('^(re)?(-)?crystalli[sz](ation|ed)$', re.I) +Optional(T('RB')) + Optional(T('IN')) + Optional(I('a') + Optional(T('CD') + W(":") + T('CD')) + (I('mixture') | I('solution')) + I('of')) + Optional(T('JJ'))+ Optional(R('\[|\(|\{')))
crys_sol = (prefix + solvent)(u'crys_sol')
```

Here `solvent` accounts for variations in mentions of crystallization solvent. The following scenarios are accounted
- single solvent (ex. methanol)
- multiple solvents (ex. methanol/hexane, methanol and hexane, methanol:hexane, methanol & hexane)

`prefix` captures the occurences of word (re)crystallize and the words that follow it. Examples
- recrystallized from
- crystallized from
- crystallized from mixture of
- crystallized (solvent)
- recrystallized in 

`crys_sol` combines the `prefix` and `solvent` so that the text can be parsed to extract the solvent.

## Disclaimer
Web scraping articles from publishers website may need prior approval. The web scraping code provide here by the authors is for demonstration purpose only.
