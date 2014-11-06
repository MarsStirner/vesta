# -*- coding: utf-8 -*-
from .config import MODULE_NAME, RUS_NAME
from flask import Blueprint

module = Blueprint(MODULE_NAME, __name__,
                   template_folder='templates',
                   static_folder='static',
                   static_url_path='/{0}'.format(__name__))


@module.context_processor
def module_name():
    return dict(module_name=RUS_NAME)

from .views import *