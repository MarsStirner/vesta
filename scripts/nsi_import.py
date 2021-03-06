# -*- coding: utf-8 -*-
import os
import sys
from pymongo import TEXT, ASCENDING
sys.path.insert(0, os.path.dirname('..'))

from app.lib.nsi.data import NSI_Data, kladr_set_parents

obj = NSI_Data()
# obj.import_nsi_dictionaries(['KLD172'])
obj.import_nsi_dictionaries()

obj.create_indexes({'KLD172':[{'name': TEXT, 'level': ASCENDING}],
                    'STR172':[{'name': TEXT}]})

kladr_set_parents()