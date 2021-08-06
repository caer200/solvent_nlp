import re
from chemdataextractor import Document
from chemdataextractor.model import Compound, BaseModel,ModelType,ListType,StringType
from chemdataextractor.parse import R, I, T, Optional, join, W
from chemdataextractor.parse.base import BaseParser
from chemdataextractor.doc import Paragraph
from chemdataextractor.utils import first
from chemdataextractor.parse.cem import solvent_name, CompoundParser

solvent_name = (solvent_name | I("PE") | I("petroleum") + I("ether") | I('H2O'))

class Crystallization(BaseModel):
    solvent = StringType()

Compound.crystallization = ListType(ModelType(Crystallization))
solvent = (solvent_name + Optional(R('/|and|:|-|&|') + solvent_name))(u'solvent').add_action(join)
prefix = (R('^(re)?(-)?crystalli[sz](ation|ed)$', re.I) +Optional(T('RB')) + Optional(T('IN')) + Optional(I('a') + Optional(T('CD') + W(":") + T('CD')) + (I('mixture') | I('solution')) + I('of')) + Optional(T('JJ'))+ Optional(R('\[|\(|\{')))
crys_sol = (prefix + solvent)(u'crys_sol')


class CrySolParser(BaseParser):
    root = crys_sol

    def interpret(self,result, start, end):
        c = Compound()
        s = Crystallization(
            solvent = first(result.xpath('./solvent/text()')),
                            )

        c.crystallization.append(s)
        yield c


Paragraph.parsers = [CompoundParser(), CrySolParser()]