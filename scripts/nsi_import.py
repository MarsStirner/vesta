# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname('..'))

from app.lib.nsi.data import NSI_Data

obj = NSI_Data()
obj.import_nsi_dictionaries(['KLD116'])
# obj.import_nsi_dictionaries()