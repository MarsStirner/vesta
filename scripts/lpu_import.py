# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname('..'))

from app.lib.lpu.data import LPU_Data

obj = LPU_Data()
obj.import_lpu_dictionaries(obj.get_rb_names())