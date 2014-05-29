# -*- coding: utf-8 -*-
import os
import sys
from pymongo import TEXT
sys.path.insert(0, os.path.dirname('..'))

from app.lib.nsi.data import NSI_Data

obj = NSI_Data()
# obj.import_nsi_dictionaries(['KLD116'])
obj.import_nsi_dictionaries()

obj.create_indexes({'KLD116':[{'name', TEXT}],
                    'STR172':[{'name', TEXT}]})